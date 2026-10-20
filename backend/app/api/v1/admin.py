"""
Administrative API endpoints for platform management, user administration,
fleet oversight, billing overrides, AI telemetry, and system diagnostics.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, get_auth_db
from app.core.security import get_password_hash, require_role
from app.domains.auth.models import User
from app.services.admin_service import AdminService
from app.services.admin_telemetry_service import AdminTelemetryService
from app.api.v1.admin_schemas import (
    AdminUserCreate, AdminUserUpdate, ResetPasswordRequest,
    UserListItem, SubscriptionOverrideRequest, PlatformSettingsUpdate,
    ProjectStatusUpdate
)

router = APIRouter(dependencies=[Depends(require_role("admin"))])


@router.get("/dashboard")
async def get_dashboard_metrics(days: int = Query(30, ge=1, le=90), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve high-level platform KPI metrics."""
    return await AdminService.get_dashboard_metrics(db, days)


@router.get("/health")
async def get_system_health(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve real-time health diagnostics across database, cache, and AI engine."""
    return await AdminService.get_system_health(db)


@router.get("/users", response_model=List[UserListItem])
async def list_users(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_auth_db),
) -> Any:
    """List and search platform users."""
    query = select(User)
    if q:
        like = f"%{q.lower()}%"
        query = query.where((User.email.ilike(like)) | (User.name.ilike(like)))
    query = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/users", response_model=UserListItem, status_code=status.HTTP_201_CREATED)
async def create_user(payload: AdminUserCreate, db: AsyncSession = Depends(get_auth_db)) -> Any:
    """Create a new platform user."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already exists")
    user = User(
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        name=payload.name,
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    AdminTelemetryService.record_audit_action("CREATE_USER", "admin", f"Created user {user.email}")
    return user


@router.patch("/users/{user_id}", response_model=UserListItem)
async def update_user(user_id: UUID, payload: AdminUserUpdate, db: AsyncSession = Depends(get_auth_db)) -> Any:
    """Update user account status or permissions."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        user.name = payload.name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    await db.commit()
    await db.refresh(user)
    AdminTelemetryService.record_audit_action("UPDATE_USER", "admin", f"Updated user {user.email}")
    return user


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(user_id: UUID, payload: ResetPasswordRequest, db: AsyncSession = Depends(get_auth_db)) -> None:
    """Reset a user's password."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    AdminTelemetryService.record_audit_action("RESET_PASSWORD", "admin", f"Reset password for {user.email}")


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_auth_db)) -> None:
    """Deactivate or remove a user account."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    await db.commit()
    AdminTelemetryService.record_audit_action("DEACTIVATE_USER", "admin", f"Deactivated user {user.email}")


@router.get("/projects")
async def list_projects(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List tenant store fleet projects."""
    return await AdminService.list_projects(db, q=q, page=page, page_size=page_size)


@router.patch("/projects/{project_id}")
async def update_project(project_id: UUID, payload: ProjectStatusUpdate, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Toggle project fleet tenant status."""
    success = await AdminService.update_project_status(db, project_id, payload.is_active)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "project_id": str(project_id), "is_active": payload.is_active}


@router.get("/billing/subscriptions")
async def list_subscriptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List all user subscriptions and quotas."""
    return await AdminService.list_subscriptions(db, page=page, page_size=page_size)


@router.patch("/billing/subscriptions/{user_id}")
async def override_subscription(
    user_id: UUID, payload: SubscriptionOverrideRequest, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Override a user's subscription tier and resource limits."""
    result = await AdminService.override_subscription(db, user_id, payload.tier, payload.limits)
    if not result:
        raise HTTPException(status_code=404, detail="Subscription record not found")
    AdminTelemetryService.record_audit_action("OVERRIDE_SUBSCRIPTION", "admin", f"Overrode limits for {user_id}")
    return result


@router.get("/ai/telemetry")
async def get_ai_telemetry(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retrieve AI model usage and performance metrics."""
    return await AdminTelemetryService.get_ai_telemetry(db)


@router.get("/webhooks/logs")
async def list_webhook_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """List recent webhook event deliveries."""
    return await AdminTelemetryService.list_webhook_logs(db, page, page_size, status_filter)


@router.post("/webhooks/logs/{delivery_id}/retry")
async def retry_webhook(delivery_id: UUID, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Retry a failed webhook delivery attempt."""
    success = await AdminTelemetryService.retry_webhook_delivery(db, delivery_id)
    if not success:
        raise HTTPException(status_code=404, detail="Webhook delivery not found")
    return {"success": True, "delivery_id": str(delivery_id), "status": "pending"}


@router.get("/system/audit-logs")
async def get_audit_logs(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    """Fetch administrative action audit logs."""
    return AdminTelemetryService.get_audit_logs(page, page_size)


@router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    """Fetch global platform settings."""
    return AdminTelemetryService.get_settings()


@router.patch("/settings")
async def update_settings(payload: PlatformSettingsUpdate) -> Dict[str, Any]:
    """Update global platform settings."""
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    return AdminTelemetryService.update_settings(updates, admin_email="admin")


@router.get("/usage/summary")
async def usage_summary(days: int = Query(7, ge=1, le=90), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Legacy usage summary endpoint."""
    return await AdminService.get_dashboard_metrics(db, days)
