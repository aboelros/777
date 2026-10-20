"""
Pydantic schemas and data validation models for administrative API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.auth.models import UserRole


class AdminUserCreate(BaseModel):
    """Payload for administrative user creation."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True


class AdminUserUpdate(BaseModel):
    """Payload for updating an existing user account."""
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    """Payload for resetting a user account password."""
    new_password: str = Field(..., min_length=8, max_length=100)


class UserListItem(BaseModel):
    """Response model for user listing."""
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionOverrideRequest(BaseModel):
    """Payload for overriding a user's subscription tier and resource quotas."""
    tier: Optional[str] = None
    limits: Optional[Dict[str, int]] = None


class PlatformSettingsUpdate(BaseModel):
    """Payload for updating platform settings."""
    maintenance_mode: Optional[bool] = None
    user_registration_enabled: Optional[bool] = None
    default_free_messages: Optional[int] = None
    default_free_orders: Optional[int] = None
    ai_primary_model: Optional[str] = None
    ai_temperature: Optional[float] = None
    system_announcement: Optional[str] = None


class ProjectStatusUpdate(BaseModel):
    """Payload for toggling project active status."""
    is_active: bool
