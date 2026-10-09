from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload
import structlog

from app.core.context import TenantContext
from app.core.uow import UnitOfWork
from app.domains.crm.models import DripCampaign, DripStep, CampaignEnrollment
from app.domains.crm.repository import DripCampaignRepository
from app.domains.customers.models import CustomerProfile
from app.domains.messages.service import MessageService

logger = structlog.get_logger(__name__)


class DripEngine:
    """Handles the execution of automated drip campaigns."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.message_service = MessageService(UnitOfWork(db))

    async def enroll_customer(self, project_id: UUID, campaign_id: UUID, customer_id: UUID) -> Optional[CampaignEnrollment]:
        """Enroll a customer into a drip campaign with strict tenant validation."""
        context = TenantContext(project_id=project_id, roles=["system"])
        campaign_repo = DripCampaignRepository(self.db, context)
        return await campaign_repo.enroll_customer(
            campaign_id=campaign_id,
            customer_id=customer_id,
            context=context
        )

    async def process_due_steps(self) -> int:
        """Check all active enrollments and execute due steps under derived TenantContext."""
        now = datetime.utcnow()

        result = await self.db.execute(
            select(CampaignEnrollment)
            .options(joinedload(CampaignEnrollment.campaign), joinedload(CampaignEnrollment.customer))
            .where(CampaignEnrollment.status == "active")
            .where(CampaignEnrollment.next_execution_at <= now)
        )
        enrollments = result.scalars().all()
        processed = 0

        for enrollment in enrollments:
            try:
                context = TenantContext(project_id=enrollment.project_id, roles=["system"])
                await self._execute_step(enrollment, context)
                processed += 1
            except Exception as e:
                logger.error(
                    "Failed to process drip step for enrollment",
                    enrollment_id=str(enrollment.id),
                    project_id=str(enrollment.project_id),
                    error=str(e)
                )

        return processed

    async def _execute_step(self, enrollment: CampaignEnrollment, context: TenantContext):
        """Execute current step ensuring tenant boundaries."""
        campaign_repo = DripCampaignRepository(self.db, context)
        campaign = await campaign_repo.get_by_context(enrollment.campaign_id, context=context)
        if not campaign or enrollment.project_id != context.project_id:
            logger.warning(
                "Campaign tenant mismatch in background step execution",
                enrollment_id=str(enrollment.id),
                project_id=str(context.project_id)
            )
            return

        step = await self._get_step(enrollment.campaign_id, enrollment.current_step)
        if not step:
            enrollment.status = "completed"
            enrollment.completed_at = datetime.utcnow()
            await self.db.commit()
            return

        try:
            customer_name = enrollment.customer.name if enrollment.customer else "Customer"
            content = step.content_template.replace("{{name}}", customer_name or "Customer")

            logger.info(
                "Executing drip message",
                customer_id=str(enrollment.customer_id) if enrollment.customer_id else "unknown",
                content_preview=content[:50]
            )

            enrollment.current_step += 1
            next_step = await self._get_step(enrollment.campaign_id, enrollment.current_step)
            if next_step:
                enrollment.next_execution_at = datetime.utcnow() + timedelta(hours=next_step.delay_hours)
            else:
                enrollment.status = "completed"
                enrollment.completed_at = datetime.utcnow()

            await self.db.commit()

        except Exception as e:
            logger.error("Failed to execute drip step", error=str(e), enrollment_id=str(enrollment.id))

    async def _get_step(self, campaign_id: UUID, step_order: int) -> Optional[DripStep]:
        result = await self.db.execute(
            select(DripStep).where(
                DripStep.campaign_id == campaign_id,
                DripStep.step_order == step_order
            )
        )
        return result.scalar_one_or_none()
