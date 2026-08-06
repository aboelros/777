from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.access_control import verify_project_access
from app.domains.crm.models import PipelineStage, Deal
from app.domains.projects.models import Project

router = APIRouter()

# --- Stages ---

@router.get("/{project_id}/stages")
async def get_stages(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get all pipeline stages for a project."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(PipelineStage)
        .where(PipelineStage.project_id == project_id)
        .where(PipelineStage.is_active == True)
        .order_by(asc(PipelineStage.index))
    )
    return result.scalars().all()

@router.post("/{project_id}/stages")
async def create_stage(
    project_id: UUID,
    name: str,
    index: int = 0,
    color: str = "#6366f1",
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new pipeline stage."""
    await verify_project_access(project_id, user_id, db)
    
    stage = PipelineStage(
        project_id=project_id,
        name=name,
        index=index,
        color=color
    )
    db.add(stage)
    await db.commit()
    await db.refresh(stage)
    return stage

# --- Deals ---

@router.get("/{project_id}/deals")
async def get_deals(
    project_id: UUID,
    stage_id: Optional[UUID] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get deals, optionally filtered by stage."""
    await verify_project_access(project_id, user_id, db)
    
    query = select(Deal).where(Deal.project_id == project_id)
    
    if stage_id:
        query = query.where(Deal.stage_id == stage_id)
        
    query = query.order_by(desc(Deal.updated_at))
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{project_id}/deals")
async def create_deal(
    project_id: UUID,
    title: str,
    stage_id: UUID,
    value: float = 0.0,
    customer_id: Optional[UUID] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new deal."""
    await verify_project_access(project_id, user_id, db)
    
    # Verify stage exists and belongs to project
    stage_result = await db.execute(
        select(PipelineStage)
        .where(PipelineStage.id == stage_id)
        .where(PipelineStage.project_id == project_id)
    )
    if not stage_result.scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Stage not found")

    deal = Deal(
        project_id=project_id,
        stage_id=stage_id,
        title=title,
        value=value,
        customer_id=customer_id
    )
    db.add(deal)
    await db.commit()
    await db.refresh(deal)
    return deal

@router.patch("/{project_id}/deals/{deal_id}")
async def update_deal(
    project_id: UUID,
    deal_id: UUID,
    stage_id: Optional[UUID] = None,
    value: Optional[float] = None,
    status: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a deal (move stage, change value)."""
    await verify_project_access(project_id, user_id, db)
    
    result = await db.execute(
        select(Deal)
        .where(Deal.id == deal_id)
        .where(Deal.project_id == project_id)
    )
    deal = result.scalar_one_or_none()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
        
    if stage_id:
         deal.stage_id = stage_id
    if value is not None:
         deal.value = value
    if status:
         deal.status = status
         
    await db.commit()
    await db.refresh(deal)
    return deal
