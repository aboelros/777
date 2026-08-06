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


class MessageDirection(str, enum.Enum):
    """Message direction enum."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"



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

