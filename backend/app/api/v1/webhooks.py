"""
Webhook endpoints for receiving messages from integrations.
"""

from typing import Any, Optional
from fastapi import APIRouter, Request, HTTPException, status, BackgroundTasks, Depends
from uuid import UUID
import structlog

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = structlog.get_logger(__name__)

@router.post("/inbound")
async def inbound_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    explicit_project_id: Optional[UUID] = None
) -> Any:
    """
    Centralized Webhook Gateway.
    All platforms should point here.
    """
    logger.debug("Inbound webhook received", method=request.method, path=str(request.url.path))
    from app.services.webhook_gateway import WebhookGateway

    gateway = WebhookGateway(db, background_tasks)
    return await gateway.handle_inbound(request, explicit_project_id=explicit_project_id)

@router.get("/inbound")
async def verify_inbound_webhook(request: Request) -> Any:
    """
    Verification endpoint for Meta (Facebook/WhatsApp).
    """
    from fastapi.responses import PlainTextResponse
    from app.core.config import settings

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    verify_token = settings.WHATSAPP_VERIFY_TOKEN or getattr(settings, "META_VERIFY_TOKEN", None)

    if mode == "subscribe" and token == verify_token:
        return PlainTextResponse(challenge)

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

# --- Legacy Proxies (Delegating to Central Gateway) ---
# These ensure backward compatibility for existing webhooks.

@router.post("/whatsapp")
async def whatsapp_business_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Legacy endpoint for WhatsApp Business API."""
    logger.debug("WhatsApp webhook received", method=request.method)
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.get("/whatsapp")
async def verify_whatsapp_business_webhook(request: Request) -> Any:
    """Legacy verification for WhatsApp Business API."""
    return await verify_inbound_webhook(request)

@router.post("/telegram/{project_id}")
async def telegram_webhook(
    project_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Legacy endpoint for Telegram."""
    logger.debug("Telegram webhook received", project_id=str(project_id))
    # project_id is ignored as Gateway resolves it internally
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.post("/instagram/{project_id}")
async def instagram_webhook(
    project_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Legacy endpoint for Instagram."""
    logger.debug("Instagram webhook received", project_id=str(project_id))
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.get("/instagram/{project_id}")
async def instagram_verify(project_id: UUID, request: Request) -> Any:
    """Legacy verification for Instagram."""
    return await verify_inbound_webhook(request)

@router.post("/facebook/{project_id}")
async def facebook_webhook(
    project_id: UUID,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Legacy endpoint for Facebook."""
    logger.debug("Facebook webhook received", project_id=str(project_id))
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.get("/facebook/{project_id}")
async def facebook_verify(project_id: UUID, request: Request) -> Any:
    """Legacy verification for Facebook."""
    return await verify_inbound_webhook(request)

@router.post("/go-whatsapp")
async def go_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Legacy endpoint for Go WhatsApp."""
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.post("/whatsapp/go_whatsapp")
async def go_whatsapp_webhook_alt(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Alternative legacy endpoint for Go WhatsApp."""
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.post("/wa-gateway/session")
async def wa_gateway_session_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Handle WA-Gateway session status updates.
    """
    logger.info("Session webhook received (legacy handler)")
    return {"status": "ok"}

@router.post("/tiktok")
async def tiktok_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Endpoint for TikTok Business Messages."""
    logger.debug("TikTok webhook received")
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)

@router.post("/discord")
async def discord_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Endpoint for Discord Interactions."""
    logger.debug("Discord webhook received")
    return await inbound_webhook(request, background_tasks, db, explicit_project_id=project_id)
