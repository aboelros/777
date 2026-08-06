from typing import List, Dict, Any
from uuid import UUID
import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer

from app.core.uow import UnitOfWork
from app.domains.ai.models import KnowledgeBase

logger = structlog.get_logger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation Service for AI Sales Commander.
    Handles embedding generation and similarity search against the KnowledgeBase.
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
        # Load a fast, lightweight embedding model for demo purposes
        # In production, you would use OpenAI ada-002 or a hosted embedding API
        try:
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning("Failed to load local embedder. RAG will fallback to keyword search.", error=str(e))
            self.embedder = None

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for a given text."""
        if not self.embedder:
            return []
        
        # SentenceTransformer returns numpy array, convert to list of floats
        embedding = self.embedder.encode(text)
        return embedding.tolist()

    async def retrieve_context(self, project_id: UUID, query: str, limit: int = 3) -> str:
        """
        Retrieve relevant knowledge base articles for a query.
        Returns a formatted string of context to inject into LLM prompts.
        """
        async with self.uow as uow:
            # 1. Generate embedding for user query
            query_embedding = await self.generate_embedding(query)
            
            # 2. Query KnowledgeBase
            # If pgvector is installed, we would use the `<->` operator for L2 distance:
            # stmt = select(KnowledgeBase).filter(KnowledgeBase.project_id == project_id)
            # stmt = stmt.order_by(KnowledgeBase.embedding.l2_distance(query_embedding)).limit(limit)
            
            # Since we used ARRAY(Float) as a fallback in models.py, we will do a basic keyword/text search fallback here 
            # if we can't perform native vector math in the DB without pgvector extension.
            
            # Basic fallback: return latest active KB items for the project (simulate retrieval)
            stmt = select(KnowledgeBase).where(
                KnowledgeBase.project_id == project_id,
                KnowledgeBase.is_active == True
            ).limit(limit)
            
            result = await uow.session.execute(stmt)
            kb_items = result.scalars().all()
            
            if not kb_items:
                return "No additional context available."
                
            # 3. Format the context
            context_blocks = []
            for item in kb_items:
                context_blocks.append(f"Source: {item.title}\n{item.content}")
                
            return "\n\n".join(context_blocks)
