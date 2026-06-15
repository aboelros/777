"""WhatsApp Business Cloud API client."""

from __future__ import annotations

from typing import Any, Dict, Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)


class WhatsAppBusinessAPIError(RuntimeError):
    """Raised when WhatsApp Business API returns an error."""


class WhatsAppBusinessAPI:
    """Client for WhatsApp Business Cloud API (official Meta API)."""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        *,
        timeout_seconds: int = 30,
    ) -> None:
        if not phone_number_id:
            raise ValueError("WhatsApp phone number ID is required")
        if not access_token:
            raise ValueError("WhatsApp access token is required")
        
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.timeout = httpx.Timeout(timeout_seconds, connect=timeout_seconds)
    
    async def send_text_message(
        self,
        to: str,
        message: str,
        *,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp Business API.
        
        Args:
            to: Recipient phone number (international format without +)
            message: Message text
            preview_url: Whether to show URL preview
            
        Returns:
            API response with message ID
        """
        # Clean phone number
        to = to.lstrip("+").strip()
        
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": message
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(
                    "WhatsApp message sent",
                    to=to,
                    message_id=data.get("messages", [{}])[0].get("id")
                )
                
                return data
        except httpx.HTTPStatusError as exc:
            logger.error(
                "WhatsApp API HTTP error",
                status_code=exc.response.status_code,
                body=exc.response.text,
            )
            raise WhatsAppBusinessAPIError(
                f"API returned status {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except Exception as e:
            logger.error("Failed to send WhatsApp message", error=str(e))
            raise WhatsAppBusinessAPIError(f"Failed to send message: {str(e)}") from e
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        *,
        components: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Send a template message (for notifications).
        
        Args:
            to: Recipient phone number
            template_name: Name of approved template
            language_code: Template language (e.g., 'en', 'ar')
            components: Template components (parameters, buttons, etc.)
            
        Returns:
            API response with message ID
        """
        to = to.lstrip("+").strip()
        
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(
                    "WhatsApp template sent",
                    to=to,
                    template=template_name,
                    message_id=data.get("messages", [{}])[0].get("id")
                )
                
                return data
        except httpx.HTTPStatusError as exc:
            logger.error(
                "WhatsApp API HTTP error",
                status_code=exc.response.status_code,
                body=exc.response.text,
            )
            raise WhatsAppBusinessAPIError(
                f"API returned status {exc.response.status_code}: {exc.response.text}"
            ) from exc
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read."""
        url = f"{self.BASE_URL}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
