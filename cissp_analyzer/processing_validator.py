#!/usr/bin/env python3
"""
Processing Validator - Comprehensive validation for exam processing pipeline.
Validates answer sheets, folder structures, PDFs, and data consistency.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingValidator:
    """Validates exam data and processing pipeline integrity."""

    # Required columns in answer sheets (case-insensitive)
    REQUIRED_COLUMNS = ["question", "answer"]

    # Valid answer formats
    VALID_ANSWER_PATTERN = re.compile(r"^[A-D]$|^\d+-[A-D](,\d+-[A-D])*$")

    def __init__(self):
        """Initialize ProcessingValidator with validation rules."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_answer_sheet(self, excel_path: str) -> Tuple[bool, str]:
        """
        Validate Excel answer sheet format and contents.

        Args:
            excel_path: Path to Excel file

        Returns:
            (is_valid, error_message)
        """
        excel_file = Path(excel_path)

        # Check file exists
        if not excel_file.exists():
            msg = f"File not found: {excel_path}"
            logger.error(msg)
            return False, msg

        # Check file extension
        if excel_file.suffix.lower() != ".xlsx":
            msg = f"File must be .xlsx format, got: {excel_file.suffix}"
            logger.error(msg)
            return False, msg

        # Check file is readable
        if not excel_file.is_file():
            msg = f"Path is not a file: {excel_path}"
            logger.error(msg)
            return False, msg

        try:
            import pandas as pd

            df = pd.read_excel(excel_file)

            # Check not empty
            if df.empty:
                msg = "Excel file is empty"
                logger.error(msg)
                return False, msg

            # Check has required columns (case-insensitive)
            df_columns_lower = [col.lower() for col in df.columns]
            missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df_columns_lower]

            if missing_columns:
                msg = f"Missing required columns: {missing_columns}. " f"Found: {list(df.columns)}"
                logger.error(msg)
                return False, msg

            # Check for empty rows in critical columns
            question_col = self._find_column_case_insensitive(df.columns, "question")
            answer_col = self._find_column_case_insensitive(df.columns, "answer")

            if not question_col or not answer_col:
                msg = "Could not find question or answer columns"
                logger.error(msg)
                return False, msg

            empty_questions = df[question_col].isna().sum()
            empty_answers = df[answer_col].isna().sum()

            if empty_questions > 0 or empty_answers > 0:
                msg = (
                    f"Found empty cells: {empty_questions} empty questions, "
                    f"{empty_answers} empty answers"
                )
                logger.warning(msg)
                self.warnings.append(msg)

            logger.info(f"✓ Answer sheet valid: {excel_file.name}")
            return True, ""

        except Exception as e:
            msg = f"Error reading Excel file: {str(e)}"
            logger.error(msg)
            return False, msg

    def validate_question_match(
        self,
        answers: Dict[int, str],
        questions: List[Dict],
    ) -> Tuple[bool, List]:
        """
        Validate answers match available questions.

        Args:
            answers: Dictionary {question_number: answer_letter}
            questions: List of question dictionaries with 'number' key

        Returns:
            (is_valid, list_of_mismatches)
        """
        mismatches = []

        if not questions:
            msg = "No questions available for validation"
            logger.warning(msg)
            return False, [msg]

        if not answers:
            msg = "No answers provided"
            logger.warning(msg)
            return False, [msg]

        # Get valid question numbers
        valid_q_numbers = {q.get("number", i) for i, q in enumerate(questions)}

        # Check all answer question IDs exist in questions
        for q_num in answers.keys():
            if q_num not in valid_q_numbers:
                mismatch = f"Answer for non-existent question: Q{q_num}"
                mismatches.append(mismatch)
                logger.warning(mismatch)

        # Check answer format (A-D or multi-part)
        for q_num, answer in answers.items():
            if not self._is_valid_answer_format(answer):
                mismatch = (
                    f"Invalid answer format for Q{q_num}: '{answer}' (expected A-D or multi-part)"
                )
                mismatches.append(mismatch)
                logger.warning(mismatch)

        is_valid = len(mismatches) == 0
        if is_valid:
            logger.info(f"✓ Questions match valid ({len(answers)} answers)")
        else:
            logger.error(f"✗ Question mismatch found ({len(mismatches)} issues)")

        return is_valid, mismatches

    def check_duplicate_student_names(self, names: List[str]) -> List[str]:
        """
        Find duplicate student names.

        Args:
            names: List of student names

        Returns:
            List of duplicate names (empty if no duplicates)
        """
        if not names:
            return []

        # Count occurrences
        name_counts: Dict[str, int] = {}
        for name in names:
            name_lower = name.lower().strip()
            name_counts[name_lower] = name_counts.get(name_lower, 0) + 1

        # Find duplicates
        duplicates = [name for name, count in name_counts.items() if count > 1]

        if duplicates:
            logger.warning(f"Found duplicate student names: {duplicates}")
        else:
            logger.info(f"✓ No duplicate student names ({len(names)} students)")

        return duplicates

    def validate_folder_structure(self, exam_folder: Path) -> Tuple[bool, str]:
        """
        Validate exam folder structure.

        Checks:
        - exam_folder exists and is directory
        - .exam_metadata.json exists and is valid
        - reports/ directory exists
        - exam.pdf exists

        Args:
            exam_folder: Path to exam folder

        Returns:
            (is_valid, error_message)
        """
        exam_folder = Path(exam_folder)

        # Check folder exists
        if not exam_folder.exists():
            msg = f"Exam folder not found: {exam_folder}"
            logger.error(msg)
            return False, msg

        if not exam_folder.is_dir():
            msg = f"Path is not a directory: {exam_folder}"
            logger.error(msg)
            return False, msg

        errors = []

        # Check metadata file
        metadata_file = exam_folder / ".exam_metadata.json"
        if not metadata_file.exists():
            errors.append(f"Missing metadata file: {metadata_file.name}")
        else:
            # Validate metadata JSON
            try:
                with open(metadata_file, "r") as f:
                    json.load(f)
                logger.info(f"✓ Metadata file valid")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid metadata JSON: {str(e)}")

        # Check PDF exists
        pdf_file = exam_folder / "exam.pdf"
        if not pdf_file.exists():
            errors.append(f"Missing PDF file: exam.pdf")
        else:
            logger.info(f"✓ PDF file exists")

        # Check/create reports directory
        reports_dir = exam_folder / "reports"
        if not reports_dir.exists():
            try:
                reports_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"✓ Created reports directory")
            except Exception as e:
                errors.append(f"Could not create reports directory: {str(e)}")

        # Compile results
        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"✗ Folder validation failed: {error_msg}")
            return False, error_msg

        logger.info(f"✓ Folder structure valid")
        return True, ""

    def validate_pdf(self, pdf_path: str) -> Tuple[bool, str]:
        """
        Validate PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            (is_valid, error_message)
        """
        pdf_file = Path(pdf_path)

        # Check file exists
        if not pdf_file.exists():
            msg = f"PDF file not found: {pdf_path}"
            logger.error(msg)
            return False, msg

        # Check file extension
        if pdf_file.suffix.lower() != ".pdf":
            msg = f"File is not a PDF: {pdf_file.suffix}"
            logger.error(msg)
            return False, msg

        # Check file is readable
        if not pdf_file.is_file():
            msg = f"Path is not a file: {pdf_path}"
            logger.error(msg)
            return False, msg

        try:
            from pypdf import PdfReader

            with open(pdf_file, "rb") as f:
                reader = PdfReader(f)

                # Check has pages
                if len(reader.pages) == 0:
                    msg = "PDF has no pages"
                    logger.error(msg)
                    return False, msg

                logger.info(f"✓ PDF valid ({len(reader.pages)} pages)")

        except Exception as e:
            msg = f"Invalid PDF file: {str(e)}"
            logger.error(msg)
            return False, msg

        # Try to extract questions (check if PDFParser works)
        try:
            from cissp_analyzer.pdf_parser import PDFParser

            parser = PDFParser(pdf_path)
            questions = parser.extract_questions()

            if not questions:
                logger.warning("Warning: Could not extract questions from PDF")
            else:
                logger.info(f"✓ Extracted {len(questions)} questions from PDF")

        except Exception as e:
            logger.warning(f"Could not extract questions: {str(e)}")
            # Don't fail - PDF might be valid but questions unextractable

        return True, ""

    def validate_all(
        self,
        exam_folder: Path,
        excel_path: Optional[str] = None,
        answers: Optional[Dict] = None,
        questions: Optional[List] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Run all validations.

        Args:
            exam_folder: Path to exam folder
            excel_path: Optional Excel file to validate
            answers: Optional answers dict to validate
            questions: Optional questions list for matching

        Returns:
            (all_valid, list_of_errors)
        """
        self.errors = []
        self.warnings = []

        # Validate folder structure
        folder_valid, folder_error = self.validate_folder_structure(exam_folder)
        if not folder_valid:
            self.errors.append(folder_error)

        # Validate Excel if provided
        if excel_path:
            excel_valid, excel_error = self.validate_answer_sheet(excel_path)
            if not excel_valid:
                self.errors.append(excel_error)

        # Validate question match if provided
        if answers and questions:
            match_valid, mismatches = self.validate_question_match(answers, questions)
            if not match_valid:
                self.errors.extend(mismatches)

        all_valid = len(self.errors) == 0
        return all_valid, self.errors

    @staticmethod
    def _find_column_case_insensitive(columns: List[str], target: str) -> Optional[str]:
        """Find column name case-insensitively."""
        target_lower = target.lower()
        for col in columns:
            if col.lower() == target_lower:
                return col
        return None

    @staticmethod
    def _is_valid_answer_format(answer: str) -> bool:
        """Check if answer is valid format (A-D or multi-part)."""
        if not answer:
            return False

        answer_str = str(answer).upper().strip()

        # Single letter A-D
        if len(answer_str) == 1 and answer_str in "ABCD":
            return True

        # Multi-part: 1-A,2-B,3-C
        if re.match(r"^\d+-[A-D](,\d+-[A-D])*$", answer_str):
            return True

        return False

    def get_error_summary(self) -> str:
        """Get formatted summary of validation errors."""
        summary = "\n"
        if self.errors:
            summary += f"❌ Validation Errors ({len(self.errors)}):\n"
            for error in self.errors:
                summary += f"  • {error}\n"
        if self.warnings:
            summary += f"\n⚠️  Warnings ({len(self.warnings)}):\n"
            for warning in self.warnings:
                summary += f"  • {warning}\n"
        return summary if self.errors or self.warnings else "✓ All validations passed\n"
