from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from enum import Enum

from app.domains.auth.models import UserRole
from app.domains.projects.models import ProjectRole
from app.domains.integrations.models import IntegrationStatus, IntegrationProvider as Provider, IntegrationProvider
from app.domains.messages.models import MessageDirection
from app.domains.billing.models import SubscriptionTier, SubscriptionStatus
from app.domains.orders.models import OrderStatus
from app.domains.ai.models import ModelTrainingStatus



class AssistantQuery(BaseModel):
    project_id: UUID
    message: str
    context: Optional[Dict[str, Any]] = {}
    order_id: Optional[UUID] = None
    use_function_calling: bool = True



class FunctionCall(BaseModel):
    name: str
    parameters: Dict[str, Any]



class AssistantResponse(BaseModel):
    reply: str
    function_calls: Optional[List[FunctionCall]] = []
    tokens_used: int
    cost: float
    model: str
    confidence: Optional[float] = None



class GenerateReplyRequest(BaseModel):
    project_id: UUID
    order_id: UUID
    customer_message: str



class ModelTrainRequest(BaseModel):
    project_id: UUID
    dataset_location: Optional[str] = None
    training_params: Dict[str, Any] = {}



class ModelTrainResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    gemini_model: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True



class KnowledgeBaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source_type: str = "text"
    source_url: Optional[str] = None
    is_active: bool = True
    tags: List[str] = []
    metadata_info: Dict[str, Any] = {}



class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source_type: Optional[str] = None
    source_url: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    metadata_info: Optional[Dict[str, Any]] = None



class KnowledgeBaseResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    content: str
    source_type: str
    source_url: Optional[str]
    is_active: bool
    tags: List[str]
    metadata_info: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Report Schemas
# ============================================================================
