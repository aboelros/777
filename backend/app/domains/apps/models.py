from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class DeveloperApp(Base):
    """Third-party application registered on the platform."""
    __tablename__ = "developer_apps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    developer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(1000))
    website_url = Column(String(255))
    
    # Simple API Key authentication for the MVP
    api_key = Column(String(255), nullable=False, unique=True, index=True)
    api_secret = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    developer = relationship("User")
    installations = relationship("AppInstallation", back_populates="app", cascade="all, delete-orphan")


class AppInstallation(Base):
    """Tracks which Project has installed which DeveloperApp."""
    __tablename__ = "app_installations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    app_id = Column(UUID(as_uuid=True), ForeignKey("developer_apps.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Granted scopes (e.g., ["read:orders", "write:messages"])
    scopes = Column(JSONB, default=[])
    
    is_active = Column(Boolean, default=True)
    installed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    app = relationship("DeveloperApp", back_populates="installations")
    project = relationship("Project")
    
    __table_args__ = (
        Index("idx_app_installation", "app_id", "project_id", unique=True),
    )
