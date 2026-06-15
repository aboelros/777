"""
WhatsApp Business API integration service.
"""

from typing import Dict, Any
import structlog
import httpx
from app.core.config import settings

logger = structlog.get_logger(__name__)


class WhatsAppService:
    """Service for WhatsApp Business API integration."""
    
    def __init__(self, business_id: str, access_token: str):
        """Initialize WhatsApp service with credentials."""
        self.business_id = business_id
        self.access_token = access_token
        self.api_url = "https://graph.facebook.com/v18.0"
    
    async def send_message(
        self,
        to: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Send a message via WhatsApp.
        
        Args:
            to: Recipient phone number (international format)
            message: Message content
            message_type: Type of message (text, template, etc.)
            
        Returns:
            Response from WhatsApp API
        """
        url = f"{self.api_url}/{self.business_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": message_type,
        }
        
        if message_type == "text":
            payload["text"] = {"body": message}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                result = response.json()
                logger.info("WhatsApp message sent", to=to, message_id=result.get("messages", [{}])[0].get("id"))
                
                return result
        except httpx.HTTPError as e:
            logger.error("Failed to send WhatsApp message", error=str(e))
            raise
    
    async def send_template(
        self,
        to: str,
        template_name: str,
        language: str = "en_US",
        components: list = None
    ) -> Dict[str, Any]:
        """
        Send a pre-approved template message.
        
        Args:
            to: Recipient phone number
            template_name: Name of the approved template
            language: Template language code
            components: Template components with parameters
            
        Returns:
            Response from WhatsApp API
        """
        url = f"{self.api_url}/{self.business_id}/messages"
        
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
                "language": {"code": language},
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to send WhatsApp template", error=str(e))
            raise
    
    def parse_webhook(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse incoming webhook data from WhatsApp.
        
        Args:
            data: Webhook payload
            
        Returns:
            Parsed message data
        """
        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return None
            
            message = messages[0]
            
            return {
                "message_id": message.get("id"),
                "from": message.get("from"),
                "timestamp": message.get("timestamp"),
                "type": message.get("type"),
                "text": message.get("text", {}).get("body") if message.get("type") == "text" else None,
                "contact": value.get("contacts", [{}])[0],
            }
        except (KeyError, IndexError) as e:
            logger.error("Failed to parse WhatsApp webhook", error=str(e))
            return None
    
    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            True if successful
        """
        url = f"{self.api_url}/{self.business_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error("Failed to mark message as read", error=str(e))
            return False
