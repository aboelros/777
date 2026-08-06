from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional
from uuid import UUID

from app.core.repository import BaseRepository
from app.domains.ai.models import ModelTraining, BotInstruction, KnowledgeBase, AutoResponseTemplate

class ModelTrainingRepository(BaseRepository[ModelTraining]):
    def __init__(self, session: AsyncSession):
        super().__init__(ModelTraining, session)

    async def get_by_project(self, project_id: UUID) -> List[ModelTraining]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class BotInstructionRepository(BaseRepository[BotInstruction]):
    def __init__(self, session: AsyncSession):
        super().__init__(BotInstruction, session)

    async def get_by_project(self, project_id: UUID) -> List[BotInstruction]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    def __init__(self, session: AsyncSession):
        super().__init__(KnowledgeBase, session)

    async def get_by_project(self, project_id: UUID) -> List[KnowledgeBase]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

class AutoResponseTemplateRepository(BaseRepository[AutoResponseTemplate]):
    def __init__(self, session: AsyncSession):
        super().__init__(AutoResponseTemplate, session)

    async def get_by_project(self, project_id: UUID) -> List[AutoResponseTemplate]:
        query = select(self.model).where(self.model.project_id == project_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
