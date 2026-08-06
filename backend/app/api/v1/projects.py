"""
Project management endpoints.
"""

from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.uow import UnitOfWork
from app.domains.projects.service import ProjectService
from app.domains.projects.models import ProjectRole
from app.domains.projects.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberResponse

router = APIRouter()
logger = structlog.get_logger(__name__)

async def get_project_service(db: AsyncSession = Depends(get_db)) -> ProjectService:
    return ProjectService(UnitOfWork(db))


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.create_project(user_id, project_data)


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.get_user_projects(user_id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.get_project(str(project_id), user_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.update_project(str(project_id), user_id, project_data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> None:
    await service.delete_project(str(project_id), user_id)


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.list_project_members(str(project_id), user_id)


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: UUID,
    member_email: str,
    role: ProjectRole = ProjectRole.WORKER,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.add_project_member(str(project_id), user_id, member_email, role)


@router.patch("/{project_id}/members/{target_user_id}")
async def update_project_member_role(
    project_id: UUID,
    target_user_id: UUID,
    role: ProjectRole,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.update_project_member_role(str(project_id), user_id, str(target_user_id), role)


@router.delete("/{project_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: UUID,
    target_user_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> None:
    await service.remove_project_member(str(project_id), user_id, str(target_user_id))


@router.get("/{project_id}/dashboard")
async def get_project_dashboard(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    service: ProjectService = Depends(get_project_service)
) -> Any:
    return await service.get_project_dashboard(str(project_id), user_id)
