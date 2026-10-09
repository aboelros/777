import httpx
import structlog
from typing import Dict, Any, Optional, List

logger = structlog.get_logger(__name__)

class WAGatewayService:
    """Service for WA-Gateway (Node.js Baileys) integration."""

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=headers
        )

    async def start_session(self, session_id: str, project_id: str = None) -> Dict[str, Any]:
        """Start a new WhatsApp session via POST /sessions"""
        url = f"{self.base_url}/sessions"
        
        payload = {
            "integration_id": session_id
        }
        if project_id:
            payload["project_id"] = project_id
            
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # The node.js gateway returns status, qr, message
            qr_code = data.get("qr")
            if qr_code:
                return {
                    "status": "success",
                    "qr_code": qr_code,
                    "message": "Scan QR code"
                }
            
            if data.get("status") == "connected":
                 return {
                    "status": "connected",
                    "message": "Session is already connected"
                }
            
            return {"status": "pending", "message": "Initializing session..."}
            
        except httpx.HTTPStatusError as e:
            logger.error("WA-Gateway returned error", status_code=e.response.status_code, text=e.response.text)
            raise e
        except Exception as e:
            logger.error("Failed to start WA-Gateway session", error=str(e))
            raise e

    async def send_text_message(
        self,
        session_id: str,
        to: str,
        text: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send a message via POST /sessions/:sessionId/messages"""
        url = f"{self.base_url}/sessions/{session_id}/messages"
        
        number = to.split('@')[0]
        
        payload = {
            "to": number,
            "message": text,
            "message_type": message_type
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to send message via WA-Gateway", error=str(e))
            raise e

    async def logout_session(self, session_id: str) -> Dict[str, Any]:
        """Close session via POST /sessions/:sessionId/close"""
        url = f"{self.base_url}/sessions/{session_id}/close"
        try:
            response = await self.client.post(url)
            return response.json()
        except Exception as e:
            logger.warning("Failed to logout WA-Gateway session", error=str(e))
            return {}

    async def close(self):
        await self.client.aclose()

    def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Parse incoming webhook from WA-Gateway"""
        try:
            session_id = payload.get("session_id")
            msg = payload.get("message", {})
            metadata = payload.get("metadata", {})
            
            key = msg.get("key", {})
            from_number = key.get("remoteJid", "").split("@")[0]
            from_me = key.get("fromMe", False)
            message_id = key.get("id", "")
            
            msg_content = msg.get("message", {})
            text = msg_content.get("conversation") or msg_content.get("extendedTextMessage", {}).get("text", "")
            
            return {
                "session_id": session_id,
                "from": from_number,
                "text": text,
                "from_me": from_me,
                "timestamp": msg.get("messageTimestamp", 0),
                "message_id": message_id,
                "raw_message": payload,
                "project_id": metadata.get("project_id"),
                "media_type": None,
                "media_data": None
            }
        except Exception as e:
             logger.error("Failed to parse WA-Gateway webhook", error=str(e))
             raise e
