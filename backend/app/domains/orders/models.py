from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, Index, JSON, Enum as SQLEnum, LargeBinary, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"



class Order(Base):
    """Unified order model from all platforms."""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True)
    external_id = Column(String(255), nullable=False)  # Platform-specific order ID
    provider = Column(String(50), nullable=False)  # shopify, custom, etc.
    status = Column(String(50))  # pending, fulfilled, cancelled, etc.
    
    # Customer information
    customer = Column(JSONB, default={})  # name, email, phone, address
    
    # Order details
    items = Column(JSONB, default=[])  # line items
    total = Column(Float)
    currency = Column(String(3), default="USD")
    
    # Extra data
    extra_data = Column(JSONB, default={})
    tags = Column(JSONB, default=[])
    
    # Timestamps
    order_date = Column(DateTime(timezone=True))
    fulfilled_date = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="orders")
    customer_profile = relationship("CustomerProfile", back_populates="orders")
    messages = relationship("Message", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_order_external_provider", "external_id", "provider"),
        Index("idx_order_project_status", "project_id", "status"),
        Index("idx_order_date", "order_date"),
    )
    
    def __repr__(self):
        return f"<Order {self.external_id} - {self.status}>"

