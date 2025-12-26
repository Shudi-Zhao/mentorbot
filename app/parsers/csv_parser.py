"""CSV document parser."""
import hashlib
from pathlib import Path
from typing import Dict, List
import pandas as pd


class CSVParser:
    """Parser for CSV documents."""

    @staticmethod
    def parse(file_path: Path) -> List[Dict[str, str]]:
        """
        Parse a CSV file and convert rows to text format.

        Args:
            file_path: Path to the CSV file

        Returns:
            List of dictionaries with row-level metadata and content
        """
        try:
            # Read CSV
            df = pd.read_csv(file_path)

            # Calculate content hash
            with open(file_path, "rb") as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()

            parsed_rows = []

            # First, add a summary of the CSV structure
            summary = CSVParser._create_summary(df, file_path)
            parsed_rows.append(summary)

            # Then add individual rows
            for idx, row in df.iterrows():
                # Convert row to readable text
                row_text = CSVParser._row_to_text(row, df.columns)

                parsed_rows.append(
                    {
                        "doc_id": file_path.stem,
                        "filename": file_path.name,
                        "source": str(file_path),
                        "row": idx + 2,  # +2 because of header row and 0-indexing
                        "total_rows": len(df) + 1,  # +1 for header
                        "content": row_text,
                        "content_hash": content_hash,
                        "file_type": "csv",
                    }
                )

            return parsed_rows

        except Exception as e:
            raise ValueError(f"Error parsing CSV {file_path.name}: {str(e)}")

    @staticmethod
    def _create_summary(df: pd.DataFrame, file_path: Path) -> Dict[str, str]:
        """Create a summary of the CSV structure."""
        columns_info = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])

        summary_text = f"""CSV File Summary:
Filename: {file_path.name}
Total Rows: {len(df)}
Total Columns: {len(df.columns)}
Columns: {columns_info}

Sample Data (first 3 rows):
{df.head(3).to_string(index=False)}
"""

        with open(file_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()

        return {
            "doc_id": file_path.stem,
            "filename": file_path.name,
            "source": str(file_path),
            "row": 0,  # Summary row
            "total_rows": len(df) + 1,
            "content": summary_text,
            "content_hash": content_hash,
            "file_type": "csv",
        }

    @staticmethod
    def _row_to_text(row: pd.Series, columns: pd.Index) -> str:
        """Convert a DataFrame row to readable text."""
        parts = []
        for col in columns:
            value = row[col]
            # Skip NaN values
            if pd.notna(value):
                parts.append(f"{col}: {value}")

        return " | ".join(parts)
