"""
Project management endpoints.
"""

from typing import List, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import structlog

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.db.models import Project, ProjectRole
from app.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectMemberResponse

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new project/brand.
    
    Projects allow multi-tenant support where each user can manage multiple brands.
    Each project must have a unique project_code (e.g., 'PROJ-001', 'STORE-ABC').
    """
    try:
        # Check if project_code already exists
        result = await db.execute(
            select(Project).where(Project.project_code == project_data.project_code)
        )
        existing_project = result.scalar_one_or_none()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{project_data.project_code}' already exists. Please choose a different code."
            )
        
        new_project = Project(
            owner_id=UUID(user_id),
            project_code=project_data.project_code,
            name=project_data.name,
            description=project_data.description,
            timezone=project_data.timezone,
            settings=project_data.settings or {}
        )
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        logger.info(
            "Project created", 
            project_id=str(new_project.id),
            project_code=new_project.project_code,
            user_id=user_id
        )
        
        return new_project
        
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate project_code)
        raise
    except Exception as e:
        logger.error("Failed to create project", error=str(e), user_id=user_id)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List all projects the user has access to (owned + member).
    """
    from app.db.models import User, ProjectMember
    
    # 1. Get owned projects
    owned_result = await db.execute(
        select(Project, User.name)
        .join(User, Project.owner_id == User.id)
        .where(Project.owner_id == UUID(user_id))
        .order_by(Project.created_at.desc())
    )
    
    projects_list = []
    
    # Add owned projects with role='owner'
    for project, owner_name in owned_result.all():
        project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
        project_dict["owner_name"] = owner_name
        project_dict["role"] = ProjectRole.OWNER
        projects_list.append(project_dict)
        
    # 2. Get member projects
    member_result = await db.execute(
        select(Project, User.name, ProjectMember.role)
        .join(ProjectMember, Project.id == ProjectMember.project_id)
        .join(User, Project.owner_id == User.id)
        .where(ProjectMember.user_id == UUID(user_id))
        .order_by(Project.created_at.desc())
    )
    
    # Add member projects with their specific role
    for project, owner_name, role in member_result.all():
        # Avoid duplicates if for some reason someone is both owner and member (shouldn't happen but safe to check)
        if not any(p["id"] == project.id for p in projects_list):
            project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
            project_dict["owner_name"] = owner_name
            project_dict["role"] = role
            projects_list.append(project_dict)
    
    # Sort combined list by created_at desc
    projects_list.sort(key=lambda x: x.get("created_at") or datetime.min, reverse=True)
    
    return projects_list


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific project by ID.
    Checks ownership OR membership.
    """
    from app.db.models import User, ProjectMember
    
    # Check ownership
    result = await db.execute(
        select(Project, User.name)
        .join(User, Project.owner_id == User.id)
        .where(Project.id == project_id)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
        
    project, owner_name = row
    
    # Determine Access & Role
    user_role = None
    
    if project.owner_id == UUID(user_id):
        user_role = ProjectRole.OWNER
    else:
        # Check membership
        member_result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == UUID(user_id)
            )
        )
        member = member_result.scalar_one_or_none()
        if member:
            user_role = member.role
            
    if not user_role:
        raise HTTPException(status_code=403, detail="Access denied")
    
    project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
    project_dict["owner_name"] = owner_name
    project_dict["role"] = user_role
    
    return project_dict


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Update a project's information.
    
    If updating project_code, it must be unique across all projects.
    """
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    update_data = project_data.dict(exclude_unset=True)
    
    # If updating project_code, check for uniqueness
    if "project_code" in update_data and update_data["project_code"] != project.project_code:
        result = await db.execute(
            select(Project).where(Project.project_code == update_data["project_code"])
        )
        existing_project = result.scalar_one_or_none()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{update_data['project_code']}' already exists. Please choose a different code."
            )
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    from app.db.models import User
    # Get owner name for response
    result = await db.execute(select(User.name).where(User.id == project.owner_id))
    owner_name = result.scalar_one_or_none()
    
    project_dict = {c.name: getattr(project, c.name) for c in project.__table__.columns}
    project_dict["owner_name"] = owner_name
    
    return project_dict


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a project.
    
    WARNING: This will cascade delete all associated data:
    - Integrations
    - Orders
    - Messages
    - Reports
    - Training data
    """
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == UUID(user_id))
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()
    
    logger.info("Project deleted", project_id=str(project_id), user_id=user_id)
    
    return None


async def verify_project_access(
    project_id: UUID, 
    user_id: str, 
    db: AsyncSession,
    required_roles: List[ProjectRole] = None
) -> Project:
    """
    Verify that a user has access to a project with required roles.
    If required_roles is None, any member role is allowed.
    The Project Owner (Project.owner_id) always has full access.
    """
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
    from app.db.models import ProjectMember
    member_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == UUID(user_id)
        )
    )
    member = member_result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied"
        )
        
    # 3. Check role requirement
    if required_roles and member.role not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Action requires one of these roles: {[r.value for r in required_roles]}"
        )
    
    # Return the project associated with the member
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one()


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List all members of a project."""
    await verify_project_access(project_id, user_id, db)
    
    from app.db.models import ProjectMember, User
    result = await db.execute(
        select(ProjectMember, User.name, User.email)
        .join(User, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
    )
    members = []
    for row in result.all():
        pm, name, email = row
        members.append({
            "user_id": pm.user_id,
            "role": pm.role,
            "name": name,
            "email": email
        })
    
    return members


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: UUID,
    member_email: str,
    role: ProjectRole = ProjectRole.WORKER,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Add a user to the project with a specific role."""
    # Only Owner or Moderator can add members
    await verify_project_access(project_id, user_id, db, required_roles=[ProjectRole.OWNER, ProjectRole.MODERATOR])
    
    from app.db.models import User, ProjectMember
    # Find user by email
    user_result = await db.execute(select(User).where(User.email == member_email))
    target_user = user_result.scalar_one_or_none()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if already a member
    existing = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a project member")
        
    new_member = ProjectMember(
        project_id=project_id,
        user_id=target_user.id,
        role=role
    )
    db.add(new_member)
    await db.commit()
    
    return {"status": "success", "message": f"Added {member_email} as {role.value}"}


@router.patch("/{project_id}/members/{target_user_id}")
async def update_project_member_role(
    project_id: UUID,
    target_user_id: UUID,
    role: ProjectRole,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a member's role in the project."""
    # Only Owner can change roles
    await verify_project_access(project_id, user_id, db, required_roles=[ProjectRole.OWNER])
    
    from app.db.models import ProjectMember
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id
        )
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Member not found")
        
    pm.role = role
    await db.commit()
    return {"status": "success", "message": f"Updated role to {role.value}"}


@router.delete("/{project_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_project_member(
    project_id: UUID,
    target_user_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Remove a member from the project."""
    # Only Owner or Moderator can remove members
    await verify_project_access(project_id, user_id, db, required_roles=[ProjectRole.OWNER, ProjectRole.MODERATOR])
    
    from app.db.models import ProjectMember
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == target_user_id
        )
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Member not found")
        
    await db.delete(pm)
    await db.commit()
    return None


@router.get("/{project_id}/dashboard")
async def get_project_dashboard(
    project_id: UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get dashboard data for a project with REAL statistics from database.
    
    Returns:
        - Order statistics (count, revenue, pending)
        - Message statistics (total, unread, by platform)
        - Customer count
        - Integration status
        - Usage statistics vs limits
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func
    from app.db.models import Message, Order, Integration, CustomerProfile, MessageDirection
    from app.services.usage_tracker import UsageTracker
    
    # Verify access
    await verify_project_access(project_id, user_id, db)
    
    # Get date ranges
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # === ORDER STATISTICS ===
    # Total orders
    result = await db.execute(
        select(func.count(Order.id))
        .where(Order.project_id == project_id)
    )
    total_orders = result.scalar() or 0
    
    # Orders this month
    result = await db.execute(
        select(func.count(Order.id))
        .where(Order.project_id == project_id)
        .where(Order.created_at >= month_start)
    )
    orders_this_month = result.scalar() or 0
    
    # Pending orders
    result = await db.execute(
        select(func.count(Order.id))
        .where(Order.project_id == project_id)
        .where(Order.status.in_(["pending", "processing"]))
    )
    pending_orders = result.scalar() or 0
    
    # Total revenue
    result = await db.execute(
        select(func.sum(Order.total))
        .where(Order.project_id == project_id)
    )
    total_revenue = result.scalar() or 0.0
    
    # Revenue this month
    result = await db.execute(
        select(func.sum(Order.total))
        .where(Order.project_id == project_id)
        .where(Order.created_at >= month_start)
    )
    revenue_this_month = result.scalar() or 0.0
    
    # === MESSAGE STATISTICS ===
    # Total messages
    result = await db.execute(
        select(func.count(Message.id))
        .where(Message.project_id == project_id)
    )
    total_messages = result.scalar() or 0
    
    # Unread messages
    result = await db.execute(
        select(func.count(Message.id))
        .where(Message.project_id == project_id)
        .where(Message.direction == MessageDirection.INBOUND)
        .where(Message.is_read == False)
    )
    unread_messages = result.scalar() or 0
    
    # Messages this month
    result = await db.execute(
        select(func.count(Message.id))
        .where(Message.project_id == project_id)
        .where(Message.created_at >= month_start)
    )
    messages_this_month = result.scalar() or 0
    
    # === CUSTOMER STATISTICS ===
    result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(CustomerProfile.project_id == project_id)
    )
    total_customers = result.scalar() or 0
    
    # === INTEGRATION STATUS ===
    result = await db.execute(
        select(Integration)
        .where(Integration.project_id == project_id)
    )
    integrations = result.scalars().all()
    
    integration_status = {
        "total": len(integrations),
        "connected": sum(1 for i in integrations if i.status == "connected"),
        "by_provider": {}
    }
    
    for integration in integrations:
        provider = integration.provider
        if provider not in integration_status["by_provider"]:
            integration_status["by_provider"][provider] = {
                "status": integration.status.value,
                "name": integration.name
            }
    
    # === USAGE STATISTICS ===
    tracker = UsageTracker(db)
    usage_limits = await tracker.check_usage_limits(project_id, UUID(user_id))
    
    return {
        "orders": {
            "total": total_orders,
            "this_month": orders_this_month,
            "pending": pending_orders,
            "revenue": {
                "total": round(total_revenue, 2),
                "this_month": round(revenue_this_month, 2),
                "currency": "USD"
            }
        },
        "messages": {
            "total": total_messages,
            "this_month": messages_this_month,
            "unread": unread_messages
        },
        "customers": {
            "total": total_customers
        },
        "integrations": integration_status,
        "usage": usage_limits
    }
