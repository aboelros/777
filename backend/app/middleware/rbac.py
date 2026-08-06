"""
Role-Based Access Control (RBAC) Middleware
Enforces permissions and data isolation based on user roles.
"""
from typing import List, Optional, Callable
from fastapi import HTTPException, Request, Depends
from functools import wraps
from sqlalchemy import select
from app.domains.auth.models import User, UserRole
from app.domains.projects.models import ProjectRole
from app.core.database import get_db, AsyncSession
import structlog

logger = structlog.get_logger(__name__)


class RBACMiddleware:
    """
    Middleware for role-based access control.
    """
    
    # Permission matrix: resource -> action -> allowed roles
    PERMISSIONS = {
        'projects': {
            'create': [UserRole.ADMIN],
            'read': [UserRole.ADMIN, UserRole.USER],
            'update': [UserRole.ADMIN],
            'delete': [UserRole.ADMIN]
        },
        'users': {
            'create': [UserRole.ADMIN],
            'read': [UserRole.ADMIN],
            'update': [UserRole.ADMIN],
            'delete': [UserRole.ADMIN]
        },
        'messages': {
            'create': [UserRole.ADMIN, UserRole.USER],
            'read': [UserRole.ADMIN, UserRole.USER],
            'update': [UserRole.ADMIN, UserRole.USER],
            'delete': [UserRole.ADMIN]
        },
        'orders': {
            'create': [UserRole.ADMIN, UserRole.USER],
            'read': [UserRole.ADMIN, UserRole.USER],
            'update': [UserRole.ADMIN, UserRole.USER],
            'delete': [UserRole.ADMIN]
        },
        'ai_settings': {
            'create': [UserRole.ADMIN],
            'read': [UserRole.ADMIN, UserRole.USER],
            'update': [UserRole.ADMIN],
            'delete': [UserRole.ADMIN]
        }
    }
    
    @staticmethod
    async def check_permission(
        user: User,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user has permission for an action on a resource.
        
        Args:
            user: User object
            resource: Resource name (e.g., 'projects', 'messages')
            action: Action name (e.g., 'read', 'update')
            
        Returns:
            True if user has permission, False otherwise
        """
        if resource not in RBACMiddleware.PERMISSIONS:
            logger.warning(f"Unknown resource: {resource}")
            return False
        
        if action not in RBACMiddleware.PERMISSIONS[resource]:
            logger.warning(f"Unknown action: {action} for resource: {resource}")
            return False
        
        allowed_roles = RBACMiddleware.PERMISSIONS[resource][action]
        return user.role in allowed_roles
    
    @staticmethod
    async def check_project_access(
        user_id: int,
        project_id: int,
        db: AsyncSession,
        required_role: Optional[ProjectRole] = None
    ) -> bool:
        """
        Check if user has access to a specific project.
        
        Args:
            user_id: User ID
            project_id: Project ID
            db: Database session
            required_role: Required project role (optional)
            
        Returns:
            True if user has access, False otherwise
        """
        # Check if user is project owner or member
        from app.domains.projects.models import Project, ProjectMember
        
        # Check if user owns the project
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.user_id == user_id
            )
        )
        project = result.scalar_one_or_none()
        
        if project:
            return True  # Owner has full access
        
        # Check if user is a project member
        result = await db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            return False
        
        # If specific role required, check it
        if required_role:
            return membership.role == required_role or membership.role == ProjectRole.OWNER
        
        return True


def require_permission(resource: str, action: str):
    """
    Decorator to require specific permission for an endpoint.
    
    Usage:
        @router.get("/projects")
        @require_permission('projects', 'read')
        async def get_projects(user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs (injected by get_current_user dependency)
            user = kwargs.get('user') or kwargs.get('current_user')
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Authentication required"
                )
            
            # Check permission
            has_permission = await RBACMiddleware.check_permission(
                user, resource, action
            )
            
            if not has_permission:
                logger.warning(
                    "Permission denied",
                    user_id=user.id,
                    resource=resource,
                    action=action
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"No permission for {action} on {resource}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_project_access(required_role: Optional[ProjectRole] = None):
    """
    Decorator to require project access for an endpoint.
    
    Usage:
        @router.get("/projects/{project_id}/messages")
        @require_project_access()
        async def get_messages(
            project_id: int,
            user: User = Depends(get_current_user),
            db: AsyncSession = Depends(get_db)
        ):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('user') or kwargs.get('current_user')
            db = kwargs.get('db')
            project_id = kwargs.get('project_id')
            
            if not user:
                raise HTTPException(401, "Authentication required")
            
            if not db:
                raise HTTPException(500, "Database session not available")
            
            if not project_id:
                raise HTTPException(400, "Project ID required")
            
            # Check project access
            has_access = await RBACMiddleware.check_project_access(
                user.id, project_id, db, required_role
            )
            
            if not has_access:
                logger.warning(
                    "Project access denied",
                    user_id=user.id,
                    project_id=project_id,
                    required_role=required_role
                )
                raise HTTPException(
                    status_code=403,
                    detail="Access denied to this project"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


class DataIsolation:
    """
    Ensures data isolation between projects and users.
    """
    
    @staticmethod
    def filter_by_project(query, project_id: int, model):
        """
        Add project filter to query for data isolation.
        
        Args:
            query: SQLAlchemy query
            project_id: Project ID to filter by
            model: Model class
            
        Returns:
            Filtered query
        """
        if hasattr(model, 'project_id'):
            return query.where(model.project_id == project_id)
        return query
    
    @staticmethod
    def filter_by_user(query, user_id: int, model):
        """
        Add user filter to query for data isolation.
        
        Args:
            query: SQLAlchemy query
            user_id: User ID to filter by
            model: Model class
            
        Returns:
            Filtered query
        """
        if hasattr(model, 'user_id'):
            return query.where(model.user_id == user_id)
        return query
