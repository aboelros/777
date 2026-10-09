from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PipelineStageBase(BaseModel):
    name: str
    index: int = 0
    color: str = "#6366f1"
    is_active: bool = True

class PipelineStageCreate(PipelineStageBase):
    pass

class PipelineStageResponse(PipelineStageBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class DealBase(BaseModel):
    stage_id: UUID
    customer_id: Optional[UUID] = None
    title: str
    value: float = 0.0
    currency: str = "USD"
    probability: float = 0.5
    priority: str = "medium"
    expected_close_date: Optional[datetime] = None
    tags: List[str] = []
    notes: Optional[str] = None
    extra_data: Dict[str, Any] = {}
    is_active: bool = True
    status: str = "open"

class DealCreate(DealBase):
    pass

class DealUpdate(BaseModel):
    stage_id: Optional[UUID] = None
    title: Optional[str] = None
    value: Optional[float] = None
    status: Optional[str] = None
    
class DealResponse(DealBase):
    id: UUID
    project_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)
