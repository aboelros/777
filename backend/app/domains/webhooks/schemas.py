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



class ShopifyWebhook(BaseModel):
    id: int
    email: Optional[str]
    created_at: str
    updated_at: str
    total_price: str
    currency: str
    financial_status: str
    fulfillment_status: Optional[str]
    customer: Dict[str, Any]
    line_items: List[Dict[str, Any]]



class WhatsAppWebhook(BaseModel):
    object: str
    entry: List[Dict[str, Any]]


# ============================================================================
# Analytics Schemas
# ============================================================================
