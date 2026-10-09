from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func

from app.core.uow import UnitOfWork
from app.core.context import TenantContext
from app.domains.crm.repository import PipelineStageRepository, DealRepository, DripCampaignRepository
from app.domains.crm.models import PipelineStage, Deal, DripCampaign, DripStep


class CRMService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def list_stages(self, context: TenantContext) -> List[PipelineStage]:
        async with self.uow as uow:
            repo = PipelineStageRepository(uow.session, context)
            return await repo.list_by_context(context)

    async def create_stage(self, context: TenantContext, name: str, index: int = 0, color: str = "#6366f1") -> PipelineStage:
        async with self.uow as uow:
            repo = PipelineStageRepository(uow.session, context)
            return await repo.create_stage(name, index, color, context=context)

    async def list_deals(self, context: TenantContext, stage_id: Optional[UUID] = None) -> List[Deal]:
        async with self.uow as uow:
            repo = DealRepository(uow.session, context)
            return await repo.list_by_context(stage_id=stage_id, context=context)

    async def create_deal(
        self,
        context: TenantContext,
        title: str,
        stage_id: UUID,
        value: float = 0.0,
        customer_id: Optional[UUID] = None
    ) -> Deal:
        async with self.uow as uow:
            # Verify stage exists and belongs to the project
            stage_repo = PipelineStageRepository(uow.session, context)
            stage = await stage_repo.get_stage_by_context(stage_id, context=context)
            if not stage:
                raise HTTPException(status_code=404, detail="Stage not found")

            repo = DealRepository(uow.session, context)
            return await repo.create_deal(
                title=title,
                stage_id=stage_id,
                value=value,
                customer_id=customer_id,
                context=context
            )

    async def update_deal(
        self,
        context: TenantContext,
        deal_id: UUID,
        stage_id: Optional[UUID] = None,
        value: Optional[float] = None,
        status: Optional[str] = None
    ) -> Deal:
        async with self.uow as uow:
            repo = DealRepository(uow.session, context)
            deal = await repo.get_deal_by_context(deal_id, context=context)
            if not deal:
                raise HTTPException(status_code=404, detail="Deal not found")

            if stage_id:
                # Assuming if stage_id is provided, it must belong to the tenant.
                # Since we don't strictly require validating the stage again here for simplicity if it's trusted,
                # but to be safe, we should validate it.
                stage_repo = PipelineStageRepository(uow.session, context)
                stage = await stage_repo.get_stage_by_context(stage_id, context=context)
                if not stage:
                    raise HTTPException(status_code=404, detail="Stage not found")
                deal.stage_id = stage_id

            if value is not None:
                deal.value = value
            if status:
                deal.status = status

            await uow.commit()
            return deal

    async def list_campaigns(self, context: TenantContext) -> List[DripCampaign]:
        async with self.uow as uow:
            repo = DripCampaignRepository(uow.session, context)
            return await repo.list_by_context(context)

    async def list_campaigns_by_context(self, context: TenantContext) -> List[DripCampaign]:
        async with self.uow as uow:
            repo = DripCampaignRepository(uow.session, context)
            return await repo.list_by_context(context)

    async def create_campaign_by_context(
        self,
        context: TenantContext,
        name: str,
        trigger_type: str = "manual"
    ) -> DripCampaign:
        async with self.uow as uow:
            repo = DripCampaignRepository(uow.session, context)
            return await repo.create_campaign(name=name, trigger_type=trigger_type, context=context)

    async def add_step_by_context(
        self,
        context: TenantContext,
        campaign_id: UUID,
        step_order: int,
        content_template: str,
        delay_hours: int = 24
    ) -> DripStep:
        async with self.uow as uow:
            repo = DripCampaignRepository(uow.session, context)
            return await repo.add_step(
                campaign_id=campaign_id,
                step_order=step_order,
                content_template=content_template,
                delay_hours=delay_hours,
                context=context
            )
