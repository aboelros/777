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


class ModelTrainingStatus(str, enum.Enum):
    """Model training job status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"



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


class BotActivity(Base):
    """Bot activity logging model for monitoring and feed tracking."""
    __tablename__ = "bot_activities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customer_profiles.id", ondelete="SET NULL"), nullable=True)
    activity_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    details = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", backref="bot_activities")
    customer = relationship("CustomerProfile", backref="bot_activities")

    # Indexes matching migration 034157d2ccf7
    __table_args__ = (
        Index("idx_bot_activity_project", "project_id", "created_at"),
    )

    def __repr__(self):
        return f"<BotActivity {self.id} - {self.activity_type}>"

