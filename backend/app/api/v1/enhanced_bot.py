"""
Enhanced AI Bot endpoints with conversation memory, order extraction, and business context.
"""

from typing import Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import hashlib
from sqlalchemy import text

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.services.enhanced_ai_service import EnhancedAIService
from app.api.v1.enhanced_bot_social import social_router
from app.api.v1.enhanced_bot_context import context_router
from app.api.v1.enhanced_bot_schemas import (
    MessageWithContext,
    OrderExtractionRequest,
    BusinessContextCreate,
)

router = APIRouter()
router.include_router(social_router)
router.include_router(context_router)
logger = structlog.get_logger(__name__)


@router.post("/{project_id}/message/process-with-context")
async def process_message_with_full_context(
    project_id: UUID,
    message: MessageWithContext,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Process message with full conversation context and memory.
    """
    clean_id = str(message.customer_id).split('@')[0].replace('+', '').replace(' ', '').strip()
    clean_text = message.customer_message.strip()
    lock_key_str = f"{clean_id}:{clean_text}"
    lock_key = int(hashlib.sha256(lock_key_str.encode('utf-8')).hexdigest()[:15], 16)

    lock_result = await db.execute(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": lock_key})
    if not lock_result.scalar():
        logger.warning("🔒 LOCK: EnhancedBot skipping duplicate", customer_id=message.customer_id)
        return {"success": False, "status": "skipped"}

    ai_service = EnhancedAIService(db, context.project_id)

    try:
        persona = "ai_saler" if message.platform in ["whatsapp", "telegram"] else "web_assistant"

        result = await ai_service.generate_context_aware_response(
            customer_message=message.customer_message,
            customer_id=message.customer_id,
            platform=message.platform,
            order_id=UUID(message.order_id) if message.order_id else None,
            persona=persona
        )

        await ai_service.update_customer_profile(
            customer_id=message.customer_id,
            platform=message.platform,
            name=message.customer_name
        )

        logger.info(
            "Message processed with context",
            project_id=str(context.project_id),
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
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get conversation history for a customer.
    """
    ai_service = EnhancedAIService(db, context.project_id)

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
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get comprehensive customer profile.
    """
    ai_service = EnhancedAIService(db, context.project_id)
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


@router.post("/{project_id}/order/extract-from-message")
async def extract_order_from_message(
    project_id: UUID,
    request: OrderExtractionRequest,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Extract order information from customer message using AI.
    """
    ai_service = EnhancedAIService(db, context.project_id)

    try:
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
