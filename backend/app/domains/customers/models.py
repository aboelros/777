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


class CustomerProfile(Base):
    """Comprehensive customer profile with preferences and history."""
    __tablename__ = "customer_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Customer identification (unified across platforms)
    customer_id = Column(String(255), nullable=False)  # Unique ID (phone, email, or platform ID)
    
    # Platform accounts
    platform_accounts = Column(JSONB, default={})  # {whatsapp: "+1234", instagram: "@user", etc.}
    
    # Personal info
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    avatar_url = Column(Text)  # URL to profile picture
    last_sync = Column(DateTime(timezone=True))  # Last time profile info was synced from platform
    
    # Preferences learned from interactions
    preferred_language = Column(String(10), default="en")
    preferred_platform = Column(String(50))
    communication_style = Column(String(50))  # formal, casual, emoji-friendly
    
    # Behavioral data
    interaction_count = Column(Integer, default=0)  # Total interactions
    last_interaction = Column(DateTime(timezone=True))
    first_interaction = Column(DateTime(timezone=True))
    
    # Purchase history summary
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    average_order_value = Column(Float)
    favorite_products = Column(JSONB, default=[])  # Product IDs or names
    
    # Sentiment and satisfaction
    overall_sentiment = Column(String(50))  # positive, neutral, negative
    satisfaction_score = Column(Float)  # 0-100 based on interactions
    
    # Customer type
    customer_type = Column(String(50))  # new, regular, vip, problematic
    tags = Column(JSONB, default=[])  # Custom tags
    
    # AI insights
    interests = Column(JSONB, default=[])  # Inferred interests
    purchase_patterns = Column(JSONB, default={})  # When they buy, what they buy together
    lifetime_value_estimate = Column(Float)  # Predicted LTV
    
    # AI Control
    ai_enabled = Column(Boolean, default=True)
    ai_settings = Column(JSONB, default={}) # Overrides for this specific customer
    
    # Notes and context
    notes = Column(Text)  # Manual or AI-generated notes
    special_instructions = Column(Text)  # E.g., "allergic to peanuts", "prefers eco-friendly"
    
    # Flags
    is_vip = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    requires_special_attention = Column(Boolean, default=False)
    
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # Relationships
    project = relationship("Project", backref="customer_profiles")
    messages = relationship("Message", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer")
    
    # Indexes
    __table_args__ = (
        Index("idx_customer_profile_project", "project_id"),
        Index("idx_customer_profile_customer_id", "customer_id"),
        Index("idx_customer_profile_email", "email"),
        Index("idx_customer_profile_phone", "phone"),
        Index("idx_customer_profile_type", "customer_type"),
    )

