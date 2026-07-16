#!/usr/bin/env python3
"""
State Tracker - Tracks processed files to prevent re-processing.
Maintains a .processed.json file in each exam folder to record which
answer sheets have been analyzed.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ProcessedFileTracker:
    """Tracks which files have been processed in an exam folder."""

    def __init__(self, exam_folder: Path):
        """
        Initialize ProcessedFileTracker with an exam folder.

        Args:
            exam_folder: Path to the exam folder
        """
        self.exam_folder = Path(exam_folder)
        self.processed_file = self.exam_folder / ".processed.json"
        self.processed_files: List[Dict] = self._load_processed_files()

    def _load_processed_files(self) -> List[Dict]:
        """
        Load processed files list from .processed.json.

        Returns:
            List of dictionaries with processed file information
        """
        if self.processed_file.exists():
            try:
                with open(self.processed_file, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []

    def _save_processed_files(self) -> None:
        """Save processed files list to .processed.json."""
        with open(self.processed_file, "w") as file:
            json.dump(self.processed_files, file, indent=2)

    def is_processed(self, filename: str) -> bool:
        """
        Check if a file has already been processed.

        Args:
            filename: The filename to check

        Returns:
            True if file has been processed, False otherwise
        """
        return any(record["filename"] == filename for record in self.processed_files)

    def mark_processed(
        self, filename: str, report_path: str, timestamp: Optional[str] = None
    ) -> None:
        """
        Mark a file as processed.

        Args:
            filename: The filename to mark as processed
            report_path: Path to the generated report
            timestamp: Optional timestamp (defaults to now if not provided)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        if not self.is_processed(filename):
            record = {
                "filename": filename,
                "report_path": report_path,
                "processed_date": timestamp,
            }
            self.processed_files.append(record)
            self._save_processed_files()

    def get_unprocessed_files(self, all_files: List[str]) -> List[str]:
        """
        Get list of files that have not been processed yet.

        Args:
            all_files: List of all filenames to check

        Returns:
            List of filenames that haven't been processed
        """
        processed_filenames = {record["filename"] for record in self.processed_files}
        return [f for f in all_files if f not in processed_filenames]

    def get_processing_history(self) -> List[Dict]:
        """
        Get the full processing history.

        Returns:
            List of dictionaries with file processing records
        """
        return self.processed_files.copy()

    def clear_history(self) -> None:
        """Clear all processing history (use with caution)."""
        self.processed_files = []
        self._save_processed_files()
