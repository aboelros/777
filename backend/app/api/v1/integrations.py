"""
Integration management endpoints for connecting external platforms.
"""

from typing import List, Any, Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.projects.models import Project
from app.domains.integrations.models import Integration, IntegrationStatus
from pydantic import BaseModel
from app.domains.integrations.schemas import IntegrationConnect, IntegrationUpdate, IntegrationResponse, TelegramSettings, WhatsAppSettings, InstagramSettings, FacebookSettings
from app.domains.integrations.service import IntegrationService
from app.core.uow import UnitOfWork
# WhatsApp Business API (official Meta API)
from app.services.integrations.whatsapp_business import WhatsAppBusinessService
from app.services.integrations.meta_oauth import MetaOAuthService
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_integration_service(db: AsyncSession = Depends(get_db)) -> IntegrationService:
    return IntegrationService(UnitOfWork(db))


def _merge_settings(existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge nested settings dictionaries without mutating the originals."""
    base = existing.copy() if isinstance(existing, dict) else {}
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_settings(base.get(key, {}), value)
        else:
            base[key] = value
    return base


async def verify_project_access(project_id: UUID, user_id: str, db: AsyncSession) -> Project:
    """Helper to verify user has access to project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
    
    return project


@router.post("/{project_id}/connect", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def connect_integration(
    project_id: UUID,
    integration_data: IntegrationConnect,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    service: IntegrationService = Depends(get_integration_service)
) -> Any:
    """
    Connect a new integration to a project.
    
    Supported providers:
    - **shopify**: E-commerce platform
    - **whatsapp**: WhatsApp Business API
    - **instagram**: Instagram Direct Messages
    - **facebook**: Facebook Messenger
    - **telegram**: Telegram Bot API
    
    The config object should contain provider-specific credentials.
    """
    integration = await service.connect_integration(str(project_id), user_id, integration_data)
    
    logger.info(
        "Integration saved, starting verification",
        integration_id=str(integration.id),
        config_keys=list(integration.config.keys()) if integration.config else [],
        has_api_key="api_key" in integration.config if integration.config else False
    )
    
    # Verify and setup integration
    try:
        await _verify_and_setup_integration(integration, db)
        logger.info("Integration verification successful", integration_id=str(integration.id))
    except Exception as e:
        logger.error("Integration verification failed", error=str(e), integration_id=str(integration.id))
        # Keep as pending - user can retry verification
    
    # Fresh query to return the integration
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration.id)
    )
    final_integration = result.scalar_one()
    
    return final_integration


@router.post("/{project_id}/test-data")
async def test_integration_data(
    project_id: UUID,
    integration_data: IntegrationConnect,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Test endpoint to see what data is being received.
    """
    return {
        "received_provider": integration_data.provider.value,
        "received_config": integration_data.config,
        "config_keys": list(integration_data.config.keys()) if integration_data.config else [],
        "has_api_key": "api_key" in integration_data.config if integration_data.config else False,
        "api_key_length": len(integration_data.config.get("api_key", "")) if integration_data.config else 0,
        "project_id": str(project_id)
    }


@router.get("/{project_id}", response_model=List[IntegrationResponse])
async def list_integrations(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationService = Depends(get_integration_service)
) -> Any:
    """
    List all integrations for a project.
    """
    try:
        return await service.list_integrations(str(project_id), user_id)
    except Exception as e:
        logger.error("Failed to list integrations", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list integrations"
        )


@router.get("/{project_id}/{integration_id}", response_model=IntegrationResponse)
async def get_integration(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationService = Depends(get_integration_service)
) -> Any:
    """
    Get a specific integration by ID.
    """
    try:
        return await service.get_integration(str(project_id), str(integration_id), user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get integration", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get integration"
        )


@router.post("/{project_id}/{integration_id}/whatsapp/session", response_model=Dict[str, Any])
async def create_whatsapp_session(
    project_id: UUID,
    integration_id: UUID,
    metadata: Optional[Dict[str, Any]] = Body(default=None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    await verify_project_access(project_id, user_id, db)
    integration = await _get_whatsapp_integration(db, project_id, integration_id)
    result = await ensure_linked_device_session(db, integration, metadata=metadata)
    return result


@router.get("/{project_id}/{integration_id}/whatsapp/session/{session_id}", response_model=Dict[str, Any])
async def get_whatsapp_session_status(
    project_id: UUID,
    integration_id: UUID,
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    await verify_project_access(project_id, user_id, db)
    integration = await _get_whatsapp_integration(db, project_id, integration_id)
    return await sync_linked_device_session(db, integration, session_id)


@router.post("/{project_id}/{integration_id}/whatsapp/session/{session_id}/close", response_model=Dict[str, Any])
async def close_whatsapp_session(
    project_id: UUID,
    integration_id: UUID,
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    await verify_project_access(project_id, user_id, db)
    integration = await _get_whatsapp_integration(db, project_id, integration_id)
    return await close_linked_device_session(db, integration, session_id)


@router.patch("/{project_id}/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    project_id: UUID,
    integration_id: UUID,
    integration_data: IntegrationUpdate,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationService = Depends(get_integration_service)
) -> Any:
    """
    Update an integration's configuration or status.
    """
    try:
        return await service.update_integration(str(project_id), str(integration_id), user_id, integration_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update integration", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update integration"
        )


@router.delete("/{project_id}/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: IntegrationService = Depends(get_integration_service)
) -> None:
    """
    Disconnect and delete an integration.
    """
    try:
        await service.delete_integration(str(project_id), str(integration_id), user_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to disconnect integration", error=str(e), integration_id=str(integration_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect integration"
        )
    
    return None


@router.post("/{project_id}/{integration_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_integration(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Trigger manual sync for an integration.
    
    This will queue a background task to fetch latest data from the platform.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    if integration.status != IntegrationStatus.CONNECTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration must be connected to sync"
        )
    
    # Queue background task
    from app.workers.celery_app import celery_app
    
    if integration.provider == "shopify":
        celery_app.send_task("app.workers.tasks.sync_shopify_orders")
    
    elif integration.provider in ["facebook", "instagram"]:
        # Specific repair action: Ensure App is subscribed to Page events
        try:
            from app.services.integrations.facebook import FacebookClient
            
            # Reconstruct config needed for client
            fb_config = {
                "page_id": integration.config.get("page_id"),
                "access_token": integration.config.get("access_token"),
            }
            client = FacebookClient(fb_config)
            
            # This is the "Magic Repair" - calling /subscribed_apps
            await client.subscribe_app()
            
            logger.info("Attempted Meta App Subscription repair", integration_id=str(integration_id))
        except Exception as e:
            logger.error("Failed to repair Meta App Subscription", error=str(e))
    
    # Update last_synced_at immediately to reflect user action
    from datetime import datetime
    integration.last_sync = datetime.utcnow()
    await db.commit()

    logger.info(
        "Integration sync queued",
        integration_id=str(integration_id),
        provider=integration.provider
    )
    
    return {
        "status": "queued",
        "message": f"Sync task queued for {integration.provider} integration",
        "last_synced_at": integration.last_sync
    }


@router.post("/{project_id}/refresh-identities", status_code=status.HTTP_200_OK)
async def refresh_identities_endpoint(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Refresh customer identities (fix 'Unknown' names) for a project.
    """
    await verify_project_access(project_id, user_id, db)
    
    from app.services.customer_service import refresh_customer_identities
    result = await refresh_customer_identities(db, project_id)
    
    return result


@router.post("/{project_id}/{integration_id}/verify")
async def verify_integration(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Manually verify and setup integration.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get integration
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    logger.info(
        "Starting manual verification",
        integration_id=str(integration_id),
        provider=integration.provider,
        config_keys=list(integration.config.keys()) if integration.config else []
    )
    
    try:
        await _verify_and_setup_integration(integration, db)
        logger.info("Manual verification successful", integration_id=str(integration_id))
        # Get updated extra data
        extra = integration.extra_data or {}
        qr_code = extra.get("qr_code") or extra.get("automation", {}).get("qr_code")
        
        return {
            "status": "success",
            "message": f"{integration.provider} integration verified successfully",
            "integration_status": integration.status.value,
            "qr_code": qr_code,
            "session_id": extra.get("session_id")
        }
    except Exception as e:
        logger.error("Manual verification failed", error=str(e), integration_id=str(integration_id))
        return {
            "status": "error", 
            "message": str(e),
            "integration_status": integration.status.value
        }


@router.get("/{project_id}/{integration_id}/debug")
async def debug_integration(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Debug endpoint to check integration data.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get integration
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return {
        "id": str(integration.id),
        "provider": integration.provider,
        "status": integration.status.value,
        "config_keys": list(integration.config.keys()) if integration.config else [],
        "config_values": {k: "***" if "key" in k.lower() or "token" in k.lower() or "secret" in k.lower() 
                         else v for k, v in integration.config.items()} if integration.config else {},
        "created_at": integration.created_at.isoformat() if integration.created_at else None,
        "updated_at": integration.updated_at.isoformat() if integration.updated_at else None
    }


@router.get("/{project_id}/logs", response_model=List[Dict[str, Any]])
async def get_integration_logs(
    project_id: UUID,
    limit: int = 50,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get recent webhook/API logs for the 'Live Terminal'.
    """
    await verify_project_access(project_id, user_id, db)
    
    from app.domains.analytics.models import APILog
    
    # Fetch logs where endpoint contains 'webhook'
    # In a real scenario, we might want to filter more strictly
    result = await db.execute(
        select(APILog)
        .where(APILog.project_id == project_id)
        # .where(APILog.endpoint.ilike("%webhook%"))  # Filter for webhook endpoints
        .order_by(APILog.created_at.desc())
        .limit(limit)
    )
    
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "method": log.method,
            "endpoint": log.endpoint,
            "status": log.status_code,
            "payload": log.request,
            "response": log.response,
            "timestamp": log.created_at.isoformat()
        }
        for log in logs
    ]


def _mask_sensitive_config(config: dict, provider: str) -> dict:
    """Mask sensitive configuration values, including nested structures."""
    if not isinstance(config, dict):
        return {}

    sensitive_terms = [
        "api_key",
        "api_secret",
        "access_token",
        "refresh_token",
        "password",
        "secret",
        "token",
    ]

    def mask_value(value: Any) -> str:
        if isinstance(value, str) and len(value) > 8:
            return f"{value[:4]}...{value[-4:]}"
        if isinstance(value, str) and value:
            return "***"
        return "***"

    def recurse(node: Any) -> Any:
        if isinstance(node, dict):
            result: Dict[str, Any] = {}
            for key, value in node.items():
                if any(term in key.lower() for term in sensitive_terms):
                    result[key] = mask_value(value)
                else:
                    result[key] = recurse(value)
            return result
        if isinstance(node, list):
            return [recurse(item) for item in node]
        return node

    return recurse(config)


def _serialize_integration(integration: Integration) -> IntegrationResponse:
    """Return an integration response with masked config without mutating the model."""
    response = IntegrationResponse.model_validate(integration)
    masked_config = _mask_sensitive_config(response.config, integration.provider)
    return response.model_copy(update={"config": masked_config})

async def _verify_and_setup_integration(integration: Integration, db: AsyncSession):
    """Verify integration connection and setup webhooks."""
    if integration.provider == "telegram":
        await _setup_telegram_integration(integration, db)
    elif integration.provider == "whatsapp":
        await _setup_whatsapp_integration(integration, db)
    elif integration.provider == "shopify":
        await _setup_shopify_integration(integration, db)
    elif integration.provider == "instagram":
        await _setup_instagram_integration(integration, db)
    elif integration.provider == "facebook":
        await _setup_facebook_integration(integration, db)
    elif integration.provider == "tiktok":
        await _setup_tiktok_integration(integration, db)
    elif integration.provider == "discord":
        await _setup_discord_integration(integration, db)
    else:
        # For unsupported providers, just mark as connected for now
        integration.status = IntegrationStatus.CONNECTED
        await db.commit()
        logger.info(f"Integration {integration.provider} marked as connected (no verification implemented)")


async def _setup_telegram_integration(integration: Integration, db: AsyncSession):
    """Setup Telegram bot webhook and verify connection."""
    import httpx
    from app.core.config import settings
    
    logger.info(
        "Setting up Telegram integration", 
        integration_id=str(integration.id),
        config_keys=list(integration.config.keys()) if integration.config else [],
        config_type=type(integration.config).__name__,
        config_is_none=integration.config is None
    )
    
    # Log the actual config content (with sensitive data masked)
    if integration.config:
        masked_config = {k: "***" if "key" in k.lower() or "token" in k.lower() else v 
                        for k, v in integration.config.items()}
        logger.info("Config content", masked_config=masked_config)
    
    bot_token = integration.config.get("api_key") if integration.config else None
    if not bot_token:
        logger.error(
            "No bot token found in config", 
            config=integration.config,
            config_keys=list(integration.config.keys()) if integration.config else [],
            api_key_exists="api_key" in integration.config if integration.config else False
        )
        raise ValueError("Telegram bot token is required")
    
    # Verify bot token by getting bot info
    async with httpx.AsyncClient() as client:
        try:
            # Test bot token
            response = await client.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            response.raise_for_status()
            bot_info = response.json()
            
            if not bot_info.get("ok"):
                raise ValueError("Invalid Telegram bot token")
            
            # Setup webhook
            webhook_url = f"{settings.API_BASE_URL}/api/v1/webhooks/telegram/{integration.project_id}"
            webhook_response = await client.post(
                f"https://api.telegram.org/bot{bot_token}/setWebhook",
                json={"url": webhook_url}
            )
            webhook_response.raise_for_status()
            webhook_result = webhook_response.json()
            
            if webhook_result.get("ok"):
                # Update integration status to connected
                integration.status = IntegrationStatus.CONNECTED
                integration.extra_data = {
                    "bot_info": bot_info.get("result", {}),
                    "webhook_url": webhook_url
                }
                await db.commit()
                
                logger.info(
                    "Telegram integration verified and webhook set",
                    integration_id=str(integration.id),
                    bot_username=bot_info.get("result", {}).get("username")
                )
            else:
                raise ValueError("Failed to set Telegram webhook")
                
        except httpx.HTTPError as e:
            logger.error("HTTP error verifying Telegram bot", error=str(e))
            raise ValueError(f"Failed to verify Telegram bot: {str(e)}")
        except Exception as e:
            raise


async def _setup_whatsapp_integration(integration: Integration, db: AsyncSession):
    """
    Setup WhatsApp integration.
    
    Supports two providers:
    1. WhatsApp Business API (official Meta API)
    2. WA-Gateway (self-hosted gateway)
    """
    from app.core.config import settings
    
    # Get provider type from config
    whatsapp_provider = (integration.config or {}).get("whatsapp_provider", "business_api")
    
    if whatsapp_provider == "go_whatsapp":
        # Go WhatsApp setup
        base_url = (integration.config or {}).get("base_url")
        session_id = (integration.config or {}).get("session_id", "default")
        
        if not base_url:
            raise ValueError("Base URL is required for Go WhatsApp")
            
        # Store provider info in extra_data
        integration.extra_data = {
            "provider": "go_whatsapp",
            "session_id": session_id,
            "base_url": base_url,
            "setup_method": "manual"
        }
        integration.status = IntegrationStatus.PENDING
        
        logger.info(
            "Go WhatsApp integration setup",
            integration_id=str(integration.id),
            base_url=base_url,
            status="pending_qr_scan"
        )
        
    else:
        # WhatsApp Business API setup
        phone_number = (integration.config or {}).get("phone_number")
        if not phone_number:
            raise ValueError("WhatsApp phone number is required for WhatsApp integration")
        
        # Check if credentials are provided in config (OAuth flow) or env vars (Manual/Env flow)
        phone_number_id = (integration.config or {}).get("phone_number_id") or settings.WHATSAPP_PHONE_NUMBER_ID
        access_token = (integration.config or {}).get("access_token") or settings.WHATSAPP_ACCESS_TOKEN
        business_account_id = (integration.config or {}).get("business_account_id")
        
        if not phone_number_id or not access_token:
            raise ValueError(
                "WhatsApp Business API credentials missing. "
                "Please provide phone_number_id and access_token via OAuth or environment variables."
            )
        
        # Encrypt sensitive credentials before storing in extra_data
        from app.core.security import encrypt_pii
        integration.extra_data = {
            "provider": "business_api",
            "phone_number": phone_number,
            "phone_number_id": phone_number_id,
            "business_account_id": business_account_id,
            "access_token": encrypt_pii(access_token),  # Encrypted at rest
            "setup_method": "oauth" if (integration.config or {}).get("access_token") else "manual"
        }
        integration.status = IntegrationStatus.CONNECTED  # Business API is ready immediately
        
        logger.info(
            "WhatsApp Business API integration setup",
            integration_id=str(integration.id),
            phone_number=phone_number,
            phone_number_id=phone_number_id,
            status="connected"
        )
    
    await db.commit()


async def _get_whatsapp_integration(
    db: AsyncSession,
    project_id: UUID,
    integration_id: UUID,
) -> Integration:
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


async def _setup_shopify_integration(integration: Integration, db: AsyncSession):
    """Setup Shopify integration."""
    import httpx
    
    api_key = integration.config.get("api_key")
    api_secret = integration.config.get("api_secret")
    shop_domain = integration.config.get("shop_domain", "").replace(".myshopify.com", "")
    
    if not api_key:
        raise ValueError("Shopify API key is required")
    
    if not shop_domain:
        raise ValueError("Shopify shop domain is required")
    
    # Verify Shopify API credentials
    try:
        async with httpx.AsyncClient() as client:
            auth = httpx.BasicAuth(api_key, api_secret or "")
            response = await client.get(
                f"https://{shop_domain}.myshopify.com/admin/api/2023-10/shop.json",
                auth=auth
            )
            response.raise_for_status()
            shop_info = response.json()
            
            integration.status = IntegrationStatus.CONNECTED
            integration.extra_data = {
                "shop_info": shop_info.get("shop", {}),
                "shop_domain": shop_domain
            }
            await db.commit()
            
            logger.info(
                "Shopify integration verified",
                integration_id=str(integration.id),
                shop_name=shop_info.get("shop", {}).get("name")
            )
            
    except httpx.HTTPError as e:
        logger.error("Failed to verify Shopify credentials", error=str(e))
        raise ValueError(f"Invalid Shopify credentials: {str(e)}")


async def _setup_instagram_integration(integration: Integration, db: AsyncSession):
    """Setup Instagram integration."""
    access_token = integration.config.get("api_key")
    page_id = integration.config.get("page_id")
    ig_id = integration.config.get("instagram_business_account_id")
    
    if not access_token:
        raise ValueError("Instagram access token is required")
        
    if not ig_id:
        raise ValueError("Instagram Business Account ID is required")
    
    # Store all necessary IDs for webhook handling — encrypt token at rest
    from app.core.security import encrypt_pii
    integration.status = IntegrationStatus.CONNECTED
    integration.extra_data = {
        "setup_method": "oauth",
        "page_id": page_id,
        "instagram_business_account_id": ig_id,
        "access_token": encrypt_pii(access_token),  # Encrypted at rest
    }
    
    # NEW: Automatically subscribe app to events
    try:
        from app.services.integrations.facebook import FacebookClient
        client = FacebookClient({
            "page_id": page_id,
            "access_token": access_token
        })
        await client.subscribe_app()
        logger.info("Automatically subscribed Meta App to Instagram/Page events")
    except Exception as e:
        logger.error("Failed auto-subscription during Instagram setup", error=str(e))

    await db.commit()


async def _setup_facebook_integration(integration: Integration, db: AsyncSession):
    """Setup Facebook integration."""
    access_token = integration.config.get("api_key")
    page_id = integration.config.get("page_id")
    
    if not access_token:
        raise ValueError("Facebook access token is required")
        
    if not page_id:
        raise ValueError("Facebook Page ID is required")
    
    # Store all necessary IDs for webhook handling — encrypt token at rest
    from app.core.security import encrypt_pii
    integration.status = IntegrationStatus.CONNECTED
    integration.extra_data = {
        "setup_method": "oauth",
        "page_id": page_id,
        "access_token": encrypt_pii(access_token),  # Encrypted at rest
    }

    # NEW: Automatically subscribe app to events
    try:
        from app.services.integrations.facebook import FacebookClient
        client = FacebookClient({
            "page_id": page_id,
            "access_token": access_token
        })
        await client.subscribe_app()
        logger.info("Automatically subscribed Meta App to Facebook Page events")
    except Exception as e:
        logger.error("Failed auto-subscription during Facebook setup", error=str(e))

    await db.commit()


async def _setup_tiktok_integration(integration: Integration, db: AsyncSession):
    """Setup TikTok integration."""
    app_key = integration.config.get("api_key")
    shop_id = integration.config.get("shop_id")
    
    if not app_key:
        raise ValueError("TikTok App Key is required")
        
    if not shop_id:
        raise ValueError("TikTok Shop ID is required")
    
    # TODO: Verify TikTok API credentials
    # For now, just mark as connected
    integration.status = IntegrationStatus.CONNECTED
    integration.extra_data = {
        "setup_method": "manual",
        "shop_id": shop_id
    }
    await db.commit()


async def _setup_discord_integration(integration: Integration, db: AsyncSession):
    """Setup Discord integration."""
    bot_token = integration.config.get("api_key") or integration.config.get("bot_token")
    guild_id = integration.config.get("guild_id")

    if not bot_token:
        raise ValueError("Discord bot token is required")

    from app.services.discord_integration import DiscordIntegration
    client = DiscordIntegration(bot_token=bot_token, guild_id=guild_id)
    
    # Verify connection
    is_valid = await client.verify_connection()
    if not is_valid:
        raise ValueError("Failed to verify Discord bot token. Please check your token and bot permissions.")

    integration.status = IntegrationStatus.CONNECTED
    integration.extra_data = {
        "setup_method": "manual",
        "guild_id": guild_id
    }
    await db.commit()


# ============================================================================
# WhatsApp Business API Integration
# ============================================================================
# All WhatsApp integration now uses the official WhatsApp Business Cloud API
# No QR codes, Baileys, or linked device flows are supported


# ============================================================================
# WA-Gateway Endpoints (Alternative Self-Hosted Gateway)
# ============================================================================

@router.post("/{project_id}/whatsapp/{integration_id}/wa-gateway/start-session", status_code=status.HTTP_200_OK)
async def start_wa_gateway_session(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Start WA-Gateway session and return QR code URL.
    
    This endpoint initializes a new session with the wa-gateway instance
    and returns the QR code URL for scanning with WhatsApp mobile app.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get integration
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
        .where(Integration.provider == "whatsapp")
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp integration not found"
        )
    
    # Get session ID and base_url from config
    session_id = integration.config.get("session_id")
    base_url = integration.config.get("base_url")
    
    # Fall back to environment variable if base_url not in config
    if not base_url:
        from app.core.config import settings
        base_url = settings.WA_GATEWAY_BASE_URL
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session ID not found in integration config"
        )
    
    if not base_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WA-Gateway base URL not configured. Please either: 1) Set base_url in integration config, or 2) Set WA_GATEWAY_BASE_URL environment variable."
        )
    
    try:
        # Determine which service to use
        whatsapp_provider = integration.config.get("whatsapp_provider", "wa_gateway")
        
        # Explicitly get API key from config
        config_api_key = integration.config.get("api_key")
        
        if whatsapp_provider == "go_whatsapp":
            from app.services.integrations.go_whatsapp_service import GoWhatsAppService
            
            gateway_service = GoWhatsAppService(
                base_url=base_url,
                api_key=config_api_key
            )
            logger.info("Using Go WhatsApp Service")

        else:
             # Default or Error
             if whatsapp_provider == "wa_gateway" or whatsapp_provider == "wppconnect":
                  raise HTTPException(status_code=400, detail="Provider not supported")
             
             # Fallback to Go WhatsApp if not specified? No, better to error.
             # But for backward compatibility with existing "wa_gateway" configs, maybe we should error.
             raise HTTPException(status_code=400, detail=f"Unsupported WhatsApp provider: {whatsapp_provider}")
        
        logger.info(
            "Starting WhatsApp session",
            integration_id=str(integration_id),
            session_id=session_id,
            base_url=base_url,
            provider=whatsapp_provider,
            has_api_key=bool(config_api_key),
            api_key_preview=config_api_key[:3] + "***" if config_api_key else "None"
        )
        
        # Start session using the service (handles WAHA API)
        try:
            session_result = await gateway_service.start_session(session_id)
            qr_code_data = session_result.get("qr_code")
            
            if not qr_code_data and session_result.get("status") == "pending":
                logger.info("Session pending, QR code might be generating...", session_id=session_id)
                
        except Exception as e:
            logger.error("Failed to start session via service", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start WhatsApp session: {str(e)}"
            )

        # Update integration extra_data with session info
        extra = integration.extra_data or {}
        extra["provider"] = whatsapp_provider
        extra["session_id"] = session_id
        # We don't have a direct session URL for the user to visit anymore, 
        # as we display the QR code directly.
        extra["session_url"] = "" 
        
        if qr_code_data:
            extra["qr_url"] = qr_code_data
            
        integration.extra_data = extra
        integration.status = IntegrationStatus.PENDING
        
        await db.commit()
        
        logger.info(
            "WA-Gateway session initialized",
            integration_id=str(integration_id),
            session_id=session_id,
            has_qr=bool(qr_code_data)
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "qr_url": qr_code_data, # Frontend can display this directly
            "message": "Scan the QR code to connect WhatsApp",
            "instructions": "Scan the QR code with your WhatsApp mobile app"
        }
        
    except Exception as e:
        import traceback
        logger.error(
            "Failed to start WA-Gateway session", 
            error=str(e),
            traceback=traceback.format_exc()
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.get("/{project_id}/whatsapp/{integration_id}/wa-gateway/qr", status_code=status.HTTP_200_OK)
async def get_wa_gateway_qr(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get QR code URL for WA-Gateway session.
    
    Returns the QR code URL for an existing session.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get integration
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
        .where(Integration.provider == "whatsapp")
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp integration not found"
        )
    
    # Get QR URL from extra_data
    extra = integration.extra_data or {}
    qr_url = extra.get("qr_url")
    session_id = extra.get("session_id")
    
    if not qr_url or not session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found. Please start a session first."
        )
    
    return {
        "status": "success",
        "session_id": session_id,
        "qr_url": qr_url,
        "message": "Scan QR code with WhatsApp mobile app"
    }


@router.post("/{project_id}/whatsapp/{integration_id}/wa-gateway/logout", status_code=status.HTTP_200_OK)
async def logout_wa_gateway_session(
    project_id: UUID,
    integration_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Logout WA-Gateway session.
    
    This will disconnect the WhatsApp session and require re-scanning QR code.
    """
    # Verify project access
    await verify_project_access(project_id, user_id, db)
    
    # Get integration
    result = await db.execute(
        select(Integration)
        .where(Integration.id == integration_id)
        .where(Integration.project_id == project_id)
        .where(Integration.provider == "whatsapp")
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp integration not found"
        )
    
    # Get session ID
    session_id = (integration.extra_data or {}).get("session_id")
    
    if not session_id:
        return {
            "status": "success",
            "message": "No active session to logout"
        }
    
    # Get WA-Gateway service
    whatsapp_provider = integration.config.get("whatsapp_provider", "wa_gateway")
    from app.core.config import settings
    
    base_url = integration.config.get("base_url") or settings.WA_GATEWAY_BASE_URL
    api_key = integration.config.get("api_key")
    
    if whatsapp_provider == "go_whatsapp":
        from app.services.integrations.go_whatsapp_service import GoWhatsAppService
        gateway_service = GoWhatsAppService(base_url=base_url, api_key=api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported WhatsApp provider: {whatsapp_provider}")
        
    try:
        # Logout session
        await gateway_service.logout_session(session_id)
        
        # Update integration
        integration.status = IntegrationStatus.ERROR
        extra = integration.extra_data or {}
        extra["qr_url"] = None
        integration.extra_data = extra
        
        await db.commit()
        
        logger.info(
            "WA-Gateway session logged out",
            integration_id=str(integration_id),
            session_id=session_id
        )
        
        return {
            "status": "success",
            "message": "Session logged out successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to logout session: {str(e)}"
        )


# ============================================================================
# Meta (Facebook) OAuth Endpoints
# ============================================================================

@router.get("/{project_id}/meta/auth-url")
async def get_meta_auth_url(
    project_id: UUID,
    redirect_uri: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Get Facebook Login URL for OAuth flow."""
    await verify_project_access(project_id, user_id, db)
    
    logger.info("Checking Meta Config", 
        app_id_set=bool(settings.FACEBOOK_APP_ID), 
        secret_set=bool(settings.FACEBOOK_APP_SECRET),
        app_id_preview=str(settings.FACEBOOK_APP_ID)[:3] if settings.FACEBOOK_APP_ID else "None"
    )

    if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
        import os
        logger.error("Meta configuration missing", 
            env_vars_in_process=list(os.environ.keys()),
            facebook_app_id_env=os.environ.get("FACEBOOK_APP_ID"),
            settings_app_id=settings.FACEBOOK_APP_ID
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meta App ID/Secret missing. Config sees: AppID={bool(settings.FACEBOOK_APP_ID)}, Secret={bool(settings.FACEBOOK_APP_SECRET)}. PLEASE REDEPLOY."
        )
        
    oauth_service = MetaOAuthService(
        app_id=settings.FACEBOOK_APP_ID,
        app_secret=settings.FACEBOOK_APP_SECRET,
        redirect_uri=redirect_uri
    )
    
    # We pass project_id in state to verify it on callback if needed, 
    # but frontend handles the callback usually.
    # Scopes required for:
    # 1. Listing Pages (pages_show_list)
    # 2. Managing Page Messages (pages_messaging)
    # 3. Instagram Messaging (instagram_basic, instagram_manage_messages)
    # 4. WhatsApp Business (whatsapp_business_management, whatsapp_business_messaging)
    scopes = (
        "email,public_profile,"
        "pages_show_list,"
        "pages_read_engagement,"
        "pages_manage_metadata,"
        "pages_messaging,"
        "instagram_basic,"
        "instagram_manage_messages,"
        "whatsapp_business_management,"
        "whatsapp_business_messaging"
    )
    
    return {
        "auth_url": oauth_service.get_auth_url(state=str(project_id), scope=scopes)
    }


class MetaCallbackRequest(BaseModel):
    code: str
    redirect_uri: str
    provider: str = "facebook"

@router.post("/{project_id}/meta/callback")
async def handle_meta_callback(
    project_id: UUID,
    payload: MetaCallbackRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Exchange code for token and create/update integration.
    """
    await verify_project_access(project_id, user_id, db)
    
    if not settings.FACEBOOK_APP_ID or not settings.FACEBOOK_APP_SECRET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Meta App ID and Secret not configured"
        )
        
    oauth_service = MetaOAuthService(
        app_id=settings.FACEBOOK_APP_ID,
        app_secret=settings.FACEBOOK_APP_SECRET,
        redirect_uri=payload.redirect_uri
    )
    
    try:
        # 1. Exchange code for short-lived token
        token_data = await oauth_service.exchange_code_for_token(payload.code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("No access token returned from Meta")
            
        # 2. Exchange for long-lived token
        long_lived_data = await oauth_service.get_long_lived_token(access_token)
        long_lived_token = long_lived_data.get("access_token") or access_token
        
        # 3. Get User Pages/Accounts
        accounts_data = await oauth_service.get_user_pages(long_lived_token)
        accounts = accounts_data.get("data", [])
        
        # 4. Get WhatsApp Accounts
        whatsapp_data = await oauth_service.get_whatsapp_accounts(long_lived_token)
        whatsapp_accounts = whatsapp_data.get("data", [])
        
        # We return the accounts so the user can select which one to connect
        return {
            "status": "success",
            "access_token": long_lived_token,
            "accounts": accounts,
            "whatsapp_accounts": whatsapp_accounts
        }
        
    except Exception as e:
        logger.error("Meta OAuth failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meta authentication failed: {str(e)}"
        )


# ============================================================================
# Social Feed and Comments (Meta)
# ============================================================================

@router.get("/{project_id}/meta/feed")
async def get_meta_feed(
    project_id: UUID,
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Fetch recent posts/media from connected Facebook/Instagram accounts."""
    await verify_project_access(project_id, user_id, db)
    
    # Find active meta integrations
    result = await db.execute(
        select(Integration)
        .where(Integration.project_id == project_id)
        .where(Integration.provider.in_(["facebook", "instagram"]))
        .where(Integration.status == IntegrationStatus.CONNECTED)
    )
    integrations = result.scalars().all()
    
    if not integrations:
        return {"data": [], "message": "No connected Meta integrations found"}
        
    all_feed = []
    
    for integration in integrations:
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
                    # Normalize IG fields to match FB
                    item["message"] = item.get("caption") 
                    item["full_picture"] = item.get("media_url")
                    item["permalink_url"] = item.get("permalink")
                all_feed.extend(media)
                
        except Exception as e:
            logger.error(f"Failed to fetch feed for {integration.provider}", error=str(e))
            
    # Sort by created_time desc
    all_feed.sort(key=lambda x: x.get("created_time") or x.get("timestamp") or "", reverse=True)
    
    return {"data": all_feed[:limit]}


@router.get("/{project_id}/meta/comments/{object_id}")
async def get_meta_comments(
    project_id: UUID,
    object_id: str,
    platform: str, # "facebook" or "instagram"
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Fetch comments for a specific post/media."""
    await verify_project_access(project_id, user_id, db)
    
    # Get the appropriate integration
    result = await db.execute(
        select(Integration)
        .where(Integration.project_id == project_id)
        .where(Integration.provider == platform)
        .where(Integration.status == IntegrationStatus.CONNECTED)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail=f"Integration for {platform} not found")
        
    try:
        if platform == "facebook":
            from app.services.integrations.facebook import FacebookClient
            client = FacebookClient({
                "page_id": integration.config.get("page_id"),
                "access_token": integration.config.get("access_token")
            })
            comments = await client.get_comments(object_id)
            return {"data": comments}
            
        elif platform == "instagram":
            from app.services.integrations.instagram import InstagramClient
            client = InstagramClient({
                "page_id": integration.config.get("instagram_business_account_id"),
                "access_token": integration.config.get("access_token")
            })
            comments = await client.get_comments(object_id)
            # Normalize IG text to message
            for c in comments:
                c["message"] = c.get("text")
            return {"data": comments}
            
    except Exception as e:
        logger.error(f"Failed to fetch comments for {platform}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/meta/comments/{comment_id}/reply")
async def reply_meta_comment(
    project_id: UUID,
    comment_id: str,
    platform: str,
    message: str = Body(..., embed=True),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Reply to a comment on Facebook or Instagram."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Integration)
        .where(Integration.project_id == project_id)
        .where(Integration.provider == platform)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
        
    try:
        if platform == "facebook":
            from app.services.integrations.facebook import FacebookClient
            client = FacebookClient({
                "page_id": integration.config.get("page_id"),
                "access_token": integration.config.get("access_token")
            })
            return await client.reply_to_comment(comment_id, message)
            
        elif platform == "instagram":
            from app.services.integrations.instagram import InstagramClient
            client = InstagramClient({
                "page_id": integration.config.get("instagram_business_account_id"),
                "access_token": integration.config.get("access_token")
            })
            return await client.reply_to_comment(comment_id, message)
            
    except Exception as e:
        logger.error(f"Failed to reply to comment on {platform}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
