from typing import List, Dict, Any, Union, Optional
from uuid import UUID
import structlog

from app.core.uow import UnitOfWork
from app.core.context import TenantContext
from app.domains.ai.repository import KnowledgeBaseRepository
from app.domains.ai.models import KnowledgeBase
from app.domains.ai.rag.schemas import KnowledgeDocument
from app.domains.ai.rag.retriever import tenant_rag_retriever

logger = structlog.get_logger(__name__)


class RAGService:
    """
    Production Retrieval-Augmented Generation Service.
    Enforces tenant isolation, document chunking, and similarity search
    against the KnowledgeBase.
    """

    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        self.retriever = tenant_rag_retriever
        self.embedder = None
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.debug("Local sentence-transformer not loaded, utilizing normalized term-frequency similarity", error=str(e))

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for a given text."""
        if not self.embedder:
            return []
        embedding = self.embedder.encode(text)
        return embedding.tolist()

    async def sync_tenant_documents(self, tenant_ctx: TenantContext):
        """Sync and re-index active database knowledge items into retriever index."""
        async with self.uow as uow:
            kb_repo = KnowledgeBaseRepository(uow.session)
            items = await kb_repo.get_active_by_context(tenant_ctx, limit=100)
            for item in items:
                doc = KnowledgeDocument(
                    id=item.id,
                    project_id=tenant_ctx.project_id,
                    title=item.title,
                    content=item.content,
                    source_type=item.source_type or "text",
                    source_url=item.source_url,
                    is_active=item.is_active
                )
                self.retriever.index_document(doc)

    async def retrieve_context(
        self,
        context: Union[TenantContext, UUID],
        query: str,
        limit: int = 3
    ) -> str:
        """
        Retrieve relevant knowledge base articles for a query strictly scoped to tenant.
        Returns a formatted string of context with source attribution.
        """
        if isinstance(context, UUID):
            tenant_ctx = TenantContext(project_id=context, roles=["system"])
        else:
            tenant_ctx = context

        # Sync active database items for this tenant
        try:
            await self.sync_tenant_documents(tenant_ctx)
        except Exception as e:
            logger.warning("Failed to sync tenant documents for RAG", error=str(e))

        result = self.retriever.retrieve(
            project_id=tenant_ctx.project_id,
            query=query,
            top_k=limit
        )

        if not result.has_sufficient_evidence:
            return "No additional context available."

        return result.formatted_context
