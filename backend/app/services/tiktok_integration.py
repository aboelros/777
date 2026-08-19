"""
TikTok Integration Service
Handles TikTok Business Messages integration for customer support.
"""

import hashlib
import hmac
import time
import json
import urllib.parse
from typing import Dict, Any, Optional, List
import structlog
import aiohttp
from datetime import datetime

logger = structlog.get_logger(__name__)

class TikTokIntegration:
    """
    TikTok Shop Customer Service API Integration.
    """
    
    def __init__(self, app_key: str, app_secret: str, shop_id: str, access_token: str):
        self.app_key = app_key
        self.app_secret = app_secret
        self.shop_id = shop_id
        self.access_token = access_token
        self.base_url = "https://open-api.tiktokglobalshop.com"
        
    def _generate_sign(self, path: str, query_params: Dict[str, str], body: str = "") -> str:
        # Sort query parameter keys alphabetically
        sorted_keys = sorted(query_params.keys())
        param_string = "".join([f"{k}{query_params[k]}" for k in sorted_keys])
        
        # Construct the base string
        message = f"{path}{param_string}{body}"
        
        # Wrap with app_secret
        final_message = f"{self.app_secret}{message}{self.app_secret}"
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.app_secret.encode('utf-8'),
            final_message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
        
    def _build_url(self, path: str, additional_params: Dict[str, str] = None, body: str = "") -> str:
        params = {
            "app_key": self.app_key,
            "timestamp": str(int(time.time())),
            "shop_cipher": self.shop_id # often shop_cipher is used or shop_id
        }
        if additional_params:
            params.update(additional_params)
            
        sign = self._generate_sign(path, params, body)
        params["sign"] = sign
        
        query_string = urllib.parse.urlencode(params)
        return f"{self.base_url}{path}?{query_string}"
        
    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json"
        }
        if self.access_token:
            headers["x-tts-access-token"] = self.access_token
        return headers

    async def send_message(
        self,
        conversation_id: str,
        message_text: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message via TikTok Shop API."""
        path = f"/customer_service/202309/conversations/{conversation_id}/messages"
        
        # TikTok Shop Message format
        payload = {
            "type": "TEXT",
            "content": json.dumps({"text": message_text})
        }
        
        if media_url:
            payload["type"] = "IMAGE"
            payload["content"] = json.dumps({"image_url": media_url})
            
        body = json.dumps(payload, separators=(',', ':'))
        url = self._build_url(path, body=body)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=body, headers=self._get_headers()) as response:
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
        path = "/customer_service/202309/conversations"
        params = {"page_size": str(limit)}
        if cursor:
            params["page_token"] = cursor
            
        url = self._build_url(path, additional_params=params)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        return await response.json()
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
        path = f"/customer_service/202309/conversations/{conversation_id}/messages"
        params = {"page_size": str(limit)}
        url = self._build_url(path, additional_params=params)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("data", {}).get("messages", [])
                    else:
                        logger.error("Failed to get TikTok messages", status=response.status)
                        return []
        except Exception as e:
            logger.error("TikTok get messages failed", error=str(e))
            return []

    async def send_product_card(self, conversation_id: str, product_id: str, product_name: str, product_price: float, product_image_url: str, product_url: str) -> Dict[str, Any]:
        """Send a product card."""
        path = f"/customer_service/202309/conversations/{conversation_id}/messages"
        payload = {
            "type": "PRODUCT_CARD",
            "content": json.dumps({
                "product_id": product_id,
                "product_name": product_name,
                "price": str(product_price),
                "image_url": product_image_url,
            })
        }
        body = json.dumps(payload, separators=(',', ':'))
        url = self._build_url(path, body=body)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=body, headers=self._get_headers()) as response:
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

    async def send_order_status(self, conversation_id: str, order_number: str, status: str, tracking_url: Optional[str] = None):
        """Send order status update."""
        message_text = f"Order #{order_number} Update: {status.upper()}"
        if tracking_url:
            message_text += f"\\nTracking: {tracking_url}"
        await self.send_message(conversation_id, message_text)

    async def mark_as_read(self, conversation_id: str, message_id: str) -> bool:
        """Mark as read via Shop API."""
        path = f"/customer_service/202309/conversations/{conversation_id}/messages/read"
        payload = {"message_id": message_id}
        body = json.dumps(payload, separators=(',', ':'))
        url = self._build_url(path, body=body)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=body, headers=self._get_headers()) as response:
                    return response.status == 200
        except Exception:
            return False

    async def verify_connection(self) -> bool:
        """Verify TikTok Shop API connection."""
        path = "/authorization/202309/shops"
        url = self._build_url(path)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self._get_headers()) as response:
                    return response.status == 200
        except Exception:
            return False

    async def setup_webhook(self, webhook_url: str, events: List[str] = None) -> Dict[str, Any]:
        """Setup webhook for receiving TikTok Shop messages."""
        logger.info("TikTok Shop webhooks should be configured in the Partner Center console.")
        return {"status": "success", "message": "Configure via Partner Center"}

def get_tiktok_client(config: Dict[str, Any]) -> TikTokIntegration:
    """Factory function to create TikTok Shop client."""
    app_key = config.get("api_key") or config.get("app_key")
    app_secret = config.get("api_secret") or config.get("app_secret")
    shop_id = config.get("shop_id")
    access_token = config.get("access_token")
    
    if not app_key or not app_secret or not shop_id:
        raise ValueError("TikTok App Key, App Secret, and Shop ID are required")
        
    return TikTokIntegration(
        app_key=app_key, 
        app_secret=app_secret, 
        shop_id=shop_id, 
        access_token=access_token or ""
    )
