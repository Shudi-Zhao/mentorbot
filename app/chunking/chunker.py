"""Token-based text chunking."""
import hashlib
from typing import Dict, List
import tiktoken


class TokenBasedChunker:
    """Chunk text based on token count with overlap."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50, encoding_name: str = "cl100k_base"):
        """
        Initialize the chunker.

        Args:
            chunk_size: Maximum number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
            encoding_name: Tiktoken encoding to use (cl100k_base for GPT-3.5/4)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Chunk a list of documents.

        Args:
            documents: List of document dictionaries with 'content' and metadata

        Returns:
            List of chunk dictionaries with metadata
        """
        all_chunks = []

        for doc in documents:
            chunks = self._chunk_single_document(doc)
            all_chunks.extend(chunks)

        return all_chunks

    def _chunk_single_document(self, document: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Chunk a single document.

        Args:
            document: Document dictionary with 'content' and metadata

        Returns:
            List of chunk dictionaries
        """
        content = document.get("content", "")
        if not content.strip():
            return []

        # Encode text to tokens
        tokens = self.encoding.encode(content)

        chunks = []
        start_idx = 0

        while start_idx < len(tokens):
            # Calculate end index
            end_idx = min(start_idx + self.chunk_size, len(tokens))

            # Extract chunk tokens
            chunk_tokens = tokens[start_idx:end_idx]

            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)

            # Create chunk metadata
            chunk_id = self._generate_chunk_id(document, start_idx)

            chunk = {
                **document,  # Inherit all metadata from parent document
                "chunk_id": chunk_id,
                "chunk_text": chunk_text,
                "chunk_index": len(chunks),
                "start_token": start_idx,
                "end_token": end_idx,
                "total_tokens": len(chunk_tokens),
            }

            chunks.append(chunk)

            # Move to next chunk with overlap
            if end_idx >= len(tokens):
                break

            start_idx = end_idx - self.chunk_overlap

        return chunks

    @staticmethod
    def _generate_chunk_id(document: Dict[str, str], start_token: int) -> str:
        """
        Generate a unique chunk ID.

        Args:
            document: Parent document
            start_token: Starting token position

        Returns:
            Unique chunk identifier
        """
        doc_id = document.get("doc_id", "unknown")
        content_hash = document.get("content_hash", "")[:8]

        # Add page/section/row identifier to ensure uniqueness across multi-part documents
        location_id = ""
        if "page" in document:
            location_id = f"_p{document['page']}"
        elif "section_number" in document:
            location_id = f"_s{document['section_number']}"
        elif "row" in document:
            location_id = f"_r{document['row']}"

        return f"{doc_id}_{content_hash}{location_id}_{start_token}"

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))
