from uuid import uuid4
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class FinancialScenario(Base):
    """
    User-configured financial scenarios and simulation records.
    Strictly isolated per tenant project. Does not modify live billing records.
    """
    __tablename__ = "financial_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    scenario_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_baseline = Column(Boolean, default=False, nullable=False)
    
    # Serialized ScenarioSimulationConfig
    parameters = Column(JSONB, nullable=False, default={})
    
    # Snapshot summary of outcomes
    results_summary = Column(JSONB, nullable=False, default={})
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_financial_scenarios_project", "project_id"),
        Index("idx_financial_scenarios_name", "project_id", "scenario_name"),
    )

    def __repr__(self) -> str:
        return f"<FinancialScenario {self.scenario_name} (project={self.project_id})>"
