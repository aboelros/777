from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import func
import structlog

from app.core.uow import UnitOfWork
from app.core.context import TenantContext
from app.domains.integrations.repository import IntegrationRepository
from app.domains.integrations.models import Integration, IntegrationStatus, IntegrationProvider
from app.domains.integrations.schemas import IntegrationConnect, IntegrationUpdate, IntegrationConfigUpdate
from app.domains.projects.repository import ProjectRepository

logger = structlog.get_logger(__name__)

def _merge_settings(existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    base = existing.copy() if isinstance(existing, dict) else {}
    for key, value in (updates or {}).items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _merge_settings(base.get(key, {}), value)
        else:
            base[key] = value
    return base

class IntegrationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def connect_integration(self, context: TenantContext, integration_data: IntegrationConnect) -> Integration:
        async with self.uow as uow:
            proj_uuid = context.project_id
            
            config_payload = integration_data.config or {}
            provider = integration_data.provider.value
            
            if provider == "whatsapp":
                whatsapp_provider = config_payload.get("whatsapp_provider", "business_api")
                if whatsapp_provider == "go_whatsapp":
                    if not config_payload.get("base_url"):
                        raise HTTPException(status_code=400, detail="Base URL is required for Go WhatsApp")
                    if not config_payload.get("session_id"):
                        config_payload["session_id"] = "default"
                else:
                    if not config_payload.get("phone_number"):
                        raise HTTPException(status_code=400, detail="WhatsApp phone number is required for Business API setup")
            else:
                if not config_payload.get("api_key"):
                    raise HTTPException(status_code=400, detail="API key is required in config")
                    
            repo = IntegrationRepository(uow.session)
            existing = await repo.get_by_provider(proj_uuid, provider)
            
            if existing:
                existing.config = config_payload
                if provider == "whatsapp" and config_payload.get("whatsapp_provider") == "go_whatsapp":
                    extra = existing.extra_data or {}
                    extra["session_id"] = config_payload.get("session_id")
                    existing.extra_data = extra
                existing.status = IntegrationStatus.PENDING
                existing.updated_at = func.now()
                integration = existing
            else:
                extra_data = {}
                if provider == "whatsapp" and config_payload.get("whatsapp_provider") == "go_whatsapp":
                    extra_data["session_id"] = config_payload.get("session_id")
                
                integration = Integration(
                    project_id=proj_uuid,
                    provider=provider,
                    config=config_payload,
                    extra_data=extra_data,
                    status=IntegrationStatus.PENDING
                )
                repo.add(integration)
                
            await uow.commit()
            await uow.session.refresh(integration)
            return integration

    async def list_integrations(self, context: TenantContext) -> List[Integration]:
        async with self.uow as uow:
            proj_uuid = context.project_id
            
            repo = IntegrationRepository(uow.session)
            return await repo.get_project_integrations(proj_uuid)

    async def get_integration(self, context: TenantContext, integration_id: str) -> Integration:
        async with self.uow as uow:
            proj_uuid = context.project_id
            
            repo = IntegrationRepository(uow.session)
            integration = await repo.get_tenant_integration(proj_uuid, UUID(integration_id))
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
                
            return integration

    async def update_integration(self, context: TenantContext, integration_id: str, update_data: IntegrationUpdate) -> Integration:
        async with self.uow as uow:
            proj_uuid = context.project_id
            int_uuid = UUID(integration_id)
            repo = IntegrationRepository(uow.session)
            integration = await repo.get_tenant_integration(proj_uuid, int_uuid)
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
                
            if update_data.status:
                integration.status = update_data.status
                
            if update_data.config:
                current_config = integration.config or {}
                updates = update_data.config.model_dump(exclude_unset=True)
                
                # SQLAlchemy JSON mutations require reassignment
                new_config = current_config.copy()
                
                if "api_key" in updates:
                    new_config["api_key"] = updates["api_key"]
                if "phone_number" in updates:
                    new_config["phone_number"] = updates["phone_number"]
                if "shop_id" in updates:
                    new_config["shop_id"] = updates["shop_id"]
                    
                provider = integration.provider
                if provider == IntegrationProvider.TELEGRAM and updates.get("telegram_settings"):
                    new_config["telegram_settings"] = _merge_settings(
                        current_config.get("telegram_settings", {}), updates["telegram_settings"]
                    )
                elif provider == IntegrationProvider.WHATSAPP and updates.get("whatsapp_settings"):
                    new_config["whatsapp_settings"] = _merge_settings(
                        current_config.get("whatsapp_settings", {}), updates["whatsapp_settings"]
                    )
                elif provider == IntegrationProvider.INSTAGRAM and updates.get("instagram_settings"):
                    new_config["instagram_settings"] = _merge_settings(
                        current_config.get("instagram_settings", {}), updates["instagram_settings"]
                    )
                elif provider == IntegrationProvider.FACEBOOK and updates.get("facebook_settings"):
                    new_config["facebook_settings"] = _merge_settings(
                        current_config.get("facebook_settings", {}), updates["facebook_settings"]
                    )
                elif provider == IntegrationProvider.DISCORD and updates.get("discord_settings"):
                    new_config["discord_settings"] = _merge_settings(
                        current_config.get("discord_settings", {}), updates["discord_settings"]
                    )
                elif provider == IntegrationProvider.TIKTOK and updates.get("tiktok_settings"):
                    new_config["tiktok_settings"] = _merge_settings(
                        current_config.get("tiktok_settings", {}), updates["tiktok_settings"]
                    )
                    
                integration.config = new_config
                
            integration.updated_at = func.now()
            await uow.commit()
            await uow.session.refresh(integration)
            return integration

    async def delete_integration(self, context: TenantContext, integration_id: str) -> None:
        async with self.uow as uow:
            proj_uuid = context.project_id
            int_uuid = UUID(integration_id)
            repo = IntegrationRepository(uow.session)
            integration = await repo.get_tenant_integration(proj_uuid, int_uuid)
            
            if not integration:
                raise HTTPException(status_code=404, detail="Integration not found")
                
            await repo.delete(integration)
            await uow.commit()

