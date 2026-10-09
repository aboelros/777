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


class OAuthState(Base):
    """OAuth authorization state for security validation."""
    __tablename__ = "oauth_states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)
    state_token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Optional extra info to persist across redirect
    redirect_uri = Column(String(1024), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_oauth_state_token", "state_token"),
    )
