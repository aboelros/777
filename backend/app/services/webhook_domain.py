from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class EventType(str, Enum):
    # Messaging
    MESSAGE_CREATED = "message.created"
    MESSAGE_STATUS_UPDATED = "message.status.updated"
    MESSAGE_READ = "message.read"
    MESSAGE_DELIVERED = "message.delivered"
    
    # Social
    COMMENT_CREATED = "comment.created"
    POST_CREATED = "post.created"
    
    # Commerce
    ORDER_CREATED = "order.created"
    ORDER_UPDATED = "order.updated"
    CUSTOMER_CREATED = "customer.created"
    CART_UPDATED = "cart.updated"
    
    # System
    CONNECTION_UPDATED = "connection.updated"
    UNKNOWN = "unknown"

class WebhookEvent(BaseModel):
    """
    Unified Internal Event Model.
    Everything from the outside world becomes this.
    """
    event_id: str
    event_type: EventType
    timestamp: datetime
    
    # Routing Info
    platform: str  # meta, telegram, shopify, tiktok
    channel: str   # whatsapp, instagram, facebook, store
    project_id: Optional[UUID] = None  # Resolved tenant ID
    
    # The Actor (Who did it?)
    sender_id: str
    sender_name: Optional[str] = None
    
    # The Content (What happened?)
    payload: Dict[str, Any]  # Normalized payload (text, media, order details)
    raw_data: Dict[str, Any] # Original payload for debugging
    
    class Config:
        use_enum_values = True

class NormalizedPayload(BaseModel):
    """Standardized payload structure for different event types."""
    pass

class MessagePayload(NormalizedPayload):
    text: Optional[str] = None
    media: Optional[List[Dict[str, Any]]] = None
    is_echo: bool = False
    metadata: Dict[str, Any] = {}

class OrderPayload(NormalizedPayload):
    order_id: str
    amount: float
    currency: str
    status: str
    items: List[Dict[str, Any]]
    customer: Dict[str, Any]

class NormalizedMessage(BaseModel):
    """Standardized message format for internal processing."""
    external_id: str
    content: str
    sender_id: str  # Phone number or platform ID
    sender_name: Optional[str] = "Unknown"
    platform: str  # whatsapp, telegram, instagram, etc.
    provider: str  # business_api, go_whatsapp, etc.
    direction: str = "inbound"  # Default to inbound for incoming webhook messages
    media_url: Optional[str] = None
    media_type: Optional[str] = None  # image, audio, video, document
    extra_data: Dict[str, Any] = {}
    is_from_me: bool = False
    metadata: Dict[str, Any] = {}  # For additional platform-specific data
