"""Automatic cleanup utilities for temporary data management."""
import os
import time
from pathlib import Path
from typing import Optional
import logging
import shutil

logger = logging.getLogger(__name__)


class DataCleanupManager:
    """Manages automatic cleanup of uploaded files and database."""

    def __init__(self, upload_dir: Path, chroma_dir: Path, max_age_hours: float = 1.0):
        """
        Initialize cleanup manager.

        Args:
            upload_dir: Directory for uploaded files
            chroma_dir: Directory for ChromaDB
            max_age_hours: Maximum age of files in hours before cleanup (supports decimals)
        """
        self.upload_dir = upload_dir
        self.chroma_dir = chroma_dir
        self.max_age_seconds = max_age_hours * 3600

    def cleanup_old_uploads(self) -> tuple[int, int]:
        """
        Remove uploaded files older than max_age_hours.

        Returns:
            Tuple of (files_deleted, bytes_freed)
        """
        files_deleted = 0
        bytes_freed = 0
        current_time = time.time()

        try:
            for file_path in self.upload_dir.glob("*"):
                if file_path.name == ".gitkeep":
                    continue

                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > self.max_age_seconds:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_deleted += 1
                        bytes_freed += file_size
                        logger.info(f"Deleted old file: {file_path.name} (age: {file_age/3600:.1f}h)")

        except Exception as e:
            logger.error(f"Error during upload cleanup: {e}")

        return files_deleted, bytes_freed

    def cleanup_old_chroma_data(self) -> bool:
        """
        Remove ChromaDB data older than max_age_hours.

        Returns:
            True if cleanup was performed
        """
        try:
            # Check if chroma directory has old data
            chroma_db_file = self.chroma_dir / "chroma.sqlite3"
            if chroma_db_file.exists():
                current_time = time.time()
                db_age = current_time - chroma_db_file.stat().st_mtime

                if db_age > self.max_age_seconds:
                    # Remove all ChromaDB data
                    for item in self.chroma_dir.glob("*"):
                        if item.name == ".gitkeep":
                            continue
                        if item.is_file():
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)
                    logger.info(f"Cleaned ChromaDB data (age: {db_age/3600:.1f}h)")
                    return True

        except Exception as e:
            logger.error(f"Error during ChromaDB cleanup: {e}")

        return False

    def get_storage_usage(self) -> dict:
        """
        Get current storage usage statistics.

        Returns:
            Dictionary with storage stats
        """
        stats = {
            "upload_count": 0,
            "upload_size_mb": 0,
            "chroma_size_mb": 0,
            "total_size_mb": 0,
        }

        try:
            # Count uploads
            for file_path in self.upload_dir.glob("*"):
                if file_path.is_file() and file_path.name != ".gitkeep":
                    stats["upload_count"] += 1
                    stats["upload_size_mb"] += file_path.stat().st_size / (1024 * 1024)

            # Count ChromaDB size
            for item in self.chroma_dir.rglob("*"):
                if item.is_file() and item.name != ".gitkeep":
                    stats["chroma_size_mb"] += item.stat().st_size / (1024 * 1024)

            stats["total_size_mb"] = stats["upload_size_mb"] + stats["chroma_size_mb"]

        except Exception as e:
            logger.error(f"Error calculating storage usage: {e}")

        return stats

    def enforce_storage_limits(self, max_size_mb: int = 100) -> bool:
        """
        Enforce storage limits by cleaning up if exceeded.

        Args:
            max_size_mb: Maximum total storage in MB

        Returns:
            True if cleanup was performed
        """
        stats = self.get_storage_usage()

        if stats["total_size_mb"] > max_size_mb:
            logger.warning(f"Storage limit exceeded: {stats['total_size_mb']:.1f}MB > {max_size_mb}MB")

            # Clean up oldest files first
            self.cleanup_old_uploads()
            self.cleanup_old_chroma_data()
            return True

        return False

    def full_cleanup(self) -> dict:
        """
        Perform full cleanup of all temporary data.

        Returns:
            Dictionary with cleanup results
        """
        results = {
            "uploads_deleted": 0,
            "bytes_freed": 0,
            "chroma_cleaned": False,
        }

        try:
            # Clean uploads
            files_deleted, bytes_freed = self.cleanup_old_uploads()
            results["uploads_deleted"] = files_deleted
            results["bytes_freed"] = bytes_freed

            # Clean ChromaDB
            results["chroma_cleaned"] = self.cleanup_old_chroma_data()

            logger.info(f"Full cleanup completed: {results}")

        except Exception as e:
            logger.error(f"Error during full cleanup: {e}")

        return results


def schedule_cleanup(cleanup_manager: DataCleanupManager, interval_minutes: int = 60):
    """
    Background cleanup scheduler (for production deployment).

    Args:
        cleanup_manager: CleanupManager instance
        interval_minutes: Cleanup interval in minutes
    """
    import threading

    def cleanup_job():
        while True:
            time.sleep(interval_minutes * 60)
            logger.info("Running scheduled cleanup...")
            cleanup_manager.full_cleanup()
            cleanup_manager.enforce_storage_limits()

    thread = threading.Thread(target=cleanup_job, daemon=True)
    thread.start()
    logger.info(f"Cleanup scheduler started (interval: {interval_minutes} minutes)")
