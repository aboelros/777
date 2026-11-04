from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    """Normalized document representation for ingestion."""
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    source_type: str = Field(default="text")  # text, document, policy, faq
    source_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class KnowledgeChunk(BaseModel):
    """A semantic chunk derived from an ingested document."""
    chunk_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    project_id: UUID
    title: str
    text: str
    chunk_index: int = 0
    token_estimate: int = 0
    vector: Optional[List[float]] = None
    source_url: Optional[str] = None


class SourceReference(BaseModel):
    """Attribution metadata for retrieved knowledge."""
    document_id: UUID
    title: str
    source_url: Optional[str] = None
    relevance_score: float = 0.0


class RetrievalResult(BaseModel):
    """Result of tenant-scoped retrieval query."""
    query: str
    chunks: List[KnowledgeChunk] = Field(default_factory=list)
    sources: List[SourceReference] = Field(default_factory=list)
    has_sufficient_evidence: bool = False
    is_conflicting: bool = False
    formatted_context: str = ""
