"""
AI Assistant endpoints using Google Gemini.
"""

from typing import Any
from uuid import UUID
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Project, Order, Message, MessageDirection, APILog, Product, BotInstruction
from app.models.schemas import AssistantQuery, AssistantResponse, FunctionCall, GenerateReplyRequest
from app.services.service_factory import get_gemini_without_tracking, ServiceFactory
from app.services.bot_function_executor import BotFunctionExecutor

router = APIRouter()
logger = structlog.get_logger(__name__)


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


@router.post("/query", response_model=AssistantResponse)
async def query_assistant(
    query: AssistantQuery,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Send a query to the AI assistant and get a response.
    
    The assistant can:
    - Answer questions about orders and customers
    - Generate message replies
    - Suggest actions (via function calling)
    - Analyze sentiment and urgency
    
    If `use_function_calling` is enabled, the response may include
    structured actions that your application can execute.
    """
    # Verify project access
    await verify_project_access(query.project_id, user_id, db)
    
    # Build context
    context = query.context or {}
    
    # Get product catalog for context
    products_result = await db.execute(
        select(Product)
        .where(Product.project_id == query.project_id)
        .where(Product.is_active == True)
        .limit(20)  # Top 20 products
    )
    products = products_result.scalars().all()
    
    if products:
        context["product_catalog"] = [
            {
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "in_stock": p.in_stock,
                "faq": p.faq,
                "keywords": p.keywords
            }
            for p in products
        ]
    
    # Get custom bot instructions
    instructions_result = await db.execute(
        select(BotInstruction)
        .where(BotInstruction.project_id == query.project_id)
        .where(BotInstruction.is_active == True)
        .order_by(BotInstruction.priority.desc())
    )
    instructions = instructions_result.scalars().all()
    
    if instructions:
        context["custom_instructions"] = [
            {
                "title": i.title,
                "instruction": i.instruction,
                "category": i.category,
                "priority": i.priority
            }
            for i in instructions
        ]
    
    # Add order context if order_id provided
    if query.order_id:
        result = await db.execute(
            select(Order)
            .where(Order.id == query.order_id)
            .where(Order.project_id == query.project_id)
        )
        order = result.scalar_one_or_none()
        
        if order:
            context["order"] = {
                "id": str(order.id),
                "external_id": order.external_id,
                "status": order.status,
                "customer": order.customer,
                "items": order.items,
                "total": order.total,
                "currency": order.currency
            }
            
            # Get conversation history for this order
            result = await db.execute(
                select(Message)
                .where(Message.order_id == query.order_id)
                .order_by(Message.created_at.desc())
                .limit(10)
            )
            messages = result.scalars().all()
            
            context["conversation_history"] = [
                {
                    "role": "assistant" if msg.direction == MessageDirection.OUTBOUND else "user",
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in reversed(messages)
            ]
    
    try:
        # Get subscription service
        subscription_service = ServiceFactory.get_subscription_service(db)
        
        # Check usage limits
        limit_check = await subscription_service.check_and_enforce_limit(UUID(user_id), "ai_requests")
        if not limit_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=limit_check.get("reason", "Usage limit exceeded")
            )

        # Get Gemini client without internal tracking (we handle it here)
        gemini_client = get_gemini_without_tracking()
        
        # Generate response from Gemini
        logger.info(
            "Querying Gemini assistant",
            project_id=str(query.project_id),
            message_length=len(query.message),
            user_id=user_id
        )
        
        response = await gemini_client.generate_response(
            prompt=query.message,
            context=context,
            use_functions=query.use_function_calling,
            user_id=None  # Don't pass user_id to avoid double tracking
        )
        
        # Track usage
        try:
            await subscription_service.track_ai_usage(
                user_id=UUID(user_id),
                tokens_input=0,  # We count total in output for simplicity as Gemini gives total
                tokens_output=response.get("tokens_used", 0),
                model_used=response.get("model", "gemini-2.0-flash")
            )
        except Exception as e:
            logger.error("Failed to track AI usage", error=str(e))
        
        # Log API usage (non-blocking)
        try:
            api_log = APILog(
                project_id=query.project_id,
                user_id=UUID(user_id),
                endpoint="/api/v1/assistant/query",
                method="POST",
                request={"message": query.message, "context_keys": list(context.keys())},
                response={"text_length": len(response.get("text", ""))},
                status_code=200,
                ai_tokens_used=response.get("tokens_used", 0),
                cost_estimate=response.get("cost", 0.0)
            )
            db.add(api_log)
            await db.commit()
        except Exception as log_error:
            logger.warning("Failed to log API usage", error=str(log_error))
            await db.rollback()  # Rollback failed transaction
        
        # Parse function calls
        function_calls = []
        for fc in response.get("function_calls", []):
            function_calls.append(
                FunctionCall(
                    name=fc["name"],
                    parameters=fc["parameters"]
                )
            )
        
        logger.info(
            "Gemini response generated",
            project_id=str(query.project_id),
            tokens_used=response.get("tokens_used", 0),
            function_calls=len(function_calls)
        )
        
        # Execute function calls if present
        function_results = []
        if function_calls and query.use_function_calling:
            executor = BotFunctionExecutor(
                db=db,
                project_id=query.project_id,
                user_id=UUID(user_id)
            )
            
            for fc in function_calls:
                try:
                    result = await executor.execute_function(
                        function_name=fc.name,
                        parameters=fc.parameters
                    )
                    function_results.append({
                        "function": fc.name,
                        "result": result
                    })
                    logger.info(
                        "Function executed",
                        function=fc.name,
                        success=result.get("success", False)
                    )
                except Exception as e:
                    logger.error(
                        "Function execution failed",
                        function=fc.name,
                        error=str(e)
                    )
                    function_results.append({
                        "function": fc.name,
                        "error": str(e)
                    })
            
            # If we have function results, generate a follow-up response
            if function_results:
                follow_up_context = {
                    **context,
                    "function_results": function_results
                }
                
                follow_up_prompt = f"""Based on the function results, provide a helpful response to the user.
                
Original query: {query.message}
                
Function results:
                {json.dumps(function_results, indent=2)}
                
Provide a clear, formatted response explaining the results."""
                
                follow_up_response = await gemini_client.generate_response(
                    prompt=follow_up_prompt,
                    context=follow_up_context,
                    use_functions=False
                )
                
                response["text"] = follow_up_response.get("text", response.get("text", ""))
                response["tokens_used"] += follow_up_response.get("tokens_used", 0)
                response["cost"] += follow_up_response.get("cost", 0.0)
        
        return AssistantResponse(
            reply=response.get("text", ""),
            function_calls=function_calls if function_calls else None,
            tokens_used=response.get("tokens_used", 0),
            cost=response.get("cost", 0.0),
            model=response.get("model", "gemini-2.0-flash")
        )
        
    except Exception as e:
        logger.error("Gemini query failed", error=str(e), project_id=str(query.project_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI assistant error: {str(e)}"
        )


@router.post("/generate-reply", response_model=AssistantResponse)
async def generate_reply(
    request: GenerateReplyRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate an AI reply to a customer message.
    
    This is a specialized endpoint for customer service scenarios.
    """
    # Verify project access
    await verify_project_access(request.project_id, user_id, db)
    
    # Get order details
    result = await db.execute(
        select(Order)
        .where(Order.id == request.order_id)
        .where(Order.project_id == request.project_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Get conversation history
    result = await db.execute(
        select(Message)
        .where(Message.order_id == request.order_id)
        .order_by(Message.created_at.desc())
        .limit(10)
    )
    messages = result.scalars().all()
    
    conversation_history = [
        {
            "role": "assistant" if msg.direction == MessageDirection.OUTBOUND else "user",
            "content": msg.content
        }
        for msg in reversed(messages)
    ]
    
    order_context = {
        "id": str(order.id),
        "external_id": order.external_id,
        "status": order.status,
        "customer": order.customer,
        "total": order.total,
        "currency": order.currency
    }
    
    try:
        # Get subscription service
        subscription_service = ServiceFactory.get_subscription_service(db)
        
        # Check usage limits
        limit_check = await subscription_service.check_and_enforce_limit(UUID(user_id), "ai_requests")
        if not limit_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=limit_check.get("reason", "Usage limit exceeded")
            )

        # Get Gemini client
        gemini_client = get_gemini_without_tracking()

        response = await gemini_client.generate_sales_reply(
            customer_message=request.customer_message,
            order_context=order_context,
            conversation_history=conversation_history
        )
        
        # Track usage
        try:
            await subscription_service.track_ai_usage(
                user_id=UUID(user_id),
                tokens_input=0,
                tokens_output=response.get("tokens_used", 0),
                model_used=response.get("model", "gemini-1.5-pro")
            )
        except Exception as e:
            logger.error("Failed to track AI usage", error=str(e))
        
        # Log API usage (non-blocking)
        try:
            api_log = APILog(
                project_id=request.project_id,
                user_id=UUID(user_id),
                endpoint="/api/v1/assistant/generate-reply",
                method="POST",
                request={"order_id": str(request.order_id)},
                response={"text_length": len(response.get("text", ""))},
                status_code=200,
                ai_tokens_used=response.get("tokens_used", 0),
                cost_estimate=response.get("cost", 0.0)
            )
            db.add(api_log)
            await db.commit()
        except Exception as log_error:
            logger.warning("Failed to log API usage", error=str(log_error))
            await db.rollback()
        
        # Parse function calls
        function_calls = []
        for fc in response.get("function_calls", []):
            function_calls.append(
                FunctionCall(
                    name=fc["name"],
                    parameters=fc["parameters"]
                )
            )
        
        return AssistantResponse(
            reply=response.get("text", ""),
            function_calls=function_calls if function_calls else None,
            tokens_used=response.get("tokens_used", 0),
            cost=response.get("cost", 0.0),
            model=response.get("model", "gemini-1.5-pro")
        )
        
    except Exception as e:
        logger.error("Reply generation failed", error=str(e), order_id=str(request.order_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reply generation error: {str(e)}"
        )


@router.post("/analyze-sentiment")
async def analyze_sentiment(
    project_id: UUID,
    message: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Analyze the sentiment and urgency of a customer message.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    try:
        # Get subscription service
        subscription_service = ServiceFactory.get_subscription_service(db)
        
        # Check usage limits
        limit_check = await subscription_service.check_and_enforce_limit(UUID(user_id), "ai_requests")
        if not limit_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=limit_check.get("reason", "Usage limit exceeded")
            )

        # Get Gemini client
        gemini_client = get_gemini_without_tracking()

        analysis = await gemini_client.analyze_sentiment(message)
        
        # Track usage (estimate tokens for analysis)
        try:
            # Estimate tokens since analyze_sentiment returns dict, not full response with usage
            estimated_tokens = len(message) // 4 + 100  # Input + output estimate
            await subscription_service.track_ai_usage(
                user_id=UUID(user_id),
                tokens_input=len(message) // 4,
                tokens_output=100,
                model_used="gemini-flash"
            )
        except Exception as e:
            logger.error("Failed to track AI usage", error=str(e))
        
        # Log API usage (non-blocking)
        try:
            api_log = APILog(
                project_id=project_id,
                user_id=UUID(user_id),
                endpoint="/api/v1/assistant/analyze-sentiment",
                method="POST",
                request={"message_length": len(message)},
                response=analysis,
                status_code=200
            )
            db.add(api_log)
            await db.commit()
        except Exception as log_error:
            logger.warning("Failed to log API usage", error=str(log_error))
            await db.rollback()
        
        return analysis
        
    except Exception as e:
        logger.error("Sentiment analysis failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis error: {str(e)}"
        )


@router.get("/usage/{project_id}")
async def get_ai_usage(
    project_id: UUID,
    days: int = 30,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get AI usage statistics for a project.
    
    Returns token usage, costs, and API call counts.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get API logs
    result = await db.execute(
        select(
            func.count(APILog.id).label("total_calls"),
            func.sum(APILog.ai_tokens_used).label("total_tokens"),
            func.sum(APILog.cost_estimate).label("total_cost")
        )
        .where(APILog.project_id == project_id)
        .where(APILog.created_at >= start_date)
    )
    
    row = result.first()
    
    return {
        "period_days": days,
        "total_api_calls": row.total_calls or 0,
        "total_tokens_used": row.total_tokens or 0,
        "total_cost_usd": float(row.total_cost or 0.0),
        "average_cost_per_call": float((row.total_cost or 0.0) / (row.total_calls or 1))
    }
