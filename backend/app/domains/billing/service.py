from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func

from app.core.uow import UnitOfWork
from app.domains.billing.repository import (
    SubscriptionRepository, 
    UsageTrackingRepository, 
    InvoiceRepository, 
    PaymentLinkRepository
)
from app.domains.billing.models import Subscription, UsageTracking, Invoice, PaymentLink
from app.domains.projects.repository import ProjectRepository

class BillingService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _verify_project_access(self, project_id: UUID, user_id: UUID) -> Any:
        project_repo = ProjectRepository(self.uow.session)
        project = await project_repo.get(project_id)
        if not project or project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
        return project

    async def get_subscription(self, project_id: str, user_id: str) -> Optional[Subscription]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = SubscriptionRepository(uow.session)
            subscriptions = await repo.get_by_project(proj_uuid)
            if subscriptions:
                return subscriptions[0]
            return None

    async def list_invoices(self, project_id: str, user_id: str) -> List[Invoice]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = InvoiceRepository(uow.session)
            return await repo.get_by_project(proj_uuid)
