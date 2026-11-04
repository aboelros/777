from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ToolTraceEntry(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    tool_name: str
    risk_level: str
    status: str
    execution_time_ms: float
    error: Optional[str] = None


class AgentTraceRecord(BaseModel):
    """Structured privacy-conscious trace record for an agent execution turn."""
    model_config = ConfigDict(protected_namespaces=())
    trace_id: UUID = Field(default_factory=uuid4)
    conversation_id: Optional[str] = None
    project_id: UUID
    customer_id: Optional[UUID] = None
    prompt_version: str
    model_name: str
    cache_hit: bool = False
    retrieval_count: int = 0
    tools: List[ToolTraceEntry] = Field(default_factory=list)
    latency_total_ms: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    status: str = "success"  # success, refused, error
    flagged_reason: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
