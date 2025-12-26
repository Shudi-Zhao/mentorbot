"""ChromaDB vector database service."""
from typing import Dict, List, Optional, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)


class ChromaService:
    """Service for managing ChromaDB vector database."""

    def __init__(self, persist_directory: Path, collection_name: str = "rag_documents"):
        """
        Initialize ChromaDB service.

        Args:
            persist_directory: Directory for ChromaDB persistence
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=str(persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "RAG document chunks with embeddings"},
        )

        logger.info(f"ChromaDB initialized at {persist_directory}")
        logger.info(f"Collection '{collection_name}' has {self.collection.count()} documents")

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """
        Add chunks with embeddings to the collection.

        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
        """
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to add")
            return

        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) length mismatch")

        # Prepare data for ChromaDB
        ids = []
        documents = []
        metadatas = []

        for chunk, embedding in zip(chunks, embeddings):
            chunk_id = chunk.get("chunk_id", "")
            chunk_text = chunk.get("chunk_text", "")

            if not chunk_id or not chunk_text:
                logger.warning(f"Skipping chunk with missing id or text: {chunk}")
                continue

            # Prepare metadata (exclude large text fields)
            metadata = {
                "doc_id": chunk.get("doc_id", ""),
                "filename": chunk.get("filename", ""),
                "source": chunk.get("source", ""),
                "content_hash": chunk.get("content_hash", ""),
                "file_type": chunk.get("file_type", ""),
                "chunk_index": chunk.get("chunk_index", 0),
                "total_tokens": chunk.get("total_tokens", 0),
            }

            # Add file-type specific metadata
            if "page" in chunk:
                metadata["page"] = chunk["page"]
            if "section" in chunk:
                metadata["section"] = chunk["section"]
            if "row" in chunk:
                metadata["row"] = chunk["row"]

            ids.append(chunk_id)
            documents.append(chunk_text)
            metadatas.append(metadata)

        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings[: len(ids)],  # Match the filtered length
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Added {len(ids)} chunks to collection '{self.collection_name}'")

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Query the collection with an embedding.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_metadata: Optional metadata filter

        Returns:
            Query results with documents, metadata, and distances
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata,
            include=["documents", "metadatas", "distances"],
        )

        # Flatten single query results
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
        }

    def get_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.

        Args:
            doc_id: Document ID

        Returns:
            List of chunks with metadata
        """
        results = self.collection.get(
            where={"doc_id": doc_id},
            include=["documents", "metadatas"],
        )

        chunks = []
        if results["documents"]:
            for doc, metadata in zip(results["documents"], results["metadatas"]):
                chunks.append({"document": doc, "metadata": metadata})

        return chunks

    def delete_by_doc_id(self, doc_id: str) -> int:
        """
        Delete all chunks for a specific document.

        Args:
            doc_id: Document ID

        Returns:
            Number of chunks deleted
        """
        # Get chunks to count them
        chunks = self.get_by_doc_id(doc_id)
        count = len(chunks)

        if count > 0:
            self.collection.delete(where={"doc_id": doc_id})
            logger.info(f"Deleted {count} chunks for doc_id '{doc_id}'")

        return count

    def check_document_exists(self, content_hash: str) -> bool:
        """
        Check if a document with the given content hash exists.

        Args:
            content_hash: Content hash of the document

        Returns:
            True if document exists, False otherwise
        """
        results = self.collection.get(
            where={"content_hash": content_hash},
            limit=1,
        )

        return len(results["ids"]) > 0

    def reset_collection(self) -> None:
        """Delete and recreate the collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "RAG document chunks with embeddings"},
        )
        logger.info(f"Collection '{self.collection_name}' reset")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.

        Returns:
            Dictionary with collection stats
        """
        count = self.collection.count()

        # Get unique doc_ids
        all_docs = self.collection.get(include=["metadatas"])
        doc_ids = set()
        file_types = {}

        if all_docs["metadatas"]:
            for metadata in all_docs["metadatas"]:
                doc_id = metadata.get("doc_id", "")
                if doc_id:
                    doc_ids.add(doc_id)

                file_type = metadata.get("file_type", "unknown")
                file_types[file_type] = file_types.get(file_type, 0) + 1

        return {
            "total_chunks": count,
            "total_documents": len(doc_ids),
            "file_types": file_types,
            "collection_name": self.collection_name,
        }
