"""
WhatsApp Gateway Service bridging AIOrchestrator to WhatsAppBaileysService.
"""

from typing import Dict, Any, Optional
import structlog
from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService

logger = structlog.get_logger(__name__)


class WhatsAppGatewayService:
    """Service wrapper for Baileys gateway communication used by AIOrchestrator."""

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        self.base_url = base_url
        self.api_key = api_key

    @staticmethod
    def normalize_jid(to_number: str) -> str:
        """Ensure recipient is in standard @s.whatsapp.net JID format."""
        if not to_number:
            return ""
        # Strip internal labels or LID formats
        clean = to_number.split("@")[0].lstrip("+").strip()
        # Basic check to avoid invalid numbers
        if not clean.isdigit() or len(clean) < 7:
            return ""
        return f"{clean}@s.whatsapp.net"

    async def send_text_message(
        self,
        session_id: str,
        to: str,
        text: str,
        quoting: Optional[Dict[str, Any]] = None,
        mentions: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Send text message with optional quoting context."""
        service = WhatsAppBaileysService(
            session_id=session_id,
            base_url=self.base_url,
            api_key=self.api_key
        )
        try:
            extra = {}
            if quoting:
                extra["quoting"] = quoting
            if mentions:
                extra["mentions"] = mentions

            res = await service.send_message(
                to=to,
                message=text,
                message_type="text",
                extra=extra if extra else None
            )
            return res
        finally:
            await service.aclose()

    async def start_session(self, session_id: str, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Start or retrieve session QR code."""
        service = WhatsAppBaileysService(
            session_id=session_id,
            base_url=self.base_url,
            api_key=self.api_key
        )
        try:
            return await service.start_session(project_id=project_id)
        finally:
            await service.aclose()

    async def logout_session(self, session_id: str) -> Dict[str, Any]:
        """Close session."""
        service = WhatsAppBaileysService(
            session_id=session_id,
            base_url=self.base_url,
            api_key=self.api_key
        )
        try:
            return await service.logout_session()
        finally:
            await service.aclose()
