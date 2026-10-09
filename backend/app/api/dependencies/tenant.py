from uuid import UUID
from fastapi import Depends, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.core.context import TenantContext
from app.domains.projects.models import Project, ProjectMember, ProjectRole

async def resolve_tenant_context(
    project_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> TenantContext:
    """
    Enforces project authorization and returns a trusted TenantContext.
    
    This replaces raw project_id usage and guarantees that the caller is an active
    member or owner of the project before any business logic executes.
    """
    # Check if user is the global owner of the project
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == user_id
        )
    )
    project = result.scalar_one_or_none()
    
    if project:
        # User is the owner
        return TenantContext(
            user_id=user_id,
            project_id=project_id,
            role=ProjectRole.OWNER.value,
            permissions=frozenset(["*"]),
            membership_id=None
        )
        
    # Check ProjectMember table
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        # 404 instead of 403 to prevent project enumeration by attackers
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
        
    return TenantContext(
        user_id=user_id,
        project_id=project_id,
        role=member.role.value,
        permissions=frozenset([]),  # Extended in future RBAC phase
        membership_id=member.id
    )


async def get_tenant_context(
    project_id: UUID = Path(..., description="The ID of the project"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> TenantContext:
    """FastAPI path-based dependency wrapping resolve_tenant_context."""
    return await resolve_tenant_context(project_id, UUID(user_id), db)
