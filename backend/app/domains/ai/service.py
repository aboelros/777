from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import HTTPException, status

from app.core.uow import UnitOfWork
from app.domains.ai.repository import (
    ModelTrainingRepository, 
    BotInstructionRepository,
    KnowledgeBaseRepository,
    AutoResponseTemplateRepository
)
from app.domains.ai.models import ModelTraining, BotInstruction, KnowledgeBase, AutoResponseTemplate
from app.domains.projects.repository import ProjectRepository

class AIService:
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

    async def list_bot_instructions(self, project_id: str, user_id: str) -> List[BotInstruction]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = BotInstructionRepository(uow.session)
            return await repo.get_by_project(proj_uuid)

    async def list_knowledge_bases(self, project_id: str, user_id: str) -> List[KnowledgeBase]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = KnowledgeBaseRepository(uow.session)
            return await repo.get_by_project(proj_uuid)
