from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.domains.projects.models import ProjectMember, ProjectRole

async def get_project_member(
    project_id: UUID = Path(...),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> ProjectMember:
    """
    Dependency to verify a user is a member of the requested project.
    Returns the ProjectMember record.
    """
    stmt = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project."
        )
        
    return member

def require_project_role(allowed_roles: list[ProjectRole]):
    """
    Dependency factory to enforce RBAC within a project.
    """
    async def role_checker(member: ProjectMember = Depends(get_project_member)) -> ProjectMember:
        if member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of the following roles: {', '.join([r.value for r in allowed_roles])}."
            )
        return member
    return role_checker

from fastapi.security import APIKeyHeader
from app.domains.apps.models import DeveloperApp

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_developer_app(
    api_key: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_db)
) -> DeveloperApp:
    """
    Validates a DeveloperApp API Key.
    Used for Machine-to-Machine third-party API integration.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key."
        )
        
    stmt = select(DeveloperApp).where(
        DeveloperApp.api_key == api_key,
        DeveloperApp.is_active == True
    )
    result = await db.execute(stmt)
    app = result.scalar_one_or_none()
    
    if not app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or deactivated API Key."
        )
        
    return app
