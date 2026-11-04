"""
Session management helpers for WhatsApp Baileys gateway integration.
"""

from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.domains.integrations.models import Integration, IntegrationStatus
from app.services.integrations.whatsapp_baileys import WhatsAppBaileysService

logger = structlog.get_logger(__name__)


def _sanitize_session_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure no credentials or raw secrets leak in session status responses."""
    sanitized = dict(data)
    for sensitive_key in ("api_key", "access_token", "token", "secret", "password"):
        sanitized.pop(sensitive_key, None)
    if "metadata" in sanitized and isinstance(sanitized["metadata"], dict):
        clean_meta = dict(sanitized["metadata"])
        for sensitive_key in ("api_key", "access_token", "token", "secret"):
            clean_meta.pop(sensitive_key, None)
        sanitized["metadata"] = clean_meta
    return sanitized


def resolve_session_id(integration: Integration) -> str:
    """Ensure a deterministic per-tenant unique session ID."""
    extra = integration.extra_data or {}
    config = integration.config or {}
    sid = extra.get("session_id") or config.get("session_id")
    if not sid or sid == "default":
        return str(integration.id)
    return sid


async def get_whatsapp_integration(
    db: AsyncSession,
    project_id: UUID,
    integration_id: UUID,
) -> Integration:
    """Fetch and validate WhatsApp integration ownership."""
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
    )
    integration = result.scalar_one_or_none()
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )
    if integration.provider != "whatsapp":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration is not a WhatsApp provider",
        )
    return integration


async def ensure_linked_device_session(
    db: AsyncSession,
    integration: Integration,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Start or retrieve session QR code for Baileys gateway."""
    extra = integration.extra_data or {}
    config = integration.config or {}
    session_id = resolve_session_id(integration)
    base_url = config.get("base_url")
    api_key = config.get("api_key")

    service = WhatsAppBaileysService(
        session_id=session_id,
        base_url=base_url,
        api_key=api_key
    )

    try:
        session_meta = {
            "project_id": str(integration.project_id),
            "integration_id": str(integration.id),
            **(metadata or {})
        }
        res = await service.start_session(project_id=str(integration.project_id), metadata=session_meta)
        
        qr_code = res.get("qr_code") or res.get("qr")
        new_extra = {
            **extra,
            "session_id": session_id,
            "provider": "baileys",
            "qr_url": qr_code,
            "last_status": res.get("status", "pending")
        }
        integration.extra_data = new_extra
        integration.status = IntegrationStatus.PENDING
        await db.commit()

        return _sanitize_session_response({
            "status": "success",
            "session_id": session_id,
            "qr_code": qr_code,
            "qr_url": qr_code,
            "pairing_code": res.get("pairing_code"),
            "integration_status": "pending",
            "message": "Scan QR code to connect"
        })
    except Exception as e:
        logger.error("Failed ensuring WhatsApp Baileys session", error=str(e), integration_id=str(integration.id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize WhatsApp gateway session"
        )
    finally:
        await service.aclose()


async def sync_linked_device_session(
    db: AsyncSession,
    integration: Integration,
    session_id: str,
) -> Dict[str, Any]:
    """Query gateway status and synchronize integration model state."""
    config = integration.config or {}
    base_url = config.get("base_url")
    api_key = config.get("api_key")

    service = WhatsAppBaileysService(
        session_id=session_id,
        base_url=base_url,
        api_key=api_key
    )

    try:
        status_res = await service.get_status()
        raw_status = status_res.get("status")

        extra = integration.extra_data or {}
        if raw_status == "connected":
            integration.status = IntegrationStatus.CONNECTED
            extra["qr_url"] = None
        elif raw_status in ("qr_ready", "connecting"):
            integration.status = IntegrationStatus.PENDING
            if status_res.get("qr_code"):
                extra["qr_url"] = status_res.get("qr_code")
        elif raw_status in ("disconnected", "not_found"):
            integration.status = IntegrationStatus.DISCONNECTED

        extra["last_status"] = raw_status
        integration.extra_data = extra
        await db.commit()

        return _sanitize_session_response({
            "session_id": session_id,
            "status": raw_status,
            "integration_status": integration.status.value,
            "qr_code": status_res.get("qr_code") or extra.get("qr_url"),
            "pairing_code": status_res.get("pairing_code"),
            "connected": raw_status == "connected"
        })
    except Exception as e:
        logger.error("Failed syncing Baileys session", error=str(e), session_id=session_id)
        return {
            "session_id": session_id,
            "status": "error",
            "integration_status": integration.status.value,
            "message": "Unable to contact gateway"
        }
    finally:
        await service.aclose()


async def close_linked_device_session(
    db: AsyncSession,
    integration: Integration,
    session_id: str,
) -> Dict[str, Any]:
    """Terminate Baileys session and update integration status."""
    config = integration.config or {}
    base_url = config.get("base_url")
    api_key = config.get("api_key")

    service = WhatsAppBaileysService(
        session_id=session_id,
        base_url=base_url,
        api_key=api_key
    )

    try:
        await service.logout_session()
    except Exception as e:
        logger.warning("Gateway logout reported error", error=str(e), session_id=session_id)
    finally:
        await service.aclose()

    integration.status = IntegrationStatus.DISCONNECTED
    extra = integration.extra_data or {}
    extra["qr_url"] = None
    extra["last_status"] = "disconnected"
    integration.extra_data = extra
    await db.commit()

    return {
        "status": "success",
        "session_id": session_id,
        "integration_status": "disconnected",
        "message": "Session disconnected successfully"
    }
