from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.repository import BaseRepository
from app.domains.social.models import SocialMediaComment, SocialMediaPost

class SocialMediaCommentRepository(BaseRepository[SocialMediaComment]):
    def __init__(self, session: AsyncSession):
        super().__init__(SocialMediaComment, session)

    async def get_by_project(self, project_id: UUID) -> List[SocialMediaComment]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class SocialMediaPostRepository(BaseRepository[SocialMediaPost]):
    def __init__(self, session: AsyncSession):
        super().__init__(SocialMediaPost, session)

    async def get_by_project(self, project_id: UUID) -> List[SocialMediaPost]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
