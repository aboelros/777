"""
Centralized Webhook Gateway for receiving and dispatching events from all integration platforms.
"""

from typing import Dict, Any, Optional
from uuid import UUID
import structlog
from fastapi import Request, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import ServiceContext
from app.services.webhook_domain import WebhookEvent, EventType, NormalizedMessage
from app.services.webhook_adapters import (
    MetaAdapter,
    TelegramAdapter,
    WAGatewayAdapter,
    ShopifyAdapter,
    TikTokAdapter,
    DiscordAdapter,
    BaseAdapter
)
from app.services.webhook_processor import WebhookProcessor
from app.services.webhook_resolver import WebhookProjectResolver

logger = structlog.get_logger(__name__)


class WebhookGateway:
    """Centralized inbound gateway dispatching to domain processors."""

    def __init__(self, db: AsyncSession, background_tasks: BackgroundTasks):
        self.db = db
        self.background_tasks = background_tasks
        self.resolver = WebhookProjectResolver(db)
        self.adapters: Dict[str, BaseAdapter] = {
            "meta": MetaAdapter(),
            "telegram": TelegramAdapter(),
            "wa_gateway": WAGatewayAdapter(),
            "shopify": ShopifyAdapter(),
            "tiktok": TikTokAdapter(),
            "discord": DiscordAdapter()
        }

    async def handle_inbound(
        self,
        request: Request,
        explicit_project_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Handle incoming webhook request across supported platforms."""
        try:
            body = await request.body()
            payload = await request.json()
        except Exception:
            payload = {}
            body = b""

        platform = self._detect_platform(request, payload)
        if not platform:
            logger.warning("Unknown webhook platform", headers=request.headers)
            return {"status": "ignored", "reason": "unknown_platform"}

        adapter = self.adapters.get(platform)
        if not adapter:
            logger.error("No adapter for platform", platform=platform)
            return {"status": "error", "reason": "no_adapter"}

        if not adapter.verify_signature(request, body):
            if platform == "discord":
                raise HTTPException(status_code=401, detail="Invalid signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

        if platform == "discord" and payload.get("type") == 1:
            return {"type": 1}

        event = adapter.normalize(payload)
        if not event:
            return {"status": "ignored"}

        project_id = await self.resolver.resolve_project(event, explicit_project_id)
        if not project_id:
            logger.warning("Could not resolve project for event", event_id=event.event_id, platform=platform)
            return {"status": "ignored", "reason": "project_not_found"}

        event.project_id = project_id
        await self._dispatch(event)
        return {"status": "processed", "project_id": str(project_id)}

    def _detect_platform(self, request: Request, payload: Dict[str, Any]) -> Optional[str]:
        """Detect incoming platform from headers or payload patterns."""
        headers = request.headers

        if "X-Hub-Signature-256" in headers and "object" in payload:
            return "meta"
        if "X-WA-Signature" in headers:
            return "wa_gateway"
        if "X-Telegram-Bot-Api-Secret-Token" in headers:
            return "telegram"
        if "X-Shopify-Hmac-Sha256" in headers:
            return "shopify"
        if "X-Signature-Ed25519" in headers:
            return "discord"
        if "X-Tiktok-Signature" in headers:
            return "tiktok"

        if "object" in payload and payload["object"] in ["whatsapp_business_account", "page", "instagram"]:
            return "meta"
        if "session_id" in payload or ("data" in payload and "session_id" in payload["data"]):
            return "wa_gateway"
        if "update_id" in payload:
            return "telegram"
        if "order_number" in payload or ("first_name" in payload and "orders_count" in payload):
            return "shopify"
        if "shop_id" in payload and "type" in payload and isinstance(payload["type"], int):
            return "tiktok"
        if "event" in payload and payload["event"].startswith("message."):
            return "tiktok"
        if "message" in payload:
            return "telegram"

        return None

    async def _dispatch(self, event: WebhookEvent) -> None:
        """Dispatch validated and normalized event to WebhookProcessor."""
        content = event.payload.get("text") or ""
        media_type = "text"

        if event.event_type == EventType.ORDER_CREATED:
            order_id = event.payload.get("order_number", event.event_id)
            total = f"{event.payload.get('total_price', '0')} {event.payload.get('currency', '')}"
            content = f"System Event: New Order #{order_id} received. Total: {total}"
            media_type = "event_order"

        elif event.event_type == EventType.CUSTOMER_CREATED:
            content = f"System Event: New Customer Registered: {event.sender_name}"
            media_type = "event_customer"

        elif event.event_type == EventType.COMMENT_CREATED:
            content = f"New Comment on {event.platform}: {event.payload.get('text') or ''}"
            media_type = "comment"

        final_content = content.strip() if content else ""
        if not final_content:
            logger.warning("Empty content in webhook event, skipping", event_id=event.event_id, sender_id=event.sender_id)
            return

        normalized = NormalizedMessage(
            external_id=event.event_id,
            content=final_content,
            sender_id=event.sender_id,
            sender_name=event.sender_name,
            platform=event.channel,
            provider=event.platform,
            media_url=None,
            media_type=media_type,
            extra_data=event.raw_data,
            is_from_me=event.payload.get("is_echo", False)
        )

        processor = WebhookProcessor(self.db, self.background_tasks)
        context = ServiceContext(service_name="webhook_gateway", project_id=event.project_id, operation="process_event")
        await processor.process_message(context, normalized)
