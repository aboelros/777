"""
WhatsApp Business API integration service.
Uses official Meta WhatsApp Cloud API.
"""

from typing import Dict, Any, Optional
import structlog
from app.services.whatsapp_business_api import WhatsAppBusinessAPI, WhatsAppBusinessAPIError
from app.core.config import settings

logger = structlog.get_logger(__name__)


class WhatsAppBusinessService:
    """Service for WhatsApp integration via official Business API."""
    
    def __init__(self):
        """Initialize WhatsApp Business API service."""
        if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
            raise ValueError(
                "WhatsApp Business API credentials not configured. "
                "Set WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN environment variables."
            )
        
        self.client = WhatsAppBusinessAPI(
            phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
            access_token=settings.WHATSAPP_ACCESS_TOKEN
        )
    
    async def send_message(
        self,
        to: str,
        message: str,
        *,
        preview_url: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp.
        
        Args:
            to: Recipient phone number (international format without +)
            message: Message content
            preview_url: Whether to show URL preview
            
        Returns:
            Response with message ID
        """
        try:
            response = await self.client.send_text_message(
                to=to,
                message=message,
                preview_url=preview_url
            )
            
            logger.info(
                "WhatsApp message sent via Business API",
                to=to,
                message_id=response.get("messages", [{}])[0].get("id")
            )
            
            return {
                "success": True,
                "message_id": response.get("messages", [{}])[0].get("id"),
                "status": "sent"
            }
        except WhatsAppBusinessAPIError as e:
            logger.error("Failed to send WhatsApp message", error=str(e))
            raise
    
    async def send_template(
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
            language_code: Template language
            components: Template components
            
        Returns:
            Response with message ID
        """
        try:
            response = await self.client.send_template_message(
                to=to,
                template_name=template_name,
                language_code=language_code,
                components=components
            )
            
            logger.info(
                "WhatsApp template sent",
                to=to,
                template=template_name,
                message_id=response.get("messages", [{}])[0].get("id")
            )
            
            return {
                "success": True,
                "message_id": response.get("messages", [{}])[0].get("id"),
                "status": "sent"
            }
        except WhatsAppBusinessAPIError as e:
            logger.error("Failed to send WhatsApp template", error=str(e))
            raise
    
    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.
        
        Args:
            message_id: WhatsApp message ID
            
        Returns:
            True if successful
        """
        try:
            await self.client.mark_as_read(message_id)
            logger.info("Message marked as read", message_id=message_id)
            return True
        except Exception as e:
            logger.error("Failed to mark message as read", error=str(e))
            return False
    
    def parse_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook data from WhatsApp Business API.
        
        Args:
            data: Webhook payload from Meta
            
        Returns:
            Parsed message data or None
        """
        try:
            # WhatsApp Business API webhook structure
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            messages = value.get("messages", [])
            if not messages:
                logger.warning("No messages in webhook")
                return None
            
            message = messages[0]
            
            # Extract message details
            parsed = {
                "message_id": message.get("id"),
                "from": message.get("from"),
                "timestamp": message.get("timestamp"),
                "type": message.get("type", "text"),
                "text": None,
                "contact": {
                    "phone": message.get("from"),
                    "name": value.get("contacts", [{}])[0].get("profile", {}).get("name", "Unknown")
                }
            }
            
            # Extract text content based on type
            if message.get("type") == "text":
                parsed["text"] = message.get("text", {}).get("body")
            elif message.get("type") == "button":
                parsed["text"] = message.get("button", {}).get("text")
            elif message.get("type") == "interactive":
                interactive = message.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    parsed["text"] = interactive.get("button_reply", {}).get("title")
                elif interactive.get("type") == "list_reply":
                    parsed["text"] = interactive.get("list_reply", {}).get("title")
            
            if not parsed["text"]:
                logger.warning("Could not extract text from message", message_type=message.get("type"))
                return None
            
            return parsed
            
        except (KeyError, IndexError, AttributeError) as e:
            logger.error("Failed to parse WhatsApp webhook", error=str(e))
            return None
