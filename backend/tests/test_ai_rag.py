"""
Unit and regression tests for Grounded Business Knowledge (RAG).
Verifies text chunking, similarity retrieval, cross-tenant denial, and negative fallbacks.
"""

import pytest
from uuid import uuid4
from app.domains.ai.rag.schemas import KnowledgeDocument
from app.domains.ai.rag.chunker import TextNormalizer, DocumentChunker
from app.domains.ai.rag.retriever import TenantRAGRetriever


def test_text_normalizer_and_chunker():
    raw_text = "Paragraph 1 with info.\n\n\n\nParagraph 2 with more words.\x00\x07"
    normalized = TextNormalizer.normalize(raw_text)
    assert "\x00" not in normalized
    assert "\n\n\n" not in normalized

    doc = KnowledgeDocument(
        project_id=uuid4(),
        title="Shipping Guide",
        content="Express shipping takes 24 hours. Standard shipping takes 3-5 business days."
    )
    chunker = DocumentChunker(target_chunk_size=50, overlap_size=10)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 1
    assert all(c.project_id == doc.project_id for c in chunks)
    assert all(c.document_id == doc.id for c in chunks)


def test_tenant_rag_retriever_grounding_and_isolation():
    retriever = TenantRAGRetriever(min_similarity_threshold=0.2)
    proj_a = uuid4()
    proj_b = uuid4()

    doc_a = KnowledgeDocument(
        project_id=proj_a,
        title="Tenant A Return Policy",
        content="Customers may return undamaged shoes within 14 days of delivery for a full refund."
    )
    doc_b = KnowledgeDocument(
        project_id=proj_b,
        title="Tenant B Secret Formula",
        content="Tenant B confidential internal discount code is TOPSECRET100."
    )

    retriever.index_document(doc_a)
    retriever.index_document(doc_b)

    # Tenant A asks about return policy
    res_a = retriever.retrieve(proj_a, "What is your return policy for shoes?")
    assert res_a.has_sufficient_evidence is True
    assert len(res_a.chunks) > 0
    assert "14 days" in res_a.formatted_context
    assert "TOPSECRET100" not in res_a.formatted_context

    # Tenant A attempts to retrieve Tenant B confidential data -> MUST be denied/empty
    cross_res = retriever.retrieve(proj_a, "TOPSECRET100 confidential discount")
    assert "TOPSECRET100" not in cross_res.formatted_context
    assert cross_res.has_sufficient_evidence is False

    # Negative fallback: completely irrelevant query has no evidence
    irrelevant_res = retriever.retrieve(proj_a, "Do you sell rocket ships to Jupiter?")
    assert irrelevant_res.has_sufficient_evidence is False
    assert "No relevant" in irrelevant_res.formatted_context


def test_rag_document_update_and_deletion():
    retriever = TenantRAGRetriever()
    proj = uuid4()

    doc = KnowledgeDocument(
        project_id=proj,
        title="Policy V1",
        content="Delivery fee is 20 dollars."
    )
    retriever.index_document(doc)

    res1 = retriever.retrieve(proj, "delivery fee")
    assert "20 dollars" in res1.formatted_context

    # Update document to 30 dollars
    doc_updated = KnowledgeDocument(
        id=doc.id,
        project_id=proj,
        title="Policy V2",
        content="Delivery fee is 30 dollars."
    )
    retriever.index_document(doc_updated)

    res2 = retriever.retrieve(proj, "delivery fee")
    assert "30 dollars" in res2.formatted_context
    assert "20 dollars" not in res2.formatted_context

    # Delete document
    deleted = retriever.delete_document(proj, doc.id)
    assert deleted is True
    res3 = retriever.retrieve(proj, "delivery fee")
    assert res3.has_sufficient_evidence is False
