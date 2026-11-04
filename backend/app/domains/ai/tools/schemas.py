from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class ToolRiskLevel(str, Enum):
    READ_ONLY = "read_only"
    STATE_CHANGING = "state_changing"
    HIGH_RISK_CONFIRMATION = "high_risk_confirmation"


class SearchProductsInput(BaseModel):
    query: str = Field(default="", max_length=100)
    limit: int = Field(default=5, ge=1, le=20)


class ProductSummary(BaseModel):
    id: str
    name: str
    price: float
    stock_quantity: int
    is_in_stock: bool


class SearchProductsOutput(BaseModel):
    results: List[ProductSummary]
    count: int


class CheckInventoryInput(BaseModel):
    product_name_or_id: str = Field(..., min_length=1, max_length=100)


class CheckInventoryOutput(BaseModel):
    product_name: str
    in_stock: bool
    status_label: str  # e.g., "In Stock", "Limited availability", "Out of stock"
    unit_price: Optional[float] = None


class GetOrderStatusInput(BaseModel):
    order_identifier: str = Field(..., min_length=1, max_length=100)
    customer_id: Optional[UUID] = None


class GetOrderStatusOutput(BaseModel):
    order_number: str
    status: str
    total_amount: str
    order_date: Optional[str] = None
    tracking_status: Optional[str] = None


class CreateTicketInput(BaseModel):
    subject: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=5, max_length=1000)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    customer_id: Optional[UUID] = None


class CreateTicketOutput(BaseModel):
    ticket_id: str
    status: str
    message: str


class EscalateConversationInput(BaseModel):
    reason: str = Field(..., min_length=3, max_length=300)
    customer_id: Optional[UUID] = None


class EscalateConversationOutput(BaseModel):
    escalated: bool
    ticket_reference: Optional[str] = None
    customer_message: str


class GetPolicyInput(BaseModel):
    policy_type: str = Field(default="return", pattern="^(return|shipping|payment|privacy)$")


class GetPolicyOutput(BaseModel):
    policy_type: str
    summary: str
    max_return_days: Optional[int] = None
    free_shipping_threshold: Optional[float] = None


class ToolExecutionOutcome(BaseModel):
    tool_name: str
    status: str  # "success" or "error"
    risk_level: ToolRiskLevel
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
