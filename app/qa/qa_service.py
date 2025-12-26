"""Question answering service using OpenAI."""
from typing import Dict, List, Any, Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class QAService:
    """Service for answering questions using retrieved context."""

    SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided context.

IMPORTANT RULES:
1. Use ONLY the information from the provided context chunks to answer questions
2. If the answer is not found in the context, respond with: "Not found in uploaded documents"
3. Do not use any external knowledge or information beyond what is provided
4. Always cite your sources by referencing the chunk numbers (e.g., [Source 1], [Source 2])
5. If the context is ambiguous or incomplete, say so clearly
6. Be concise but thorough in your answers"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", temperature: float = 0.1, max_tokens: int = 1000):
        """
        Initialize the QA service.

        Args:
            api_key: OpenAI API key
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"QA Service initialized with model: {model}")

    def answer_question(
        self,
        question: str,
        retrieved_chunks: List[Dict[str, Any]],
        metadatas: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Answer a question using retrieved context.

        Args:
            question: User's question
            retrieved_chunks: List of retrieved text chunks
            metadatas: List of metadata for each chunk

        Returns:
            Dictionary with answer and citations
        """
        if not retrieved_chunks:
            return {
                "answer": "Not found in uploaded documents. Please upload relevant documents first.",
                "citations": [],
                "sources": [],
            }

        # Build context from retrieved chunks
        context = self._build_context(retrieved_chunks, metadatas)

        # Create user prompt
        user_prompt = f"""Context from uploaded documents:
{context}

Question: {question}

Answer the question using ONLY the context provided above. Include source references."""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            answer = response.choices[0].message.content.strip()

            # Extract citations
            citations = self._extract_citations(metadatas)

            return {"answer": answer, "citations": citations, "sources": retrieved_chunks}

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "citations": [],
                "sources": [],
            }

    def _build_context(self, chunks: List[str], metadatas: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved chunks.

        Args:
            chunks: List of text chunks
            metadatas: List of metadata dictionaries

        Returns:
            Formatted context string
        """
        context_parts = []

        for i, (chunk, metadata) in enumerate(zip(chunks, metadatas), start=1):
            # Build source info
            source_info = self._format_source_info(metadata, i)

            context_parts.append(f"[Source {i}] {source_info}\n{chunk}\n")

        return "\n".join(context_parts)

    def _format_source_info(self, metadata: Dict[str, Any], source_num: int) -> str:
        """
        Format source information from metadata.

        Args:
            metadata: Metadata dictionary
            source_num: Source number for reference

        Returns:
            Formatted source string
        """
        filename = metadata.get("filename", "Unknown")
        file_type = metadata.get("file_type", "")

        parts = [f"File: {filename}"]

        # Add file-type specific info
        if file_type == "pdf" and "page" in metadata:
            parts.append(f"Page: {metadata['page']}")
        elif file_type == "markdown" and "section" in metadata:
            parts.append(f"Section: {metadata['section']}")
        elif file_type == "csv" and "row" in metadata:
            row = metadata["row"]
            if row == 0:
                parts.append("(Summary)")
            else:
                parts.append(f"Row: {row}")

        return " | ".join(parts)

    def _extract_citations(self, metadatas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract citation information from metadatas.

        Args:
            metadatas: List of metadata dictionaries

        Returns:
            List of citation dictionaries
        """
        citations = []

        for i, metadata in enumerate(metadatas, start=1):
            citation = {
                "source_number": i,
                "filename": metadata.get("filename", "Unknown"),
                "file_type": metadata.get("file_type", ""),
                "chunk_id": metadata.get("doc_id", "") + f"_chunk_{i}",
            }

            # Add file-type specific info
            if "page" in metadata:
                citation["page"] = metadata["page"]
            if "section" in metadata:
                citation["section"] = metadata["section"]
            if "row" in metadata:
                citation["row"] = metadata["row"]

            citations.append(citation)

        return citations
