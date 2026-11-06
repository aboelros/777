"""Session management helpers for WhatsApp Baileys gateway integration."""
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
    """Ensure no credentials or raw secrets leak in session responses."""
    sanitized = dict(data)
    for k in ("api_key", "access_token", "token", "secret", "password"):
        sanitized.pop(k, None)
    if "metadata" in sanitized and isinstance(sanitized["metadata"], dict):
        clean_meta = dict(sanitized["metadata"])
        for k in ("api_key", "access_token", "token", "secret"):
            clean_meta.pop(k, None)
        sanitized["metadata"] = clean_meta
    return sanitized


def _format_status(status_val: Any) -> str:
    """Safely format status to lowercase string."""
    return str(getattr(status_val, "value", status_val or "disconnected")).lower()


def resolve_session_id(integration: Integration) -> str:
    """Ensure a deterministic per-tenant unique session ID."""
    extra = integration.extra_data or {}
    config = integration.config or {}
    sid = extra.get("session_id") or config.get("session_id")
    return str(integration.id) if (not sid or sid == "default") else str(sid)


async def get_whatsapp_integration(
    db: AsyncSession,
    project_id: UUID,
    integration_id: UUID,
) -> Integration:
    """Fetch WhatsApp integration, auto-resolving to active connected channel if caller ID is stale."""
    result = await db.execute(
        select(Integration).where(Integration.id == integration_id, Integration.project_id == project_id)
    )
    integration = result.scalar_one_or_none()

    # If requested integration is disconnected or not found, check if an active connected one exists
    is_conn = integration and _format_status(integration.status) == "connected"
    if not is_conn:
        conn_res = await db.execute(
            select(Integration)
            .where(
                Integration.project_id == project_id,
                Integration.provider == "whatsapp",
                Integration.status == IntegrationStatus.CONNECTED
            )
            .order_by(Integration.updated_at.desc().nullslast(), Integration.created_at.desc())
        )
        active_conn = conn_res.scalars().first()
        if active_conn:
            return active_conn

    if not integration:
        fb = await db.execute(
            select(Integration)
            .where(Integration.project_id == project_id, Integration.provider == "whatsapp")
            .order_by(Integration.created_at.desc())
        )
        integration = fb.scalars().first()

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")
    if integration.provider != "whatsapp":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integration is not a WhatsApp provider")
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
    service = WhatsAppBaileysService(
        session_id=session_id,
        base_url=config.get("base_url"),
        api_key=config.get("api_key")
    )
    try:
        session_meta = {
            "project_id": str(integration.project_id),
            "integration_id": str(integration.id),
            **(metadata or {})
        }
        res = await service.start_session(project_id=str(integration.project_id), metadata=session_meta)
        qr_code = res.get("qr_code") or res.get("qr")
        is_conn = res.get("status") == "connected" or bool(res.get("connected"))

        integration.extra_data = {
            **extra,
            "session_id": session_id,
            "provider": "baileys",
            "qr_url": None if is_conn else (qr_code or extra.get("qr_url")),
            "last_status": "connected" if is_conn else res.get("status", "pending")
        }
        integration.status = IntegrationStatus.CONNECTED if is_conn else IntegrationStatus.PENDING
        await db.commit()

        return _sanitize_session_response({
            "status": "connected" if is_conn else "success",
            "connected": is_conn,
            "session_id": session_id,
            "qr_code": None if is_conn else (qr_code or extra.get("qr_url")),
            "qr_url": None if is_conn else (qr_code or extra.get("qr_url")),
            "pairing_code": res.get("pairing_code"),
            "integration_status": "connected" if is_conn else "pending",
            "message": "WhatsApp connected successfully" if is_conn else "Scan QR code to connect"
        })
    except Exception as e:
        await db.rollback()
        logger.warning("WhatsApp session start pending gateway startup", error=str(e), integration_id=str(integration.id))
        return {
            "status": "loading",
            "session_id": session_id,
            "connected": False,
            "qr_code": extra.get("qr_url"),
            "qr_url": extra.get("qr_url"),
            "message": "Gateway starting up, generating QR code..."
        }
    finally:
        await service.aclose()


async def sync_linked_device_session(
    db: AsyncSession,
    integration: Integration,
    session_id: str,
) -> Dict[str, Any]:
    """Query gateway status and synchronize integration model state."""
    config = integration.config or {}
    service = WhatsAppBaileysService(
        session_id=session_id,
        base_url=config.get("base_url"),
        api_key=config.get("api_key")
    )
    try:
        status_res = await service.get_status()
        raw_status = status_res.get("status")
        is_conn = raw_status == "connected" or bool(status_res.get("connected"))

        extra = integration.extra_data or {}
        if is_conn:
            integration.status = IntegrationStatus.CONNECTED
            extra["qr_url"] = None
            extra["last_status"] = "connected"
            integration.extra_data = extra
            await db.commit()
        elif raw_status in ("qr_ready", "connecting"):
            integration.status = IntegrationStatus.PENDING
            if status_res.get("qr_code"):
                extra["qr_url"] = status_res.get("qr_code")
            extra["last_status"] = raw_status
            integration.extra_data = extra
            await db.commit()
        elif raw_status == "loading":
            return _sanitize_session_response({
                "session_id": session_id,
                "status": "loading",
                "connected": False,
                "integration_status": _format_status(integration.status),
                "qr_code": extra.get("qr_url"),
                "pairing_code": status_res.get("pairing_code"),
                "message": status_res.get("message", "Loading session status...")
            })
        elif raw_status in ("disconnected", "not_found"):
            integration.status = IntegrationStatus.DISCONNECTED
            extra["last_status"] = raw_status
            extra["qr_url"] = None
            integration.extra_data = extra
            await db.commit()

        return _sanitize_session_response({
            "session_id": session_id,
            "status": "connected" if is_conn else raw_status,
            "connected": is_conn,
            "integration_status": _format_status(integration.status),
            "qr_code": None if is_conn else (status_res.get("qr_code") or extra.get("qr_url")),
            "pairing_code": status_res.get("pairing_code"),
        })
    except Exception as e:
        await db.rollback()
        logger.error("Failed syncing Baileys session", error=str(e), session_id=session_id)
        return {
            "session_id": session_id,
            "status": "loading" if (integration.extra_data or {}).get("qr_url") else "error",
            "connected": _format_status(integration.status) == "connected",
            "integration_status": _format_status(integration.status),
            "qr_code": (integration.extra_data or {}).get("qr_url"),
            "message": "Syncing with gateway..."
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
    service = WhatsAppBaileysService(
        session_id=session_id,
        base_url=config.get("base_url"),
        api_key=config.get("api_key")
    )
    try:
        await service.logout_session()
    except Exception as e:
        logger.warning("Gateway logout reported error", error=str(e), session_id=session_id)
    finally:
        await service.aclose()

    try:
        integration.status = IntegrationStatus.DISCONNECTED
        extra = integration.extra_data or {}
        extra["qr_url"] = None
        extra["last_status"] = "disconnected"
        integration.extra_data = extra
        await db.commit()
    except Exception:
        await db.rollback()

    return {
        "status": "success",
        "session_id": session_id,
        "integration_status": "disconnected",
        "message": "Session disconnected successfully"
    }
