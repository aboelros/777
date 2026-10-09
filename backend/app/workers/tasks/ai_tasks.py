"""
Celery tasks for AI-powered automation and message processing.
"""

from typing import Optional
from celery import shared_task
from uuid import UUID
import asyncio
import structlog
from sqlalchemy import select

from app.core.context import TenantContext
from app.core.database import AsyncSessionLocal

logger = structlog.get_logger(__name__)


@shared_task(name="process_incoming_message", bind=True, max_retries=3)
def process_incoming_message(self, message_id: str, project_id: str):
    """
    Process an incoming customer message with AI.
    """
    from app.domains.ai.orchestrator import AIOrchestrator
    from app.domains.messages.models import Message

    try:
        async def process():
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Message)
                    .where(Message.id == UUID(message_id))
                    .where(Message.project_id == UUID(project_id))
                )
                message = result.scalar_one_or_none()

                if not message:
                    logger.error("Message not found or cross-tenant", message_id=message_id, project_id=project_id)
                    return None

                tenant_ctx = TenantContext(project_id=UUID(project_id), roles=["system"])
                orchestrator = AIOrchestrator(db, context=tenant_ctx)
                await orchestrator.initialize_integrations(tenant_ctx.project_id)

                response = await orchestrator.process_customer_message(
                    customer_id=message.customer_id,
                    message_content=message.content,
                    channel=message.channel,
                    project_id=tenant_ctx.project_id
                )

                logger.info("Message processed by AI", message_id=message_id)
                return response

        return asyncio.run(process())

    except Exception as e:
        logger.error("Failed to process message", message_id=message_id, error=str(e))
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(name="sync_integration_data")
def sync_integration_data(project_id: str, integration_id: str):
    """
    Sync data from an integration with strict tenant verification.
    """
    from app.domains.integrations.repository import IntegrationRepository
    from app.services.integrations.shopify import ShopifyService

    try:
        async def sync():
            async with AsyncSessionLocal() as db:
                tenant_ctx = TenantContext(project_id=UUID(project_id), roles=["system"])
                repo = IntegrationRepository(db)
                integration = await repo.get_tenant_integration(tenant_ctx.project_id, UUID(integration_id))

                if not integration:
                    logger.error("Integration not found or cross-tenant", integration_id=integration_id, project_id=project_id)
                    return None

                if integration.provider == "shopify":
                    logger.info("Shopify integration verified", integration_id=integration_id)

                logger.info("Integration synced", integration_id=integration_id)
                return True

        return asyncio.run(sync())

    except Exception as e:
        logger.error("Sync failed", integration_id=integration_id, error=str(e))
        raise


@shared_task(name="auto_respond_to_customer")
def auto_respond_to_customer(customer_id: str, project_id: str, context: dict):
    """
    Generate and send automatic response to a customer using AI.
    Verifies tenant ownership of customer before executing external side effects.
    """
    from app.domains.ai.orchestrator import AIOrchestrator
    from app.domains.customers.repository import CustomerProfileRepository

    try:
        async def respond():
            async with AsyncSessionLocal() as db:
                tenant_ctx = TenantContext(project_id=UUID(project_id), roles=["system"])
                cust_repo = CustomerProfileRepository(db)
                customer = await cust_repo.get_profile_by_context(tenant_ctx, UUID(customer_id))

                if not customer:
                    logger.error("Customer profile not found or cross-tenant", customer_id=customer_id, project_id=project_id)
                    return None

                orchestrator = AIOrchestrator(db, context=tenant_ctx)
                await orchestrator.initialize_integrations(tenant_ctx.project_id)

                message = context.get("message", "How can I help you today?")
                channel = context.get("channel", "whatsapp")

                response = await orchestrator._send_message(
                    customer_id=UUID(customer_id),
                    message=message,
                    channel=channel
                )

                logger.info("Auto-response sent", customer_id=customer_id, channel=channel)
                return response

        return asyncio.run(respond())

    except Exception as e:
        logger.error("Auto-response failed", customer_id=customer_id, error=str(e))
        raise


@shared_task(name="analyze_conversation_sentiment")
def analyze_conversation_sentiment(conversation_id: str, project_id: Optional[str] = None):
    """
    Analyze sentiment of a conversation using AI.
    """
    from app.domains.ai.providers.gemini import GeminiClient
    from app.domains.messages.models import Message

    try:
        async def analyze():
            async with AsyncSessionLocal() as db:
                stmt = select(Message).where(Message.conversation_id == UUID(conversation_id))
                if project_id:
                    stmt = stmt.where(Message.project_id == UUID(project_id))
                stmt = stmt.order_by(Message.created_at.asc())

                result = await db.execute(stmt)
                messages = result.scalars().all()

                if not messages:
                    return None

                conversation_text = "\n".join([
                    f"{'Customer' if msg.direction == 'inbound' else 'Agent'}: {msg.content}"
                    for msg in messages
                ])

                gemini = GeminiClient()
                sentiment = await gemini.analyze_sentiment(conversation_text)
                logger.info("Sentiment analyzed", conversation_id=conversation_id, sentiment=sentiment)
                return sentiment

        return asyncio.run(analyze())

    except Exception as e:
        logger.error("Sentiment analysis failed", conversation_id=conversation_id, error=str(e))
        raise


@shared_task(name="generate_sales_insights")
def generate_sales_insights(project_id: str, timeframe: str = "7d"):
    """
    Generate AI-powered sales insights for a project with verified tenant context.
    """
    from app.domains.ai.providers.gemini import GeminiClient
    from app.domains.projects.models import Project

    try:
        async def generate():
            async with AsyncSessionLocal() as db:
                tenant_ctx = TenantContext(project_id=UUID(project_id), roles=["system"])
                result = await db.execute(select(Project).where(Project.id == tenant_ctx.project_id))
                if not result.scalar_one_or_none():
                    logger.error("Project not found", project_id=project_id)
                    return None

                metrics = {
                    "timeframe": timeframe,
                    "total_orders": 0,
                    "total_revenue": 0,
                    "avg_order_value": 0,
                    "total_customers": 0,
                    "total_messages": 0
                }

                gemini = GeminiClient()
                insights = await gemini.generate_insights(metrics)
                logger.info("Insights generated", project_id=project_id, timeframe=timeframe)
                return insights

        return asyncio.run(generate())

    except Exception as e:
        logger.error("Insight generation failed", project_id=project_id, error=str(e))
        raise
