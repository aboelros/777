from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from enum import Enum

from app.domains.auth.models import UserRole
from app.domains.projects.models import ProjectRole
from app.domains.integrations.models import IntegrationStatus, IntegrationProvider as Provider, IntegrationProvider
from app.domains.messages.models import MessageDirection
from app.domains.billing.models import SubscriptionTier, SubscriptionStatus
from app.domains.orders.models import OrderStatus
from app.domains.ai.models import ModelTrainingStatus



class ProjectCreate(BaseModel):
    project_code: str = Field(..., min_length=3, max_length=50, description="Unique project identifier (e.g., 'PROJ-001', 'STORE-ABC')")
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    timezone: str = "UTC"
    settings: Dict[str, Any] = {}



class ProjectUpdate(BaseModel):
    project_code: Optional[str] = Field(None, min_length=3, max_length=50, description="Unique project identifier")
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    timezone: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None



class ProjectResponse(BaseModel):
    id: UUID
    owner_id: UUID
    owner_name: Optional[str] = None
    project_code: str
    name: str
    description: Optional[str] = None
    timezone: str = "UTC"
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    role: Optional[ProjectRole] = "owner"
    
    class Config:
        from_attributes = True


# ============================================================================
# Integration Schemas
# ============================================================================


class ProjectMemberResponse(BaseModel):
    user_id: UUID
    role: ProjectRole
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

