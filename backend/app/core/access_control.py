"""
Centralized project access verification utility.
This ensures consistent security across all API endpoints.
"""

from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

logger = structlog.get_logger(__name__)


async def verify_project_access(
    project_id: UUID,
    user_id: str,
    db: AsyncSession,
    required_roles: list = None
):
    """
    Verify that a user has access to a specific project.
    
    This function ensures data isolation between user accounts by checking
    that the project belongs to the requesting user OR if the user is a member.
    
    Args:
        project_id: UUID of the project to access
        user_id: UUID of the user (as string) making the request
        db: Database session
        required_roles: Optional list of ProjectRoles required for access
        
    Returns:
        Project: The project object if access is granted
        
    Raises:
        HTTPException: 404 if project not found or access denied
        HTTPException: 403 if user lacks required role
    """
    from app.domains.projects.models import Project, ProjectMember
    
    try:
        # 1. Check if user is the global owner of the project
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.owner_id == UUID(user_id)
            )
        )
        project = result.scalar_one_or_none()
        
        if project:
            return project
            
        # 2. Check ProjectMember table
        member_result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == UUID(user_id)
            )
        )
        member = member_result.scalar_one_or_none()
        
        if not member:
            logger.warning(
                "Project access denied",
                project_id=str(project_id),
                user_id=user_id,
                reason="not_found_or_not_member"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or access denied"
            )
            
        # 3. Check role requirement
        if required_roles and member.role not in required_roles:
            logger.warning(
                "Project role denied",
                project_id=str(project_id),
                user_id=user_id,
                role=member.role,
                required=required_roles
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of these roles: {[r.value for r in required_roles]}"
            )
        
        # Return the project associated with the member
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one()
        
        return project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Error verifying project access",
            project_id=str(project_id),
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify project access"
        )


async def verify_resource_access(
    resource_id: UUID,
    resource_type: str,
    user_id: str,
    db: AsyncSession
):
    """
    Verify that a user has access to a specific resource (message, order, etc.)
    by checking if the resource's project belongs to the user.
    
    Args:
        resource_id: UUID of the resource (message, order, integration, etc.)
        resource_type: Type of resource ('message', 'order', 'integration', etc.)
        user_id: UUID of the user (as string) making the request
        db: Database session
        
    Returns:
        tuple: (resource, project) if access is granted
        
    Raises:
        HTTPException: 404 if resource not found or user doesn't own it
    """
    from app.domains.projects.models import Project
    from app.domains.messages.models import Message
    from app.domains.orders.models import Order
    from app.domains.integrations.models import Integration
    from app.domains.customers.models import CustomerProfile
    
    # Map resource types to models
    model_map = {
        'message': Message,
        'order': Order,
        'integration': Integration,
        'customer': CustomerProfile
    }
    
    if resource_type not in model_map:
        raise ValueError(f"Unknown resource type: {resource_type}")
    
    model = model_map[resource_type]
    
    try:
        # Get the resource
        result = await db.execute(
            select(model).where(model.id == resource_id)
        )
        resource = result.scalar_one_or_none()
        
        if not resource:
            logger.warning(
                f"{resource_type.capitalize()} not found",
                resource_id=str(resource_id),
                user_id=user_id
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{resource_type.capitalize()} not found"
            )
        
        # Verify project ownership
        project = await verify_project_access(
            resource.project_id,
            user_id,
            db
        )
        
        return resource, project
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error verifying {resource_type} access",
            resource_id=str(resource_id),
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify {resource_type} access"
        )


async def list_user_projects(user_id: str, db: AsyncSession):
    """
    List all projects owned by a user.
    
    Args:
        user_id: UUID of the user (as string)
        db: Database session
        
    Returns:
        list: List of Project objects owned by the user
    """
    from app.domains.projects.models import Project
    
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == UUID(user_id))
        .where(Project.is_active == True)
        .order_by(Project.created_at.desc())
    )
    
    return result.scalars().all()


async def count_user_projects(user_id: str, db: AsyncSession) -> int:
    """
    Count total projects owned by a user.
    
    Args:
        user_id: UUID of the user (as string)
        db: Database session
        
    Returns:
        int: Number of projects owned by the user
    """
    from app.domains.projects.models import Project
    from sqlalchemy import func
    
    result = await db.execute(
        select(func.count(Project.id))
        .where(Project.owner_id == UUID(user_id))
        .where(Project.is_active == True)
    )
    
    return result.scalar() or 0
