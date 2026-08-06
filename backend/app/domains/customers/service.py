from typing import List, Optional, Any, Dict
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select, func

from app.core.uow import UnitOfWork
from app.domains.customers.repository import CustomerProfileRepository
from app.domains.customers.models import CustomerProfile
from app.domains.projects.repository import ProjectRepository

class CustomerService:
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

    async def list_customers(self, project_id: str, user_id: str) -> List[CustomerProfile]:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = CustomerProfileRepository(uow.session)
            return await repo.get_by_project(proj_uuid)

    async def get_customer(self, project_id: str, profile_id: str, user_id: str) -> CustomerProfile:
        async with self.uow as uow:
            proj_uuid = UUID(project_id)
            user_uuid = UUID(user_id)
            await self._verify_project_access(proj_uuid, user_uuid)
            
            repo = CustomerProfileRepository(uow.session)
            customer = await repo.get(UUID(profile_id))
            if not customer or customer.project_id != proj_uuid:
                raise HTTPException(status_code=404, detail="Customer not found")
            return customer
