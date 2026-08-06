from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.repository import BaseRepository
from app.domains.analytics.models import Report, APILog

class ReportRepository(BaseRepository[Report]):
    def __init__(self, session: AsyncSession):
        super().__init__(Report, session)

    async def get_by_project(self, project_id: UUID) -> List[Report]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class APILogRepository(BaseRepository[APILog]):
    def __init__(self, session: AsyncSession):
        super().__init__(APILog, session)

    async def get_by_project(self, project_id: UUID) -> List[APILog]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
