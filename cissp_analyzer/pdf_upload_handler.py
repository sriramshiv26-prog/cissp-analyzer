#!/usr/bin/env python3
"""
PDF Upload Handler - Handles questionnaire PDF uploads and validation.
Manages file validation, metadata collection, and exam folder creation.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

from cissp_analyzer.exam_folder_manager import ExamFolderManager
from cissp_analyzer.menu_controller import MenuController


class PDFUploadHandler:
    """Handles PDF upload, validation, and exam folder creation."""

    def __init__(self, exam_folder_manager: Optional[ExamFolderManager] = None):
        """
        Initialize PDFUploadHandler.

        Args:
            exam_folder_manager: Optional ExamFolderManager instance
        """
        self.exam_manager = exam_folder_manager or ExamFolderManager()
        self.menu = MenuController()

    def handle_pdf_upload(self) -> Optional[Tuple[str, str]]:
        """
        Handle PDF upload workflow.

        Prompts user for file path, validates it, collects metadata,
        and creates exam folder.

        Returns:
            Tuple of (exam_name, folder_path) or None if cancelled
        """
        # Get PDF path from user
        pdf_path = self._prompt_pdf_path()
        if not pdf_path:
            self.menu.show_warning_message("PDF upload cancelled.")
            return None

        # Validate PDF
        if not self.validate_pdf(pdf_path):
            return None

        # Extract question count
        question_count = self.extract_question_count(pdf_path)

        # Get exam metadata from user
        metadata = self.prompt_exam_metadata()
        if not metadata:
            self.menu.show_warning_message("Exam setup cancelled.")
            return None

        # Create exam folder
        try:
            folder_path = self.exam_manager.create_exam_folder(
                exam_name=metadata["exam_name"],
                pdf_path=pdf_path,
            )

            self.menu.show_success_message(
                f"Questionnaire '{metadata['exam_name']}' created with "
                f"{question_count} questions. Folder: {folder_path}"
            )

            return (metadata["exam_name"], str(folder_path))

        except Exception as e:
            self.menu.show_error_message(f"Failed to create exam folder: {str(e)}")
            return None

    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if valid, False otherwise
        """
        pdf_file = Path(pdf_path)

        # Check file exists
        if not pdf_file.exists():
            self.menu.show_error_message(f"File not found: {pdf_path}")
            return False

        # Check file is PDF
        if pdf_file.suffix.lower() != ".pdf":
            self.menu.show_error_message("File must be a PDF (.pdf)")
            return False

        # Check file is readable
        if not os.access(pdf_file, os.R_OK):
            self.menu.show_error_message("PDF file is not readable")
            return False

        # Try to open with pypdf for basic validation
        try:
            from pypdf import PdfReader

            with open(pdf_file, "rb") as f:
                reader = PdfReader(f)
                if len(reader.pages) == 0:
                    self.menu.show_error_message("PDF has no pages")
                    return False

            self.menu.show_success_message(f"PDF validated: {len(reader.pages)} pages")
            return True

        except Exception as e:
            self.menu.show_error_message(f"Invalid PDF file: {str(e)}")
            return False

    def extract_question_count(self, pdf_path: str) -> int:
        """
        Extract total question count from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Number of questions (0 if unable to extract)
        """
        try:
            from cissp_analyzer.pdf_parser import PDFParser

            parser = PDFParser(pdf_path)
            questions = parser.extract_questions()
            count = len(questions)

            if count > 0:
                self.menu.show_info_message(f"Extracted {count} questions from PDF")
            else:
                self.menu.show_warning_message("Could not extract question count from PDF")

            return count

        except Exception as e:
            self.menu.show_warning_message(
                f"Error extracting questions: {str(e)}. Proceeding with unknown count."
            )
            return 0

    def prompt_exam_metadata(self) -> Optional[Dict]:
        """
        Prompt user for exam metadata.

        Returns:
            Dictionary with exam_name and description, or None if cancelled
        """
        print("\n" + "=" * 70)
        print("Questionnaire Metadata")
        print("=" * 70 + "\n")

        # Get exam name
        while True:
            exam_name = input("Exam name (e.g., CISSP_June_2026): ").strip()
            if exam_name:
                break
            print("Exam name cannot be empty.")

        # Get optional description
        description = input("Description (optional, press Enter to skip): ").strip()

        # Confirm
        print(f"\nExam Name: {exam_name}")
        print(f"Description: {description if description else '(none)'}")
        print()

        while True:
            confirm = input("Confirm? (y/n): ").strip().lower()
            if confirm == "y":
                return {
                    "exam_name": exam_name,
                    "description": description,
                }
            elif confirm == "n":
                return None
            else:
                print("Please enter 'y' or 'n'")

    def _prompt_pdf_path(self) -> Optional[str]:
        """
        Prompt user for PDF file path.

        Returns:
            Valid file path or None if cancelled
        """
        print("\n" + "=" * 70)
        print("Upload Questionnaire PDF")
        print("=" * 70 + "\n")

        pdf_path = input("Enter PDF file path (or drag/drop): ").strip()

        # Remove quotes if present (from drag/drop)
        pdf_path = pdf_path.strip("'\"")

        if not pdf_path:
            return None

        return pdf_path

    def create_exam_folder(
        self,
        exam_name: str,
        pdf_path: str,
        question_count: int = 0,
    ) -> Path:
        """
        Create exam folder with metadata.

        Args:
            exam_name: Name of the exam
            pdf_path: Path to PDF file
            question_count: Optional question count

        Returns:
            Path to created exam folder

        Raises:
            FileNotFoundError: If PDF not found
            ValueError: If parameters invalid
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not exam_name or not exam_name.strip():
            raise ValueError("Exam name cannot be empty")

        return self.exam_manager.create_exam_folder(
            exam_name=exam_name,
            pdf_path=pdf_path,
        )
