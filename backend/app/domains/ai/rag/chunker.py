import re
from typing import List
from uuid import UUID
from .schemas import KnowledgeDocument, KnowledgeChunk


class TextNormalizer:
    """Cleans and standardizes raw text before chunking."""

    @staticmethod
    def normalize(text: str) -> str:
        """Strip invisible chars, normalize unicode whitespaces and newlines."""
        if not text:
            return ""
        # Replace multiple spaces/tabs with single space
        cleaned = re.sub(r"[ \t]+", " ", text)
        # Collapse excessive newlines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        # Strip control characters except newline and tab
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
        return cleaned.strip()


class DocumentChunker:
    """
    Splits normalized documents into structured, overlapping chunks.
    Ensures context continuity across chunk boundaries.
    """

    def __init__(self, target_chunk_size: int = 400, overlap_size: int = 80):
        self.target_chunk_size = target_chunk_size
        self.overlap_size = overlap_size

    def chunk_document(self, document: KnowledgeDocument) -> List[KnowledgeChunk]:
        """Convert a KnowledgeDocument into a sequence of KnowledgeChunks."""
        normalized = TextNormalizer.normalize(document.content)
        if not normalized:
            return []

        # Split by paragraph first, then by sentence/words if too long
        paragraphs = normalized.split("\n\n")
        chunks: List[KnowledgeChunk] = []
        current_text = ""
        chunk_idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_text) + len(para) + 2 <= self.target_chunk_size:
                current_text = f"{current_text}\n\n{para}".strip()
            else:
                if current_text:
                    chunks.append(
                        self._create_chunk(document, current_text, chunk_idx)
                    )
                    chunk_idx += 1
                    # Retain tail as overlap
                    overlap = current_text[-self.overlap_size:] if len(current_text) > self.overlap_size else ""
                    current_text = f"{overlap}\n\n{para}".strip()
                else:
                    # Paragraph itself exceeds target size; hard slice by words
                    words = para.split(" ")
                    sub_text = ""
                    for word in words:
                        if len(sub_text) + len(word) + 1 <= self.target_chunk_size:
                            sub_text = f"{sub_text} {word}".strip()
                        else:
                            chunks.append(
                                self._create_chunk(document, sub_text, chunk_idx)
                            )
                            chunk_idx += 1
                            overlap = sub_text[-self.overlap_size:] if len(sub_text) > self.overlap_size else ""
                            sub_text = f"{overlap} {word}".strip()
                    current_text = sub_text

        if current_text.strip():
            chunks.append(
                self._create_chunk(document, current_text.strip(), chunk_idx)
            )

        return chunks

    @staticmethod
    def _create_chunk(
        doc: KnowledgeDocument,
        text: str,
        index: int
    ) -> KnowledgeChunk:
        """Helper to build a KnowledgeChunk instance."""
        token_estimate = max(1, len(text) // 4)
        return KnowledgeChunk(
            document_id=doc.id,
            project_id=doc.project_id,
            title=doc.title,
            text=text,
            chunk_index=index,
            token_estimate=token_estimate,
            source_url=doc.source_url
        )
