"""
HTTP client for WhatsApp Baileys Gateway microservice.
"""

from typing import Dict, Any, Optional
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class WhatsAppGatewayError(Exception):
    """Base exception for WhatsApp Gateway client errors."""
    pass


class WhatsAppGatewayClient:
    """Client for communicating with the self-hosted WhatsApp Baileys gateway."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        raw_url = base_url or getattr(settings, "WA_GATEWAY_BASE_URL", None) or "http://localhost:3000"
        self.base_url = raw_url.rstrip("/")
        self.api_key = api_key or getattr(settings, "WA_GATEWAY_API_KEY", None)
        self.timeout = timeout

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            headers=headers
        )

    def _sanitize_message(self, message: str) -> str:
        """Strip internal tokens, secrets, and raw keys from error descriptions."""
        if not message:
            return "Unknown error"
        sanitized = message
        if self.api_key and len(self.api_key) > 4:
            sanitized = sanitized.replace(self.api_key, "[REDACTED]")
        for term in ("Bearer ", "api_key=", "password="):
            if term in sanitized:
                sanitized = "[REDACTED] Error during gateway communication"
        return sanitized

    async def aclose(self) -> None:
        """Close underlying HTTP client connection pool."""
        await self._client.aclose()

    async def __aenter__(self) -> "WhatsAppGatewayClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()

    async def get_health(self) -> Dict[str, Any]:
        """Check gateway health status."""
        try:
            resp = await self._client.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning("Gateway health check failed", error=self._sanitize_message(str(e)))
            return {"status": "unavailable", "error": self._sanitize_message(str(e))}

    async def create_session(
        self,
        session_id: str,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Request new or re-opened session with QR generation."""
        payload: Dict[str, Any] = {
            "integration_id": session_id,
            "project_id": project_id,
            "metadata": metadata or {}
        }
        try:
            resp = await self._client.post(f"{self.base_url}/sessions", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            msg = self._sanitize_message(e.response.text)
            logger.error("Failed to create session on gateway", status=e.response.status_code, error=msg)
            raise WhatsAppGatewayError(f"Gateway returned {e.response.status_code}: {msg}") from e
        except Exception as e:
            msg = self._sanitize_message(str(e))
            logger.error("Gateway connection failure", error=msg)
            raise WhatsAppGatewayError(f"Could not connect to WhatsApp Gateway: {msg}") from e

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Fetch current session pairing/connection status."""
        try:
            resp = await self._client.get(f"{self.base_url}/sessions/{session_id}")
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"status": "not_found", "message": "Session not registered"}
            msg = self._sanitize_message(e.response.text)
            raise WhatsAppGatewayError(f"Failed to query session: {msg}") from e
        except Exception as e:
            msg = self._sanitize_message(str(e))
            raise WhatsAppGatewayError(f"Gateway error: {msg}") from e

    async def send_message(
        self,
        session_id: str,
        to: str,
        message: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send message through active session."""
        payload = {
            "to": to,
            "message": message,
            "message_type": message_type,
            "extra": extra or {}
        }
        try:
            resp = await self._client.post(f"{self.base_url}/sessions/{session_id}/messages", json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            msg = self._sanitize_message(e.response.text)
            logger.error("Gateway failed to send message", session_id=session_id, error=msg)
            raise WhatsAppGatewayError(f"Failed sending message: {msg}") from e
        except Exception as e:
            msg = self._sanitize_message(str(e))
            raise WhatsAppGatewayError(f"Gateway send error: {msg}") from e

    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Terminate and clean up session on gateway."""
        try:
            resp = await self._client.post(f"{self.base_url}/sessions/{session_id}/close")
            if resp.status_code in (200, 201, 204):
                return resp.json() if resp.content else {"status": "closed"}
            return {"status": "closed"}
        except Exception as e:
            logger.warning("Error during session logout", session_id=session_id, error=self._sanitize_message(str(e)))
            return {"status": "closed", "note": self._sanitize_message(str(e))}
