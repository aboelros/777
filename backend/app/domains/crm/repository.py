from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, asc
from sqlalchemy.orm import selectinload

from app.core.repository import BaseRepository
from app.core.context import TenantContext
from app.domains.crm.models import (
    PipelineStage,
    Deal,
    DripCampaign,
    DripStep,
    CampaignEnrollment,
)
from app.domains.customers.models import CustomerProfile


class PipelineStageRepository(BaseRepository[PipelineStage]):
    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(PipelineStage, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        ctx = context or self.context
        if not ctx or not ctx.project_id:
            raise ValueError("TenantContext with valid project_id is required")
        return ctx

    async def get_by_project(self, project_id: UUID) -> List[PipelineStage]:
        # Legacy method; kept for internal compatibility if needed, but new endpoints should use context
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_context(self, context: Optional[TenantContext] = None) -> List[PipelineStage]:
        ctx = self._get_context(context)
        query = (
            select(self.model)
            .where(
                self.model.project_id == ctx.project_id,
                self.model.is_active == True
            )
            .order_by(asc(self.model.index))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_stage(self, name: str, index: int = 0, color: str = "#6366f1", context: Optional[TenantContext] = None) -> PipelineStage:
        ctx = self._get_context(context)
        stage = PipelineStage(
            project_id=ctx.project_id,
            name=name,
            index=index,
            color=color
        )
        self.session.add(stage)
        await self.session.commit()
        await self.session.refresh(stage)
        return stage

    async def get_stage_by_context(self, stage_id: UUID, context: Optional[TenantContext] = None) -> Optional[PipelineStage]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.id == stage_id,
            self.model.project_id == ctx.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(Deal, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        ctx = context or self.context
        if not ctx or not ctx.project_id:
            raise ValueError("TenantContext with valid project_id is required")
        return ctx

    async def get_by_project(self, project_id: UUID) -> List[Deal]:
        # Legacy method
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def list_by_context(self, stage_id: Optional[UUID] = None, context: Optional[TenantContext] = None) -> List[Deal]:
        ctx = self._get_context(context)
        query = select(self.model).where(self.model.project_id == ctx.project_id)

        if stage_id:
            query = query.where(self.model.stage_id == stage_id)

        query = query.order_by(desc(self.model.updated_at))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_deal_by_context(self, deal_id: UUID, context: Optional[TenantContext] = None) -> Optional[Deal]:
        ctx = self._get_context(context)
        query = select(self.model).where(
            self.model.id == deal_id,
            self.model.project_id == ctx.project_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_deal(self, title: str, stage_id: UUID, value: float = 0.0, customer_id: Optional[UUID] = None, context: Optional[TenantContext] = None) -> Deal:
        ctx = self._get_context(context)
        deal = Deal(
            project_id=ctx.project_id,
            stage_id=stage_id,
            title=title,
            value=value,
            customer_id=customer_id
        )
        self.session.add(deal)
        await self.session.commit()
        await self.session.refresh(deal)
        return deal


class DripCampaignRepository(BaseRepository[DripCampaign]):
    def __init__(self, session: AsyncSession, context: Optional[TenantContext] = None):
        super().__init__(DripCampaign, session)
        self.context = context

    def _get_context(self, context: Optional[TenantContext] = None) -> TenantContext:
        ctx = context or self.context
        if not ctx or not ctx.project_id:
            raise ValueError("TenantContext with valid project_id is required")
        return ctx

    async def get_by_context(self, campaign_id: UUID, context: Optional[TenantContext] = None) -> Optional[DripCampaign]:
        ctx = self._get_context(context)
        query = (
            select(self.model)
            .options(selectinload(self.model.steps))
            .where(
                self.model.id == campaign_id,
                self.model.project_id == ctx.project_id
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_by_context(self, context: Optional[TenantContext] = None) -> List[DripCampaign]:
        ctx = self._get_context(context)
        query = (
            select(self.model)
            .options(selectinload(self.model.steps))
            .where(self.model.project_id == ctx.project_id)
            .order_by(desc(self.model.created_at))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_campaign(
        self,
        name: str,
        trigger_type: str = "manual",
        context: Optional[TenantContext] = None
    ) -> DripCampaign:
        ctx = self._get_context(context)
        campaign = DripCampaign(
            project_id=ctx.project_id,
            name=name,
            trigger_type=trigger_type
        )
        self.session.add(campaign)
        await self.session.commit()
        await self.session.refresh(campaign)
        return campaign

    async def add_step(
        self,
        campaign_id: UUID,
        step_order: int,
        content_template: str,
        delay_hours: int = 24,
        context: Optional[TenantContext] = None
    ) -> DripStep:
        ctx = self._get_context(context)
        campaign = await self.get_by_context(campaign_id, context=ctx)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or access denied"
            )

        step = DripStep(
            campaign_id=campaign_id,
            step_order=step_order,
            content_template=content_template,
            delay_hours=delay_hours
        )
        self.session.add(step)
        await self.session.commit()
        await self.session.refresh(step)
        return step

    async def enroll_customer(
        self,
        campaign_id: UUID,
        customer_id: UUID,
        context: Optional[TenantContext] = None
    ) -> CampaignEnrollment:
        ctx = self._get_context(context)
        campaign = await self.get_by_context(campaign_id, context=ctx)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found or access denied"
            )

        # Verify customer profile belongs to the tenant
        customer_res = await self.session.execute(
            select(CustomerProfile).where(
                CustomerProfile.id == customer_id,
                CustomerProfile.project_id == ctx.project_id
            )
        )
        customer = customer_res.scalar_one_or_none()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found or access denied"
            )

        # Check existing enrollment
        existing_res = await self.session.execute(
            select(CampaignEnrollment).where(
                CampaignEnrollment.project_id == ctx.project_id,
                CampaignEnrollment.campaign_id == campaign_id,
                CampaignEnrollment.customer_id == customer_id
            )
        )
        existing = existing_res.scalar_one_or_none()
        if existing:
            return existing

        # Get first step delay
        first_step = None
        for s in campaign.steps:
            if s.step_order == 1:
                first_step = s
                break

        delay = first_step.delay_hours if first_step else 24
        next_run = datetime.utcnow() + timedelta(hours=delay)

        enrollment = CampaignEnrollment(
            project_id=ctx.project_id,
            campaign_id=campaign_id,
            customer_id=customer_id,
            status="active",
            current_step=1,
            next_execution_at=next_run
        )
        self.session.add(enrollment)
        await self.session.commit()
        await self.session.refresh(enrollment)
        return enrollment

    async def get_by_project(self, project_id: UUID) -> List[DripCampaign]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
