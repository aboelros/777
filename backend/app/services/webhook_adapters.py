import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from fastapi import Request, HTTPException

from app.services.webhook_domain import WebhookEvent, EventType
from app.core.config import settings

class BaseAdapter:
    """Base class for all platform adapters."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        """Verify the webhook signature."""
        return True

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        """Convert raw payload to Unified Event."""
        raise NotImplementedError

class MetaAdapter(BaseAdapter):
    """Adapter for Meta (WhatsApp, Instagram, Facebook)."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        # Meta uses X-Hub-Signature-256
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            return False

        if not settings.FACEBOOK_APP_SECRET:
            logger.warning("FACEBOOK_APP_SECRET not set, bypassing signature verification")
            return True

        try:
            # Check if signature starts with sha256=
            if signature.startswith("sha256="):
                signature = signature[7:]

            expected = hmac.new(
                settings.FACEBOOK_APP_SECRET.encode(),
                body,
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error("Signature verification failed", error=str(e))
            return False

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        # Detect specific channel within Meta
        object_type = payload.get("object")

        if object_type == "whatsapp_business_account":
            return self._normalize_whatsapp(payload)
        elif object_type == "instagram":
            print("DEBUG: Normalizing Instagram payload")
            return self._normalize_instagram(payload)
        elif object_type == "page":
            return self._normalize_facebook(payload)

        print(f"DEBUG: Unknown Meta object type: {object_type}")
        return None

    def _normalize_whatsapp(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})

        if "messages" not in value:
            return None

        message = value["messages"][0]
        contact = value.get("contacts", [{}])[0]

        return WebhookEvent(
            event_id=message.get("id"),
            event_type=EventType.MESSAGE_CREATED,
            timestamp=datetime.fromtimestamp(int(message.get("timestamp", 0))),
            platform="meta",
            channel="whatsapp",
            sender_id=message.get("from"),
            sender_name=contact.get("profile", {}).get("name"),
            payload={
                "text": message.get("text", {}).get("body"),
                "type": message.get("type"),
                "media": self._extract_media(message),
                "metadata": value.get("metadata", {}) # Contains phone_number_id
            },
            raw_data=payload
        )

    def _extract_media(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_type = message.get("type")
        if msg_type in ["image", "audio", "video", "document", "sticker"]:
            return message.get(msg_type)
        return None

    def _normalize_instagram(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        print(f"DEBUG: Instagram payload received: {json.dumps(payload)}")
        entries = payload.get("entry", [])
        if not entries:
            return None
        entry = entries[0]

        # 1. Check for changes (comments or messages delivered via changes)
        if "changes" in entry and entry["changes"]:
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})
                if field == "comments":
                    from_user = value.get("from", {})
                    return WebhookEvent(
                        event_id=value.get("id", "unknown_comment"),
                        event_type=EventType.COMMENT_CREATED,
                        timestamp=datetime.now(),
                        platform="meta",
                        channel="instagram",
                        sender_id=from_user.get("id"),
                        sender_name=from_user.get("username"),
                        payload={
                            "text": value.get("text"),
                            "is_comment": True,
                            "media_id": value.get("media", {}).get("id")
                        },
                        raw_data=payload
                    )
                elif field == "messages":
                    sender = value.get("sender", {}) or value.get("from", {})
                    recipient = value.get("recipient", {})
                    msg = value.get("message", value)
                    if msg.get("is_echo"):
                        print("DEBUG: Skipping Instagram echo message via changes")
                        return None
                    return WebhookEvent(
                        event_id=msg.get("mid", f"ig_msg_{value.get('id', 'unknown')}"),
                        event_type=EventType.MESSAGE_CREATED,
                        timestamp=datetime.now(),
                        platform="meta",
                        channel="instagram",
                        sender_id=sender.get("id"),
                        sender_name=sender.get("username"),
                        payload={
                            "text": msg.get("text") or value.get("text"),
                            "media": msg.get("attachments"),
                            "is_echo": False,
                            "page_id": recipient.get("id") or entry.get("id"),
                        },
                        raw_data=payload
                    )

        # 2. Check messaging and standby arrays
        messaging_list = entry.get("messaging", []) or entry.get("standby", [])
        if not messaging_list:
            print(f"DEBUG: No messaging or standby items in Instagram entry: {entry}")
            return None

        messaging = messaging_list[0]
        sender_id = messaging.get("sender", {}).get("id")
        recipient_id = messaging.get("recipient", {}).get("id")
        message = messaging.get("message", {})

        if message.get("is_echo"):
            print("DEBUG: Skipping Instagram echo message (sent by page)")
            return None

        if "delivery" in messaging:
            print("DEBUG: Skipping Instagram delivery notification")
            return None

        if "read" in messaging:
            return WebhookEvent(
                event_id=f"read_{sender_id}_{messaging.get('timestamp')}",
                event_type=EventType.MESSAGE_READ,
                timestamp=datetime.fromtimestamp(int(messaging.get("timestamp", 0)) / 1000),
                platform="meta",
                channel="instagram",
                sender_id=sender_id,
                sender_name=None,
                payload={"read": True, "page_id": recipient_id or entry.get("id")},
                raw_data=payload
            )

        msg_text = message.get("text")
        msg_mid = message.get("mid", "unknown")
        msg_attachments = message.get("attachments")

        print(f"DEBUG: Instagram msg | mid={msg_mid} | text='{msg_text}' | has_attachments={bool(msg_attachments)}")

        if not msg_text and not msg_attachments:
            print("DEBUG: Skipping Instagram message with no text and no attachments")
            return None

        return WebhookEvent(
            event_id=msg_mid,
            event_type=EventType.MESSAGE_CREATED,
            timestamp=datetime.fromtimestamp(int(messaging.get("timestamp", 0)) / 1000),
            platform="meta",
            channel="instagram",
            sender_id=sender_id,
            sender_name=messaging.get("sender", {}).get("username"),
            payload={
                "text": msg_text,
                "media": msg_attachments,
                "is_echo": message.get("is_echo", False),
                "page_id": recipient_id or entry.get("id"),
            },
            raw_data=payload
        )

    def _normalize_facebook(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        entry = payload.get("entry", [])[0]

        if "changes" in entry:
            change = entry["changes"][0]
            if change.get("field") == "feed" and change.get("value", {}).get("item") == "comment":
                value = change.get("value", {})
                return WebhookEvent(
                    event_id=value.get("comment_id", "unknown_comment"),
                    event_type=EventType.COMMENT_CREATED,
                    timestamp=datetime.now(),
                    platform="meta",
                    channel="facebook",
                    sender_id=value.get("from", {}).get("id"),
                    sender_name=value.get("from", {}).get("name"),
                    payload={
                        "text": value.get("message"),
                        "is_comment": True,
                        "post_id": value.get("post_id")
                    },
                    raw_data=payload
                )
            return None

        messaging_list = entry.get("messaging", [])
        if not messaging_list:
            return None

        messaging = messaging_list[0]

        sender_id = messaging.get("sender", {}).get("id")
        message = messaging.get("message", {})

        # Early echo rejection: skip messages sent BY the page (our own outbound)
        if message.get("is_echo"):
            print(f"DEBUG: Skipping Facebook echo message (sent by page)")
            return None

        if "read" in messaging:
            return WebhookEvent(
                event_id=f"read_{sender_id}_{messaging['timestamp']}",
                event_type=EventType.MESSAGE_READ,
                timestamp=datetime.fromtimestamp(int(messaging.get("timestamp", 0)) / 1000),
                platform="meta",
                channel="facebook",
                sender_id=sender_id,
                sender_name=None,
                payload={"read": True},
                raw_data=payload
            )

        if "delivery" in messaging:
             return WebhookEvent(
                event_id=f"delivery_{sender_id}_{messaging['timestamp']}",
                event_type=EventType.MESSAGE_DELIVERED,
                timestamp=datetime.fromtimestamp(int(messaging.get("timestamp", 0)) / 1000),
                platform="meta",
                channel="facebook",
                sender_id=sender_id,
                sender_name=None,
                payload={"delivery": messaging.get("delivery")},
                raw_data=payload
            )

        if not message.get("text") and not message.get("attachments"):
            return None

        return WebhookEvent(
            event_id=message.get("mid", "unknown"),
            event_type=EventType.MESSAGE_CREATED,
            timestamp=datetime.fromtimestamp(int(messaging.get("timestamp", 0)) / 1000),
            platform="meta",
            channel="facebook",
            sender_id=sender_id,
            sender_name=None,
            payload={
                "text": message.get("text"),
                "media": message.get("attachments"),
                "is_echo": message.get("is_echo", False),
                "profile_pic": messaging.get("sender", {}).get("profile_pic"),
                "page_id": entry.get("id"),
            },
            raw_data=payload
        )

class TelegramAdapter(BaseAdapter):
    """Adapter for Telegram."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        # Telegram uses X-Telegram-Bot-Api-Secret-Token
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        # We would need to match this against what we set.
        return True

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        message = payload.get("message", {})
        if not message:
            return None

        from_user = message.get("from", {})
        chat = message.get("chat", {})

        return WebhookEvent(
            event_id=str(message.get("message_id")),
            event_type=EventType.MESSAGE_CREATED,
            timestamp=datetime.fromtimestamp(message.get("date", 0)),
            platform="telegram",
            channel="telegram",
            sender_id=str(from_user.get("id")),
            sender_name=f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip(),
            payload={
                "text": message.get("text"),
                "chat_id": str(chat.get("id")),
                "username": from_user.get("username")
            },
            raw_data=payload
        )

class WAGatewayAdapter(BaseAdapter):
    """Adapter for WA Gateway (Self-hosted)."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        """
        Verify the webhook signature for WA Gateway.
        Expects an HMAC-SHA256 signature in X-WA-Signature header
        and a timestamp in X-WA-Timestamp to prevent replay attacks.
        """
        import hmac
        import hashlib
        import time
        from app.core.config import settings

        signature = request.headers.get("X-WA-Signature")
        timestamp_str = request.headers.get("X-WA-Timestamp")

        if not signature or not timestamp_str:
            return False

        if not settings.WA_GATEWAY_API_KEY:
            # Cannot verify without the secret
            return False

        # 1. Replay protection (reject if older than 5 minutes)
        try:
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            if abs(current_time - timestamp) > 300:
                return False
        except ValueError:
            return False

        # 2. HMAC-SHA256 verification
        # The signature should be computed over the concatenation of timestamp and body
        payload_to_sign = f"{timestamp_str}.".encode("utf-8") + body

        expected_signature = hmac.new(
            settings.WA_GATEWAY_API_KEY.encode("utf-8"),
            msg=payload_to_sign,
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        # WA Gateway structure
        data = payload.get("data", payload) # Sometimes wrapped in data

        if not data.get("text") and not data.get("media"):
             return None

        return WebhookEvent(
            event_id=data.get("message_id", "unknown"),
            event_type=EventType.MESSAGE_CREATED,
            timestamp=datetime.now(), # GoWA might not send timestamp
            platform="wa_gateway",
            channel="whatsapp",
            sender_id=data.get("from"),
            sender_name=data.get("pushName"),
            payload={
                "text": data.get("text"),
                "media": data.get("media_data"),
                "session_id": data.get("session_id")
            },
            raw_data=payload
        )

class ShopifyAdapter(BaseAdapter):
    """Adapter for Shopify."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        # Shopify uses X-Shopify-Hmac-Sha256
        signature = request.headers.get("X-Shopify-Hmac-Sha256")
        if not signature:
            return False

        # We need the app secret to verify.
        if not settings.SHOPIFY_API_SECRET:
            return True # Skip if not configured

        import base64
        expected = base64.b64encode(hmac.new(
            settings.SHOPIFY_API_SECRET.encode(),
            body,
            hashlib.sha256
        ).digest()).decode()

        return hmac.compare_digest(expected, signature)

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        # Shopify events are usually determined by the topic header, not payload content
        # But we can infer from keys

        if "order_number" in payload:
            return self._normalize_order(payload)
        elif "first_name" in payload and "last_name" in payload and "orders_count" in payload:
            return self._normalize_customer(payload)

        return None

    def _normalize_order(self, payload: Dict[str, Any]) -> WebhookEvent:
        return WebhookEvent(
            event_id=str(payload.get("id")),
            event_type=EventType.ORDER_CREATED, # Simplified assumption
            timestamp=datetime.fromisoformat(payload.get("created_at").replace("Z", "+00:00")),
            platform="shopify",
            channel="store",
            sender_id=str(payload.get("customer", {}).get("id", "guest")),
            sender_name=f"{payload.get('customer', {}).get('first_name', '')} {payload.get('customer', {}).get('last_name', '')}".strip(),
            payload={
                "order_id": str(payload.get("id")),
                "order_number": str(payload.get("order_number")),
                "total_price": payload.get("total_price"),
                "currency": payload.get("currency"),
                "financial_status": payload.get("financial_status"),
                "items": payload.get("line_items", [])
            },
            raw_data=payload
        )

    def _normalize_customer(self, payload: Dict[str, Any]) -> WebhookEvent:
        return WebhookEvent(
            event_id=str(payload.get("id")),
            event_type=EventType.CUSTOMER_CREATED,
            timestamp=datetime.fromisoformat(payload.get("created_at").replace("Z", "+00:00")),
            platform="shopify",
            channel="store",
            sender_id=str(payload.get("id")),
            sender_name=f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip(),
            payload={
                "email": payload.get("email"),
                "phone": payload.get("phone"),
                "orders_count": payload.get("orders_count")
            },
            raw_data=payload
        )

class TikTokAdapter(BaseAdapter):
    """Adapter for TikTok."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        signature = request.headers.get("Authorization") # TikTok Shop uses Authorization header
        if not signature:
             signature = request.headers.get("X-Tiktok-Signature")

        if not signature:
            # If no signature, and we have a secret, fail.
            if settings.TIKTOK_APP_SECRET:
                 return False
            return True

        if not settings.TIKTOK_APP_SECRET:
            return True

        import hmac, hashlib
        app_key = getattr(settings, "TIKTOK_APP_KEY", "")

        # Verify TikTok Shop HMAC-SHA256 (AppKey + Body)
        expected = hmac.new(
            settings.TIKTOK_APP_SECRET.encode('utf-8'),
            (app_key + body.decode('utf-8')).encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        # TikTok Shop Payload Structure
        if payload.get("type") == 14:  # 14 = NEW_MESSAGE event
            data = payload.get("data", {})
            content_str = data.get("content", "{}")
            import json
            try:
                content = json.loads(content_str)
            except Exception:
                content = {"text": content_str}

            return WebhookEvent(
                event_id=data.get("message_id", "unknown"),
                event_type=EventType.MESSAGE_CREATED,
                timestamp=datetime.fromtimestamp(data.get("create_time", 0)),
                platform="tiktok",
                channel="tiktok",
                sender_id=data.get("sender_id"),
                sender_name=None,
                payload={
                    "text": content.get("text", ""),
                    "message_type": data.get("message_type", "TEXT")
                },
                raw_data=payload
            )

        # Legacy TikTok Business Payload structure
        event_type = payload.get("event")
        if event_type == "message.receive":
            content = payload.get("content", {})
            return WebhookEvent(
                event_id=payload.get("id", "unknown"),
                event_type=EventType.MESSAGE_CREATED,
                timestamp=datetime.fromtimestamp(payload.get("create_time", 0)),
                platform="tiktok",
                channel="tiktok",
                sender_id=payload.get("from_user_id"),
                sender_name=None,
                payload={
                    "text": content.get("text"),
                    "message_type": content.get("message_type")
                },
                raw_data=payload
            )
        return None

class DiscordAdapter(BaseAdapter):
    """Adapter for Discord Interactions."""

    def verify_signature(self, request: Request, body: bytes) -> bool:
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")

        if not signature or not timestamp or not settings.DISCORD_PUBLIC_KEY:
            return False

        try:
            from nacl.signing import VerifyKey
            from nacl.exceptions import BadSignatureError

            verify_key = VerifyKey(bytes.fromhex(settings.DISCORD_PUBLIC_KEY))
            verify_key.verify(f"{timestamp}{body.decode()}".encode(), bytes.fromhex(signature))
            return True
        except ImportError:
            # If pynacl is not installed, we can't verify. Use logic to determine if we should fail.
            print("WARNING: pynacl not installed, skipping Discord verification")
            return True # Allow for now if missing dep, but insecure
        except BadSignatureError:
            return False
        except Exception as e:
            print(f"Discord verification error: {e}")
            return False

    def normalize(self, payload: Dict[str, Any]) -> Optional[WebhookEvent]:
        # Discord Interaction Payload
        t = payload.get("type")

        # 1 = PING (Handled by Gateway/Router usually before this, but if normalized here...)
        if t == 1:
             return None # PING is handled separately

        # 4 = Application Command
        if t == 4 or t == 1:
             # Only if we treat commands as messages...
             pass

        # We are interested in actual messages if possible, but Interactions are usually Commands.
        # If we receive a DM, it might be via Gateway, not webhook.
        # However, if this ADAPTER is used, it assumes we received an Interaction.

        member = payload.get("member", {}).get("user", {}) if "member" in payload else payload.get("user", {})

        data = payload.get("data", {})

        return WebhookEvent(
            event_id=payload.get("id"),
            event_type=EventType.MESSAGE_CREATED,
            timestamp=datetime.now(),
            platform="discord",
            channel="discord",
            sender_id=member.get("id"),
            sender_name=member.get("username"),
            payload={
                "text": f"Command: {data.get('name')}" if data else "Interaction",
                "interaction_token": payload.get("token"),
                "interaction_id": payload.get("id")
            },
            raw_data=payload
        )
