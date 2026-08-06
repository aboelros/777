from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from enum import Enum


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




