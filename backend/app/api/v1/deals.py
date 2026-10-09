from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.uow import UnitOfWork

from app.core.context import TenantContext
from app.api.dependencies.tenant import get_tenant_context
from app.domains.crm.models import PipelineStage, Deal
from app.domains.crm.service import CRMService
from app.domains.crm.schemas import PipelineStageResponse, DealResponse
from app.domains.projects.models import Project

router = APIRouter()

def get_crm_service(db: AsyncSession = Depends(get_db)) -> CRMService:
    return CRMService(uow=UnitOfWork(db))

# --- Stages ---

@router.get("/{project_id}/stages", response_model=List[PipelineStageResponse])
async def get_stages(
    project_id: UUID,
    context: TenantContext = Depends(get_tenant_context),
    service: CRMService = Depends(get_crm_service)
) -> Any:
    """Get all pipeline stages for a project."""
    return await service.list_stages(context)

@router.post("/{project_id}/stages", response_model=PipelineStageResponse)
async def create_stage(
    project_id: UUID,
    name: str,
    index: int = 0,
    color: str = "#6366f1",
    context: TenantContext = Depends(get_tenant_context),
    service: CRMService = Depends(get_crm_service)
) -> Any:
    """Create a new pipeline stage."""
    return await service.create_stage(
        context=context,
        name=name,
        index=index,
        color=color
    )

# --- Deals ---

@router.get("/{project_id}/deals", response_model=List[DealResponse])
async def get_deals(
    project_id: UUID,
    stage_id: Optional[UUID] = None,
    context: TenantContext = Depends(get_tenant_context),
    service: CRMService = Depends(get_crm_service)
) -> Any:
    """Get deals, optionally filtered by stage."""
    return await service.list_deals(context=context, stage_id=stage_id)

@router.post("/{project_id}/deals", response_model=DealResponse)
async def create_deal(
    project_id: UUID,
    title: str,
    stage_id: UUID,
    value: float = 0.0,
    customer_id: Optional[UUID] = None,
    context: TenantContext = Depends(get_tenant_context),
    service: CRMService = Depends(get_crm_service)
) -> Any:
    """Create a new deal."""
    return await service.create_deal(
        context=context,
        title=title,
        stage_id=stage_id,
        value=value,
        customer_id=customer_id
    )

@router.patch("/{project_id}/deals/{deal_id}", response_model=DealResponse)
async def update_deal(
    project_id: UUID,
    deal_id: UUID,
    stage_id: Optional[UUID] = None,
    value: Optional[float] = None,
    status: Optional[str] = None,
    context: TenantContext = Depends(get_tenant_context),
    service: CRMService = Depends(get_crm_service)
) -> Any:
    """Update a deal (move stage, change value)."""
    return await service.update_deal(
        context=context,
        deal_id=deal_id,
        stage_id=stage_id,
        value=value,
        status=status
    )
