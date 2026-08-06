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



class CustomerProfileResponse(BaseModel):
    id: UUID
    customer_id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    platform_accounts: Dict[str, Any]
    customer_type: Optional[str]
    overall_sentiment: Optional[str]
    total_orders: int
    total_spent: float
    is_vip: bool
    ai_enabled: bool
    ai_settings: Dict[str, Any]
    tags: List[str]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Pagination
# ============================================================================
