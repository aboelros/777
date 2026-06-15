"""
Enhanced AI Bot endpoints with conversation memory, order extraction, and social media monitoring.
"""

from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
import structlog
import hashlib
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Project, MessageDirection
from app.services.enhanced_ai_service import EnhancedAIService
from app.services.social_media_monitor import SocialMediaMonitor

router = APIRouter()
logger = structlog.get_logger(__name__)


class MessageWithContext(BaseModel):
    """Message with full context for intelligent processing."""
    customer_message: str
    customer_id: str
    platform: str  # whatsapp, instagram, facebook, telegram, tiktok
    customer_name: Optional[str] = None
    order_id: Optional[str] = None


class OrderExtractionRequest(BaseModel):
    """Request to extract order from message."""
    message: str
    customer_id: str
    platform: str
    auto_create: bool = False  # Automatically create order if detected


class CommentReplyRequest(BaseModel):
    """Request to generate comment reply."""
    comment_id: UUID
    use_templates: bool = True
    auto_send: bool = False


class PostAnalysisRequest(BaseModel):
    """Request to analyze post."""
    post_id: UUID
    analyze_comments: bool = True


class BusinessContextCreate(BaseModel):
    """Create business context."""
    context_type: str  # brand_voice, policy, product_info, faq
    context_key: str
    title: str
    content: str
    tags: list[str] = []
    platforms: list[str] = []  # Empty for all platforms


class AutoResponseConfig(BaseModel):
    """Configure auto-response settings."""
    max_responses_per_run: int = 10
    post_id: Optional[UUID] = None


async def verify_project_access(project_id: UUID, user_id: str, db: AsyncSession) -> Project:
    """Helper to verify user has access to project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project


# ============================================================================
# Conversation Memory & Context Endpoints
# ============================================================================

@router.post("/{project_id}/message/process-with-context")
async def process_message_with_full_context(
    project_id: UUID,
    message: MessageWithContext,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Process message with full conversation context and memory.
    
    **Features:**
    - Retrieves conversation history
    - Uses customer profile
    - Applies business context
    - Generates personalized response
    - Saves conversation for future reference
    """
    await verify_project_access(project_id, user_id, db)
    
    # 🔒 DISTRIBUTED LOCK: Prevent duplicate processing if this endpoint is used as a webhook
    clean_id = str(message.customer_id).split('@')[0].replace('+', '').replace(' ', '').strip()
    clean_text = message.customer_message.strip()
    lock_key_str = f"{clean_id}:{clean_text}"
    lock_key = int(hashlib.sha256(lock_key_str.encode('utf-8')).hexdigest()[:15], 16)
    
    lock_result = await db.execute(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": lock_key})
    if not lock_result.scalar():
        logger.warning("🔒 LOCK: EnhancedBot skipping duplicate", customer_id=message.customer_id)
        return {"success": False, "status": "skipped"}
    
    ai_service = EnhancedAIService(db, project_id)
    
    try:
        # Determine persona: WhatsApp/Telegram -> Sales Agent, Others -> Business Assistant
        # This ensures webhooks get Sales Agent, while Website gets Business Assistant
        persona = "ai_saler" if message.platform in ["whatsapp", "telegram"] else "web_assistant"

        # Generate context-aware response
        result = await ai_service.generate_context_aware_response(
            customer_message=message.customer_message,
            customer_id=message.customer_id,
            platform=message.platform,
            order_id=UUID(message.order_id) if message.order_id else None,
            persona=persona
        )
        
        # Update customer profile
        await ai_service.update_customer_profile(
            customer_id=message.customer_id,
            platform=message.platform,
            name=message.customer_name
        )
        
        logger.info(
            "Message processed with context",
            project_id=str(project_id),
            customer_id=message.customer_id
        )
        
        return {
            "success": True,
            "response": result["response"],
            "intent": result["intent"],
            "sentiment": result["sentiment"],
            "context_used": result["context_used"]
        }
        
    except Exception as e:
        logger.error("Failed to process message", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/{project_id}/conversation/{customer_id}")
async def get_conversation_history(
    project_id: UUID,
    customer_id: str,
    platform: str,
    limit: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get conversation history for a customer.
    
    Returns past messages with context and analysis.
    """
    await verify_project_access(project_id, user_id, db)
    
    ai_service = EnhancedAIService(db, project_id)
    
    history = await ai_service.get_conversation_history(
        customer_id=customer_id,
        platform=platform,
        limit=limit
    )
    
    return {
        "customer_id": customer_id,
        "platform": platform,
        "total_messages": len(history),
        "history": [
            {
                "id": str(h.id),
                "content": h.message_content,
                "direction": h.message_direction.value,
                "intent": h.intent,
                "sentiment": h.sentiment,
                "summary": h.summary,
                "created_at": h.created_at.isoformat()
            }
            for h in history
        ]
    }


@router.get("/{project_id}/customer/{customer_id}/profile")
async def get_customer_profile(
    project_id: UUID,
    customer_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get comprehensive customer profile with purchase history and preferences.
    """
    await verify_project_access(project_id, user_id, db)
    
    ai_service = EnhancedAIService(db, project_id)
    profile = await ai_service.get_customer_profile(customer_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    
    return {
        "customer_id": profile.customer_id,
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone,
        "platform_accounts": profile.platform_accounts,
        "preferred_language": profile.preferred_language,
        "preferred_platform": profile.preferred_platform,
        "communication_style": profile.communication_style,
        "interaction_count": profile.interaction_count,
        "total_orders": profile.total_orders,
        "total_spent": profile.total_spent,
        "average_order_value": profile.average_order_value,
        "customer_type": profile.customer_type,
        "overall_sentiment": profile.overall_sentiment,
        "satisfaction_score": profile.satisfaction_score,
        "interests": profile.interests,
        "is_vip": profile.is_vip,
        "last_interaction": profile.last_interaction.isoformat() if profile.last_interaction else None,
        "first_interaction": profile.first_interaction.isoformat() if profile.first_interaction else None
    }


# ============================================================================
# Order Extraction Endpoints
# ============================================================================

@router.post("/{project_id}/order/extract-from-message")
async def extract_order_from_message(
    project_id: UUID,
    request: OrderExtractionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Extract order information from customer message using AI.
    
    **Can detect:**
    - Product names and quantities
    - Delivery addresses
    - Special instructions
    - Urgency level
    
    **Optional:** Automatically create order if detected
    """
    await verify_project_access(project_id, user_id, db)
    
    ai_service = EnhancedAIService(db, project_id)
    
    try:
        # Extract order data
        order_data = await ai_service.extract_order_from_message(
            message_content=request.message,
            customer_id=request.customer_id,
            platform=request.platform
        )
        
        if not order_data:
            return {
                "order_detected": False,
                "message": "No order information found in message"
            }
        
        # Create order if requested
        created_order = None
        if request.auto_create and order_data.get("is_order"):
            created_order = await ai_service.create_order_from_message(
                customer_id=request.customer_id,
                platform=request.platform,
                order_data=order_data
            )
        
        return {
            "order_detected": True,
            "confidence": order_data.get("confidence"),
            "order_data": order_data,
            "order_created": created_order is not None,
            "order_id": str(created_order.id) if created_order else None,
            "order_external_id": created_order.external_id if created_order else None
        }
        
    except Exception as e:
        logger.error("Failed to extract order", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract order: {str(e)}"
        )


# ============================================================================
# Business Context Management
# ============================================================================

@router.post("/{project_id}/context/create")
async def create_business_context(
    project_id: UUID,
    context: BusinessContextCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create business-specific context for AI to use.
    
    **Context Types:**
    - brand_voice: How the business communicates
    - policy: Return policy, shipping policy, etc.
    - product_info: Detailed product information
    - faq: Frequently asked questions
    - common_response: Common situations and responses
    """
    await verify_project_access(project_id, user_id, db)
    
    from app.db.models import BusinessContext
    
    business_context = BusinessContext(
        project_id=project_id,
        context_type=context.context_type,
        context_key=context.context_key,
        title=context.title,
        content=context.content,
        tags=context.tags,
        active_for_platforms=context.platforms,
        learned_from="manual",
        confidence_score=1.0
    )
    
    db.add(business_context)
    await db.commit()
    await db.refresh(business_context)
    
    logger.info("Business context created", context_id=str(business_context.id))
    
    return {
        "success": True,
        "context_id": str(business_context.id),
        "message": "Business context created successfully"
    }


@router.get("/{project_id}/context/list")
async def list_business_contexts(
    project_id: UUID,
    context_type: Optional[str] = None,
    platform: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all business contexts for the project.
    """
    await verify_project_access(project_id, user_id, db)
    
    ai_service = EnhancedAIService(db, project_id)
    contexts = await ai_service.get_business_context(
        context_type=context_type,
        platform=platform
    )
    
    return {
        "total": len(contexts),
        "contexts": [
            {
                "id": str(c.id),
                "type": c.context_type,
                "key": c.context_key,
                "title": c.title,
                "content": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                "tags": c.tags,
                "times_used": c.times_used,
                "relevance_score": c.relevance_score,
                "platforms": c.active_for_platforms
            }
            for c in contexts
        ]
    }


# ============================================================================
# Social Media Post Monitoring
# ============================================================================

@router.post("/{project_id}/posts/analyze")
async def analyze_social_post(
    project_id: UUID,
    request: PostAnalysisRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Analyze a social media post using AI.
    
    **Extracts:**
    - Sentiment analysis
    - Main topics
    - Keywords
    - Engagement metrics
    - Comment sentiment
    """
    await verify_project_access(project_id, user_id, db)
    
    monitor = SocialMediaMonitor(db, project_id)
    
    try:
        analysis = await monitor.analyze_post(
            post_id=request.post_id,
            fetch_comments=request.analyze_comments
        )
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error("Failed to analyze post", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze post: {str(e)}"
        )


@router.post("/{project_id}/comments/generate-reply")
async def generate_comment_reply(
    project_id: UUID,
    request: CommentReplyRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate AI-powered reply to a social media comment.
    
    **Features:**
    - Uses templates when available
    - Personalized responses
    - Platform-appropriate tone
    - Optional auto-send
    """
    await verify_project_access(project_id, user_id, db)
    
    monitor = SocialMediaMonitor(db, project_id)
    
    try:
        reply = await monitor.generate_comment_reply(
            comment_id=request.comment_id,
            use_templates=request.use_templates,
            auto_send=request.auto_send
        )
        
        return {
            "success": True,
            **reply
        }
        
    except Exception as e:
        logger.error("Failed to generate reply", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate reply: {str(e)}"
        )


@router.post("/{project_id}/comments/auto-respond")
async def auto_respond_comments(
    project_id: UUID,
    config: AutoResponseConfig,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Automatically respond to pending comments.
    
    **Prioritizes:**
    - Urgent/negative comments
    - Questions
    - High-value customers
    
    **Safety:** Won't auto-respond to complex issues requiring human attention.
    """
    await verify_project_access(project_id, user_id, db)
    
    monitor = SocialMediaMonitor(db, project_id)
    
    try:
        results = await monitor.auto_respond_to_comments(
            post_id=config.post_id,
            max_responses=config.max_responses_per_run
        )
        
        return {
            "success": True,
            **results
        }
        
    except Exception as e:
        logger.error("Failed to auto-respond", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to auto-respond: {str(e)}"
        )


@router.post("/{project_id}/posts/{post_id}/learn")
async def learn_from_post(
    project_id: UUID,
    post_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Learn from high-performing post and update business context.
    
    **Extracts insights about:**
    - What content works
    - Optimal posting times
    - Audience preferences
    - Engagement patterns
    """
    await verify_project_access(project_id, user_id, db)
    
    monitor = SocialMediaMonitor(db, project_id)
    
    try:
        learnings = await monitor.learn_from_post_performance(post_id)
        
        return {
            "success": True,
            **learnings
        }
        
    except Exception as e:
        logger.error("Failed to learn from post", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to learn from post: {str(e)}"
        )


# ============================================================================
# Statistics & Insights
# ============================================================================

@router.get("/{project_id}/insights/overview")
async def get_ai_insights_overview(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get comprehensive AI insights overview.
    
    **Includes:**
    - Total conversations tracked
    - Customer profiles created
    - Business contexts learned
    - Orders extracted from messages
    - Comments auto-responded
    """
    await verify_project_access(project_id, user_id, db)
    
    from app.db.models import ConversationHistory, CustomerProfile, BusinessContext, SocialMediaComment
    from sqlalchemy import func, select
    
    # Count conversations
    result = await db.execute(
        select(func.count(ConversationHistory.id))
        .where(ConversationHistory.project_id == project_id)
    )
    conversation_count = result.scalar() or 0
    
    # Count customer profiles
    result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(CustomerProfile.project_id == project_id)
    )
    customer_count = result.scalar() or 0
    
    # Count business contexts
    result = await db.execute(
        select(func.count(BusinessContext.id))
        .where(BusinessContext.project_id == project_id)
    )
    context_count = result.scalar() or 0
    
    # Count auto-responded comments
    result = await db.execute(
        select(func.count(SocialMediaComment.id))
        .where(
            and_(
                SocialMediaComment.project_id == project_id,
                SocialMediaComment.responded == True,
                SocialMediaComment.auto_generated == True
            )
        )
    )
    auto_response_count = result.scalar() or 0
    
    # Count unresponded comments
    result = await db.execute(
        select(func.count(SocialMediaComment.id))
        .where(
            and_(
                SocialMediaComment.project_id == project_id,
                SocialMediaComment.responded == False
            )
        )
    )
    pending_comments = result.scalar() or 0
    
    return {
        "conversations_tracked": conversation_count,
        "customer_profiles": customer_count,
        "business_contexts": context_count,
        "comments_auto_responded": auto_response_count,
        "pending_comments": pending_comments,
        "ai_learning_active": context_count > 0
    }
