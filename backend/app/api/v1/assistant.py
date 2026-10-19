"""
AI Assistant endpoints using Google Gemini with strict tenant isolation.
"""

from typing import Any, Optional
from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context, resolve_tenant_context
from app.core.uow import UnitOfWork
from app.domains.ai.service import AIService
from app.domains.ai.schemas import AssistantQuery, AssistantResponse, FunctionCall, GenerateReplyRequest
from app.domains.orders.repository import OrderRepository
from app.domains.messages.models import Message, MessageDirection
from app.services.service_factory import get_gemini_without_tracking
from app.services.bot_function_executor import BotFunctionExecutor
from app.api.v1.assistant_helpers import check_ai_limit, build_assistant_context, log_and_track_ai_usage

router = APIRouter()
logger = structlog.get_logger(__name__)


async def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(UnitOfWork(db))


@router.post("/query", response_model=AssistantResponse)
async def query_assistant(
    query: AssistantQuery,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Send a query to the AI assistant with strict tenant isolation."""
    context = await resolve_tenant_context(query.project_id, UUID(user_id), db)
    req_context = await build_assistant_context(db, context, query.context, query.order_id)
    await check_ai_limit(db, context.user_id)

    gemini_client = get_gemini_without_tracking()
    executor = BotFunctionExecutor(db, context.project_id, context.user_id)

    response = await gemini_client.generate_response(
        prompt=query.message,
        context=req_context,
        use_functions=query.use_function_calling,
        user_id=None
    )

    function_calls = []
    if response.get("function_calls"):
        for fc in response["function_calls"]:
            result = await executor.execute_function(fc["name"], fc.get("parameters", {}))
            function_calls.append(FunctionCall(name=fc["name"], parameters=fc.get("parameters", {})))
            if result.get("success") and "context_update" in result:
                req_context.update(result["context_update"])


    tokens_used = response.get("tokens_used", 0)
    cost = response.get("cost", 0.0)
    model = response.get("model", "gemini-1.5-pro")

    await log_and_track_ai_usage(
        db, context, "/api/v1/assistant/query", "POST",
        {"query_length": len(query.message), "has_order": query.order_id is not None},
        tokens_used, cost, model, response.get("text", "")
    )

    return AssistantResponse(
        reply=response.get("text", ""),
        function_calls=function_calls if function_calls else None,
        tokens_used=tokens_used,
        cost=cost,
        model=model
    )


@router.post("/generate-reply", response_model=AssistantResponse)
async def generate_reply(
    request: GenerateReplyRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Generate an AI-powered sales reply for a customer message regarding a scoped order."""
    context = await resolve_tenant_context(request.project_id, UUID(user_id), db)
    order_repo = OrderRepository(db)
    order = await order_repo.get_by_context(request.order_id, context)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    msg_res = await db.execute(
        select(Message)
        .where(Message.order_id == request.order_id, Message.project_id == context.project_id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    messages = msg_res.scalars().all()
    conversation_history = [
        {"role": "assistant" if m.direction == MessageDirection.OUTBOUND else "user", "content": m.content}
        for m in reversed(messages)
    ]

    order_context = {
        "id": str(order.id), "external_id": order.external_id, "status": order.status,
        "customer": order.customer, "total": order.total, "currency": order.currency
    }

    await check_ai_limit(db, context.user_id)
    gemini_client = get_gemini_without_tracking()
    response = await gemini_client.generate_sales_reply(
        customer_message=request.customer_message,
        order_context=order_context,
        conversation_history=conversation_history
    )

    tokens_used = response.get("tokens_used", 0)
    cost = response.get("cost", 0.0)
    model = response.get("model", "gemini-1.5-pro")

    await log_and_track_ai_usage(
        db, context, "/api/v1/assistant/generate-reply", "POST",
        {"order_id": str(request.order_id)}, tokens_used, cost, model, response.get("text", "")
    )

    function_calls = [
        FunctionCall(name=fc["name"], parameters=fc["parameters"])
        for fc in response.get("function_calls", [])
    ]

    return AssistantResponse(
        reply=response.get("text", ""),
        function_calls=function_calls if function_calls else None,
        tokens_used=tokens_used,
        cost=cost,
        model=model
    )


@router.post("/analyze-sentiment")
async def analyze_sentiment(
    project_id: UUID,
    message: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Analyze customer message sentiment scoped to tenant."""
    context = await resolve_tenant_context(project_id, UUID(user_id), db)
    await check_ai_limit(db, context.user_id)

    gemini_client = get_gemini_without_tracking()
    analysis = await gemini_client.analyze_sentiment(message)

    await log_and_track_ai_usage(
        db, context, "/api/v1/assistant/analyze-sentiment", "POST",
        {"message_length": len(message)}, len(message) // 4 + 100, 0.0, "gemini-flash", str(analysis)
    )

    return analysis


@router.get("/usage/{project_id}")
async def get_ai_usage(
    project_id: UUID,
    days: int = 30,
    context: TenantContext = Depends(get_tenant_context),
    service: AIService = Depends(get_ai_service)
) -> Any:
    """Get AI usage statistics for a project scoped strictly to TenantContext."""
    return await service.get_ai_usage_stats(context, days=days)
