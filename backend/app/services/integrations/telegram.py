"""
Telegram Bot API integration service.
"""

from typing import Dict, Any, Optional
import structlog
import httpx
from app.core.config import settings

logger = structlog.get_logger(__name__)


class TelegramService:
    """Service for Telegram Bot API integration."""
    
    def __init__(self, bot_token: str):
        """Initialize Telegram service with bot token."""
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a text message.
        
        Args:
            chat_id: Unique identifier for the target chat
            text: Message text
            parse_mode: Message formatting (HTML, Markdown, MarkdownV2)
            reply_markup: Inline keyboard or custom keyboard
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.api_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get("content-type") == "application/json" else response.text
                    logger.error(
                        "Telegram API error",
                        status_code=response.status_code,
                        error=error_data,
                        url=url,
                        chat_id=chat_id
                    )
                    response.raise_for_status()
                
                result = response.json()
                logger.info("Telegram message sent", chat_id=chat_id)
                
                return result
        except httpx.HTTPError as e:
            logger.error(
                "Failed to send Telegram message",
                error=str(e),
                chat_id=chat_id,
                url=url
            )
            raise
        except Exception as e:
            logger.error(
                "Unexpected error sending Telegram message",
                error=str(e),
                error_type=type(e).__name__,
                chat_id=chat_id
            )
            raise
    
    async def send_photo(
        self,
        chat_id: str,
        photo: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a photo.
        
        Args:
            chat_id: Target chat ID
            photo: Photo URL or file_id
            caption: Photo caption
            
        Returns:
            Response from Telegram API
        """
        url = f"{self.api_url}/sendPhoto"
        
        payload = {
            "chat_id": chat_id,
            "photo": photo,
        }
        
        if caption:
            payload["caption"] = caption
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to send Telegram photo", error=str(e))
            raise
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """
        Set webhook URL for receiving updates.
        
        Args:
            webhook_url: HTTPS URL to send updates to
            
        Returns:
            True if successful
        """
        url = f"{self.api_url}/setWebhook"
        
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                logger.info("Telegram webhook set", url=webhook_url, result=result)
                
                return result.get("ok", False)
        except httpx.HTTPError as e:
            logger.error("Failed to set Telegram webhook", error=str(e))
            return False
    
    def parse_webhook(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook update from Telegram.
        
        Args:
            data: Webhook payload (Update object)
            
        Returns:
            Parsed message data
        """
        try:
            message = data.get("message")
            if not message:
                # Could be callback_query or other update type
                return None
            
            return {
                "message_id": message.get("message_id"),
                "chat_id": message.get("chat", {}).get("id"),
                "from_user": {
                    "id": message.get("from", {}).get("id"),
                    "username": message.get("from", {}).get("username"),
                    "first_name": message.get("from", {}).get("first_name"),
                    "last_name": message.get("from", {}).get("last_name"),
                },
                "date": message.get("date"),
                "text": message.get("text"),
                "type": "text" if message.get("text") else "other",
            }
        except (KeyError, IndexError) as e:
            logger.error("Failed to parse Telegram webhook", error=str(e))
            return None
    
    async def get_me(self) -> Dict[str, Any]:
        """
        Get bot information.
        
        Returns:
            Bot user object
        """
        url = f"{self.api_url}/getMe"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get bot info", error=str(e))
            raise
    
    def create_inline_keyboard(self, buttons: list) -> Dict[str, Any]:
        """
        Create inline keyboard markup.
        
        Args:
            buttons: List of button rows, each containing button dicts
            
        Returns:
            Inline keyboard markup
        """
        return {
            "inline_keyboard": buttons
        }


class TelegramClient:
    """Client wrapper for Telegram integration with AIOrchestrator."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Telegram client with config."""
        self.config = config
        self.bot_token = config.get("api_key")
        if not self.bot_token:
            raise ValueError("Telegram bot token (api_key) is required")
        
        self.service = TelegramService(self.bot_token)
    
    async def send_message(self, customer_id: str, message: str) -> Dict[str, Any]:
        """
        Send message to customer via Telegram.
        
        Args:
            customer_id: Customer UUID (we need to get their telegram_id)
            message: Message text to send
            
        Returns:
            Response from Telegram API
        """
        # For now, assume customer_id is the telegram chat_id
        # In a real implementation, we'd look up the customer's telegram_id
        try:
            result = await self.service.send_message(
                chat_id=customer_id,
                text=message
            )
            
            logger.info(
                "Message sent via Telegram",
                customer_id=customer_id,
                message_id=result.get("result", {}).get("message_id")
            )
            
            return {
                "status": "sent",
                "id": result.get("result", {}).get("message_id"),
                "platform": "telegram"
            }
            
        except Exception as e:
            logger.error("Failed to send Telegram message", error=str(e))
            raise
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information."""
        return await self.service.get_me()
    
    async def set_webhook(self, webhook_url: str) -> bool:
        """Set webhook URL."""
        return await self.service.set_webhook(webhook_url)
