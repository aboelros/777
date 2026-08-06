from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.repository import BaseRepository
from app.domains.crm.models import PipelineStage, Deal, DripCampaign, DripStep, CampaignEnrollment

class PipelineStageRepository(BaseRepository[PipelineStage]):
    def __init__(self, session: AsyncSession):
        super().__init__(PipelineStage, session)

    async def get_by_project(self, project_id: UUID) -> List[PipelineStage]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(Deal, session)

    async def get_by_project(self, project_id: UUID) -> List[Deal]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class DripCampaignRepository(BaseRepository[DripCampaign]):
    def __init__(self, session: AsyncSession):
        super().__init__(DripCampaign, session)

    async def get_by_project(self, project_id: UUID) -> List[DripCampaign]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
