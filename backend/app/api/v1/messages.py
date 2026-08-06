"""
Message management and communication endpoints.
"""

from typing import List, Any, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, update
from sqlalchemy.orm import joinedload, selectinload
import structlog
from app.core.config import settings

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.projects.models import Project, ProjectRole
from app.domains.messages.models import Message, MessageDirection
from app.domains.orders.models import Order
from app.domains.customers.models import CustomerProfile
from app.domains.messages.schemas import MessageSend, MessageResponse, ConversationSummary, ConversationMessage
from app.domains.customers.schemas import CustomerProfileResponse
from app.domains.messages.service import MessageService
from app.core.uow import UnitOfWork

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    return MessageService(UnitOfWork(db))


async def verify_project_access(
    project_id: UUID, 
    user_id: str, 
    db: AsyncSession,
    required_roles: List[ProjectRole] = None
) -> Project:
    """Helper to verify user has access to project."""
    from app.core.access_control import verify_project_access as base_verify
    return await base_verify(project_id, user_id, db, required_roles)


@router.patch("/{project_id}/customers/{profile_id}/toggle-ai")
async def toggle_customer_ai(
    project_id: UUID,
    profile_id: UUID,
    enabled: bool,
    user_id: str = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service)
) -> Any:
    """Enable or disable AI automation for a specific customer."""
    return await service.toggle_customer_ai(str(project_id), str(profile_id), enabled, user_id)


def _sanitize_name(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    placeholders = ["Instagram User", "Facebook User", "Unknown", "User"]
    if name.strip() in placeholders:
        return None
    return name.strip()


def _get_api_base_url(request: Request) -> str:
    """Resolve the absolute base URL for the API."""
    if settings.API_BASE_URL:
        return settings.API_BASE_URL.rstrip("/")
    # Fallback to current request URL host
    scheme = request.url.scheme
    host = request.url.netloc
    return f"{scheme}://{host}"


def _to_absolute_url(url: Optional[str], base_url: str) -> Optional[str]:
    """Convert relative storage paths to absolute URLs."""
    if not url:
        return None
    if url.startswith("http"):
        return url
    path = url.lstrip("/")
    return f"{base_url}/{path}"


def _resolve_customer_payload(msg: Message) -> Dict[str, Any]:
    if msg.direction == MessageDirection.INBOUND:
        return msg.sender or {}
    return msg.recipient or {}


def _resolve_conversation_id(msg: Message, customer_payload: Dict[str, Any]) -> str:
    # 1. Prefer linked Customer Profile ID (Gold Standard)
    if msg.customer_id:
        return str(msg.customer_id)

    # 2. Extract platform ID from payload
    # Payload usually comes from 'sender' (inbound) or 'recipient' (outbound)
    platform_id = customer_payload.get("id") or customer_payload.get("customer_id")
    
    candidate_fields = [
        platform_id,
        customer_payload.get("profile_id"),
        customer_payload.get("conversation_id"),
        customer_payload.get("phone"),
        customer_payload.get("email"),
        customer_payload.get("username"),
        # Fallback to order ID last to prevent splitting
        str(msg.order_id) if msg.order_id else None,
    ]

    for candidate in candidate_fields:
        if candidate:
            return str(candidate)

    # Fallback to message id to ensure uniqueness
    return f"message-{msg.id}"


@router.post("/{project_id}/send", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    project_id: UUID,
    message_data: MessageSend,
    user_id: str = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service)
) -> Any:
    """
    Send a message to a customer via specified provider.
    
    Supported providers: whatsapp, telegram, sms, instagram, facebook
    
    This creates a database record and queues the actual sending via background worker.
    """
    return await service.send_message(str(project_id), user_id, message_data)


@router.get("/{project_id}/inbox", response_model=List[MessageResponse])
async def get_inbox(
    project_id: UUID,
    request: Request,
    direction: Optional[str] = Query(None, description="Filter by direction: inbound or outbound"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    order_id: Optional[UUID] = Query(None, description="Filter by order ID"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    days: int = Query(7, description="Number of days to look back", ge=1, le=90),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get unified inbox with messages from all channels.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Build query
    query = select(Message).options(joinedload(Message.customer)).where(Message.project_id == project_id)
    
    # Apply filters
    if direction:
        query = query.where(Message.direction == direction)
    if provider:
        # Standardize: check both provider and platform for Meta channels
        if provider.lower() in ["instagram", "facebook", "whatsapp"]:
            query = query.where(or_(
                Message.provider == provider, 
                Message.platform == provider,
                and_(Message.provider == "meta", Message.platform == provider)
            ))
        else:
            query = query.where(Message.provider == provider)
    if order_id:
        query = query.where(Message.order_id == order_id)
    if is_read is not None:
        query = query.where(Message.is_read == is_read)
    
    # Date filter
    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.where(Message.created_at >= start_date)
    
    # Order and pagination
    query = query.order_by(Message.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Manually populate avatar_url from customer profile for MessageResponse
    base_url = _get_api_base_url(request)
    for msg in messages:
        if msg.customer:
            msg.avatar_url = _to_absolute_url(msg.customer.avatar_url, base_url)
            
    return messages


@router.get("/{project_id}/conversations", response_model=List[ConversationSummary])
async def get_conversations(
    project_id: UUID,
    request: Request,
    provider: Optional[str] = Query(None, description="Filter by provider/channel"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=180),
    limit: int = Query(50, description="Maximum conversations to return", ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by customer name, email, phone, or message"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Return aggregated conversation summaries for messaging inbox."""

    await verify_project_access(project_id, user_id, db)

    query = select(Message).options(selectinload(Message.customer)).where(Message.project_id == project_id)

    if provider and provider.lower() != "all":
        query = query.where(Message.provider == provider)

    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.where(Message.created_at >= start_date)

    # Pull recent messages (over-fetch to build summaries reliably)
    query = query.order_by(Message.created_at.desc()).limit(limit * 10)

    result = await db.execute(query)
    messages = result.scalars().all()

    conversations: dict[str, dict[str, Any]] = {}
    
    # Resolve absolute URL base for avatars
    base_url = _get_api_base_url(request)

    for msg in messages:
        try:
            customer_payload = _resolve_customer_payload(msg)
            conversation_id = _resolve_conversation_id(msg, customer_payload)

            is_vip = False
            
            # --- HISTORICAL RECONCILIATION ---
            # If the database foreign key is missing, try a dynamic lookup
            # This 'connects' orphan historical messages to the latest database data.
            current_customer = msg.customer
            if not current_customer:
                platform_id = customer_payload.get("id") or customer_payload.get("customer_id")
                if platform_id:
                    # Try to find the profile in the DB by its platform identity
                    # We search platform_accounts JSONB or basic fields
                    lookup_query = select(CustomerProfile).where(
                        CustomerProfile.project_id == project_id,
                        or_(
                            CustomerProfile.customer_id == str(platform_id),
                            CustomerProfile.phone == str(platform_id),
                            CustomerProfile.email == str(platform_id)
                        )
                    )
                    lookup_res = await db.execute(lookup_query)
                    current_customer = lookup_res.scalar_one_or_none()
            
            try:
                if current_customer:
                    real_name = current_customer.name
                    customer_email = current_customer.email
                    customer_phone = current_customer.phone
                    customer_avatar = current_customer.avatar_url
                    customer_profile_id = str(current_customer.id)
                    overall_sentiment = current_customer.overall_sentiment
                    is_vip = current_customer.is_vip
            except Exception:
                # Relationship access error
                pass
            
            convo = conversations.get(conversation_id)
            if not convo:
                convo = {
                    "channel": msg.platform or msg.provider or "unknown",
                    "customer_name": _sanitize_name(real_name) 
                    or _sanitize_name(customer_payload.get("name"))
                    or _sanitize_name(customer_payload.get("customer_name"))
                    or _sanitize_name(customer_payload.get("username")),
                    "customer_email": customer_email or customer_payload.get("email"),
                    "customer_phone": customer_phone or customer_payload.get("phone"),
                    "customer_avatar": _to_absolute_url(
                        customer_avatar 
                        or customer_payload.get("avatar_url") 
                        or customer_payload.get("profile_pic")
                        or customer_payload.get("profile_picture_url"),
                        base_url
                    ),
                    "customer_id": (customer_payload.get("customer_id") if customer_payload else None)
                    or customer_payload.get("customer_id")
                    or customer_payload.get("id")
                    or customer_payload.get("phone")
                    or customer_payload.get("email"),
                    "order_id": str(msg.order_id) if msg.order_id else None,
                    "last_message": None,
                    "last_message_at": None,
                    "unread_count": 0,
                    "total_messages": 0,
                    "ai_messages": 0,
                    "ai_enabled": False,
                    "recipient": customer_payload or {},
                    "profile_id": customer_profile_id or customer_payload.get("profile_id"),
                    "overall_sentiment": overall_sentiment,
                    "is_vip": is_vip,
                }
                conversations[conversation_id] = convo

            convo["total_messages"] += 1
            if msg.ai_generated:
                convo["ai_messages"] += 1
                convo["ai_enabled"] = True

            if msg.direction == MessageDirection.INBOUND and not msg.is_read:
                convo["unread_count"] += 1

            created_at = msg.created_at
            if created_at and (
                convo["last_message_at"] is None or created_at > convo["last_message_at"]
            ):
                convo["last_message_at"] = created_at
                convo["last_message"] = msg.content
                convo["channel"] = msg.platform or msg.provider or convo["channel"]
                
                # Update name if we found a better one (e.g. from profile)
                if real_name:
                    convo["customer_name"] = real_name
                elif not convo["customer_name"]:
                    convo["customer_name"] = (
                        customer_payload.get("name")
                        or customer_payload.get("customer_name")
                    )
                    
                convo["customer_email"] = (
                    customer_email or customer_payload.get("email") or convo["customer_email"]
                )
                convo["customer_phone"] = (
                    customer_phone or customer_payload.get("phone") or convo["customer_phone"]
                )
                convo["customer_avatar"] = (
                    customer_avatar or convo["customer_avatar"]
                )
                convo["customer_id"] = (
                    customer_payload.get("customer_id")
                    or customer_payload.get("customer_id")
                    or customer_payload.get("id")
                    or convo["customer_id"]
                )
                if msg.order_id:
                    convo["order_id"] = str(msg.order_id)
                
                # Update profile_id if available
                if customer_profile_id:
                    convo["profile_id"] = customer_profile_id
                elif not convo["profile_id"] and customer_payload.get("profile_id"):
                    convo["profile_id"] = customer_payload.get("profile_id")
                    
                convo["overall_sentiment"] = (
                    overall_sentiment or convo["overall_sentiment"]
                )
                convo["is_vip"] = (
                    is_vip or convo["is_vip"]
                )
                convo["recipient"] = customer_payload or {}
        except Exception as e:
            logger.error(f"Error processing message {msg.id}: {str(e)}")
            continue

    summaries: List[ConversationSummary] = []
    search_term = search.lower() if search else None

    import traceback

    for convo_id, data in conversations.items():
        try:
            if not data["last_message_at"]:
                continue

            if search_term:
                haystack = " ".join(
                    filter(
                        None,
                        [
                            data.get("customer_name"),
                            data.get("customer_email"),
                            data.get("customer_phone"),
                            data.get("last_message"),
                        ],
                    )
                ).lower()

                if search_term not in haystack:
                    continue
            
            # Ensure all fields match the schema
            summary = ConversationSummary(
                id=convo_id,
                channel=data["channel"],
                customer_name=data["customer_name"],
                customer_email=data["customer_email"],
                customer_phone=data["customer_phone"],
                customer_id=data["customer_id"],
                customer_avatar=data["customer_avatar"],
                order_id=data["order_id"],
                last_message=data["last_message"],
                last_message_at=data["last_message_at"],
                unread_count=data["unread_count"],
                total_messages=data["total_messages"],
                ai_messages=data["ai_messages"],
                ai_enabled=data["ai_enabled"],
                recipient=data["recipient"] or {}, # Ensure dict
                profile_id=data["profile_id"],
                overall_sentiment=data["overall_sentiment"],
                is_vip=data["is_vip"],
            )
            summaries.append(summary)
        except Exception as e:
            logger.error(f"Error creating summary for convo {convo_id}: {str(e)}")
            traceback.print_exc()
            continue

    # Sort by last message time
    summaries.sort(key=lambda x: x.last_message_at or datetime.min, reverse=True)
    
    if limit:
        return summaries[:limit]
    return summaries


@router.get(
    "/{project_id}/conversations/{conversation_id}/messages",
    response_model=List[ConversationMessage],
)
async def get_conversation_messages(
    project_id: UUID,
    conversation_id: str,
    request: Request,
    provider: Optional[str] = Query(None, description="Filter by provider/channel"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=180),
    limit: int = Query(200, description="Maximum messages to inspect", ge=50, le=500),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Return messages belonging to the resolved conversation identifier."""

    await verify_project_access(project_id, user_id, db)

    query = select(Message).options(selectinload(Message.customer)).where(Message.project_id == project_id)

    if provider and provider.lower() != "all":
        # Standardize: check both provider and platform for Meta channels
        if provider.lower() in ["instagram", "facebook", "whatsapp"]:
            query = query.where(or_(
                Message.provider == provider, 
                Message.platform == provider,
                and_(Message.provider == "meta", Message.platform == provider)
            ))
        else:
            query = query.where(Message.provider == provider)

    start_date = datetime.utcnow() - timedelta(days=days)
    query = query.where(Message.created_at >= start_date)

    query = query.order_by(Message.created_at.desc()).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    matched: List[Message] = []
    for msg in messages:
        payload = _resolve_customer_payload(msg)
        if _resolve_conversation_id(msg, payload) == conversation_id:
            matched.append(msg)

    matched.sort(key=lambda item: item.created_at or datetime.min)

    # --- BATCH SENDER RECONCILIATION ---
    # For all matched messages, ensure we have the latest name/avatar from the profile DB
    # even if the message itself is an orphan.
    final_messages = []
    base_url = _get_api_base_url(request)
    
    # Pre-fetch profiles for these messages to avoid N+1 lookups
    # (Actually we rely on joinedload/selectinload if already linked, 
    # but for orphans we do individual lookups or a smart batch lookup if needed)
    
    for message in matched:
        msg_customer = message.customer
        if not msg_customer:
            # Recompute payload to lookup profile
            c_payload = _resolve_customer_payload(message)
            p_id = c_payload.get("id") or c_payload.get("customer_id")
            if p_id:
                l_query = select(CustomerProfile).where(
                    CustomerProfile.project_id == project_id,
                    or_(
                        CustomerProfile.customer_id == str(p_id),
                        CustomerProfile.phone == str(p_id)
                    )
                )
                l_res = await db.execute(l_query)
                msg_customer = l_res.scalar_one_or_none()

        # Build consistent sender object
        sender_info = {**(message.sender or {})}
        if msg_customer and message.direction == MessageDirection.INBOUND:
            # Override with latest DB values
            sender_info["name"] = _sanitize_name(msg_customer.name) or sender_info.get("name")
            sender_info["avatar_url"] = _to_absolute_url(
                msg_customer.avatar_url or sender_info.get("avatar_url"),
                base_url
            )
        else:
            # Still sanitize name and resolve avatar to absolute for non-inbound or no-customer cases
            if not sender_info.get("name"):
                sender_info["name"] = _sanitize_name(sender_info.get("name"))
            
            if sender_info.get("avatar_url"):
                sender_info["avatar_url"] = _to_absolute_url(sender_info["avatar_url"], base_url)

        final_messages.append(
            ConversationMessage(
                id=message.id,
                direction=message.direction,
                provider=message.provider,
                content=message.content,
                content_type=message.content_type,
                created_at=message.created_at,
                ai_generated=message.ai_generated,
                status=message.status,
                sender=sender_info,
                recipient=message.recipient or {},
                metadata=message.extra_data or {},
                attachments=message.attachments
            )
        )

    return final_messages


@router.get("/{project_id}/{message_id}", response_model=MessageResponse)
async def get_message(
    project_id: UUID,
    message_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service)
) -> Any:
    """
    Get a single message by ID.
    """
    return await service.get_message(str(project_id), str(message_id), user_id)


@router.patch("/{project_id}/{message_id}/read", response_model=MessageResponse)
async def mark_message_read(
    project_id: UUID,
    message_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: MessageService = Depends(get_message_service)
) -> Any:
    """
    Mark a message as read.
    """
    return await service.mark_message_read(str(project_id), str(message_id), user_id)


@router.get("/{project_id}/conversation/{order_id}", response_model=List[MessageResponse])
async def get_conversation(
    project_id: UUID,
    order_id: UUID,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get full conversation thread for an order.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Verify order exists
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .where(Order.project_id == project_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get all messages for this order
    result = await db.execute(
        select(Message)
        .where(Message.order_id == order_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    
    # Normalize avatar URLs
    base_url = _get_api_base_url(request)
    for msg in messages:
        if hasattr(msg, 'avatar_url') and msg.avatar_url:
            msg.avatar_url = _to_absolute_url(msg.avatar_url, base_url)
        if msg.sender and msg.sender.get("avatar_url"):
            msg.sender["avatar_url"] = _to_absolute_url(msg.sender["avatar_url"], base_url)
            
    return messages


@router.get("/{project_id}/stats/summary")
async def get_message_stats(
    project_id: UUID,
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get message statistics for a project.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total messages
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .where(Message.created_at >= start_date)
    )
    messages = result.scalars().all()
    
    total_messages = len(messages)
    inbound_count = sum(1 for m in messages if m.direction == MessageDirection.INBOUND)
    outbound_count = sum(1 for m in messages if m.direction == MessageDirection.OUTBOUND)
    ai_generated_count = sum(1 for m in messages if m.ai_generated)
    unread_count = sum(1 for m in messages if not m.is_read and m.direction == MessageDirection.INBOUND)
    
    # Messages by provider
    messages_by_provider = {}
    for message in messages:
        provider = message.provider
        messages_by_provider[provider] = messages_by_provider.get(provider, 0) + 1
    
    # Total AI cost
    total_ai_cost = sum(m.ai_cost or 0 for m in messages)
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": datetime.utcnow().isoformat(),
        "total_messages": total_messages,
        "inbound_messages": inbound_count,
        "outbound_messages": outbound_count,
        "ai_generated_messages": ai_generated_count,
        "unread_messages": unread_count,
        "messages_by_provider": messages_by_provider,
        "total_ai_cost": float(total_ai_cost),
        "automation_rate": (ai_generated_count / outbound_count * 100) if outbound_count > 0 else 0.0
    }


@router.patch("/{project_id}/conversations/{conversation_id}/read", status_code=status.HTTP_200_OK)
async def mark_conversation_read(
    project_id: UUID,
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Mark all unread inbound messages in a conversation as read.
    """
    await verify_project_access(project_id, user_id, db)

    # 1. Fetch unread inbound messages for the project (recent ones, e.g. last 30 days)
    # We restrict the scan to recent messages for performance.
    
    start_date = datetime.utcnow() - timedelta(days=30)
    
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .where(Message.direction == MessageDirection.INBOUND)
        .where(Message.is_read == False)
        .where(Message.created_at >= start_date)
        .order_by(Message.created_at.desc())
    )
    unread_messages = result.scalars().all()
    
    # 2. Filter for matching conversation_id
    messages_to_update = []
    for msg in unread_messages:
        payload = _resolve_customer_payload(msg)
        if _resolve_conversation_id(msg, payload) == conversation_id:
            messages_to_update.append(msg.id)
            
    # 3. Bulk update
    if messages_to_update:
        await db.execute(
            update(Message)
            .where(Message.id.in_(messages_to_update))
            .values(is_read=True)
        )
        await db.commit()
        
    return {"count": len(messages_to_update), "status": "success"}


@router.delete("/{project_id}/conversations/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation_messages(
    project_id: UUID,
    conversation_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete all messages belonging to a specific conversation.
    """
    # 1. Verify project access
    await verify_project_access(project_id, user_id, db)

    # 2. Fetch all messages for the project to find matching conversation_id
    # We scan messages from the last 90 days to find members of this conversation
    start_date = datetime.utcnow() - timedelta(days=90)
    
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .where(Message.created_at >= start_date)
    )
    all_messages = result.scalars().all()
    
    # 3. Identify messages belonging to the conversation
    messages_to_delete = []
    outbound_meta_messages = [] # Track outbound messages for unsend
    
    for msg in all_messages:
        payload = _resolve_customer_payload(msg)
        if _resolve_conversation_id(msg, payload) == conversation_id:
            messages_to_delete.append(msg.id)
            if msg.direction == MessageDirection.OUTBOUND and msg.provider == "meta" and msg.external_id:
                outbound_meta_messages.append({
                    "id": msg.external_id,
                    "platform": msg.platform
                })
            
    # 4. Attempt platform-side unsend for outbound messages
    if outbound_meta_messages:
        try:
            from app.domains.ai.orchestrator import AIOrchestrator
            orchestrator = AIOrchestrator(db)
            await orchestrator.initialize_integrations(project_id)
            
            for meta_msg in outbound_meta_messages:
                client = orchestrator.integration_clients.get(meta_msg["platform"])
                if client and hasattr(client, "unsend_message"):
                    await client.unsend_message(meta_msg["id"])
        except Exception as e:
            logger.warning("Failed to unsend some messages on platform", error=str(e))

    # 5. Perform bulk deletion
    count = 0
    if messages_to_delete:
        from sqlalchemy import delete
        delete_stmt = delete(Message).where(Message.id.in_(messages_to_delete))
        await db.execute(delete_stmt)
        await db.commit()
        count = len(messages_to_delete)
        
    logger.info(
        "Conversation cleared",
        project_id=str(project_id),
        conversation_id=conversation_id,
        deleted_count=count
    )
    
    return {
        "status": "success",
        "message": f"Successfully deleted {count} messages",
        "deleted_count": count
    }
@router.get("/{project_id}/customers/{profile_id}", response_model=CustomerProfileResponse)
async def get_customer_profile(
    project_id: UUID,
    profile_id: UUID,
    request: Request,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Return detailed customer profile for intelligence sidebar."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(CustomerProfile)
        .where(CustomerProfile.project_id == project_id)
        .where(CustomerProfile.id == profile_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    # Normalize avatar_url to absolute
    if profile.avatar_url:
        base_url = _get_api_base_url(request)
        profile.avatar_url = _to_absolute_url(profile.avatar_url, base_url)
    
    return profile
