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

