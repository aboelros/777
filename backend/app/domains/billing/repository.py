from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.repository import BaseRepository
from app.domains.billing.models import Subscription, UsageTracking, Invoice, PaymentLink

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_by_project(self, project_id: UUID) -> List[Subscription]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class UsageTrackingRepository(BaseRepository[UsageTracking]):
    def __init__(self, session: AsyncSession):
        super().__init__(UsageTracking, session)

    async def get_by_project(self, project_id: UUID) -> List[UsageTracking]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(Invoice, session)

    async def get_by_project(self, project_id: UUID) -> List[Invoice]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class PaymentLinkRepository(BaseRepository[PaymentLink]):
    def __init__(self, session: AsyncSession):
        super().__init__(PaymentLink, session)

    async def get_by_project(self, project_id: UUID) -> List[PaymentLink]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
