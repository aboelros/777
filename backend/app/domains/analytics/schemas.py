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



class ReportGenerate(BaseModel):
    report_type: str  # sales, messages, performance
    start_date: datetime
    end_date: datetime
    filters: Optional[Dict[str, Any]] = {}



class ReportResponse(BaseModel):
    id: UUID
    project_id: UUID
    report_type: str
    payload: Dict[str, Any]
    summary: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    file_url: Optional[str]
    generated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Webhook Schemas
# ============================================================================


class DashboardStats(BaseModel):
    total_orders: int
    total_revenue: float
    total_messages: int
    ai_messages: int
    active_integrations: int
    response_rate: float
    avg_response_time: float
    period_start: datetime
    period_end: datetime




class UsageStats(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=(),
        from_attributes=True
    )
    
    project_id: UUID
    total_requests: int
    total_tokens: int
    estimated_cost: float
    usage_by_model: Dict[str, int]

