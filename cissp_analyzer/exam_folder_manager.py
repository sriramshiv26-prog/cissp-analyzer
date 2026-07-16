#!/usr/bin/env python3
"""
Exam Folder Manager - Manages exam folder structure and metadata.
Handles creation, listing, and organization of exam questionnaires.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class ExamFolderManager:
    """Manages exam folders and their metadata."""

    def __init__(self, base_dir: str = "exams"):
        """Initialize ExamFolderManager with a base directory."""
        self.base_dir = base_dir
        self._create_base_dir()

    def _create_base_dir(self) -> None:
        """Create base directory if it doesn't exist."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def list_exams(self) -> List[Dict]:
        """
        List all exam folders with their metadata.

        Returns:
            List of dictionaries containing exam information
        """
        exam_folders: List[Dict] = []
        if not os.path.exists(self.base_dir):
            return exam_folders

        for folder in os.listdir(self.base_dir):
            folder_path = Path(self.base_dir) / folder
            if not folder_path.is_dir():
                continue

            metadata_file_path = folder_path / ".exam_metadata.json"
            if metadata_file_path.exists():
                try:
                    with open(metadata_file_path, "r") as file:
                        metadata = json.load(file)
                        metadata["path"] = str(folder_path)
                        exam_folders.append(metadata)
                except json.JSONDecodeError:
                    continue

        return exam_folders

    def get_exam_metadata(self, exam_id: str) -> Dict:
        """
        Get metadata for a specific exam.

        Args:
            exam_id: The exam folder ID/name

        Returns:
            Dictionary containing exam metadata

        Raises:
            FileNotFoundError: If exam metadata file not found
        """
        exam_folder_path = Path(self.base_dir) / exam_id
        metadata_file_path = exam_folder_path / ".exam_metadata.json"

        if metadata_file_path.exists():
            with open(metadata_file_path, "r") as file:
                return json.load(file)
        else:
            raise FileNotFoundError(f"Metadata file not found for exam ID: {exam_id}")

    def create_exam_folder(self, exam_name: str, pdf_path: str) -> Path:
        """
        Create a new exam folder with metadata.

        Args:
            exam_name: Name of the exam
            pdf_path: Path to the exam PDF file

        Returns:
            Path to the created exam folder
        """
        exam_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = self._sanitize_name(exam_name)
        folder_path = Path(self.base_dir) / f"{folder_name}_{exam_date}"

        # Create the folder
        os.makedirs(folder_path, exist_ok=True)

        # Copy PDF to the folder
        pdf_destination = folder_path / "exam.pdf"
        shutil.copy(pdf_path, pdf_destination)

        # Create metadata file
        metadata = {
            "exam_name": exam_name,
            "pdf_path": str(pdf_path),
            "created_date": exam_date,
            "total_questions": self._extract_total_questions_from_pdf(pdf_path),
            "folder_id": f"{folder_name}_{exam_date}",
        }

        with open(folder_path / ".exam_metadata.json", "w") as file:
            json.dump(metadata, file, indent=2)

        return folder_path

    def get_new_answer_files(self, exam_id: str) -> List[str]:
        """
        Get list of Excel answer files in exam folder.

        Args:
            exam_id: The exam folder ID

        Returns:
            List of Excel filenames
        """
        folder_path = Path(self.base_dir) / exam_id
        answer_files: List[str] = []

        if not folder_path.exists():
            return answer_files

        for filename in os.listdir(folder_path):
            if filename.endswith(".xlsx") and not filename.startswith("~"):
                answer_files.append(filename)

        return sorted(answer_files)

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize name for use as folder name.

        Args:
            name: Name to sanitize

        Returns:
            Sanitized name (max 50 chars, no special chars)
        """
        import re

        sanitized = re.sub(r"[^\w\-_]", "_", name)
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized.strip()

    def _extract_total_questions_from_pdf(self, pdf_path: str) -> int:
        """
        Extract total number of questions from PDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Number of questions (0 if not determinable)
        """
        try:
            from cissp_analyzer.pdf_parser import PDFParser

            parser = PDFParser(pdf_path)
            questions = parser.extract_questions()
            return len(questions)
        except Exception:
            # Fallback if PDF parsing fails
            return 0
