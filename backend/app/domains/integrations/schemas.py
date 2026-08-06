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
