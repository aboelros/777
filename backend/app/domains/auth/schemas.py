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



class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: Optional[str] = None
    
    @validator("password")
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v



class UserLogin(BaseModel):
    email: str  # Allow any string format for login (including .local domains)
    password: str



class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int



class RefreshTokenRequest(BaseModel):
    refresh_token: str



class UserResponse(BaseModel):
    id: UUID
    email: str  # Allow any email format (including .local domains)
    name: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Project Schemas
# ============================================================================
