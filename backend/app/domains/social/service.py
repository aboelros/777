from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func

from app.core.uow import UnitOfWork
from app.domains.social.repository import SocialMediaCommentRepository, SocialMediaPostRepository
from app.domains.social.models import SocialMediaComment, SocialMediaPost
from app.domains.projects.repository import ProjectRepository

class SocialMediaService:
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

    async def list_comments(self, project_id: str, user_id: str) -> List[SocialMediaComment]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = SocialMediaCommentRepository(uow.session)
            return await repo.get_by_project(proj_uuid)

    async def list_posts(self, project_id: str, user_id: str) -> List[SocialMediaPost]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = SocialMediaPostRepository(uow.session)
            return await repo.get_by_project(proj_uuid)
