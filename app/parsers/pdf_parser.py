"""PDF document parser."""
import hashlib
from pathlib import Path
from typing import Dict, List
from pypdf import PdfReader


class PDFParser:
    """Parser for PDF documents."""

    @staticmethod
    def parse(file_path: Path) -> List[Dict[str, str]]:
        """
        Parse a PDF file and extract text content by page.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of dictionaries with page-level metadata and content
        """
        try:
            reader = PdfReader(str(file_path))
            pages = []

            # Calculate content hash for the entire file
            with open(file_path, "rb") as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()

            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()

                if text.strip():  # Only include pages with text
                    pages.append(
                        {
                            "doc_id": file_path.stem,
                            "filename": file_path.name,
                            "source": str(file_path),
                            "page": page_num,
                            "total_pages": len(reader.pages),
                            "content": text,
                            "content_hash": content_hash,
                            "file_type": "pdf",
                        }
                    )

            return pages

        except Exception as e:
            raise ValueError(f"Error parsing PDF {file_path.name}: {str(e)}")
