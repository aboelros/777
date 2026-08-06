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


class AITraceLog(Base):
    """Detailed telemetry for AI interactions."""
    __tablename__ = "ai_trace_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    trace_id = Column(String(255), index=True) # Ties back to API Request ID
    
    # Model details
    provider = Column(String(50), nullable=False) # e.g., gemini, openai
    model_version = Column(String(100), nullable=False)
    
    # Prompt and Response
    system_prompt = Column(Text)
    user_prompt = Column(Text)
    completion = Column(Text)
    
    # Metrics
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    latency_ms = Column(Float)
    estimated_cost = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_ai_trace_project_created", "project_id", "created_at"),
    )
