from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.integrations.models import Integration, IntegrationStatus
from app.domains.integrations.repository import IntegrationRepository
from app.api.v1.messages import _to_absolute_url, _get_api_base_url

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/{project_id}/accounts")
async def get_social_accounts(
    project_id: UUID,
    request: Request,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get connected social media accounts for authenticated tenant."""
    integration_repo = IntegrationRepository(db)
    integrations = await integration_repo.get_project_integrations(context.project_id)

    valid_integrations = [
        i for i in integrations
        if i.status == IntegrationStatus.CONNECTED and i.provider in ["facebook", "instagram", "tiktok", "whatsapp"]
    ]

    accounts = []
    for integration in valid_integrations:
        config = integration.config or {}
        name = "Unknown Account"
        username = None
        profile_pic = None
        account_id = None

        if integration.provider == "facebook":
            name = config.get("page_name", "Facebook Page")
            account_id = config.get("page_id")
            if account_id:
                profile_pic = f"https://graph.facebook.com/{account_id}/picture?type=normal"
        elif integration.provider == "instagram":
            name = config.get("instagram_username", "Instagram Account")
            username = config.get("instagram_username")
            account_id = config.get("instagram_business_account_id")
            profile_pic = config.get("profile_picture_url")
        elif integration.provider == "whatsapp":
            name = config.get("phone_number", "WhatsApp")
            account_id = config.get("phone_number_id")
        elif integration.provider == "tiktok":
            name = config.get("shop_name", "TikTok Shop")
            account_id = config.get("shop_id")

        persistent_avatar = integration.extra_data.get("persistent_avatar_url") if integration.extra_data else None
        if persistent_avatar:
            profile_pic = persistent_avatar
        elif profile_pic and profile_pic.startswith("http") and ("fbcdn.net" in profile_pic or "cdninstagram.com" in profile_pic):
            try:
                from app.services.webhook_processor import WebhookProcessor
                from fastapi import BackgroundTasks
                processor = WebhookProcessor(db, BackgroundTasks())
                stored_url = await processor._persist_avatar(context.project_id, integration.id, profile_pic)
                if stored_url:
                    new_extra = dict(integration.extra_data or {})
                    new_extra["persistent_avatar_url"] = stored_url
                    integration.extra_data = new_extra
                    await db.commit()
                    profile_pic = stored_url
            except Exception as e:
                logger.error("Failed to persist account profile picture", error=str(e))

        if profile_pic and not profile_pic.startswith("http"):
            base_url = _get_api_base_url(request)
            profile_pic = _to_absolute_url(profile_pic, base_url)

        accounts.append({
            "id": integration.id,
            "provider": integration.provider,
            "platform": integration.provider,
            "name": name,
            "username": username,
            "profile_picture": profile_pic,
            "external_id": account_id,
            "status": integration.status,
            "last_sync": integration.last_sync.isoformat() if integration.last_sync else None
        })

    return {"accounts": accounts}


@router.get("/{project_id}/feed")
async def get_live_feed(
    project_id: UUID,
    limit: int = 10,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Fetch live feed from Meta platforms under authenticated tenant boundary."""
    integration_repo = IntegrationRepository(db)
    integrations = await integration_repo.get_project_integrations(context.project_id)

    valid_integrations = [
        i for i in integrations
        if i.status == IntegrationStatus.CONNECTED and i.provider in ["facebook", "instagram"]
    ]

    all_feed = []
    for integration in valid_integrations:
        try:
            if integration.provider == "facebook":
                from app.services.integrations.facebook import FacebookClient
                client = FacebookClient({
                    "page_id": integration.config.get("page_id"),
                    "access_token": integration.config.get("access_token")
                })
                feed = await client.get_feed(limit=limit)
                for item in feed:
                    item["platform"] = "facebook"
                    item["account_name"] = integration.config.get("page_name", "Facebook Page")
                all_feed.extend(feed)
            elif integration.provider == "instagram":
                from app.services.integrations.instagram import InstagramClient
                client = InstagramClient({
                    "page_id": integration.config.get("instagram_business_account_id"),
                    "access_token": integration.config.get("access_token")
                })
                media = await client.get_media(limit=limit)
                for item in media:
                    item["platform"] = "instagram"
                    item["account_name"] = integration.config.get("instagram_username", "Instagram")
                    item["message"] = item.get("caption")
                    item["full_picture"] = item.get("media_url")
                    item["permalink_url"] = item.get("permalink")
                    item["created_time"] = item.get("timestamp")
                all_feed.extend(media)
        except Exception as e:
            logger.error(f"Failed to fetch live feed for {integration.provider}", error=str(e))

    all_feed.sort(key=lambda x: x.get("created_time") or "", reverse=True)
    return {"data": all_feed[:limit]}
