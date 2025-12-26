"""Markdown document parser."""
import hashlib
import re
from pathlib import Path
from typing import Dict, List


class MarkdownParser:
    """Parser for Markdown documents."""

    @staticmethod
    def parse(file_path: Path) -> List[Dict[str, str]]:
        """
        Parse a Markdown file and extract content by sections.

        Args:
            file_path: Path to the Markdown file

        Returns:
            List of dictionaries with section-level metadata and content
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Calculate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Split by headers (# Header) to get sections
            sections = MarkdownParser._split_by_sections(content)

            parsed_sections = []
            for idx, (section_title, section_content) in enumerate(sections, start=1):
                if section_content.strip():
                    parsed_sections.append(
                        {
                            "doc_id": file_path.stem,
                            "filename": file_path.name,
                            "source": str(file_path),
                            "section": section_title or f"Section {idx}",
                            "section_number": idx,
                            "content": section_content,
                            "content_hash": content_hash,
                            "file_type": "markdown",
                        }
                    )

            # If no sections found, return entire content
            if not parsed_sections:
                parsed_sections.append(
                    {
                        "doc_id": file_path.stem,
                        "filename": file_path.name,
                        "source": str(file_path),
                        "section": "Full Document",
                        "section_number": 1,
                        "content": content,
                        "content_hash": content_hash,
                        "file_type": "markdown",
                    }
                )

            return parsed_sections

        except Exception as e:
            raise ValueError(f"Error parsing Markdown {file_path.name}: {str(e)}")

    @staticmethod
    def _split_by_sections(content: str) -> List[tuple]:
        """
        Split markdown content by headers.

        Returns:
            List of (header_title, section_content) tuples
        """
        # Pattern to match markdown headers (# Header)
        header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

        sections = []
        last_pos = 0
        last_title = None

        for match in header_pattern.finditer(content):
            # Add previous section if exists
            if last_pos > 0:
                section_content = content[last_pos : match.start()].strip()
                sections.append((last_title, section_content))

            last_title = match.group(2).strip()
            last_pos = match.end()

        # Add last section
        if last_pos > 0:
            section_content = content[last_pos:].strip()
            sections.append((last_title, section_content))
        elif not sections:
            # No headers found, return full content
            sections.append((None, content))

        return sections
