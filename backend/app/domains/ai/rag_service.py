from typing import List, Dict, Any, Union
from uuid import UUID
import structlog

from app.core.uow import UnitOfWork
from app.core.context import TenantContext
from app.domains.ai.repository import KnowledgeBaseRepository
from app.domains.ai.models import KnowledgeBase

logger = structlog.get_logger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation Service for AI Sales Commander.
    Handles embedding generation and similarity search against the KnowledgeBase.
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning("Failed to load local embedder. RAG will fallback to keyword search.", error=str(e))
            self.embedder = None

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for a given text."""
        if not self.embedder:
            return []
        embedding = self.embedder.encode(text)
        return embedding.tolist()

    async def retrieve_context(self, context: Union[TenantContext, UUID], query: str, limit: int = 3) -> str:
        """
        Retrieve relevant knowledge base articles for a query strictly scoped to the tenant.
        Returns a formatted string of context to inject into LLM prompts.
        """
        if isinstance(context, UUID):
            tenant_ctx = TenantContext(project_id=context, roles=["system"])
        else:
            tenant_ctx = context

        async with self.uow as uow:
            kb_repo = KnowledgeBaseRepository(uow.session)
            kb_items = await kb_repo.get_active_by_context(tenant_ctx, limit=limit)
            
            if not kb_items:
                return "No additional context available."
                
            context_blocks = []
            for item in kb_items:
                context_blocks.append(f"Source: {item.title}\n{item.content}")
                
            return "\n\n".join(context_blocks)
