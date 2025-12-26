"""Configuration settings for the RAG application."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    CHROMA_DIR: Path = BASE_DIR / "data" / "chroma_db"

    # Embedding settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384  # all-MiniLM-L6-v2 dimension

    # Chunking settings
    DEFAULT_CHUNK_SIZE: int = 512  # tokens
    DEFAULT_CHUNK_OVERLAP: int = 50  # tokens
    MIN_CHUNK_SIZE: int = 100
    MAX_CHUNK_SIZE: int = 2000

    # Retrieval settings
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20

    # OpenAI settings
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 1000

    # ChromaDB settings
    CHROMA_COLLECTION_NAME: str = "rag_documents"

    # Supported file types
    SUPPORTED_EXTENSIONS: set = {".pdf", ".md", ".csv", ".txt"}

    # Cleanup settings (for portfolio/demo deployment)
    ENABLE_AUTO_CLEANUP: bool = Field(default=True, env="ENABLE_AUTO_CLEANUP")
    MAX_FILE_AGE_HOURS: float = Field(default=1.0, env="MAX_FILE_AGE_HOURS")  # Delete files older than X hours (supports decimals)
    MAX_STORAGE_MB: int = Field(default=100, env="MAX_STORAGE_MB")  # Max 100MB total storage
    MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")  # Max 10MB per file
    CLEANUP_INTERVAL_MINUTES: int = Field(default=30, env="CLEANUP_INTERVAL_MINUTES")  # Run cleanup every 30 min

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
