"""
HTTP client for WhatsApp Baileys Gateway microservice.
"""

import os
import time
from typing import Dict, Any, Optional, Tuple
import httpx
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

# In-memory TTL cache to prevent rapid polling from hammering the gateway
_STATUS_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 4.0


def resolve_gateway_url(configured_url: Optional[str] = None) -> str:
    """Resolve gateway URL prioritizing remote endpoints over localhost in cloud deployments."""
    env_url = (
        getattr(settings, "WA_GATEWAY_BASE_URL", None)
        or getattr(settings, "WHATSAPP_BAILEYS_URL", None)
        or getattr(settings, "WA_GATEWAY_URL", None)
    )
    is_cloud = bool(
        os.getenv("RENDER")
        or os.getenv("RENDER_SERVICE_ID")
        or getattr(settings, "ENVIRONMENT", "").lower() in ("production", "staging")
    )
    if is_cloud:
        if env_url and "localhost" not in env_url and "127.0.0.1" not in env_url:
            return env_url.rstrip("/")
        if configured_url and "localhost" not in configured_url and "127.0.0.1" not in configured_url:
            return configured_url.rstrip("/")
        return "https://ai-sales-bot-whatsapp-vdr6.onrender.com"
    return (configured_url or env_url or "http://localhost:3000").rstrip("/")


def resolve_gateway_api_key(configured_key: Optional[str] = None) -> Optional[str]:
    """Resolve gateway API key falling back to environment settings."""
    return (
        configured_key
        or getattr(settings, "WA_GATEWAY_API_KEY", None)
        or getattr(settings, "WHATSAPP_BAILEYS_API_KEY", None)
        or None
    )


class WhatsAppGatewayError(Exception):
    """Base exception for WhatsApp Gateway client errors."""
    pass


INTERNAL_GATEWAY_SECRET = os.getenv("INTERNAL_GATEWAY_SECRET", "automio_gateway_internal_secret_2026")


class WhatsAppGatewayClient:
    """Client for communicating with the self-hosted WhatsApp Baileys gateway."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = resolve_gateway_url(base_url)
        self.api_key = resolve_gateway_api_key(api_key) or INTERNAL_GATEWAY_SECRET
        self.timeout = timeout

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AutomioBackend/1.0",
            "X-Internal-Secret": INTERNAL_GATEWAY_SECRET,
            "Authorization": f"Bearer {self.api_key}"
        }

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
            if resp.status_code == 429:
                logger.warning("Gateway rate-limit on create_session, cool down", session_id=session_id)
                if session_id in _STATUS_CACHE:
                    return _STATUS_CACHE[session_id][1]
                return {"status": "loading", "message": "Rate limit cool-down"}
            resp.raise_for_status()
            data = resp.json()
            _STATUS_CACHE[session_id] = (time.time(), data)
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return {"status": "loading", "message": "Rate limit cool-down"}
            msg = self._sanitize_message(e.response.text)
            logger.error("Failed to create session on gateway", status=e.response.status_code, error=msg)
            raise WhatsAppGatewayError(f"Gateway returned {e.response.status_code}: {msg}") from e
        except Exception as e:
            msg = self._sanitize_message(str(e))
            logger.error("Gateway connection failure", error=msg)
            raise WhatsAppGatewayError(f"Could not connect to WhatsApp Gateway: {msg}") from e

    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Fetch current session pairing/connection status with TTL caching and 429 backoff."""
        now = time.time()
        if session_id in _STATUS_CACHE:
            cached_time, cached_val = _STATUS_CACHE[session_id]
            if now - cached_time < CACHE_TTL_SECONDS:
                return cached_val

        try:
            resp = await self._client.get(f"{self.base_url}/sessions/{session_id}")
            if resp.status_code == 429:
                logger.warning("Gateway rate-limit encountered, cooling down", session_id=session_id)
                if session_id in _STATUS_CACHE:
                    return _STATUS_CACHE[session_id][1]
                return {"status": "loading", "message": "Rate limit cool-down"}
            resp.raise_for_status()
            data = resp.json()
            _STATUS_CACHE[session_id] = (time.time(), data)
            return data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"status": "not_found", "message": "Session not registered"}
            if e.response.status_code == 429:
                if session_id in _STATUS_CACHE:
                    return _STATUS_CACHE[session_id][1]
                return {"status": "loading", "message": "Rate limit cool-down"}
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
        _STATUS_CACHE.pop(session_id, None)
        try:
            resp = await self._client.post(f"{self.base_url}/sessions/{session_id}/close", json={})
            if resp.status_code in (200, 201, 204):
                return resp.json() if resp.content else {"status": "closed"}
            return {"status": "closed"}
        except Exception as e:
            logger.warning("Error during session logout", session_id=session_id, error=self._sanitize_message(str(e)))
            return {"status": "closed", "note": self._sanitize_message(str(e))}
