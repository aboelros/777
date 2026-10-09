from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.crm.models import DripCampaign, DripStep
from app.domains.crm.repository import DripCampaignRepository

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/{project_id}/campaigns")
async def get_campaigns(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all drip campaigns for the authenticated tenant."""
    campaign_repo = DripCampaignRepository(db, context)
    return await campaign_repo.list_by_context(context)


@router.post("/{project_id}/campaigns")
async def create_campaign(
    project_id: UUID,
    name: str,
    trigger_type: str = "manual",
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new drip campaign within authenticated tenant boundary."""
    campaign_repo = DripCampaignRepository(db, context)
    return await campaign_repo.create_campaign(name=name, trigger_type=trigger_type, context=context)


@router.post("/{project_id}/campaigns/{campaign_id}/steps")
async def add_step(
    project_id: UUID,
    campaign_id: UUID,
    step_order: int,
    content_template: str,
    delay_hours: int = 24,
    context: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Add a step to a campaign with repository-enforced tenant check."""
    campaign_repo = DripCampaignRepository(db, context)
    return await campaign_repo.add_step(
        campaign_id=campaign_id,
        step_order=step_order,
        content_template=content_template,
        delay_hours=delay_hours,
        context=context
    )
