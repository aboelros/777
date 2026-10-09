"""
Helper functions for AI assistant endpoints, enforcing tenant context and tracking.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog
from fastapi import HTTPException, status

from app.core.context import TenantContext
from app.domains.products.repository import ProductRepository
from app.domains.ai.repository import BotInstructionRepository
from app.domains.orders.repository import OrderRepository
from app.domains.messages.models import Message, MessageDirection
from app.domains.analytics.models import APILog
from app.services.service_factory import ServiceFactory

logger = structlog.get_logger(__name__)


async def check_ai_limit(db: AsyncSession, user_id: UUID) -> None:
    """Check subscription limit for AI requests."""
    sub_service = ServiceFactory.get_subscription_service(db)
    limit_check = await sub_service.check_and_enforce_limit(user_id, "ai_requests")
    if not limit_check["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=limit_check.get("reason", "Usage limit exceeded")
        )


async def build_assistant_context(
    db: AsyncSession,
    context: TenantContext,
    base_context: Optional[Dict[str, Any]] = None,
    order_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """Build context for AI assistant with products, instructions, and order history."""
    req_context = dict(base_context or {})

    # Scoped products catalog
    prod_repo = ProductRepository(db)
    products = await prod_repo.get_project_products(context.project_id, limit=20)
    if products:
        req_context["product_catalog"] = [
            {
                "name": p.name, "description": p.description, "price": p.price,
                "currency": p.currency, "in_stock": p.in_stock, "faq": p.faq, "keywords": p.keywords
            }
            for p in products
        ]

    # Scoped custom bot instructions
    bot_repo = BotInstructionRepository(db)
    instructions = await bot_repo.get_active_by_context(context)
    if instructions:
        req_context["custom_instructions"] = [
            {"title": i.title, "instruction": i.instruction, "category": i.category, "priority": i.priority}
            for i in instructions
        ]

    # Scoped order context if order_id provided
    if order_id:
        order_repo = OrderRepository(db)
        order = await order_repo.get_by_context(order_id, context)
        if order:
            req_context["order"] = {
                "id": str(order.id), "external_id": order.external_id, "status": order.status,
                "customer": order.customer, "items": order.items, "total": order.total, "currency": order.currency
            }
            msg_res = await db.execute(
                select(Message)
                .where(Message.order_id == order_id, Message.project_id == context.project_id)
                .order_by(Message.created_at.desc())
                .limit(10)
            )
            messages = msg_res.scalars().all()
            req_context["conversation_history"] = [
                {
                    "role": "assistant" if msg.direction == MessageDirection.OUTBOUND else "user",
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in reversed(messages)
            ]

    return req_context


async def log_and_track_ai_usage(
    db: AsyncSession,
    context: TenantContext,
    endpoint: str,
    method: str,
    request_data: Dict[str, Any],
    tokens_used: int,
    cost: float,
    model: str,
    response_text: str = ""
) -> None:
    """Track token usage and write API log for AI assistant operations."""
    sub_service = ServiceFactory.get_subscription_service(db)
    try:
        await sub_service.track_ai_usage(
            user_id=context.user_id,
            tokens_input=0,
            tokens_output=tokens_used,
            model_used=model
        )
    except Exception as e:
        logger.error("Failed to track AI usage", error=str(e))

    try:
        api_log = APILog(
            project_id=context.project_id,
            user_id=context.user_id,
            endpoint=endpoint,
            method=method,
            request=request_data,
            response={"text_length": len(response_text)},
            status_code=200,
            ai_tokens_used=tokens_used,
            cost_estimate=cost
        )
        db.add(api_log)
        await db.commit()
    except Exception as log_error:
        logger.warning("Failed to log API usage", error=str(log_error))
        await db.rollback()
