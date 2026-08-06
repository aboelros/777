from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.access_control import verify_project_access
from app.domains.crm.models import DripCampaign, DripStep

router = APIRouter()

@router.get("/{project_id}/campaigns")
async def get_campaigns(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all drip campaigns for a project."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(DripCampaign)
        .options(selectinload(DripCampaign.steps))
        .where(DripCampaign.project_id == project_id)
        .order_by(desc(DripCampaign.created_at))
    )
    return result.scalars().all()

@router.post("/{project_id}/campaigns")
async def create_campaign(
    project_id: UUID,
    name: str,
    trigger_type: str = "manual",
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new drip campaign."""
    await verify_project_access(project_id, user_id, db)
    
    campaign = DripCampaign(
        project_id=project_id,
        name=name,
        trigger_type=trigger_type
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign

@router.post("/{project_id}/campaigns/{campaign_id}/steps")
async def add_step(
    project_id: UUID,
    campaign_id: UUID,
    step_order: int,
    content_template: str,
    delay_hours: int = 24,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Add a step to a campaign."""
    await verify_project_access(project_id, user_id, db)
    
    # Verify campaign exists
    campaign = await db.get(DripCampaign, campaign_id)
    if not campaign or campaign.project_id != project_id:
        raise HTTPException(status_code=404, detail="Campaign not found")

    step = DripStep(
        campaign_id=campaign_id,
        step_order=step_order,
        content_template=content_template,
        delay_hours=delay_hours
    )
    db.add(step)
    await db.commit()
    await db.refresh(step)
    return step
