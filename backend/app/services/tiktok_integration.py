"""
TikTok Integration Service
Handles TikTok Business Messages integration for customer support.
"""

from typing import Dict, Any, Optional, List
import structlog
import aiohttp
from datetime import datetime

logger = structlog.get_logger(__name__)


class TikTokIntegration:
    """
    TikTok Business Messages integration for customer support.
    
    Features:
    - Receive messages from TikTok direct messages
    - Send automated responses
    - Track customer conversations
    - Handle product inquiries from TikTok Shop
    """
    
    def __init__(self, access_token: str, business_id: str):
        self.access_token = access_token
        self.business_id = business_id
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        self.headers = {
            "Access-Token": access_token,
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        conversation_id: str,
        message_text: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a message via TikTok Business Messages.
        
        Args:
            conversation_id: TikTok conversation ID
            message_text: Message content
            media_url: Optional image/video URL
            
        Returns:
            TikTok API response
        """
        url = f"{self.base_url}/message/send/"
        
        payload = {
            "business_id": self.business_id,
            "conversation_id": conversation_id,
            "message": {
                "text": message_text
            }
        }
        
        if media_url:
            payload["message"]["media"] = {"url": media_url}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("TikTok message sent", conversation_id=conversation_id)
                        return result
                    else:
                        error = await response.text()
                        logger.error("Failed to send TikTok message", error=error, status=response.status)
                        raise Exception(f"TikTok API error: {error}")
        except Exception as e:
            logger.error("TikTok send message failed", error=str(e))
            raise
    
    async def get_conversations(
        self,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get conversations from TikTok Business Messages.
        
        Args:
            limit: Number of conversations to retrieve
            cursor: Pagination cursor
            
        Returns:
            List of conversations with metadata
        """
        url = f"{self.base_url}/conversation/list/"
        
        params = {
            "business_id": self.business_id,
            "limit": limit
        }
        
        if cursor:
            params["cursor"] = cursor
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        conversations = await response.json()
                        return conversations
                    else:
                        logger.error("Failed to get TikTok conversations", status=response.status)
                        return {"data": [], "has_more": False}
        except Exception as e:
            logger.error("TikTok get conversations failed", error=str(e))
            return {"data": [], "has_more": False}
    
    async def get_messages(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get messages from a TikTok conversation.
        
        Args:
            conversation_id: TikTok conversation ID
            limit: Number of messages to retrieve
            
        Returns:
            List of messages
        """
        url = f"{self.base_url}/message/list/"
        
        params = {
            "business_id": self.business_id,
            "conversation_id": conversation_id,
            "limit": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("messages", [])
                    else:
                        logger.error("Failed to get TikTok messages", status=response.status)
                        return []
        except Exception as e:
            logger.error("TikTok get messages failed", error=str(e))
            return []
    
    async def send_product_card(
        self,
        conversation_id: str,
        product_id: str,
        product_name: str,
        product_price: float,
        product_image_url: str,
        product_url: str
    ) -> Dict[str, Any]:
        """
        Send a product card (TikTok Shop integration).
        
        Args:
            conversation_id: TikTok conversation ID
            product_id: Product identifier
            product_name: Product name
            product_price: Product price
            product_image_url: Product image URL
            product_url: Product page URL
            
        Returns:
            TikTok API response
        """
        url = f"{self.base_url}/message/send/"
        
        payload = {
            "business_id": self.business_id,
            "conversation_id": conversation_id,
            "message": {
                "card": {
                    "type": "product",
                    "product_id": product_id,
                    "title": product_name,
                    "price": product_price,
                    "image_url": product_image_url,
                    "action_url": product_url
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("TikTok product card sent", product_id=product_id)
                        return result
                    else:
                        error = await response.text()
                        logger.error("Failed to send TikTok product card", error=error)
                        raise Exception(f"TikTok API error: {error}")
        except Exception as e:
            logger.error("TikTok send product card failed", error=str(e))
            raise
    
    async def send_order_status(
        self,
        conversation_id: str,
        order_number: str,
        status: str,
        tracking_url: Optional[str] = None
    ):
        """Send order status update to TikTok conversation."""
        
        message_text = f"""📦 Order Update #{order_number}

Status: {status.upper()}
"""
        
        if tracking_url:
            message_text += f"\n🚚 Track your order: {tracking_url}"
        
        if status == "shipped":
            message_text += "\n\nYour order is on its way! 🎉"
        elif status == "delivered":
            message_text += "\n\nYour order has been delivered! We hope you love it! ❤️"
        
        await self.send_message(conversation_id, message_text)
    
    async def mark_as_read(
        self,
        conversation_id: str,
        message_id: str
    ) -> bool:
        """Mark a message as read."""
        url = f"{self.base_url}/message/mark_read/"
        
        payload = {
            "business_id": self.business_id,
            "conversation_id": conversation_id,
            "message_id": message_id
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    return response.status == 200
        except Exception as e:
            logger.error("TikTok mark as read failed", error=str(e))
            return False
    
    async def verify_connection(self) -> bool:
        """Verify TikTok Business API connection."""
        url = f"{self.base_url}/business/get/"
        
        params = {"business_id": self.business_id}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        business_info = await response.json()
                        logger.info("TikTok connection verified", business_id=self.business_id)
                        return True
                    else:
                        logger.error("TikTok connection failed", status=response.status)
                        return False
        except Exception as e:
            logger.error("TikTok verification failed", error=str(e))
            return False
    
    async def setup_webhook(
        self,
        webhook_url: str,
        events: List[str] = None
    ) -> Dict[str, Any]:
        """
        Setup webhook for receiving TikTok messages.
        
        Args:
            webhook_url: Your webhook URL
            events: List of events to subscribe to
            
        Returns:
            Webhook configuration
        """
        if events is None:
            events = ["message.received", "message.read", "conversation.opened"]
        
        url = f"{self.base_url}/webhook/update/"
        
        payload = {
            "business_id": self.business_id,
            "webhook_url": webhook_url,
            "events": events
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info("TikTok webhook configured", webhook_url=webhook_url)
                        return result
                    else:
                        error = await response.text()
                        logger.error("Failed to setup TikTok webhook", error=error)
                        raise Exception(f"TikTok webhook error: {error}")
        except Exception as e:
            logger.error("TikTok webhook setup failed", error=str(e))
            raise


def get_tiktok_client(config: Dict[str, Any]) -> TikTokIntegration:
    """Factory function to create TikTok client."""
    access_token = config.get("access_token")
    business_id = config.get("business_id")
    
    if not access_token or not business_id:
        raise ValueError("TikTok access_token and business_id are required")
    
    return TikTokIntegration(access_token=access_token, business_id=business_id)
