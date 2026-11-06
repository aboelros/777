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


class ProjectRole(str, enum.Enum):
    """Project-specific roles for RBAC."""
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    WORKER = "worker"
    


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

