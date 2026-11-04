import math
import re
from typing import Dict, List, Optional, Set
from uuid import UUID
from .schemas import KnowledgeDocument, KnowledgeChunk, RetrievalResult, SourceReference
from .chunker import DocumentChunker, TextNormalizer


class TenantRAGRetriever:
    """
    Tenant-partitioned knowledge base index and retriever.
    Enforces cross-tenant denial and evidence-grounding constraints.
    """

    def __init__(self, min_similarity_threshold: float = 0.25):
        # project_id -> list of KnowledgeChunk
        self._tenant_chunks: Dict[UUID, List[KnowledgeChunk]] = {}
        # project_id -> {doc_id: KnowledgeDocument}
        self._tenant_docs: Dict[UUID, Dict[UUID, KnowledgeDocument]] = {}
        self.chunker = DocumentChunker()
        self.min_similarity_threshold = min_similarity_threshold

    def index_document(self, document: KnowledgeDocument) -> int:
        """Index or re-index a document for a specific tenant."""
        pid = document.project_id
        if pid not in self._tenant_chunks:
            self._tenant_chunks[pid] = []
            self._tenant_docs[pid] = {}

        # Remove previous chunks of this document if updating
        self._tenant_chunks[pid] = [
            c for c in self._tenant_chunks[pid] if c.document_id != document.id
        ]
        self._tenant_docs[pid][document.id] = document

        if document.is_active:
            chunks = self.chunker.chunk_document(document)
            self._tenant_chunks[pid].extend(chunks)
            return len(chunks)
        return 0

    def delete_document(self, project_id: UUID, document_id: UUID) -> bool:
        """Remove a document and its chunks from tenant index."""
        if project_id not in self._tenant_chunks:
            return False
        initial_len = len(self._tenant_chunks[project_id])
        self._tenant_chunks[project_id] = [
            c for c in self._tenant_chunks[project_id] if c.document_id != document_id
        ]
        self._tenant_docs[project_id].pop(document_id, None)
        return len(self._tenant_chunks[project_id]) < initial_len

    def retrieve(
        self,
        project_id: UUID,
        query: str,
        top_k: int = 3
    ) -> RetrievalResult:
        """
        Execute tenant-isolated similarity retrieval.
        Returns empty evidence if below similarity threshold.
        """
        chunks = self._tenant_chunks.get(project_id, [])
        normalized_query = TextNormalizer.normalize(query).lower()
        query_terms = self._tokenize(normalized_query)

        if not chunks or not query_terms:
            return RetrievalResult(
                query=query,
                has_sufficient_evidence=False,
                formatted_context="No verified business documentation available."
            )

        scored_chunks: List[tuple[KnowledgeChunk, float]] = []
        for chunk in chunks:
            chunk_terms = self._tokenize(chunk.text.lower())
            score = self._compute_similarity(query_terms, chunk_terms)
            if score >= self.min_similarity_threshold:
                scored_chunks.append((chunk, score))

        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_results = scored_chunks[:top_k]

        if not top_results:
            return RetrievalResult(
                query=query,
                has_sufficient_evidence=False,
                formatted_context="No relevant verified business documentation found."
            )

        extracted_chunks: List[KnowledgeChunk] = []
        source_refs: List[SourceReference] = []
        context_blocks: List[str] = []

        for chunk, score in top_results:
            extracted_chunks.append(chunk)
            source_refs.append(
                SourceReference(
                    document_id=chunk.document_id,
                    title=chunk.title,
                    source_url=chunk.source_url,
                    relevance_score=round(score, 3)
                )
            )
            src_label = f"Source: {chunk.title}"
            if chunk.source_url:
                src_label += f" ({chunk.source_url})"
            context_blocks.append(f"[{src_label}]\n{chunk.text}")

        # Check for conflicting statements if top results have contradictory numbers
        is_conflicting = self._detect_contradiction(top_results)

        formatted_context = "\n\n".join(context_blocks)
        return RetrievalResult(
            query=query,
            chunks=extracted_chunks,
            sources=source_refs,
            has_sufficient_evidence=True,
            is_conflicting=is_conflicting,
            formatted_context=formatted_context
        )

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Simple multilingual word tokenizer."""
        return [w for w in re.findall(r"[\w\u0600-\u06FF]+", text) if len(w) > 1]

    @staticmethod
    def _compute_similarity(query_terms: List[str], doc_terms: List[str]) -> float:
        """Compute cosine similarity over term frequencies."""
        if not query_terms or not doc_terms:
            return 0.0
        q_counts = {}
        for w in query_terms:
            q_counts[w] = q_counts.get(w, 0) + 1
        d_counts = {}
        for w in doc_terms:
            d_counts[w] = d_counts.get(w, 0) + 1

        dot_product = sum(q_counts[w] * d_counts.get(w, 0) for w in q_counts)
        q_norm = math.sqrt(sum(v * v for v in q_counts.values()))
        d_norm = math.sqrt(sum(v * v for v in d_counts.values()))

        if q_norm == 0 or d_norm == 0:
            return 0.0
        return dot_product / (q_norm * d_norm)

    @staticmethod
    def _detect_contradiction(scored_chunks: List[tuple[KnowledgeChunk, float]]) -> bool:
        """Heuristic check for conflicting policies in top candidate chunks."""
        if len(scored_chunks) < 2:
            return False
        # Look for contradictory days/percentages in policy text
        numbers = [re.findall(r"\b\d+\b", c[0].text) for c in scored_chunks]
        distinct_numbers = set(tuple(sorted(n)) for n in numbers if n)
        return len(distinct_numbers) > 1


# Global retriever instance
tenant_rag_retriever = TenantRAGRetriever()
