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


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels."""
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    PROFESSIONAL = "professional"
    SCALE = "scale"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"



class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"
    PAST_DUE = "past_due"



class Subscription(Base):
    """User subscription and billing details."""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False)
    
    # Pricing
    price_monthly = Column(Float, default=0.0)  # Monthly price
    price_annually = Column(Float, default=0.0)  # Annual price
    billing_cycle = Column(String(50), default="monthly")  # monthly, annually
    currency = Column(String(10), default="USD")
    
    # Billing dates
    started_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    trial_ends_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    next_billing_date = Column(DateTime(timezone=True))
    
    # Payment provider info
    stripe_customer_id = Column(String(255))
    stripe_subscription_id = Column(String(255))
    stripe_payment_method_id = Column(String(255))
    
    # Usage limits (per month)
    limit_messages = Column(Integer, default=100)
    limit_orders = Column(Integer, default=10)
    limit_ai_requests = Column(Integer, default=1000)
    limit_projects = Column(Integer, default=1)
    limit_integrations = Column(Integer, default=2)
    limit_storage_gb = Column(Float, default=1.0)
    limit_team_members = Column(Integer, default=1)
    
    # Features enabled
    features = Column(JSONB, default={})  # {"ai_automation": true, "advanced_reports": false}
    
    # Billing history
    total_paid = Column(Float, default=0.0)
    invoices = Column(JSONB, default=[])  # Array of invoice objects
    
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    usage_records = relationship("UsageTracking", back_populates="subscription", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_subscription_tier", "tier"),
        Index("idx_subscription_status", "status"),
        Index("idx_subscription_expires", "expires_at"),
    )



class UsageTracking(Base):
    """Track usage metrics per subscription for billing and limits."""
    __tablename__ = "usage_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Tracking period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Usage counts
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    orders_created = Column(Integer, default=0)
    ai_requests = Column(Integer, default=0)
    ai_tokens_used = Column(Integer, default=0)
    storage_used_gb = Column(Float, default=0.0)
    
    # Cost tracking
    ai_cost = Column(Float, default=0.0)  # Cost of AI usage
    storage_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Limit violations
    limits_exceeded = Column(JSONB, default=[])  # ["messages", "ai_requests"]
    overage_charges = Column(Float, default=0.0)
    
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="usage_records")
    
    # Indexes
    __table_args__ = (
        Index("idx_usage_subscription", "subscription_id"),
        Index("idx_usage_user", "user_id"),
        Index("idx_usage_period", "period_start", "period_end"),
    )
    
    def __repr__(self):
        return f"<UsageTracking {self.user_id} {self.period_start}>"



class Invoice(Base):
    """Invoices for billing customers."""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    
    # Invoice details
    invoice_number = Column(String(50), nullable=False)  # e.g., INV-001
    status = Column(String(50), default="draft")  # draft, sent, paid, void, overdue
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    
    # Financials
    amount = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    
    # Content
    items = Column(JSONB, default=[])  # [{description, quantity, price}]
    notes = Column(Text)
    
    # External integration
    stripe_invoice_id = Column(String(255))
    payment_link = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="invoices")
    customer = relationship("CustomerProfile", backref="invoices")
    order = relationship("Order", backref="invoices")
    payment_links = relationship("PaymentLink", back_populates="invoice", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_invoice_project_number", "project_id", "invoice_number"),
        Index("idx_invoice_status", "status"),
        Index("idx_invoice_customer", "customer_id"),
    )
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.total_amount}>"



class PaymentLink(Base):
    """Generated payment links for chat commerce."""
    __tablename__ = "payment_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True)
    
    # Link details
    url = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    description = Column(String(255))
    
    status = Column(String(50), default="active")  # active, paid, expired
    is_active = Column(Boolean, default=True)
    
    # Integration
    stripe_payment_link_id = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True))
    
    # Relationships
    project = relationship("Project", backref="generated_payment_links")
    invoice = relationship("Invoice", back_populates="payment_links")
    
    def __repr__(self):
        return f"<PaymentLink {self.id} - {self.amount}>"
