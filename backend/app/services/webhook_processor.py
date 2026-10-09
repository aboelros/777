from app.core.context import ServiceContext
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timezone
from uuid import UUID
import asyncio
import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import BackgroundTasks

from app.domains.messages.models import Message, MessageDirection
from app.domains.customers.models import CustomerProfile
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.orders.models import Order
from app.domains.social.models import SocialMediaComment
from app.workers.tasks import process_incoming_message
from app.services.integrations.facebook import FacebookClient
from app.services.file_storage import FileStorageService, PostgresStorageService

import aiohttp
from app.core.websockets import manager as ws_manager

logger = structlog.get_logger(__name__)


from app.services.webhook_domain import NormalizedMessage

import time
DEDUP_WINDOW_SECONDS = 60  # Reject duplicates within 60 seconds
_processing_lock = asyncio.Lock()


async def _is_duplicate(key: str) -> bool:
    """Check if message key was recently processed. Uses Redis when available, falls back to local dict."""
    try:
        from app.services.cache_service import cache
        if cache.enabled and cache.redis_client:
            redis_key = f"dedup:{key}"
            result = await cache.redis_client.get(redis_key)
            if result:
                return True
            await cache.redis_client.setex(redis_key, DEDUP_WINDOW_SECONDS, "1")
            return False
    except Exception:
        pass

    # Fallback: in-memory (single-worker environments only)
    now = time.time()
    # Purge expired entries to prevent unbounded growth
    expired = [k for k, t in _fallback_cache.items() if now - t > DEDUP_WINDOW_SECONDS]
    for k in expired:
        del _fallback_cache[k]

    if key in _fallback_cache:
        return True
    _fallback_cache[key] = now
    return False


_fallback_cache: Dict[str, float] = {}



class WebhookProcessor:
    """
    Centralized service for processing incoming webhooks.
    """

    def __init__(self, db: AsyncSession, background_tasks: BackgroundTasks):
        self.db = db
        self.background_tasks = background_tasks

    async def process_message(
        self,
        context: ServiceContext,
        message_data: NormalizedMessage
    ) -> Dict[str, Any]:
        """
        Main entry point to process a normalized message.
        """
        # Build dedup keys:
        # 1. external_id-based (catches exact same webhook retries)
        dedup_key_eid = f"{context.project_id}:{message_data.provider}:{message_data.external_id}"
        # 2. sender+content fingerprint (catches same message with different mid)
        content_hash = (message_data.content or "")[:100].strip().lower()
        dedup_key_content = f"{context.project_id}:{message_data.sender_id}:{content_hash}"

        logger.debug("Processing webhook message", sender_id=message_data.sender_id, external_id=message_data.external_id, platform=message_data.platform)

        if await _is_duplicate(dedup_key_eid):
            logger.warning(
                "⚠️ Duplicate message rejected (same external_id)",
                external_id=message_data.external_id,
            )
            return {"status": "skipped", "reason": "duplicate_external_id"}

        if await _is_duplicate(dedup_key_content):
            logger.warning(
                "⚠️ Duplicate message rejected (same sender+content within window)",
                external_id=message_data.external_id,
                sender_id=message_data.sender_id,
            )
            return {"status": "skipped", "reason": "duplicate_content_fingerprint"}

        return await self._process_message_inner(context, message_data)

    async def _process_message_inner(
        self,
        context: ServiceContext,
        message_data: NormalizedMessage
    ) -> Dict[str, Any]:
        """Inner processing logic, called after dedup checks pass."""
        # 1. Skip if message is from us (outbound/echo)
        if message_data.is_from_me:
            logger.info("Skipping echo message (mirror of outbound)", external_id=message_data.external_id)
            return {"status": "skipped", "reason": "echo_message"}

        # 2. Get or Create Customer Profile
        customer = await self._get_or_create_customer(context, message_data)

        # 3. Save Message to Database
        message = await self._save_message(context, customer.id, message_data)

        if not message:
            # Message might be a duplicate
            return {"status": "skipped", "reason": "duplicate_or_error"}

        # 3.5 Broadcast new message via WebSocket
        try:
            await ws_manager.broadcast_to_project(context.project_id, {
                "type": "new_message",
                "message": {
                    "id": str(message.id),
                    "content": message.content,
                    "direction": message.direction,
                    "platform": message.platform,
                    "created_at": message.created_at.isoformat() if message.created_at else datetime.now().isoformat(),
                    "customer_id": str(customer.id),
                    "customer_name": customer.name,
                    "customer_avatar": customer.avatar_url
                }
            })
        except Exception as ws_err:
            logger.warning("WebSocket broadcast failed", error=str(ws_err))

        # 4. Trigger AI Processing
        self._trigger_ai_processing(message.id, context.project_id)

        return {
            "status": "processed",
            "message_id": str(message.id),
            "customer_id": str(customer.id)
        }

    async def _get_or_create_customer(
        self,
        context: ServiceContext,
        data: NormalizedMessage
    ) -> CustomerProfile:
        """Find existing customer or create a new one concurrently safe."""

        query = select(CustomerProfile).where(
            CustomerProfile.project_id == context.project_id,
            CustomerProfile.customer_id == data.sender_id
        )
        result = await self.db.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            # Create new customer concurrently safe
            try:
                customer = CustomerProfile(
                    project_id=context.project_id,
                    customer_id=data.sender_id,
                    name=data.sender_name,
                    platform_accounts={data.platform: data.sender_id},
                    phone=data.sender_id if data.platform == "whatsapp" else None
                )
                self.db.add(customer)
                await self.db.commit()
                await self.db.refresh(customer)

                logger.info(
                    "Created new customer profile",
                    customer_id=str(customer.id),
                    project_id=str(context.project_id)
                )
            except IntegrityError:
                # Concurrent webhook already created the customer
                await self.db.rollback()
                result = await self.db.execute(query)
                customer = result.scalar_one()

        # Check if we should try to fetch/update the profile (both for NEW and EXISTING)
        # 1. If currently "Unknown" or generic
        is_generic_name = not customer.name or customer.name in ["Unknown", "Facebook User", "Instagram User"] or customer.name.strip() == ""
        # 2. If avatar is completely missing OR is an external Meta URL (which expire)
        is_missing_avatar = not customer.avatar_url or "facebook.com" in customer.avatar_url or "cdninstagram.com" in customer.avatar_url

        # 3. Throttle fetching to avoid API limits (once every 10 minutes for testing/setup)
        time_since_sync = 999999
        if customer.last_sync:
            time_since_sync = (datetime.now(timezone.utc) - customer.last_sync).total_seconds() / 60

        logger.debug("Customer sync check", customer_id=str(customer.customer_id), has_name=bool(customer.name), time_since_sync_min=round(time_since_sync, 1))

        # Relaxed throttle to 0.1 minutes (6 seconds) for intensive testing
        should_sync = (is_generic_name or is_missing_avatar) and (time_since_sync > 0.1)



        if should_sync:
            real_name = customer.name
            fetched_profile = None

            # Try fetching from platform API
            if data.platform in ["facebook", "instagram"]:
                logger.info("Enriching customer profile via API",
                            customer_id=data.sender_id,
                            platform=data.platform,
                            current_name=customer.name)
                fetched_profile = await self._fetch_facebook_profile(context.project_id, data.platform, data.sender_id)

            if fetched_profile:
                logger.info("Fetched profile data successfully",
                            customer_id=data.sender_id,
                            fetched_data=fetched_profile)
                # Prioritize username for Instagram, full name for Facebook
                name_from_api = None
                if data.platform == "instagram":
                    name_from_api = fetched_profile.get("username") or fetched_profile.get("name")
                else:
                    name_from_api = f"{fetched_profile.get('first_name', '')} {fetched_profile.get('last_name', '')}".strip()

                if name_from_api and name_from_api not in ["Unknown", "Facebook User", "Instagram User"]:
                    real_name = name_from_api
            else:
                logger.warning("No profile data returned from platform API", customer_id=data.sender_id)
                # LAST_SYNC FIX: Update last_sync even if fetch failed to prevent thrashing
                customer.last_sync = datetime.now(timezone.utc)
                self.db.add(customer)
                await self.db.commit()
                # Continue process - we might still use a payload fallback if available

            # Update if we found a better name or avatar
            updated = False
            if real_name != customer.name:
                logger.info("Updating customer name", old=customer.name, new=real_name)
                customer.name = real_name
                updated = True

            # Update avatar if fetched
            if fetched_profile:
                # Meta APIs use various keys/formats for profile pictures
                pic_url = None

                # 1. Check direct 'profile_pic' or 'profile_picture_url' (Instagram/Old FB)
                pic_url = fetched_profile.get("profile_pic") or fetched_profile.get("profile_picture_url")

                # 2. Check FB 'picture' object
                if not pic_url and "picture" in fetched_profile:
                    pic_data = fetched_profile["picture"]
                    if isinstance(pic_data, dict):
                        pic_url = pic_data.get("data", {}).get("url")
                    elif isinstance(pic_data, str):
                        pic_url = pic_data

                if pic_url and pic_url != customer.avatar_url:
                    logger.info("Updating customer avatar URL", avatar_url=pic_url[:50] + "...")

                    # Persist to local storage if it's an external URL
                    if pic_url.startswith("http"):
                        persistent_url = await self._persist_avatar(context.project_id, customer.id, pic_url)
                        if persistent_url:
                            customer.avatar_url = persistent_url
                            updated = True
                        else:
                            customer.avatar_url = pic_url
                            updated = True
                    else:
                        customer.avatar_url = pic_url
                        updated = True

                # Only update last_sync if we actually performed a sync attempt (even if no updates found)
                # But only if the DB was reached and we didn't error out before this
                customer.last_sync = datetime.now(timezone.utc)
                self.db.add(customer)
                await self.db.commit()
            else:
                # PAYLOAD FALLBACK: If API enrichment failed but message extra_data contains a profile pic, use it
                pic_url = None
                extra = data.extra_data or {}
                # Look into raw payload if available (Meta often nests it here)
                raw_entry = extra.get("entry", [{}])[0]
                raw_messaging = raw_entry.get("messaging", [{}])[0]

                # Check multiple potential locations for PFP
                metadata = data.metadata if isinstance(data.metadata, dict) else {}
                pic_url = (
                    raw_messaging.get("sender", {}).get("profile_pic") or
                    extra.get("profile_pic") or
                    extra.get("avatar_url") or
                    metadata.get("profile_pic")
                )

                if pic_url and "http" in str(pic_url) and pic_url != customer.avatar_url:
                    persistent_url = await self._persist_avatar(context.project_id, customer.id, str(pic_url))
                    if persistent_url:
                        customer.avatar_url = persistent_url
                        customer.last_sync = datetime.now(timezone.utc)
                        self.db.add(customer)
                        await self.db.commit()

        return customer

    async def _fetch_facebook_profile(self, project_id: UUID, platform: str, sender_id: str) -> Optional[Dict[str, Any]]:
        """Helper to fetch real profile from Facebook/Instagram."""
        try:
            # Broaden provider search to include 'meta' which might be used for unified integrations
            provider_to_match = ["facebook", "meta"] if platform == "facebook" else ["instagram", "meta"]

            query = select(Integration).where(
                Integration.project_id == project_id,
                Integration.provider.in_(provider_to_match),
                Integration.status == IntegrationStatus.CONNECTED
            )
            result = await self.db.execute(query)
            integration = result.scalars().first()

            if not integration:
                logger.warning("No connected integration found for profile fetch",
                               platform=platform,
                               providers=provider_to_match)
                return None

            client = FacebookClient(integration.config)
            profile = await client.get_user_profile(sender_id, platform=platform)

            return profile if profile else None
        except Exception as e:
            logger.error("Error fetching Meta profile", error=str(e), platform=platform, sender_id=sender_id)
            return None

    async def _persist_avatar(self, project_id: UUID, customer_profile_id: UUID, external_url: str) -> Optional[str]:
        """Download remote avatar and save to internal storage."""
        if not external_url or not external_url.startswith("http"):
            return external_url

        try:
            logger.info("Downloading avatar for persistence", url=external_url[:50] + "...")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(external_url, timeout=10) as resp:
                    if resp.status != 200:
                        logger.warning("Failed to download avatar", status=resp.status, url=external_url[:50])
                        return None

                    image_data = await resp.read()
                    content_type = resp.headers.get("Content-Type", "image/jpeg")

            # Use FileStorageService to persist
            provider = FileStorageService._get_storage_provider()
            if not provider:
                logger.warning("No storage provider available for avatar persistence")
                return None

            # Create a unique key for this avatar
            ext = ".jpg"
            if "png" in content_type: ext = ".png"
            elif "webp" in content_type: ext = ".webp"

            key = f"avatars/{project_id}/{customer_profile_id}{ext}"

            # Mock a file object for the providers
            class MockFile:
                def __init__(self, data, ct):
                    self.data = data
                    self.content_type = ct
                async def read(self): return self.data
                async def seek(self, pos): pass

            mock_file = MockFile(image_data, content_type)
            stored_key = await provider.upload_image(mock_file, key, content_type)

            if not stored_key:
                logger.warning("Failed to upload avatar to storage provider")
                return None

            if isinstance(provider, PostgresStorageService):
                from app.core.config import settings
                base_url = settings.API_BASE_URL.rstrip('/') if settings.API_BASE_URL else ""
                return f"{base_url}/api/{settings.API_VERSION}/storage/images/{stored_key}"

            elif "S3StorageService" in str(type(provider)):
                # If it's S3, return a long-lived presigned URL or public URL
                from app.core.config import settings
                if settings.S3_PUBLIC_DOMAIN:
                    return f"https://{settings.S3_PUBLIC_DOMAIN}/{stored_key}"

                # Fallback to presigned with 7 days expiration
                if hasattr(provider, "generate_presigned_url"):
                    return provider.generate_presigned_url(stored_key, expiration=3600*24*7)

            return None
        except Exception as e:
            logger.error("Failed to persist avatar", error=str(e))
            return None

    async def _save_message(
        self,
        context: ServiceContext,
        customer_id: UUID,
        data: NormalizedMessage
    ) -> Optional[Message]:
        """Save the message to the database."""

        # Check for duplicates (idempotency)
        # We rely on the unique constraint on (project_id, provider, external_id)
        # But we check explicitly to avoid DB error noise
        existing_query = select(Message).where(
            Message.project_id == context.project_id,
            Message.provider == data.provider,
            Message.external_id == data.external_id
        )
        existing_result = await self.db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            logger.info("Skipping duplicate message (already exists)", external_id=data.external_id)
            return None

        # Handle special event types
        order_id = None

        if data.media_type == "event_order":
            try:
                # Extract order details from extra_data or payload
                # Note: NormalizedMessage.extra_data contains the raw event payload
                raw_payload = data.extra_data.get("payload", {})

                new_order = Order(
                    project_id=context.project_id,
                    customer_id=customer_id,
                    external_id=data.external_id, # Use event ID as order external ID or parse from payload
                    provider=data.provider,
                    status=raw_payload.get("financial_status", "pending"),
                    total=float(raw_payload.get("total_price", 0.0)),
                    currency=raw_payload.get("currency", "USD"),
                    items=raw_payload.get("items", []),
                    extra_data=data.extra_data
                )
                self.db.add(new_order)
                await self.db.flush() # Get ID
                order_id = new_order.id
                logger.info("Created new Order record", order_id=str(order_id))

            except Exception as e:
                logger.error("Failed to create Order record", error=str(e))
                # Continue to create message anyway

        elif data.media_type == "comment":
            try:
                # Create SocialMediaComment
                new_comment = SocialMediaComment(
                    project_id=context.project_id,
                    platform=data.platform,
                    external_id=data.external_id,
                    content=data.content,
                    author_id=data.sender_id,
                    author_username=data.sender_name,
                    extra_data=data.extra_data
                )
                self.db.add(new_comment)
                await self.db.flush()
                logger.info("Created new SocialMediaComment record")
            except Exception as e:
                logger.error("Failed to create SocialMediaComment record", error=str(e))

        # Create Message object
        new_message = Message(
            project_id=context.project_id,
            customer_id=customer_id,
            order_id=order_id, # Link to order if created
            content=data.content,
            direction=MessageDirection.INBOUND,
            platform=data.platform,
            provider=data.provider,
            external_id=data.external_id,
            sender={
                "id": data.sender_id,
                "name": data.sender_name,
                "platform": data.platform
            },
            content_type=data.media_type or "text",
            status="received",
            extra_data=data.extra_data
        )

        # Check for Escalation Keywords
        if self._detect_escalation(data.content):
            new_message.extra_data["is_escalation"] = True
            new_message.extra_data["escalation_reason"] = "customer_request"
            logger.warning("🔥 Escalation detected!", customer_id=str(customer_id))

        # Analyze Sentiment (Fast)
        if data.direction == MessageDirection.INBOUND:
            sentiment = self._analyze_basic_sentiment(data.content)
            new_message.extra_data["sentiment"] = sentiment
            # Log significant sentiment
            if sentiment in ["negative", "urgent"]:
                logger.info(f"Sentiment detected: {sentiment}", customer_id=str(customer_id))

        # Handle media attachments if present
        if data.media_url:
            new_message.attachments = [{
                "url": data.media_url,
                "type": data.media_type
            }]

        try:
            self.db.add(new_message)
            await self.db.commit()
            await self.db.refresh(new_message)
            return new_message

        except IntegrityError as e:
            # Duplicate key / unique constraint violation
            logger.warning(
                "Duplicate message detected (IntegrityError)",
                external_id=data.external_id,
                project_id=str(context.project_id),
                error=str(e)[:200]
            )
            await self.db.rollback()
            return None

        except Exception as e:
            error_msg = str(e).lower()
            # Catch any other duplicate-related errors (asyncpg wrapping, etc.)
            if any(kw in error_msg for kw in ["unique constraint", "duplicate key", "uniqueviolation"]):
                logger.warning(
                    "Duplicate message detected (generic)",
                    external_id=data.external_id,
                    project_id=str(context.project_id)
                )
                await self.db.rollback()
                return None

            logger.error(
                "Failed to save message",
                error=str(e),
                external_id=data.external_id
            )
            await self.db.rollback()
            raise e

    def _detect_escalation(self, content: str) -> bool:
        """Check if message requires human attention."""
        if not content:
            return False

        keywords = [
            "talk to human", "speak to human", "real person",
            "talk to agent", "speak to agent", "representative",
            "manager", "supervisor", "complain", "complaint",
            "issue", "problem", "angry", "upset", "refund",
            "talk to someone", "support"
        ]

        text = content.lower()
        return any(k in text for k in keywords)

    def _analyze_basic_sentiment(self, content: str) -> str:
        """
        Fast rule-based sentiment analysis for immediate feedback.
        Returns: positive, negative, neutral, urgent
        """
        if not content:
            return "neutral"

        text = content.lower()

        # Urgent keywords (Highest priority)
        urgent_keywords = [
            "urgent", "asap", "emergency", "immediately", "broke",
            "crisis", "serious", "stuck", "fail", "not working",
            "cancelled", "help now"
        ]
        if any(k in text for k in urgent_keywords):
            return "urgent"

        # Positive keywords
        positive_keywords = [
            "thank", "good", "great", "awesome", "amazing", "love",
            "perfect", "excellent", "happy", "liked", "best",
            "cool", "nice", "appreciate", "wonderful", "satisfied"
        ]
        if any(k in text for k in positive_keywords):
            return "positive"

        # Negative keywords
        negative_keywords = [
            "bad", "terrible", "worst", "hate", "slow", "awful",
            "wrong", "mistake", "error", "useless", "stupid",
            "refund", "waste", "disappointed", "poor", "never"
        ]
        if any(k in text for k in negative_keywords):
            return "negative"

        return "neutral"

    def _trigger_ai_processing(self, message_id: UUID, project_id: UUID):
        """Queue the AI processing task."""

        # Define a wrapper to run the AI logic directly (bypassing Celery for now)
        # This ensures it runs even if no worker is active.
        async def run_ai_logic(msg_id: str, proj_id: str):
            try:
                from app.domains.ai.orchestrator import AIOrchestrator
                from app.domains.messages.models import Message
                from app.core.database import AsyncSessionLocal

                logger.info("Starting AI processing (direct)", message_id=msg_id)

                async with AsyncSessionLocal() as db:
                    # Fetch message
                    result = await db.execute(
                        select(Message).where(Message.id == UUID(msg_id))
                    )
                    message = result.scalar_one_or_none()

                    if not message:
                        logger.error("Message not found for AI processing", message_id=msg_id)
                        return

                    # Initialize AI orchestrator
                    orchestrator = AIOrchestrator(db)
                    await orchestrator.initialize_integrations(UUID(proj_id))

                    # Process message with AI
                    response = await orchestrator.process_customer_message(
                        customer_id=message.customer_id,
                        message_content=message.content,
                        channel=message.platform,
                        project_id=UUID(proj_id),
                        media_url=message.attachments[0].get("url") if message.attachments else None,
                        media_type=message.attachments[0].get("type") if message.attachments else message.content_type
                    )

                    logger.info(
                        "Message processed by AI (direct)",
                        message_id=msg_id,
                        response=str(response)[:100]
                    )
            except Exception as e:
                logger.error("AI processing failed (direct)", error=str(e), message_id=msg_id)
                import traceback
                traceback.print_exc()

        # Schedule the async wrapper
        # FastAPI BackgroundTasks can handle async functions
        self.background_tasks.add_task(
            run_ai_logic,
            str(message_id),
            str(project_id)
        )

        logger.info(
            "Queued AI processing (direct mode)",
            message_id=str(message_id),
            project_id=str(project_id)
        )
