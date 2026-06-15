"""
Go WhatsApp Service Adapter
For aldinokemal/go-whatsapp-web-multidevice
"""

import httpx
import structlog
from typing import Dict, Any, Optional, List

logger = structlog.get_logger(__name__)

class GoWhatsAppService:
    """Service for Go WhatsApp integration."""

    def __init__(self, base_url: str, api_key: str = None):
        """
        Initialize Go WhatsApp service.
        
        Args:
            base_url: Base URL of the Go WhatsApp instance
            api_key: Basic Auth password (username is usually 'admin' or ignored if not set)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
        # Configure client
        headers = {
            "Content-Type": "application/json"
        }
        
        # Basic Auth if api_key is provided
        auth = None
        if self.api_key:
            # Assuming 'admin' as default username if only key is provided
            # or user might provide "username:password" format?
            # Let's assume it's just the password for now, or we might need a username field.
            # For now, we'll use a custom header or just Basic Auth with "admin"
            auth = ("admin", self.api_key)
            
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=headers,
            auth=auth
        )

    async def start_session(self, session_id: str) -> Dict[str, Any]:
        """
        Start a new WhatsApp session.
        For Go WhatsApp, this usually means calling /app/login.
        """
        url = f"{self.base_url}/app/login"
        
        try:
            # Go WhatsApp might not need a payload for login, or maybe it does.
            # Usually it returns a QR code in the response.
            response = await self.client.post(url)
            response.raise_for_status()
            data = response.json()
            
            # Expected response: { "code": 200, "message": "...", "results": { "qr_link": "...", "qr_duration": ... } }
            results = data.get("results", {})
            qr_code = results.get("qr_link") or results.get("qr_code")
            
            if qr_code:
                return {
                    "status": "success",
                    "qr_code": qr_code,
                    "message": "Scan QR code"
                }
            
            if data.get("message") == "Already logged in":
                 return {
                    "status": "connected",
                    "message": "Session is already connected"
                }
            
            return {"status": "pending", "message": "Initializing session..."}
            
        except Exception as e:
            logger.error("Failed to start Go WhatsApp session", error=str(e))
            raise e

    async def send_text_message(
        self,
        session_id: str, # Go WhatsApp might not use session_id in URL if it's single session per container
        to: str,
        text: str,
        quoting: Optional[Dict[str, Any]] = None,
        mentions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send a text message.
        """
        url = f"{self.base_url}/send/message"
        
        # Clean phone number
        number = to.split('@')[0]
        
        payload = {
            "phone": number,
            "message": text
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to send message via Go WhatsApp", error=str(e))
            raise e

    async def logout_session(self, session_id: str) -> Dict[str, Any]:
        """
        Logout session.
        """
        url = f"{self.base_url}/app/logout"
        try:
            response = await self.client.post(url)
            return response.json()
        except Exception as e:
            logger.warning("Failed to logout Go WhatsApp session", error=str(e))
            return {}

    async def close(self):
        await self.client.aclose()

    def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse incoming webhook.
        """
        try:
            # Need to determine structure. 
            # Assuming standard fields based on other gateways.
            # Will log payload first to debug.
            logger.info("Go WhatsApp Webhook Payload", payload=payload)
            
            # Example structure (guess):
            # { "from": "...", "message": "...", "timestamp": ... }
            
            from_number = payload.get("from", "")
            text = payload.get("message", "") or payload.get("body", "")
            timestamp = payload.get("timestamp", 0)
            
            # If structure is different, we'll need to adjust.
            # For now, return what we can find.
            
            return {
                "session_id": "default", # Go WhatsApp usually single session
                "from": from_number,
                "text": text,
                "from_me": payload.get("from_me", False),
                "timestamp": timestamp,
                "message_id": payload.get("id", ""),
                "raw_message": payload,
                "media_type": None,
                "media_data": None
            }
            
        except Exception as e:
             logger.error("Failed to parse Go WhatsApp webhook", error=str(e))
             raise e
