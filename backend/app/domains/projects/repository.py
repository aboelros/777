from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from app.core.repository import BaseRepository
from app.domains.projects.models import Project, ProjectMember
from app.domains.auth.models import User

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get_by_code(self, project_code: str) -> Optional[Project]:
        result = await self.session.execute(
            select(self.model).where(self.model.project_code == project_code)
        )
        return result.scalar_one_or_none()

    async def get_owned_projects(self, user_id: UUID) -> List[Tuple[Project, str]]:
        result = await self.session.execute(
            select(self.model, User.name)
            .join(User, self.model.owner_id == User.id)
            .where(self.model.owner_id == user_id)
            .order_by(self.model.created_at.desc())
        )
        return list(result.all())

class ProjectMemberRepository(BaseRepository[ProjectMember]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProjectMember, session)

    async def get_member_projects(self, user_id: UUID) -> List[Tuple[ProjectMember, Project, str]]:
        result = await self.session.execute(
            select(self.model, Project, User.name)
            .join(Project, self.model.project_id == Project.id)
            .join(User, Project.owner_id == User.id)
            .where(self.model.user_id == user_id)
            .order_by(Project.created_at.desc())
        )
        return list(result.all())
        
    async def get_membership(self, project_id: UUID, user_id: UUID) -> Optional[ProjectMember]:
        result = await self.session.execute(
            select(self.model).where(
                self.model.project_id == project_id,
                self.model.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
        
    async def delete_membership(self, project_id: UUID, user_id: UUID) -> None:
        await self.session.execute(
            delete(self.model).where(
                self.model.project_id == project_id,
                self.model.user_id == user_id
            )
        )
