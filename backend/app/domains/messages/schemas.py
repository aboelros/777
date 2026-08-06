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



class MessageSend(BaseModel):
    recipient: Dict[str, Any]  # phone, username, etc.
    content: str
    provider: Provider
    content_type: str = "text"
    attachments: List[Dict[str, Any]] = []
    order_id: Optional[UUID] = None



class MessageResponse(BaseModel):
    id: UUID
    project_id: UUID
    customer_id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    direction: MessageDirection
    platform: str
    provider: str
    external_id: Optional[str] = None
    content: str
    content_type: str = "text"
    attachments: List[Dict[str, Any]] = []
    sender: Dict[str, Any] = {}
    recipient: Dict[str, Any] = {}
    ai_generated: bool = False
    ai_model: Optional[str] = None
    ai_prompt_tokens: Optional[int] = None
    ai_completion_tokens: Optional[int] = None
    ai_cost: Optional[float] = None
    extra_data: Dict[str, Any] = {}
    is_read: bool = False
    status: str = "sent"
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True



class ConversationSummary(BaseModel):
    id: str  # Conversation ID (usually message-ID or customer-ID)
    channel: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_avatar: Optional[str] = None
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    unread_count: int = 0
    total_messages: int = 0
    ai_messages: int = 0
    ai_enabled: bool = False
    recipient: Dict[str, Any] = {}
    profile_id: Optional[str] = None # UUID as string
    overall_sentiment: Optional[str] = None
    is_vip: bool = False



class ConversationMessage(BaseModel):
    id: UUID
    direction: MessageDirection
    provider: str
    content: Optional[str] = None
    content_type: str = "text"
    created_at: datetime
    ai_generated: bool = False
    status: Optional[str] = None
    is_read: bool = False
    sender: Dict[str, Any] = {}
    recipient: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    attachments: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# AI Assistant Schemas
# ============================================================================
