"""
Pydantic schemas for request/response validation and serialization.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ProjectRole(str, Enum):
    OWNER = "owner"
    MODERATOR = "moderator"
    WORKER = "worker"


class IntegrationStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class MessageDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class Provider(str, Enum):
    SHOPIFY = "shopify"
    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TELEGRAM = "telegram"
    SMS = "sms"
    TIKTOK = "tiktok"
    DISCORD = "discord"


# ============================================================================
# Authentication Schemas
# ============================================================================

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
    description: Optional[str]
    timezone: str
    settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    role: Optional[ProjectRole] = "owner"
    
    class Config:
        from_attributes = True


# ============================================================================
# Integration Schemas
# ============================================================================

class IntegrationConnect(BaseModel):
    provider: Provider
    config: Dict[str, Any]  # API keys, tokens, etc.


class TelegramCommandSettings(BaseModel):
    enabled: bool = True


class TelegramSettings(BaseModel):
    auto_reply_enabled: Optional[bool] = None
    response_delay_seconds: Optional[int] = Field(default=None, ge=0, le=3600)
    welcome_message: Optional[str] = None
    fallback_message: Optional[str] = None
    commands: Optional[Dict[str, TelegramCommandSettings]] = None


class WhatsAppSettings(BaseModel):
    business_account_id: Optional[str] = None
    phone_number_id: Optional[str] = None
    access_token: Optional[str] = None
    auto_reply_enabled: Optional[bool] = None
    default_response: Optional[str] = None
    keyword_triggers: Optional[List[str]] = None


class InstagramSettings(BaseModel):
    business_account_id: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    auto_reply_enabled: Optional[bool] = None
    auto_dm_keywords: Optional[List[str]] = None
    comment_reply_enabled: Optional[bool] = None
    default_response: Optional[str] = None


class FacebookSettings(BaseModel):
    page_id: Optional[str] = None
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    auto_reply_enabled: Optional[bool] = None
    default_response: Optional[str] = None
    keyword_triggers: Optional[List[str]] = None


class DiscordSettings(BaseModel):
    bot_token: Optional[str] = None
    guild_id: Optional[str] = None
    auto_reply_enabled: Optional[bool] = None
    monitor_channels: Optional[List[str]] = None


class TikTokSettings(BaseModel):
    shop_id: Optional[str] = None
    access_token: Optional[str] = None
    app_key: Optional[str] = None
    app_secret: Optional[str] = None


class IntegrationConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    telegram_settings: Optional[TelegramSettings] = None
    whatsapp_settings: Optional[WhatsAppSettings] = None
    instagram_settings: Optional[InstagramSettings] = None
    facebook_settings: Optional[FacebookSettings] = None
    discord_settings: Optional[DiscordSettings] = None
    tiktok_settings: Optional[TikTokSettings] = None
    whatsapp_linked_device_enabled: Optional[bool] = None
    phone_number: Optional[str] = None
    shop_id: Optional[str] = None  # Direct field support


class IntegrationUpdate(BaseModel):
    config: Optional[IntegrationConfigUpdate] = None
    status: Optional[IntegrationStatus] = None


class IntegrationResponse(BaseModel):
    """Integration response schema."""
    id: UUID
    project_id: UUID
    provider: str
    status: IntegrationStatus
    config: Dict[str, Any]  # Sensitive data should be masked
    extra_data: Dict[str, Any] = {}
    last_sync: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# Order Schemas
# ============================================================================

class OrderCreate(BaseModel):
    external_id: str
    provider: str
    customer_id: Optional[UUID] = None
    status: Optional[str] = "pending"
    customer: Dict[str, Any] = {}
    items: List[Dict[str, Any]] = []
    total: Optional[float] = None
    currency: str = "USD"
    metadata: Dict[str, Any] = {}
    tags: List[str] = []
    order_date: Optional[datetime] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    customer: Optional[Dict[str, Any]] = None
    items: Optional[List[Dict[str, Any]]] = None
    total: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
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
    metadata: Dict[str, Any]
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

class AssistantQuery(BaseModel):
    project_id: UUID
    message: str
    context: Optional[Dict[str, Any]] = {}
    order_id: Optional[UUID] = None
    use_function_calling: bool = True


class FunctionCall(BaseModel):
    name: str
    parameters: Dict[str, Any]


class AssistantResponse(BaseModel):
    reply: str
    function_calls: Optional[List[FunctionCall]] = []
    tokens_used: int
    cost: float
    model: str
    confidence: Optional[float] = None


class GenerateReplyRequest(BaseModel):
    project_id: UUID
    order_id: UUID
    customer_message: str


class ModelTrainRequest(BaseModel):
    project_id: UUID
    dataset_location: Optional[str] = None
    training_params: Dict[str, Any] = {}


class ModelTrainResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    gemini_model: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeBaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source_type: str = "text"
    source_url: Optional[str] = None
    is_active: bool = True
    tags: List[str] = []
    metadata_info: Dict[str, Any] = {}


class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata_info: Optional[Dict[str, Any]] = None


class KnowledgeBaseResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    content: str
    source_type: str
    source_url: Optional[str]
    is_active: bool
    tags: List[str]
    metadata_info: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Report Schemas
# ============================================================================

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


class ProjectMemberResponse(BaseModel):
    user_id: UUID
    role: ProjectRole
    name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True


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

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
    
    @validator("pages", pre=True, always=True)
    def calculate_pages(cls, v, values):
        if "total" in values and "page_size" in values:
            return (values["total"] + values["page_size"] - 1) // values["page_size"]
        return v


# ============================================================================
# Error Response
# ============================================================================

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# End of schemas.py




