"""
Pydantic schemas for enhanced AI bot endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel


class MessageWithContext(BaseModel):
    """Message with full context for intelligent processing."""
    customer_message: str
    customer_id: str
    platform: str
    customer_name: Optional[str] = None
    order_id: Optional[str] = None


class OrderExtractionRequest(BaseModel):
    """Request to extract order from message."""
    message: str
    customer_id: str
    platform: str
    auto_create: bool = False


class BusinessContextCreate(BaseModel):
    """Create business context."""
    context_type: str
    context_key: str
    title: str
    content: str
    tags: List[str] = []
    platforms: List[str] = []
