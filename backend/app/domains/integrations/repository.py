from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.repository import BaseRepository
from app.domains.integrations.models import Integration, IntegrationProvider

class IntegrationRepository(BaseRepository[Integration]):
    def __init__(self, session: AsyncSession):
        super().__init__(Integration, session)

    async def get_by_provider(
        self,
        project_id: UUID,
        provider: IntegrationProvider
    ) -> Optional[Integration]:
        query = select(self.model).where(
            self.model.project_id == project_id,
            self.model.provider == provider
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_project_integrations(
        self,
        project_id: UUID
    ) -> List[Integration]:
        query = select(self.model).where(
            self.model.project_id == project_id
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
