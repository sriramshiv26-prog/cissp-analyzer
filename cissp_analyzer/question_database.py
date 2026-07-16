#!/usr/bin/env python3
"""
Question Database - Phase 2 Integration
Extracts questions from PDF and saves for later lookup.
Provides indexing and search capabilities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from cissp_analyzer.pdf_parser import PDFParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuestionDatabase:
    """Manages extracted questions for an exam."""

    def __init__(self, exam_folder: Path):
        """
        Initialize QuestionDatabase for an exam.

        Args:
            exam_folder: Path to exam folder
        """
        self.exam_folder = Path(exam_folder)
        self.db_dir = self.exam_folder / "questions_db"
        self.db_dir.mkdir(exist_ok=True)
        self.questions: Dict[int, Dict] = {}
        self.metadata = {}

    def extract_from_pdf(self, pdf_path: str) -> Dict[int, Dict]:
        """
        Extract questions from PDF and save to database.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary of extracted questions indexed by question number
        """
        try:
            logger.info(f"Extracting questions from: {pdf_path}")
            parser = PDFParser(pdf_path)
            extracted = parser.extract_questions()

            if not extracted:
                logger.warning("No questions extracted from PDF")
                return {}

            # Index questions by number
            questions = {}
            for question in extracted:
                q_num = question.get("question_number")
                if q_num:
                    questions[q_num] = question

            logger.info(f"✓ Extracted {len(questions)} questions from PDF")

            # Save to database
            self._save_questions(questions)
            self.questions = questions

            return questions

        except Exception as e:
            logger.error(f"Error extracting questions: {str(e)}")
            raise

    def load_questions(self) -> Dict[int, Dict]:
        """
        Load questions from saved database.

        Returns:
            Dictionary of questions
        """
        db_file = self.db_dir / "questions.json"

        if not db_file.exists():
            logger.warning("No questions database found")
            return {}

        try:
            with open(db_file, "r") as f:
                data = json.load(f)
                # Convert string keys to integers
                questions = {int(k): v for k, v in data.items()}
                self.questions = questions
                logger.info(f"Loaded {len(questions)} questions from database")
                return questions
        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            return {}

    def get_question(self, question_number: int) -> Optional[Dict]:
        """
        Get a specific question by number.

        Args:
            question_number: Question number to retrieve

        Returns:
            Question dictionary or None if not found
        """
        if not self.questions:
            self.load_questions()

        return self.questions.get(question_number)

    def get_all_questions(self) -> Dict[int, Dict]:
        """Get all questions in the database."""
        if not self.questions:
            self.load_questions()
        return self.questions

    def validate_extraction(self, total_expected: Optional[int] = None) -> tuple:
        """
        Validate that extraction was successful.

        Args:
            total_expected: Expected total number of questions (optional)

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.questions:
            self.load_questions()

        if not self.questions:
            errors.append("No questions extracted")
            return False, errors

        # Check for basic structure
        for q_num, question in self.questions.items():
            if "question_text" not in question and "text" not in question:
                errors.append(f"Q{q_num}: Missing question text")

            # Check for options
            has_options = False
            for opt in ["A", "B", "C", "D"]:
                if opt in question:
                    has_options = True
                    break

            if not has_options:
                errors.append(f"Q{q_num}: Missing answer options")

        # Check for expected total if provided
        if total_expected:
            if len(self.questions) < total_expected * 0.8:  # Allow 20% margin
                errors.append(
                    f"Low extraction rate: {len(self.questions)}/{total_expected} "
                    f"({len(self.questions)/total_expected*100:.0f}%)"
                )

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_question_count(self) -> int:
        """Get total number of questions extracted."""
        if not self.questions:
            self.load_questions()
        return len(self.questions)

    def search_by_text(self, search_term: str) -> List[tuple]:
        """
        Search questions by text content.

        Args:
            search_term: Text to search for (case-insensitive)

        Returns:
            List of (question_number, question) tuples matching search
        """
        if not self.questions:
            self.load_questions()

        search_lower = search_term.lower()
        results = []

        for q_num, question in self.questions.items():
            text_fields = [
                question.get("question_text", ""),
                question.get("text", ""),
                str(question.get("A", "")),
                str(question.get("B", "")),
                str(question.get("C", "")),
                str(question.get("D", "")),
            ]

            combined_text = " ".join(text_fields).lower()
            if search_lower in combined_text:
                results.append((q_num, question))

        return results

    def export_metadata(self) -> Dict:
        """
        Export metadata about the question database.

        Returns:
            Dictionary with extraction metadata
        """
        if not self.questions:
            self.load_questions()

        metadata = {
            "total_questions": len(self.questions),
            "question_numbers": sorted(self.questions.keys()),
            "extraction_timestamp": __import__("datetime").datetime.now().isoformat(),
            "has_options": all(
                any(opt in q for opt in ["A", "B", "C", "D"])
                for q in self.questions.values()
            ),
        }

        return metadata

    def _save_questions(self, questions: Dict[int, Dict]) -> Path:
        """
        Save questions to database file.

        Args:
            questions: Questions dictionary to save

        Returns:
            Path to saved file
        """
        db_file = self.db_dir / "questions.json"

        # Convert integer keys to strings for JSON
        json_data = {str(k): v for k, v in questions.items()}

        with open(db_file, "w") as f:
            json.dump(json_data, f, indent=2)

        # Save metadata
        metadata = {
            "total_questions": len(questions),
            "extracted_at": __import__("datetime").datetime.now().isoformat(),
            "question_numbers": sorted(questions.keys()),
        }

        metadata_file = self.db_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✓ Saved {len(questions)} questions to {db_file}")
        return db_file
