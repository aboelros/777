"""
AI Chat Bot endpoints for automatic customer conversation management.
"""

from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.projects.models import Project
from app.services.ai_chat_bot import get_chat_bot

router = APIRouter()
logger = structlog.get_logger(__name__)


class IncomingMessage(BaseModel):
    """Incoming customer message."""
    customer_message: str
    customer_id: str
    channel: str  # whatsapp, telegram, discord, tiktok, instagram, facebook
    order_id: str | None = None
    customer_phone: str | None = None
    customer_email: str | None = None


class OrderInquiry(BaseModel):
    """Order status inquiry."""
    customer_id: str
    order_number: str
    channel: str


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


@router.post("/{project_id}/process-message")
async def process_message(
    project_id: UUID,
    message: IncomingMessage,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Process an incoming customer message with AI.
    
    The AI bot will:
    - Understand the customer's intent
    - Provide an appropriate response
    - Take necessary actions (update orders, send tracking, etc.)
    - Escalate to human if needed
    
    **Supported Channels:**
    - WhatsApp
    - Telegram
    - Discord
    - TikTok
    - Instagram
    - Facebook
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get AI chat bot with usage tracking
    chat_bot = get_chat_bot(db, project_id, UUID(user_id))
    
    # Process message
    try:
        result = await chat_bot.process_incoming_message(
            customer_message=message.customer_message,
            customer_id=message.customer_id,
            channel=message.channel,
            order_id=UUID(message.order_id) if message.order_id else None,
            customer_phone=message.customer_phone,
            customer_email=message.customer_email
        )
        
        return {
            "success": True,
            "response": result["response"],
            "intent": result.get("intent"),
            "actions_taken": result.get("actions_taken", []),
            "should_escalate": result.get("should_escalate", False),
            "tokens_used": result.get("tokens_used"),
            "cost": result.get("cost")
        }
        
    except Exception as e:
        logger.error("Failed to process message", error=str(e), project_id=str(project_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/{project_id}/order-inquiry")
async def handle_order_inquiry(
    project_id: UUID,
    inquiry: OrderInquiry,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle specific order status inquiry.
    
    Provides detailed order status information including:
    - Current status
    - Tracking number (if available)
    - Estimated delivery
    - Order details
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get AI chat bot with usage tracking
    chat_bot = get_chat_bot(db, project_id, UUID(user_id))
    
    try:
        result = await chat_bot.handle_order_inquiry(
            customer_id=inquiry.customer_id,
            order_number=inquiry.order_number,
            channel=inquiry.channel
        )
        
        return {
            "success": True,
            "response": result["response"],
            "order_id": result.get("order_id"),
            "status": result.get("status")
        }
        
    except Exception as e:
        logger.error("Failed to handle order inquiry", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to handle order inquiry: {str(e)}"
        )

@router.get("/{project_id}/stats")
async def get_bot_stats(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get AI chat bot statistics.
    
    Returns:
    - Total messages processed
    - Automation rate
    - Average response time
    - Tokens used
    - Cost savings
    """
    from app.domains.messages.models import Message, MessageDirection
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get stats for last 30 days
    start_date = datetime.utcnow() - timedelta(days=30)
    
    # Total messages
    result = await db.execute(
        select(func.count(Message.id))
        .where(Message.project_id == project_id)
        .where(Message.created_at >= start_date)
    )
    total_messages = result.scalar()
    
    # AI-generated messages
    result = await db.execute(
        select(func.count(Message.id))
        .where(Message.project_id == project_id)
        .where(Message.created_at >= start_date)
        .where(Message.direction == MessageDirection.OUTBOUND)
    )
    outbound_messages = result.scalar()
    
    # Get all messages for detailed stats
    result = await db.execute(
        select(Message)
        .where(Message.project_id == project_id)
        .where(Message.created_at >= start_date)
        .where(Message.direction == MessageDirection.OUTBOUND)
    )
    messages = result.scalars().all()
    
    ai_generated = sum(1 for m in messages if m.extra_data and m.extra_data.get("ai_generated"))
    total_tokens = sum(m.extra_data.get("tokens_used", 0) for m in messages if m.extra_data)
    total_cost = sum(m.extra_data.get("cost", 0) for m in messages if m.extra_data)
    
    # Calculate time saved (assume 5 minutes per manual response)
    time_saved_hours = (ai_generated * 5) / 60
    cost_savings = time_saved_hours * 20  # Assume $20/hour for human agent
    
    automation_rate = (ai_generated / outbound_messages * 100) if outbound_messages > 0 else 0
    
    return {
        "period_days": 30,
        "total_messages": total_messages or 0,
        "ai_generated_messages": ai_generated,
        "automation_rate": round(automation_rate, 2),
        "total_tokens_used": total_tokens,
        "total_cost_usd": round(total_cost, 4),
        "time_saved_hours": round(time_saved_hours, 2),
        "estimated_cost_savings_usd": round(cost_savings, 2)
    }
