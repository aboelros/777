import structlog
from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import Request, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.context import ServiceContext
from app.domains.integrations.models import Integration, IntegrationStatus

from app.services.webhook_domain import WebhookEvent, EventType
from app.services.webhook_adapters import (
    MetaAdapter,
    TelegramAdapter,
    WAGatewayAdapter,
    ShopifyAdapter,
    TikTokAdapter,
    DiscordAdapter, # Added
    BaseAdapter
)
from app.services.webhook_processor import WebhookProcessor
from app.services.webhook_domain import NormalizedMessage
# ... imports ...

logger = structlog.get_logger(__name__)

class WebhookGateway:
    # ...
    def __init__(self, db: AsyncSession, background_tasks: BackgroundTasks):
        self.db = db
        self.background_tasks = background_tasks
        self.adapters: Dict[str, BaseAdapter] = {
            "meta": MetaAdapter(),
            "telegram": TelegramAdapter(),
            "wa_gateway": WAGatewayAdapter(),
            "shopify": ShopifyAdapter(),
            "tiktok": TikTokAdapter(),
            "discord": DiscordAdapter() # Added
        }



    async def handle_inbound(self, request: Request, explicit_project_id: Optional[UUID] = None) -> Dict[str, Any]:
        # 1. Read Body & Payload
        try:
            body = await request.body()
            payload = await request.json()
        except Exception:
            # Some webhooks might be form-data or empty?
            # For now, assume JSON or valid body
            payload = {}
            body = b""

        # 2. Detect Platform
        platform = self._detect_platform(request, payload)

        if not platform:
             # Fallback or error?
             # For explicit endpoints (e.g. /webhooks/whatsapp), we might know the platform
             # But this gateway is generic.
             # If we can't identify it, we might log and ignore or try a default?
             logger.warning("Unknown webhook platform", headers=request.headers)
             # Try to process anyway if it looks like a message?
             # For now, return 200 to acknowledge receipt and avoid retries loop from sender
             return {"status": "ignored", "reason": "unknown_platform"}

        adapter = self.adapters.get(platform)
        if not adapter:
            logger.error(f"No adapter for platform: {platform}")
            return {"status": "error", "reason": "no_adapter"}

        # 3. Verify Signature
        if not adapter.verify_signature(request, body):
            # Discord requires 401 specifically
            if platform == "discord":
                raise HTTPException(status_code=401, detail="Invalid signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

        # 4. Normalize
        # Special Case: Discord PING
        if platform == "discord" and payload.get("type") == 1:
             return {"type": 1} # PONG

        event = adapter.normalize(payload)
        if not event:
            # Event ignored by adapter (e.g. echo, status update)
            return {"status": "ignored"}

        # 5. Resolve Project
        project_id = await self._resolve_project(event, explicit_project_id)
        if not project_id:
            logger.warning(f"Could not resolve project for event: {event.event_id}", platform=platform)
            # We still return 200 to acknowledge hook
            return {"status": "ignored", "reason": "project_not_found"}

        event.project_id = project_id

        # 6. Dispatch
        await self._dispatch(event)

        return {"status": "processed", "project_id": str(project_id)}

    def _detect_platform(self, request: Request, payload: Dict[str, Any]) -> Optional[str]:
        """Heuristic to detect platform."""
        headers = request.headers

        # Explicit headers
        if "X-Hub-Signature-256" in headers and "object" in payload:
            return "meta"
        if "X-Telegram-Bot-Api-Secret-Token" in headers or "message" in payload:
            return "telegram"
        if "X-Shopify-Hmac-Sha256" in headers:
            return "shopify"
        if "X-Signature-Ed25519" in headers:
            return "discord"
        if "X-Tiktok-Signature" in headers:
            return "tiktok"

        # Payload inspection
        if "object" in payload and payload["object"] in ["whatsapp_business_account", "page", "instagram"]:
            return "meta"
        # ... (rest of logic)
        if "update_id" in payload:
            return "telegram"
        if "session_id" in payload or ("data" in payload and "session_id" in payload["data"]):
            return "wa_gateway"
        if "order_number" in payload or ("first_name" in payload and "orders_count" in payload):
            return "shopify"

        # TikTok Shop Webhooks usually have "shop_id" and "type" (integer)
        if "shop_id" in payload and "type" in payload and isinstance(payload["type"], int):
            return "tiktok"

        # Legacy TikTok Business webhooks
        if "event" in payload and payload["event"].startswith("message."):
            return "tiktok"

        return None

    async def _resolve_project(self, event: WebhookEvent, explicit_project_id: Optional[UUID] = None) -> Optional[str]:
        """Find the project ID deterministically based on event metadata or explicit path binding."""

        # 1. Explicit project ID from URL path (e.g. Telegram / Facebook legacy webhooks)
        if explicit_project_id:
            # We must verify the integration actually exists for this tenant
            query = select(Integration).where(
                Integration.project_id == explicit_project_id,
                Integration.provider == event.channel,
                Integration.status == IntegrationStatus.CONNECTED
            )
            result = await self.db.execute(query)
            integrations = result.scalars().all()
            if len(integrations) == 1:
                return str(explicit_project_id)
            elif len(integrations) > 1:
                logger.error(f"Multiple integrations found for project {explicit_project_id} and provider {event.channel}")
                return None
            else:
                logger.warning(f"No connected integration found for project {explicit_project_id} and provider {event.channel}")
                return None

        # 2. Meta (WhatsApp Business API)
        if event.platform == "meta" and event.channel == "whatsapp":
            phone_id = event.payload.get("metadata", {}).get("phone_number_id")
            if phone_id:
                query = select(Integration).where(
                    Integration.provider == "whatsapp",
                    Integration.status == IntegrationStatus.CONNECTED
                )
                result = await self.db.execute(query)
                integrations = result.scalars().all()

                matched = []
                for integration in integrations:
                    extra = integration.extra_data or {}
                    stored_id = str(extra.get("phone_number_id", ""))
                    if stored_id == str(phone_id):
                        matched.append(integration.project_id)

                if len(matched) == 1:
                    return str(matched[0])
                elif len(matched) > 1:
                    logger.error(f"Ambiguous mapping: Multiple integrations found for phone_number_id {phone_id}")
                    return None

        # 3. Meta (Facebook/Instagram Pages)
        elif event.platform == "meta" and event.channel in ["facebook", "instagram"]:
            page_id = event.payload.get("entry", [{}])[0].get("id")
            if page_id:
                query = select(Integration).where(
                    Integration.provider.in_(["facebook", "instagram"]),
                    Integration.status == IntegrationStatus.CONNECTED
                )
                result = await self.db.execute(query)
                integrations = result.scalars().all()

                matched = []
                for integration in integrations:
                    config = integration.config or {}
                    stored_id = str(config.get("page_id", ""))
                    if stored_id == str(page_id):
                        matched.append(integration.project_id)

                if len(matched) == 1:
                    return str(matched[0])
                elif len(matched) > 1:
                    logger.error(f"Ambiguous mapping: Multiple integrations found for page_id {page_id}")
                    return None

        # 4. WA Gateway
        elif event.platform == "wa_gateway":
            session_id = event.payload.get("session_id")
            if session_id:
                query = select(Integration).where(
                    Integration.provider == "whatsapp",
                    Integration.status == IntegrationStatus.CONNECTED
                )
                result = await self.db.execute(query)
                integrations = result.scalars().all()
                matched = []
                for integration in integrations:
                    extra = integration.extra_data or {}
                    if extra.get("provider") == "wa_gateway" and str(extra.get("session_id")) == str(session_id):
                        matched.append(integration.project_id)

                if len(matched) == 1:
                    return str(matched[0])
                elif len(matched) > 1:
                    logger.error(f"Ambiguous mapping: Multiple integrations found for session_id {session_id}")
                    return None

        # If no deterministic match was found, we reject safely.
        # DO NOT fallback to .first() or invent arbitrary mappings.
        logger.warning(f"No deterministic tenant mapping found for event from {event.platform} / {event.channel}")
        return None

    async def _dispatch(self, event: WebhookEvent):
        """Send to the internal processor."""

        # Convert Event -> NormalizedMessage for the existing processor
        # (Gradual migration: Gateway -> Processor -> AI)

        # IMPORTANT: payload.get("text", "") returns None if key exists with None value
        # Use explicit `or ""` to handle both missing key AND None value
        content = event.payload.get("text") or ""
        media_type = "text"

        # Handle non-message events by creating a system-like message content
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

        # Final content safety - never pass empty or None
        final_content = content.strip() if content else ""
        if not final_content:
            print(f"DEBUG: âš ï¸ Empty content for event {event.event_id} from {event.sender_id} - skipping dispatch")
            logger.warning("Empty content in webhook event, skipping", event_id=event.event_id, sender_id=event.sender_id)
            return

        print(f"DEBUG: Dispatching message | external_id={event.event_id} | content='{final_content[:60]}' | sender={event.sender_id}")

        normalized = NormalizedMessage(
            external_id=event.event_id,
            content=final_content,
            sender_id=event.sender_id,
            sender_name=event.sender_name,
            platform=event.channel, # whatsapp, telegram, store
            provider=event.platform, # meta, wa_gateway, shopify
            media_url=None, # TODO
            media_type=media_type,
            extra_data=event.raw_data,
            is_from_me=event.payload.get("is_echo", False)
        )

        processor = WebhookProcessor(self.db, self.background_tasks)
        context = ServiceContext(service_name='webhook_gateway', project_id=event.project_id, operation='process_event')
        await processor.process_message(context, normalized)
