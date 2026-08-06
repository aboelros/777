"""
Celery background tasks for async processing.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import structlog
from celery import Task

from app.workers.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.orders.models import Order
from app.domains.messages.models import Message, MessageDirection
from app.domains.projects.models import Project
from app.domains.analytics.models import Report, APILog
from app.services.integrations.shopify import ShopifyService
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger(__name__)


class DatabaseTask(Task):
    """Base task with database session management."""
    
    _db = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = AsyncSessionLocal()
        return self._db
    
    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()


@celery_app.task(bind=True, base=DatabaseTask)
def sync_shopify_orders(self):
    """Sync orders from all connected Shopify integrations."""
    logger.info("Starting Shopify order sync")
    
    # Run async code in sync Celery task
    import asyncio
    
    async def _sync():
        synced_count = 0
        
        # Get all active Shopify integrations
        result = await self.db.execute(
            select(Integration)
            .where(Integration.provider == "shopify")
            .where(Integration.status == IntegrationStatus.CONNECTED)
        )
        integrations = result.scalars().all()
        
        for integration in integrations:
            try:
                # Initialize service
                creds = integration.credentials or {}
                service = ShopifyService(
                    shop_url=creds.get("shop_url"),
                    api_key=creds.get("api_key"),
                    api_secret=creds.get("api_secret")
                )
                
                # Fetch orders
                orders = await service.fetch_orders(limit=50)
                
                for shopify_order in orders:
                    # Transform to internal format
                    order_data = service.transform_order(shopify_order)
                    
                    # Check if order exists
                    result = await self.db.execute(
                        select(Order)
                        .where(Order.project_id == integration.project_id)
                        .where(Order.external_id == order_data["external_id"])
                        .where(Order.provider == "shopify")
                    )
                    existing_order = result.scalar_one_or_none()
                    
                    if existing_order:
                        # Update existing
                        existing_order.status = order_data["status"]
                        existing_order.total = order_data["total"]
                        existing_order.metadata = order_data["metadata"]
                        # Update other fields as needed
                    else:
                        # Create new
                        new_order = Order(
                            project_id=integration.project_id,
                            external_id=order_data["external_id"],
                            provider="shopify",
                            status=order_data["status"],
                            customer=order_data["customer"],
                            items=order_data["items"],
                            total=order_data["total"],
                            currency=order_data["currency"],
                            metadata=order_data["metadata"],
                            order_date=datetime.fromisoformat(shopify_order.get("created_at").replace("Z", "+00:00")) if shopify_order.get("created_at") else datetime.utcnow()
                        )
                        self.db.add(new_order)
                    
                    synced_count += 1
                
                await self.db.commit()
                
            except Exception as e:
                logger.error("Failed to sync integration", integration_id=str(integration.id), error=str(e))
                continue
                
        return synced_count

    loop = asyncio.get_event_loop()
    if loop.is_running():
        # We are already in an event loop (unlikely for standard Celery, but possible)
        # Use a thread or just run_until_complete if not running
        return loop.run_until_complete(_sync())
    else:
        return asyncio.run(_sync())


@celery_app.task(bind=True, base=DatabaseTask)
def sync_integration(self, integration_id: str):
    """Sync data for a specific integration."""
    logger.info("Syncing integration", integration_id=integration_id)
    
    # TODO: Implement provider-specific sync logic
    # - Shopify: fetch orders
    # - WhatsApp: fetch messages
    # - Telegram: fetch updates
    # etc.
    
    return {"status": "completed", "integration_id": integration_id}


@celery_app.task(bind=True, base=DatabaseTask)
def send_message_task(self, message_id: str):
    """
    Send a queued message via the appropriate provider.
    
    Args:
        message_id: UUID of the message to send
    """
    logger.info("Sending message", message_id=message_id)
    
    import asyncio
    from app.services.integrations.whatsapp import WhatsAppService
    
    async def _send():
        # Load message
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        
        if not message:
            logger.error("Message not found", message_id=message_id)
            return {"status": "failed", "error": "Message not found"}
            
        if message.status == "sent":
            logger.info("Message already sent", message_id=message_id)
            return {"status": "skipped", "reason": "Already sent"}
            
        try:
            # Get integration credentials
            result = await self.db.execute(
                select(Integration)
                .where(Integration.project_id == message.project_id)
                .where(Integration.provider == message.provider)
                .where(Integration.status == IntegrationStatus.CONNECTED)
            )
            integration = result.scalar_one_or_none()
            
            if not integration:
                raise Exception(f"No active integration for provider {message.provider}")
                
            creds = integration.credentials or {}
            
            # Send via provider
            # Handle standardized Meta provider
            provider = message.provider
            platform = message.platform or provider
            
            if provider == "meta" or provider in ["instagram", "facebook", "whatsapp"]:
                # Use platform for specific client routing
                routing_key = platform
            else:
                routing_key = provider

            if routing_key == "whatsapp":
                # Use Baileys service for QR code/linked device
                from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
                
                # Get session ID from integration extra_data
                session_id = (integration.extra_data or {}).get("session_id")
                if not session_id:
                    raise Exception("WhatsApp session not connected. Please scan QR code first.")
                
                service = WhatsAppBaileysService(session_id=session_id)
                
                # Determine recipient phone
                # Try 'phone' first, then 'id'
                to = message.recipient.get("phone") or message.recipient.get("id")
                if not to:
                    raise Exception("No recipient phone number or ID")
                    
                response = await service.send_message(to=to, message=message.content)
                
                # Update message status
                message.status = "sent"
                message.external_id = response.get("message_id") or response.get("id")
                message.sent_at = datetime.utcnow()
                
            elif routing_key == "telegram":
                from app.services.integrations.telegram import TelegramService
                
                # Initialize service
                bot_token = creds.get("api_key")
                if not bot_token:
                    raise Exception("Telegram bot token not found in credentials")
                    
                service = TelegramService(bot_token=bot_token)
                
                # Determine recipient chat_id
                # Try 'id' first, then 'customer_id', then 'phone'
                chat_id = message.recipient.get("id") or message.recipient.get("customer_id") or message.recipient.get("phone")
                if not chat_id:
                    raise Exception("No recipient chat ID found")
                    
                response = await service.send_message(chat_id=str(chat_id), text=message.content)
                
                # Update message status
                message.status = "sent"
                message.external_id = str(response.get("result", {}).get("message_id"))
                message.sent_at = datetime.utcnow()
                
            elif routing_key == "instagram":
                from app.services.integrations.instagram import InstagramClient
                
                # Initialize client
                client = InstagramClient(creds)
                
                # Send message
                recipient_id = message.recipient.get("id") or message.recipient.get("customer_id")
                if not recipient_id:
                    raise Exception("No Instagram recipient ID found")

                response = await client.send_message(
                    customer_id=recipient_id,
                    message=message.content
                )
                
                if response.get("status") == "error":
                    raise Exception(response.get("message", "Unknown error"))
                    
                # Update message status
                message.status = "sent"
                message.external_id = response.get("id")
                message.sent_at = datetime.utcnow()
                
            elif routing_key == "facebook":
                from app.services.integrations.facebook import FacebookClient
                
                # Initialize client
                client = FacebookClient(creds)
                
                # Send message
                recipient_id = message.recipient.get("id") or message.recipient.get("customer_id")
                if not recipient_id:
                    raise Exception("No Facebook recipient ID found")

                response = await client.send_message(
                    customer_id=recipient_id,
                    message=message.content
                )
                
                if response.get("status") == "error":
                    raise Exception(response.get("message", "Unknown error"))
                    
                # Update message status
                message.status = "sent"
                message.external_id = response.get("id")
                message.sent_at = datetime.utcnow()
                
            else:
                raise Exception(f"Unsupported provider/platform: {provider}/{platform}")
                
            await self.db.commit()
            return {"status": "sent", "message_id": message_id}
            
        except Exception as e:
            logger.error("Failed to send message", message_id=message_id, error=str(e))
            message.status = "failed"
            message.error_message = str(e)
            await self.db.commit()
            # Retry logic could go here
            raise self.retry(exc=e, countdown=60, max_retries=3)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_send())
    else:
        return asyncio.run(_send())


@celery_app.task(bind=True, base=DatabaseTask)
def process_message_queue(self):
    """Process all queued outbound messages."""
    logger.info("Processing message queue")
    
    import asyncio
    
    async def _process():
        # 1. Get all messages with status="queued"
        result = await self.db.execute(
            select(Message)
            .where(Message.status == "queued")
            .where(Message.direction == MessageDirection.OUTBOUND)
            .limit(50) # Process in batches
        )
        queued_messages = result.scalars().all()
        
        processed_count = 0
        for message in queued_messages:
            # 2. For each message, call send_message_task
            send_message_task.delay(str(message.id))
            processed_count += 1
            
        return {"status": "completed", "processed": processed_count}

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_process())
    else:
        return asyncio.run(_process())


@celery_app.task(bind=True, base=DatabaseTask)
def process_inbound_message(self, message_data: Dict[str, Any]):
    """
    Process an inbound message from a webhook.
    
    Args:
        message_data: Message payload from webhook
    """
    provider = message_data.get("provider")
    logger.info("Processing inbound message", provider=provider)
    
    import asyncio
    from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService
    
    async def _process():
        try:
            parsed_msg = None
            project_id = message_data.get("project_id")
            
            if provider == "whatsapp":
                # Use Baileys service for parsing
                service = WhatsAppBaileysService()
                parsed_msg = service.parse_webhook(message_data.get("payload", {}))
                
            elif provider == "telegram":
                # Simple parsing for Telegram
                payload = message_data.get("payload", {})
                parsed_msg = {
                    "message_id": str(payload.get("message_id")),
                    "text": payload.get("text"),
                    "from": payload.get("from", {}).get("id"),
                    "contact": {
                        "id": payload.get("from", {}).get("id"),
                        "name": payload.get("from", {}).get("first_name"),
                        "phone": None # Telegram doesn't always give phone
                    },
                    "timestamp": datetime.utcnow().timestamp()
                }
            
            if not parsed_msg or not parsed_msg.get("text"):
                logger.warning("Could not parse message or empty text", provider=provider)
                return {"status": "ignored"}
                
            # Create Message record
            new_message = Message(
                project_id=project_id,
                direction=MessageDirection.INBOUND,
                provider=provider,
                content=parsed_msg.get("text"),
                content_type="text",
                sender=parsed_msg.get("contact"),
                recipient={"type": "system"},
                status="received",
                external_id=parsed_msg.get("message_id"),
                created_at=datetime.utcnow()
            )
            
            self.db.add(new_message)
            await self.db.commit()
            await self.db.refresh(new_message)
            
            # Trigger AI response
            generate_ai_response.delay(str(new_message.id), auto_send=True)
            
            return {"status": "processed", "message_id": str(new_message.id)}
            
        except Exception as e:
            logger.error("Failed to process inbound message", error=str(e))
            return {"status": "failed", "error": str(e)}

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_process())
    else:
        return asyncio.run(_process())


@celery_app.task(bind=True, base=DatabaseTask)
def generate_ai_response(self, message_id: str, auto_send: bool = False):
    """
    Generate AI response for an inbound message.
    
    Args:
        message_id: UUID of the message to respond to
        auto_send: Whether to automatically send the generated response
    """
    logger.info("Generating AI response", message_id=message_id)
    
    import asyncio
    from app.domains.ai.providers.gemini import GeminiClient
    
    async def _generate():
        # 1. Load message
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        message = result.scalar_one_or_none()
        
        if not message:
            logger.error("Message not found", message_id=message_id)
            return {"status": "failed", "error": "Message not found"}
            
        # 2. Call Gemini to generate response
        client = GeminiClient()
        
        # Build context (simplified for now)
        context = {
            "channel": message.provider,
            "persona": "ai_saler"
        }
        
        response_data = await client.generate_response(
            prompt=message.content,
            context=context,
            user_id=message.project_id
        )
        
        response_text = response_data.get("text")
        if not response_text:
            logger.warning("Empty AI response", message_id=message_id)
            return {"status": "failed", "error": "Empty AI response"}
            
        # 3. Create new outbound Message record
        outbound_message = Message(
            project_id=message.project_id,
            direction=MessageDirection.OUTBOUND,
            provider=message.provider,
            content=response_text,
            content_type="text",
            sender={"type": "ai_assistant"},
            recipient=message.sender, # Reply to sender
            status="queued" if auto_send else "draft",
            created_at=datetime.utcnow(),
            conversation_id=message.conversation_id
        )
        
        self.db.add(outbound_message)
        await self.db.commit()
        await self.db.refresh(outbound_message)
        
        # 4. If auto_send, queue for sending
        if auto_send:
            send_message_task.delay(str(outbound_message.id))
            
        return {
            "status": "generated", 
            "message_id": str(outbound_message.id),
            "auto_sent": auto_send
        }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_generate())
    else:
        return asyncio.run(_generate())


@celery_app.task(bind=True, base=DatabaseTask)
def verify_integration(self, integration_id: str):
    """
    Verify that an integration connection is working.
    
    Args:
        integration_id: UUID of the integration to verify
    """
    logger.info("Verifying integration", integration_id=integration_id)
    
    import asyncio
    
    async def _verify():
        # 1. Load integration
        result = await self.db.execute(
            select(Integration).where(Integration.id == integration_id)
        )
        integration = result.scalar_one_or_none()
        
        if not integration:
            return {"status": "failed", "error": "Integration not found"}
            
        creds = integration.credentials or {}
        is_valid = False
        error_msg = None
        
        try:
            # 2. Test API connection with credentials
            if integration.provider == "shopify":
                from app.services.integrations.shopify import ShopifyService
                service = ShopifyService(
                    shop_url=creds.get("shop_url"),
                    api_key=creds.get("api_key"),
                    api_secret=creds.get("api_secret")
                )
                # Try to fetch 1 order to verify auth
                await service.fetch_orders(limit=1)
                is_valid = True
                
            elif integration.provider == "whatsapp":
                # Basic check if creds exist (actual API check requires sending msg)
                if creds.get("business_id") and creds.get("access_token"):
                    is_valid = True
                    
            elif integration.provider == "telegram":
                from app.services.integrations.telegram import TelegramService
                service = TelegramService(bot_token=creds.get("api_key"))
                bot_info = await service.get_me()
                is_valid = bool(bot_info.get("id"))
                
            elif integration.provider == "instagram":
                from app.services.integrations.instagram import InstagramClient
                client = InstagramClient(creds)
                is_valid = await client.test_connection()
                
            elif integration.provider == "facebook":
                from app.services.integrations.facebook import FacebookClient
                client = FacebookClient(creds)
                is_valid = await client.test_connection()
                
            else:
                error_msg = f"Unknown provider: {integration.provider}"
                
        except Exception as e:
            error_msg = str(e)
            is_valid = False
            
        # 3. Update status
        if is_valid:
            integration.status = IntegrationStatus.CONNECTED
            integration.last_sync = datetime.utcnow()
        else:
            integration.status = IntegrationStatus.ERROR
            # We might want to store the error message in a metadata field or log it
            logger.error("Integration verification failed", integration_id=integration_id, error=error_msg)
            
        await self.db.commit()
        
        return {
            "status": "verified" if is_valid else "failed", 
            "integration_id": integration_id,
            "valid": is_valid,
            "error": error_msg
        }

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_verify())
    else:
        return asyncio.run(_verify())


@celery_app.task(bind=True, base=DatabaseTask, max_retries=3)
def schedule_followup(
    self,
    customer_id: str,
    message: str,
    delay_hours: int,
    channel: str,
    project_id: str
):
    """
    Schedule a follow-up message to be sent after a delay.
    
    Args:
        customer_id: Customer identifier
        message: Message content
        delay_hours: Hours to wait before sending
        channel: Communication channel
        project_id: Project UUID
    """
    logger.info(
        "Scheduling follow-up",
        customer_id=customer_id,
        delay_hours=delay_hours,
        channel=channel
    )
    
    # Schedule the message to be sent later
    send_message_task.apply_async(
        args=[{
            "customer_id": customer_id,
            "message": message,
            "channel": channel,
            "project_id": project_id
        }],
        countdown=delay_hours * 3600  # Convert hours to seconds
    )
    
    return {"status": "scheduled"}


@celery_app.task(bind=True)
def health_check(self):
    """Simple health check task for monitoring."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Task routing configuration
celery_app.conf.task_routes = {
    "app.workers.tasks.send_message_task": {"queue": "messages"},
    "app.workers.tasks.generate_ai_response": {"queue": "ai"},
    "app.workers.tasks.train_model": {"queue": "training"},
    "app.workers.tasks.sync_*": {"queue": "sync"},
    "app.workers.tasks.generate_*": {"queue": "reports"},
}

@celery_app.task(bind=True, base=DatabaseTask)
def generate_daily_reports(self):
    """Generate daily reports for all active projects."""
    logger.info("Generating daily reports")
    
    import asyncio
    
    async def _generate():
        # Get all active projects
        result = await self.db.execute(select(Project).where(Project.status == "active"))
        projects = result.scalars().all()
        
        reports_count = 0
        for project in projects:
            # Create a dummy report for now
            report = Report(
                project_id=project.id,
                type="daily_summary",
                data={
                    "sales": 0,
                    "messages": 0,
                    "generated_at": datetime.utcnow().isoformat()
                },
                created_at=datetime.utcnow()
            )
            self.db.add(report)
            reports_count += 1
            
        await self.db.commit()
        return {"status": "completed", "reports_generated": reports_count}

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_generate())
    else:
        return asyncio.run(_generate())


@celery_app.task(bind=True, base=DatabaseTask)
def train_model(self, training_id: str):
    """
    Train or fine-tune an AI model for a project.
    
    Args:
        training_id: UUID of the ModelTraining record
    """
    logger.info("Starting model training", training_id=training_id)
    
    # Placeholder for actual training logic
    # In a real scenario, this would submit a job to Vertex AI
    
    return {"status": "completed", "training_id": training_id, "note": "Training simulation completed"}


@celery_app.task(bind=True, base=DatabaseTask)
def cleanup_old_logs(self):
    """Delete API logs older than 90 days."""
    logger.info("Cleaning up old logs")
    
    import asyncio
    from sqlalchemy import delete
    
    async def _cleanup():
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        # Delete old logs
        # Note: APILog model needs to be imported if we want to use it in delete statement
        # Assuming APILog is available from the top imports
        
        result = await self.db.execute(
            delete(APILog).where(APILog.created_at < cutoff_date)
        )
        deleted_count = result.rowcount
        await self.db.commit()
        
        return {"status": "completed", "deleted": deleted_count}

    loop = asyncio.get_event_loop()
    if loop.is_running():
        return loop.run_until_complete(_cleanup())
    else:
        return asyncio.run(_cleanup())
