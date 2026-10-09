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



class OrderCreate(BaseModel):
    external_id: str
    provider: str
    customer_id: Optional[UUID] = None
    status: Optional[str] = "pending"
    customer: Dict[str, Any] = {}
    items: List[Dict[str, Any]] = []
    total: Optional[float] = None
    currency: str = "USD"
    extra_data: Dict[str, Any] = Field(default_factory=dict, alias="metadata")

    tags: List[str] = []
    order_date: Optional[datetime] = None



class OrderUpdate(BaseModel):
    status: Optional[str] = None
    customer: Optional[Dict[str, Any]] = None
    items: Optional[List[Dict[str, Any]]] = None
    total: Optional[float] = None
    extra_data: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")

    tags: Optional[List[str]] = None
    fulfilled_date: Optional[datetime] = None



class OrderResponse(BaseModel):
    id: UUID
    project_id: UUID
    external_id: str
    provider: str
    status: Optional[str]
    customer: Dict[str, Any]
    items: List[Dict[str, Any]]
    total: Optional[float]
    currency: str
    extra_data: Dict[str, Any] = Field(default_factory=dict, validation_alias="extra_data", serialization_alias="metadata")
    tags: List[str]
    order_date: Optional[datetime]
    fulfilled_date: Optional[datetime]
    updated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Message Schemas
# ============================================================================
