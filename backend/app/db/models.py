"""
SQLAlchemy database models for all entities.
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, 
    ForeignKey, Index, JSON, Enum as SQLEnum, LargeBinary
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enum."""
    ADMIN = "admin"
    USER = "user"


class ProjectRole(str, enum.Enum):
    """Project-specific roles for RBAC."""
    OWNER = "owner"
    MODERATOR = "moderator"
    WORKER = "worker"
    

class IntegrationStatus(str, enum.Enum):
    """Integration connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    PENDING = "pending"


class IntegrationProvider(str, enum.Enum):
    """Supported integration providers."""
    SHOPIFY = "shopify"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    DISCORD = "discord"
    TIKTOK = "tiktok"


class MessageDirection(str, enum.Enum):
    """Message direction enum."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ModelTrainingStatus(str, enum.Enum):
    """Model training job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class OrderStatus(str, enum.Enum):
    """Order status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


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


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    
    # Note: Subscription details moved to separate Subscription model
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"


class RefreshToken(Base):
    """Refresh token storage for secure token rotation."""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")


class Project(Base):
    """Project/Brand model - multi-tenant support."""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Unique project identifier for easy differentiation
    project_code = Column(String(50), unique=True, nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    timezone = Column(String(50), default="UTC")
    settings = Column(JSONB, default={})
    
    # AI Specific overrides (Standardized for personality customization)
    bot_name = Column(String(100), default="Alex")
    bot_tone = Column(String(50), default="Professional")
    personality_prompt = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="project", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="project", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="project", cascade="all, delete-orphan")
    model_trainings = relationship("ModelTraining", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.project_code}: {self.name}>"


class Integration(Base):
    """External platform integration configuration."""
    __tablename__ = "integrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # shopify, whatsapp, instagram, telegram, facebook
    status = Column(SQLEnum(IntegrationStatus), default=IntegrationStatus.DISCONNECTED)
    config = Column(JSONB, nullable=False, default={})  # API keys, tokens, etc.
    extra_data = Column(JSONB, default={})  # Additional provider-specific data
    last_sync = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="integrations")
    
    # Indexes
    __table_args__ = (
        Index("idx_integration_project_provider", "project_id", "provider"),
    )
    
    def __repr__(self):
        return f"<Integration {self.provider} - {self.status}>"


class ProjectMember(Base):
    """Project membership and RBAC."""
    __tablename__ = "project_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(ProjectRole), default=ProjectRole.WORKER, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", backref="project_memberships")
    
    # Indexes and constraints
    __table_args__ = (
        Index("idx_member_project_user", "project_id", "user_id", unique=True),
        Index("idx_member_role", "role"),
    )
    
    def __repr__(self):
        return f"<ProjectMember {self.user_id} - {self.role}>"


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
    customer = relationship("CustomerProfile", back_populates="orders")
    messages = relationship("Message", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_order_external_provider", "external_id", "provider"),
        Index("idx_order_project_status", "project_id", "status"),
        Index("idx_order_date", "order_date"),
    )
    
    def __repr__(self):
        return f"<Order {self.external_id} - {self.status}>"


class Message(Base):
    """Unified message model across all channels."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="SET NULL"), nullable=True)
    
    direction = Column(SQLEnum(MessageDirection), nullable=False)
    platform = Column(String(50), nullable=False)  # whatsapp, telegram, instagram, sms, facebook, tiktok
    provider = Column(String(50), nullable=False)  # whatsapp, telegram, instagram, sms
    external_id = Column(String(255))  # Provider message ID
    
    # Message content
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")  # text, image, video, audio, file
    attachments = Column(JSONB, default=[])
    
    # Sender/Recipient info
    sender = Column(JSONB, default={})
    recipient = Column(JSONB, default={})
    
    # AI interaction
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100))
    ai_prompt_tokens = Column(Integer)
    ai_completion_tokens = Column(Integer)
    ai_cost = Column(Float)
    
    # Extra data
    extra_data = Column(JSONB, default={})
    is_read = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(String(50), default="sent")  # sent, delivered, read, failed
    error_message = Column(Text)
    sent_at = Column(DateTime(timezone=True))  # When message was actually sent
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="messages")
    customer = relationship("CustomerProfile", back_populates="messages")
    order = relationship("Order", back_populates="messages")
    
    # Indexes and Constraints
    __table_args__ = (
        Index("idx_message_project_created", "project_id", "created_at"),
        Index("idx_message_order", "order_id"),
        Index("idx_message_direction", "direction"),
        Index("idx_message_external_id_provider", "project_id", "provider", "external_id", unique=True),
    )
    
    def __repr__(self):
        return f"<Message {self.direction} - {self.provider}>"


class ModelTraining(Base):
    """AI model training job tracking."""
    __tablename__ = "model_trainings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(ModelTrainingStatus), default=ModelTrainingStatus.PENDING)
    
    # Training configuration
    gemini_model = Column(String(100))
    dataset_location = Column(String(500))
    training_params = Column(JSONB, default={})
    
    # Results
    model_version = Column(String(100))
    metrics = Column(JSONB, default={})
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="model_trainings")
    
    def __repr__(self):
        return f"<ModelTraining {self.id} - {self.status}>"


class Report(Base):
    """Generated analytics reports."""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    report_type = Column(String(50), nullable=False)  # sales, messages, performance
    
    # Report data
    payload = Column(JSONB, nullable=False, default={})
    summary = Column(Text)
    
    # Time range
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Storage
    file_url = Column(String(500))
    
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="reports")
    
    # Indexes
    __table_args__ = (
        Index("idx_report_project_type", "project_id", "report_type"),
        Index("idx_report_generated", "generated_at"),
    )
    
    def __repr__(self):
        return f"<Report {self.report_type} - {self.generated_at}>"


class APILog(Base):
    """API usage logging for billing and monitoring."""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    
    # Request info
    endpoint = Column(String(255))
    method = Column(String(10))
    request = Column(JSONB)
    response = Column(JSONB)
    status_code = Column(Integer)
    
    # Performance
    duration_ms = Column(Float)
    
    # Cost tracking
    ai_tokens_used = Column(Integer)
    cost_estimate = Column(Float)
    
    # User info
    user_id = Column(UUID(as_uuid=True))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Indexes for efficient queries
    __table_args__ = (
        Index("idx_api_log_project_created", "project_id", "created_at"),
        Index("idx_api_log_endpoint", "endpoint"),
    )



class ProductImage(Base):
    """
    Dedicated storage for product images/binary data.
    Used by PostgresStorageService when not using S3/Local.
    """
    __tablename__ = "product_images"
    
    # We use a text key as primary key (e.g. products/uuid/image.jpg)
    key = Column(String(500), primary_key=True)
    
    # Binary data
    data = Column(LargeBinary, nullable=False)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProductImage {self.key}>"


class Product(Base):
    """Product catalog for AI-powered social media responses."""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Product information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sku = Column(String(100))
    price = Column(Float)
    currency = Column(String(3), default="USD")
    
    # Inventory
    stock_quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    # Storage
    storage_locations = Column(JSONB, default=[])
    reorder_point = Column(Integer, default=0)
    safety_stock = Column(Integer, default=0)
    storage_notes = Column(Text)
    storage_attachments = Column(JSONB, default=[])
    
    # Media
    images = Column(JSONB, default=[])  # Array of image URLs
    
    # Categories and tags
    category = Column(String(100))
    tags = Column(JSONB, default=[])
    
    # Specifications
    specifications = Column(JSONB, default={})  # Size, color, material, etc.
    
    # FAQ and common questions
    faq = Column(JSONB, default=[])  # [{question: "", answer: ""}]
    
    # SEO and marketing
    keywords = Column(JSONB, default=[])  # Keywords for AI matching
    
    # Extra data
    extra_data = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="products")
    
    # Indexes
    __table_args__ = (
        Index("idx_product_project", "project_id"),
        Index("idx_product_sku", "sku"),
        Index("idx_product_name", "name"),
    )
    
    def __repr__(self):
        return f"<Product {self.name}>"


class BotInstruction(Base):
    """Custom bot instructions/training per project."""
    __tablename__ = "bot_instructions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Instruction details
    title = Column(String(255), nullable=False)
    instruction = Column(Text, nullable=False)  # The actual instruction/rule
    category = Column(String(100))  # tone, product_knowledge, response_style, etc.
    priority = Column(Integer, default=0)  # Higher priority = more important
    
    # Conditional activation
    active_for_platforms = Column(JSONB, default=[])  # ["instagram", "facebook"] or [] for all
    active_for_topics = Column(JSONB, default=[])  # ["pricing", "shipping"] or [] for all
    
    # Examples
    examples = Column(JSONB, default=[])  # Example conversations showing the instruction
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="bot_instructions")
    
    # Indexes
    __table_args__ = (
        Index("idx_bot_instruction_project", "project_id"),
        Index("idx_bot_instruction_priority", "priority"),
    )
    
    def __repr__(self):
        return f"<BotInstruction {self.title}>"


class KnowledgeBase(Base):
    """Project-specific knowledge base for RAG."""
    __tablename__ = "knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    source_type = Column(String(50), default="text")  # text, url, file, document
    source_url = Column(String(500))
    
    is_active = Column(Boolean, default=True)
    tags = Column(JSONB, default=[])
    metadata_info = Column(JSONB, default={})  # Renamed from metadata to avoid SQLAlchemy conflict
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", backref="knowledge_base_items")

    # Indexes
    __table_args__ = (
        Index("idx_kb_project", "project_id"),
        Index("idx_kb_active", "is_active"),
    )

    def __repr__(self):
        return f"<KnowledgeBase {self.title}>"


class SocialMediaComment(Base):
    """Social media comments/posts to respond to."""
    __tablename__ = "social_media_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Platform info
    platform = Column(String(50), nullable=False)  # instagram, facebook, tiktok
    external_id = Column(String(255), nullable=False)  # Platform comment ID
    post_id = Column(String(255))  # Parent post ID
    
    # Comment details
    content = Column(Text, nullable=False)
    author_username = Column(String(255))
    author_id = Column(String(255))
    
    # Response tracking
    responded = Column(Boolean, default=False)
    response_content = Column(Text)
    response_sent_at = Column(DateTime(timezone=True))
    auto_generated = Column(Boolean, default=False)
    
    # AI analysis
    sentiment = Column(String(50))  # positive, negative, neutral, question
    intent = Column(String(100))  # product_inquiry, complaint, praise, etc.
    requires_human = Column(Boolean, default=False)  # Escalate to human
    
    # Priority
    priority = Column(Integer, default=0)  # 0=normal, 1=high, 2=urgent
    
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="social_comments")
    
    # Indexes
    __table_args__ = (
        Index("idx_social_comment_project", "project_id"),
        Index("idx_social_comment_platform_external", "platform", "external_id"),
        Index("idx_social_comment_responded", "responded"),
    )
    
    def __repr__(self):
        return f"<SocialMediaComment {self.platform} - {self.external_id}>"


class AutoResponseTemplate(Base):
    """Templates for automated responses to common scenarios."""
    __tablename__ = "auto_response_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Template details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Trigger conditions
    trigger_keywords = Column(JSONB, default=[])  # Keywords that activate this template
    trigger_platforms = Column(JSONB, default=[])  # Which platforms to use on
    trigger_intent = Column(String(100))  # product_inquiry, shipping_question, etc.
    
    # Response template
    response_template = Column(Text, nullable=False)  # Can include {{product_name}} etc.
    variations = Column(JSONB, default=[])  # Alternative phrasings
    
    # Settings
    use_ai_enhancement = Column(Boolean, default=True)  # Let AI personalize the response
    requires_approval = Column(Boolean, default=False)  # Human approval before sending
    
    # Statistics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float)  # Based on follow-up interactions
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="auto_response_templates")
    
    # Indexes
    __table_args__ = (
        Index("idx_auto_response_project", "project_id"),
        Index("idx_auto_response_active", "is_active"),
    )
    
    def __repr__(self):
        return f"<AutoResponseTemplate {self.name}>"


class ConversationHistory(Base):
    """Track conversation history per customer for memory and context."""
    __tablename__ = "conversation_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Customer identification
    customer_id = Column(String(255), nullable=False)  # Platform-specific customer ID
    customer_name = Column(String(255))
    platform = Column(String(50), nullable=False)  # whatsapp, instagram, facebook, etc.
    
    # Conversation details
    conversation_id = Column(String(255))  # Thread or conversation ID
    message_content = Column(Text, nullable=False)
    message_direction = Column(SQLEnum(MessageDirection), nullable=False)  # inbound/outbound
    
    # AI context
    intent = Column(String(100))  # What customer wants (product_inquiry, order_status, etc.)
    sentiment = Column(String(50))  # positive, negative, neutral
    entities_extracted = Column(JSONB, default={})  # Product names, order IDs, etc.
    
    # Summary for quick retrieval
    summary = Column(Text)  # AI-generated summary of the message
    
    # Metadata
    embedding_vector = Column(JSONB, default=[])  # For semantic search (optional)
    extra_data = Column(JSONB, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    project = relationship("Project", backref="conversation_histories")
    
    # Indexes
    __table_args__ = (
        Index("idx_conversation_customer", "customer_id", "platform"),
        Index("idx_conversation_project_customer", "project_id", "customer_id"),
        Index("idx_conversation_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<ConversationHistory {self.customer_id} - {self.platform}>"


class BusinessContext(Base):
    """Store business-specific context, learning, and perception."""
    __tablename__ = "business_context"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Context type
    context_type = Column(String(100), nullable=False)  # brand_voice, common_questions, policies, etc.
    context_key = Column(String(255), nullable=False)  # Specific identifier
    
    # Context content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # The actual context/knowledge
    
    # Metadata
    tags = Column(JSONB, default=[])  # For categorization
    relevance_score = Column(Float, default=1.0)  # How relevant is this (learned over time)
    times_used = Column(Integer, default=0)  # How often this context is accessed
    
    # Learning
    learned_from = Column(String(100))  # manual, ai_analysis, customer_feedback, etc.
    confidence_score = Column(Float, default=0.5)  # AI confidence in this context
    
    # Platform-specific
    active_for_platforms = Column(JSONB, default=[])  # [] means all platforms
    
    # Examples
    examples = Column(JSONB, default=[])  # Example uses of this context
    
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="business_contexts")
    
    # Indexes
    __table_args__ = (
        Index("idx_business_context_project", "project_id"),
        Index("idx_business_context_type", "context_type"),
        Index("idx_business_context_key", "context_key"),
        Index("idx_business_context_used", "times_used"),
    )
    
    def __repr__(self):
        return f"<BusinessContext {self.context_type} - {self.title}>"


class SocialMediaPost(Base):
    """Track social media posts for monitoring and engagement."""
    __tablename__ = "social_media_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Platform info
    platform = Column(String(50), nullable=False)  # instagram, facebook, tiktok, twitter
    external_id = Column(String(255), nullable=False, unique=True)  # Platform post ID
    post_url = Column(String(500))
    
    # Post content
    content = Column(Text)  # Caption/text content
    media_type = Column(String(50))  # image, video, carousel, story
    media_urls = Column(JSONB, default=[])  # Array of media URLs
    
    # Author info (usually the business itself)
    author_username = Column(String(255))
    author_id = Column(String(255))
    
    # Engagement metrics
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # AI analysis
    ai_analyzed = Column(Boolean, default=False)
    sentiment = Column(String(50))  # overall sentiment of comments
    topics = Column(JSONB, default=[])  # Main topics discussed
    keywords = Column(JSONB, default=[])  # Extracted keywords
    ai_summary = Column(Text)  # AI-generated summary of post and comments
    
    # Comment monitoring
    last_comment_check = Column(DateTime(timezone=True))
    unresponded_comments = Column(Integer, default=0)
    
    # Performance tracking
    engagement_rate = Column(Float)  # Calculated engagement percentage
    best_performing = Column(Boolean, default=False)  # Flag for high-performing posts
    
    # Metadata
    hashtags = Column(JSONB, default=[])
    mentions = Column(JSONB, default=[])
    location = Column(String(255))
    
    extra_data = Column(JSONB, default={})
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="social_posts")
    
    # Indexes
    __table_args__ = (
        Index("idx_social_post_project", "project_id"),
        Index("idx_social_post_platform_external", "platform", "external_id"),
        Index("idx_social_post_engagement", "engagement_rate"),
        Index("idx_social_post_posted_at", "posted_at"),
    )
    
    def __repr__(self):
        return f"<SocialMediaPost {self.platform} - {self.external_id}>"


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
        Index("idx_subscription_user", "user_id"),
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


class PipelineStage(Base):
    """Stages for the Sales Pipeline (Kanban)."""
    __tablename__ = "pipeline_stages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(100), nullable=False)  # "New Lead", "Qualified", "Won"
    index = Column(Integer, default=0)  # Order of the column
    color = Column(String(50), default="#6366f1")  # UI Decoration
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="pipeline_stages")
    deals = relationship("Deal", back_populates="stage", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_stage_project_index", "project_id", "index"),
    )
    
    def __repr__(self):
        return f"<PipelineStage {self.name} ({self.index})>"


class Deal(Base):
    """Sales Deal / Lead."""
    __tablename__ = "deals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    stage_id = Column(UUID(as_uuid=True), ForeignKey("pipeline_stages.id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True)
    
    # Deal info
    title = Column(String(255), nullable=False)  # "Deal with Acme Corp"
    value = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # Probability & Priority
    probability = Column(Float, default=0.5)  # 0.0 to 1.0 (50%)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    expected_close_date = Column(DateTime(timezone=True))
    
    # Metadata
    tags = Column(JSONB, default=[])
    notes = Column(Text)
    extra_data = Column(JSONB, default={})
    
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="open")  # open, won, lost, abandoned
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="deals")
    stage = relationship("PipelineStage", back_populates="deals")
    customer = relationship("CustomerProfile", backref="deals")
    
    # Indexes
    __table_args__ = (
        Index("idx_deal_project_stage", "project_id", "stage_id"),
        Index("idx_deal_customer", "customer_id"),
        Index("idx_deal_status", "status"),
    )
    
    def __repr__(self):
        return f"<Deal {self.title} - {self.value}>"


class DripCampaign(Base):
    """Automated drip campaign definition."""
    __tablename__ = "drip_campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(50), default="manual")  # manual, tag_added, new_customer
    trigger_value = Column(String(255))  # e.g., tag name "interested"
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", backref="drip_campaigns")
    steps = relationship("DripStep", back_populates="campaign", cascade="all, delete-orphan", order_by="DripStep.step_order")
    enrollments = relationship("CampaignEnrollment", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DripCampaign {self.name}>"


class DripStep(Base):
    """Single step in a drip campaign."""
    __tablename__ = "drip_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("drip_campaigns.id", ondelete="CASCADE"), nullable=False)
    
    step_order = Column(Integer, nullable=False)  # 1, 2, 3...
    delay_hours = Column(Integer, default=24)  # Wait time before sending this step
    
    # Message content
    content_template = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, image
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    campaign = relationship("DripCampaign", back_populates="steps")
    
    def __repr__(self):
        return f"<DripStep {self.step_order} - {self.delay_hours}h>"


class CampaignEnrollment(Base):
    """Customer progress in a drip campaign."""
    __tablename__ = "campaign_enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("drip_campaigns.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(String(50), default="active")  # active, completed, paused, cancelled
    current_step = Column(Integer, default=1)  # The next step to execute
    next_execution_at = Column(DateTime(timezone=True))  # When to run the next step
    
    metadata_info = Column(JSONB, default={})
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    project = relationship("Project", backref="campaign_enrollments")
    campaign = relationship("DripCampaign", back_populates="enrollments")
    customer = relationship("CustomerProfile", backref="campaign_enrollments")
    
    # Indexes
    __table_args__ = (
        Index("idx_enrollment_project_campaign", "project_id", "campaign_id"),
        Index("idx_enrollment_status_execution", "status", "next_execution_at"),
        Index("idx_enrollment_customer", "customer_id"),
    )
    
    def __repr__(self):
        return f"<CampaignEnrollment {self.customer_id} - Step {self.current_step}>"


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
