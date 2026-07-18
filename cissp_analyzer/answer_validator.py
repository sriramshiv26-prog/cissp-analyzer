#!/usr/bin/env python3
"""
Answer Validator - Phase 3G Enhancement
Validates student answers against an answer key and calculates actual scores.
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, List, Optional
import json
from pypdf import PdfReader
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerValidationResult:
    """Result of answer validation with detailed metrics."""

    def __init__(self):
        self.total_questions: int = 0
        self.submitted_answers: int = 0
        self.correct_answers: int = 0
        self.wrong_answers: int = 0
        self.unanswered: int = 0
        self.score_percentage: float = 0.0
        self.passed: bool = False
        self.pass_threshold: float = 75.0
        self.wrong_questions: List[Dict] = []
        self.answer_key: Dict[int, str] = {}
        self.student_answers: Dict[int, str] = {}


class AnswerValidator:
    """Validates student answers against PDF answer key."""

    def __init__(self, pdf_path: str):
        """
        Initialize validator with PDF containing answer key.

        Args:
            pdf_path: Path to PDF with embedded answer key

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF is invalid
        """
        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.answer_key = self._extract_answer_key()

        if not self.answer_key:
            raise ValueError("Could not extract answer key from PDF")

        logger.info(
            f"✓ Loaded answer key from PDF: {len(self.answer_key)} questions"
        )

    def _extract_answer_key(self) -> Dict[int, str]:
        """Extract answer key from PDF."""
        try:
            reader = PdfReader(str(self.pdf_path))
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text = text.replace("\t", "\n")
                    text_parts.append(text)

            all_text = "\n".join(text_parts)

            answer_key = {}

            # Split text into chunks around "The correct answer is"
            chunks = re.split(
                r"The\s+correct\s+answer\s+is\s+", all_text, flags=re.IGNORECASE
            )

            # For each chunk after the first
            for i, chunk in enumerate(chunks[1:], 1):
                # Get the answer (first character after "The correct answer is")
                answer_match = re.match(r"([A-D])", chunk)
                if not answer_match:
                    continue

                answer = answer_match.group(1).upper()

                # Look backwards to find the question number
                text_before = chunks[i - 1]
                q_matches = list(re.finditer(r"\n(\d+)\.\s", text_before))

                if q_matches:
                    q_num = int(q_matches[-1].group(1))
                    answer_key[q_num] = answer

            return answer_key

        except Exception as e:
            logger.error(f"Failed to extract answer key: {str(e)}")
            return {}

    def validate(
        self,
        student_answers: Dict[int, str],
        total_questions: Optional[int] = None,
    ) -> AnswerValidationResult:
        """
        Validate student answers against the answer key.

        Args:
            student_answers: Dict of question_number -> answer (A/B/C/D)
            total_questions: Total questions in exam (for context)

        Returns:
            AnswerValidationResult with detailed metrics
        """
        result = AnswerValidationResult()
        result.answer_key = self.answer_key
        result.student_answers = student_answers
        result.total_questions = total_questions or len(self.answer_key)

        logger.info(
            f"Validating {len(student_answers)} answers against "
            f"{len(self.answer_key)} answer key"
        )

        # Compare each answer
        for q_num in sorted(self.answer_key.keys()):
            if q_num not in student_answers:
                result.unanswered += 1
                continue

            result.submitted_answers += 1

            student_ans = student_answers[q_num].upper().strip()
            correct_ans = self.answer_key[q_num]

            if student_ans == correct_ans:
                result.correct_answers += 1
            else:
                result.wrong_answers += 1
                result.wrong_questions.append(
                    {
                        "question_number": q_num,
                        "submitted": student_ans,
                        "correct": correct_ans,
                    }
                )

        # Calculate score based only on questions with answer key
        if result.submitted_answers > 0:
            result.score_percentage = (
                result.correct_answers / result.submitted_answers * 100
            )
        else:
            result.score_percentage = 0.0

        result.passed = result.score_percentage >= result.pass_threshold

        logger.info(
            f"✓ Validation complete: {result.correct_answers}/"
            f"{result.submitted_answers} = {result.score_percentage:.1f}%"
        )

        return result

    def validate_batch(
        self, students_answers: Dict[str, Dict[int, str]]
    ) -> Dict[str, AnswerValidationResult]:
        """
        Validate multiple students at once.

        Args:
            students_answers: Dict of student_name -> answers_dict

        Returns:
            Dict of student_name -> AnswerValidationResult
        """
        results = {}

        for student_name, answers in students_answers.items():
            logger.info(f"Validating {student_name}...")
            results[student_name] = self.validate(answers)

        return results
