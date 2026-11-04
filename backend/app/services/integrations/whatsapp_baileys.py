"""
WhatsApp Baileys Service for self-hosted gateway integration.
"""

from typing import Dict, Any, Optional
import structlog
from app.services.whatsapp_gateway_client import WhatsAppGatewayClient

logger = structlog.get_logger(__name__)


class WhatsAppBaileysService:
    """Service wrapping self-hosted Baileys gateway communication."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> None:
        self.session_id = session_id
        self.client = WhatsAppGatewayClient(base_url=base_url, api_key=api_key)
        self.base_url = self.client.base_url
        self.api_key = self.client.api_key

    async def aclose(self) -> None:
        """Close client resources."""
        await self.client.aclose()

    @staticmethod
    def normalize_jid(to: str) -> str:
        """Format number into standard WhatsApp recipient address."""
        clean = to.replace("@s.whatsapp.net", "").replace("@c.us", "").lstrip("+").strip()
        return f"{clean}@s.whatsapp.net" if clean else ""

    async def start_session(
        self,
        session_id_or_project_id: Optional[str] = None,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Start or refresh a Baileys session to generate pairing QR code."""
        actual_session_id = self.session_id
        actual_project_id = project_id

        # Allow flexible call signatures: start_session(project_id) or start_session(session_id)
        if session_id_or_project_id and not project_id:
            if not actual_session_id:
                actual_session_id = session_id_or_project_id
            else:
                actual_project_id = session_id_or_project_id
        elif session_id_or_project_id and project_id:
            actual_session_id = session_id_or_project_id
            actual_project_id = project_id

        if not actual_session_id:
            raise ValueError("session_id must be set to start a WhatsApp session")

        return await self.client.create_session(
            session_id=actual_session_id,
            project_id=actual_project_id,
            metadata=metadata
        )

    async def get_status(self) -> Dict[str, Any]:
        """Fetch status of current session."""
        if not self.session_id:
            return {"status": "uninitialized"}
        return await self.client.get_session_status(self.session_id)

    async def send_message(
        self,
        to: str,
        message: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send outbound text message through Baileys gateway."""
        if not self.session_id:
            raise ValueError("Cannot send message without an active session_id")
        jid = self.normalize_jid(to)
        return await self.client.send_message(
            session_id=self.session_id,
            to=jid,
            message=message,
            message_type=message_type,
            extra=extra
        )

    async def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image"
    ) -> Dict[str, Any]:
        """Send media message through Baileys gateway."""
        if not self.session_id:
            raise ValueError("Cannot send media without an active session_id")
        jid = self.normalize_jid(to)
        extra = {"media_url": media_url, "caption": caption or ""}
        return await self.client.send_message(
            session_id=self.session_id,
            to=jid,
            message=caption or "",
            message_type=media_type,
            extra=extra
        )

    async def logout_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Close and discard Baileys session."""
        target_id = session_id or self.session_id
        if not target_id:
            return {"status": "closed"}
        return await self.client.close_session(target_id)

    def parse_webhook(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize Baileys webhook payload into standard Automind format."""
        try:
            msg_obj = payload.get("message", payload)
            key = msg_obj.get("key", {})
            remote_jid = key.get("remoteJid", "")
            from_number = remote_jid.split("@")[0] if remote_jid else ""
            msg_id = key.get("id", "")
            push_name = msg_obj.get("pushName") or payload.get("pushName") or "WhatsApp User"
            timestamp = msg_obj.get("messageTimestamp", 0)

            inner_msg = msg_obj.get("message", {})
            text = (
                inner_msg.get("conversation")
                or inner_msg.get("extendedTextMessage", {}).get("text")
                or ""
            )

            media_type = None
            media_url = None
            media_data = None

            for m_key, m_type in (
                ("imageMessage", "image"),
                ("videoMessage", "video"),
                ("audioMessage", "audio"),
                ("documentMessage", "document")
            ):
                if m_key in inner_msg:
                    media_type = m_type
                    media_block = inner_msg[m_key]
                    media_url = media_block.get("url")
                    media_data = {
                        "mimetype": media_block.get("mimetype"),
                        "file_length": media_block.get("fileLength")
                    }
                    if not text:
                        text = media_block.get("caption") or ""
                    break

            metadata = payload.get("metadata", {})
            return {
                "message_id": msg_id,
                "from": from_number,
                "text": text,
                "contact": {
                    "name": push_name,
                    "phone": from_number
                },
                "timestamp": timestamp,
                "from_me": key.get("fromMe", False),
                "session_id": payload.get("session_id"),
                "project_id": metadata.get("project_id"),
                "media_type": media_type,
                "media_url": media_url,
                "media_data": media_data,
                "raw_message": payload
            }
        except Exception as e:
            logger.error("Failed parsing Baileys webhook", error=str(e))
            return None
