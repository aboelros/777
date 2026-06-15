"""
Celery tasks for AI-powered automation and message processing.
"""

from celery import shared_task
from uuid import UUID
import structlog

logger = structlog.get_logger(__name__)


@shared_task(name="process_incoming_message", bind=True, max_retries=3)
def process_incoming_message(self, message_id: str, project_id: str):
    """
    Process an incoming customer message with AI.
    
    Args:
        message_id: UUID of the message to process
        project_id: UUID of the project
    """
    from app.services.ai_orchestrator import AIOrchestrator
    from app.core.database import get_async_session
    from app.db.models import Message
    from sqlalchemy import select
    
    try:
        async def process():
            async with get_async_session() as db:
                # Fetch message
                result = await db.execute(
                    select(Message).where(Message.id == UUID(message_id))
                )
                message = result.scalar_one_or_none()
                
                if not message:
                    logger.error("Message not found", message_id=message_id)
                    return
                
                # Initialize AI orchestrator
                orchestrator = AIOrchestrator(db)
                await orchestrator.initialize_integrations(UUID(project_id))
                
                # Process message with AI
                response = await orchestrator.process_customer_message(
                    customer_id=message.customer_id,
                    message_content=message.content,
                    channel=message.channel,
                    project_id=UUID(project_id)
                )
                
                logger.info(
                    "Message processed by AI",
                    message_id=message_id,
                    response=response
                )
                
                return response
        
        # Run async function
        import asyncio
        return asyncio.run(process())
        
    except Exception as e:
        logger.error(
            "Failed to process message",
            message_id=message_id,
            error=str(e)
        )
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(name="sync_integration_data")
def sync_integration_data(integration_id: str):
    """
    Sync data from an integration (orders, customers, etc.).
    
    Args:
        integration_id: UUID of the integration to sync
    """
    from app.core.database import get_async_session
    from app.db.models import Integration
    from app.services.integrations.shopify import ShopifyClient
    from sqlalchemy import select
    
    try:
        async def sync():
            async with get_async_session() as db:
                # Fetch integration
                result = await db.execute(
                    select(Integration).where(Integration.id == UUID(integration_id))
                )
                integration = result.scalar_one_or_none()
                
                if not integration:
                    logger.error("Integration not found", integration_id=integration_id)
                    return
                
                # Sync based on provider
                if integration.provider == "shopify":
                    client = ShopifyClient(integration.config)
                    
                    # Sync orders
                    orders = await client.get_orders(limit=100)
                    logger.info(
                        "Shopify orders synced",
                        integration_id=integration_id,
                        count=len(orders)
                    )
                    
                    # TODO: Save orders to database
                
                logger.info("Integration synced", integration_id=integration_id)
        
        import asyncio
        asyncio.run(sync())
        
    except Exception as e:
        logger.error(
            "Sync failed",
            integration_id=integration_id,
            error=str(e)
        )
        raise


@shared_task(name="auto_respond_to_customer")
def auto_respond_to_customer(customer_id: str, project_id: str, context: dict):
    """
    Generate and send automatic response to a customer using AI.
    
    Args:
        customer_id: UUID of the customer
        project_id: UUID of the project
        context: Additional context for the response
    """
    from app.services.ai_orchestrator import AIOrchestrator
    from app.core.database import get_async_session
    
    try:
        async def respond():
            async with get_async_session() as db:
                orchestrator = AIOrchestrator(db)
                await orchestrator.initialize_integrations(UUID(project_id))
                
                # Generate proactive message
                message = context.get("message", "How can I help you today?")
                channel = context.get("channel", "whatsapp")
                
                response = await orchestrator._send_message(
                    customer_id=UUID(customer_id),
                    message=message,
                    channel=channel
                )
                
                logger.info(
                    "Auto-response sent",
                    customer_id=customer_id,
                    channel=channel
                )
                
                return response
        
        import asyncio
        return asyncio.run(respond())
        
    except Exception as e:
        logger.error(
            "Auto-response failed",
            customer_id=customer_id,
            error=str(e)
        )
        raise


@shared_task(name="analyze_conversation_sentiment")
def analyze_conversation_sentiment(conversation_id: str):
    """
    Analyze sentiment of a conversation using AI.
    
    Args:
        conversation_id: UUID of the conversation
    """
    from app.services.gemini_client import GeminiClient
    from app.core.database import get_async_session
    from app.db.models import Message
    from sqlalchemy import select
    
    try:
        async def analyze():
            async with get_async_session() as db:
                # Fetch conversation messages
                result = await db.execute(
                    select(Message)
                    .where(Message.conversation_id == UUID(conversation_id))
                    .order_by(Message.created_at.asc())
                )
                messages = result.scalars().all()
                
                if not messages:
                    return None
                
                # Build conversation text
                conversation_text = "\n".join([
                    f"{'Customer' if msg.direction == 'inbound' else 'Agent'}: {msg.content}"
                    for msg in messages
                ])
                
                # Analyze with AI
                gemini = GeminiClient()
                sentiment = await gemini.analyze_sentiment(conversation_text)
                
                logger.info(
                    "Sentiment analyzed",
                    conversation_id=conversation_id,
                    sentiment=sentiment
                )
                
                return sentiment
        
        import asyncio
        return asyncio.run(analyze())
        
    except Exception as e:
        logger.error(
            "Sentiment analysis failed",
            conversation_id=conversation_id,
            error=str(e)
        )
        raise


@shared_task(name="generate_sales_insights")
def generate_sales_insights(project_id: str, timeframe: str = "7d"):
    """
    Generate AI-powered sales insights for a project.
    
    Args:
        project_id: UUID of the project
        timeframe: Timeframe for analysis (7d, 30d, etc.)
    """
    from app.services.gemini_client import GeminiClient
    from app.core.database import get_async_session
    from app.db.models import Order, Customer, Message
    from sqlalchemy import select, func
    from datetime import datetime, timedelta
    
    try:
        async def generate():
            async with get_async_session() as db:
                # Calculate date range
                if timeframe == "7d":
                    days = 7
                elif timeframe == "30d":
                    days = 30
                else:
                    days = 7
                
                start_date = datetime.utcnow() - timedelta(days=days)
                
                # Fetch metrics
                # TODO: Implement actual metrics queries
                
                metrics = {
                    "timeframe": timeframe,
                    "total_orders": 0,
                    "total_revenue": 0,
                    "avg_order_value": 0,
                    "total_customers": 0,
                    "total_messages": 0
                }
                
                # Generate insights with AI
                gemini = GeminiClient()
                insights = await gemini.generate_insights(metrics)
                
                logger.info(
                    "Insights generated",
                    project_id=project_id,
                    timeframe=timeframe
                )
                
                return insights
        
        import asyncio
        return asyncio.run(generate())
        
    except Exception as e:
        logger.error(
            "Insight generation failed",
            project_id=project_id,
            error=str(e)
        )
        raise
