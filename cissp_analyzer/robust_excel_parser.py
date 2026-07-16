#!/usr/bin/env python3
"""
Robust Excel Parser - Phase 3B Enhancement
Handles multiple Excel formats with flexible column detection.
Supports various answer formats and provides detailed error messages.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobustExcelParserResult:
    """Result of Excel parsing with metadata."""

    def __init__(self):
        self.answers: Dict[int, str] = {}
        self.student_name: str = ""
        self.total_rows: int = 0
        self.valid_answers: int = 0
        self.skipped_answers: int = 0
        self.warnings: List[str] = []
        self.errors: List[str] = []
        self.column_mapping: Dict[str, str] = {}

    def validate_answers(self, total_questions: int) -> Tuple[bool, List[str]]:
        """
        Validate parsed answers.

        Args:
            total_questions: Expected total questions

        Returns:
            Tuple of (is_valid, error_list)
        """
        if not self.answers:
            return False, ["No answers found"]

        errors = []

        # Check answer count
        if len(self.answers) < total_questions * 0.5:
            errors.append(
                f"Too few answers: {len(self.answers)}/{total_questions} "
                f"({len(self.answers)/total_questions*100:.0f}%)"
            )

        return len(errors) == 0, errors


class RobustExcelParser:
    """Robust Excel file parsing with flexible column detection."""

    # Possible column name variations
    QUESTION_COLUMN_NAMES = [
        ["Question", "QUESTION"],
        ["Q", "Q#", "Qnum", "QuestionNumber"],
        ["Question Number", "Question_Number"],
        ["Qno", "Q_No", "Qu"],
    ]

    ANSWER_COLUMN_NAMES = [
        ["Answer", "ANSWER"],
        ["Ans", "ANS"],
        ["Student Answer", "StudentAnswer"],
        ["Student_Answer", "Response"],
        ["A"],  # Last resort
    ]

    STUDENT_COLUMN_NAMES = [
        ["Student", "STUDENT"],
        ["Student Name", "StudentName"],
        ["Student_Name", "Name"],
        ["Participant", "User"],
        ["Email"],  # If no student name, use email
    ]

    # Answer format variations
    ANSWER_VARIATIONS = {
        "A": ["A", "a", "answer_a", "choice_a", "1"],
        "B": ["B", "b", "answer_b", "choice_b", "2"],
        "C": ["C", "c", "answer_c", "choice_c", "3"],
        "D": ["D", "d", "answer_d", "choice_d", "4"],
    }

    def __init__(self, excel_path: str):
        """
        Initialize robust Excel parser.

        Args:
            excel_path: Path to Excel file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not valid Excel
        """
        self.excel_path = Path(excel_path)

        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        try:
            self.df = pd.read_excel(excel_path)
            logger.info(f"✓ Loaded Excel: {self.excel_path.name} ({len(self.df)} rows)")

        except Exception as e:
            raise ValueError(f"Invalid Excel file: {str(e)}")

    def parse_with_fallback(self, student_name: Optional[str] = None) -> RobustExcelParserResult:
        """
        Parse Excel file with fallback strategies.

        Args:
            student_name: Override student name from file

        Returns:
            RobustExcelParserResult with answers and metadata
        """
        result = RobustExcelParserResult()

        logger.info("Starting Excel parsing with fallback strategies...")

        # Step 1: Detect columns
        logger.info("Step 1: Detecting columns...")
        question_col, answer_col, student_col = self._detect_columns(result)

        if not question_col or not answer_col:
            logger.error("✗ Could not detect question/answer columns")
            result.errors.append("Could not detect question/answer columns in Excel")
            return result

        result.column_mapping = {
            "question": question_col,
            "answer": answer_col,
            "student": student_col or "unknown",
        }

        logger.info(f"✓ Columns detected: Q={question_col}, A={answer_col}, S={student_col}")

        # Step 2: Extract student name
        if student_name:
            result.student_name = student_name
        elif student_col:
            result.student_name = self._extract_student_name(student_col)

        if not result.student_name:
            result.student_name = self.excel_path.stem

        # Step 3: Parse answers
        logger.info("Step 3: Parsing answers...")
        result = self._parse_answers(question_col, answer_col, result)

        if result.valid_answers == 0:
            logger.error("✗ No valid answers found")
            result.errors.append("No valid answers extracted from file")
        else:
            logger.info(
                f"✓ Parsed {result.valid_answers} answers "
                f"({result.skipped_answers} skipped)"
            )

        return result

    def _detect_columns(self, result: RobustExcelParserResult) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Detect column names using fuzzy matching.

        Returns:
            Tuple of (question_col, answer_col, student_col)
        """
        columns_lower = {col.lower(): col for col in self.df.columns}

        question_col = self._find_column(
            columns_lower, self.QUESTION_COLUMN_NAMES
        )
        answer_col = self._find_column(columns_lower, self.ANSWER_COLUMN_NAMES)
        student_col = self._find_column(columns_lower, self.STUDENT_COLUMN_NAMES)

        return question_col, answer_col, student_col

    def _find_column(
        self,
        columns_lower: Dict[str, str],
        candidate_lists: List[List[str]],
    ) -> Optional[str]:
        """Find column using candidate names."""
        for candidates in candidate_lists:
            for candidate in candidates:
                if candidate.lower() in columns_lower:
                    actual_col = columns_lower[candidate.lower()]
                    logger.debug(f"  Matched column '{candidate}' → '{actual_col}'")
                    return actual_col

        return None

    def _extract_student_name(self, student_col: str) -> Optional[str]:
        """Extract student name from column."""
        try:
            # Get first non-null value
            names = self.df[student_col].dropna()
            if len(names) > 0:
                return str(names.iloc[0]).strip()
        except Exception as e:
            logger.warning(f"Could not extract student name: {str(e)}")

        return None

    def _parse_answers(
        self,
        question_col: str,
        answer_col: str,
        result: RobustExcelParserResult,
    ) -> RobustExcelParserResult:
        """Parse answers from Excel columns."""
        answers = {}
        result.total_rows = len(self.df)

        for idx, row in self.df.iterrows():
            try:
                # Get question number
                q_num_raw = row.get(question_col)
                if pd.isna(q_num_raw):
                    result.skipped_answers += 1
                    continue

                try:
                    q_num = int(q_num_raw)
                except (ValueError, TypeError):
                    result.warnings.append(f"Row {idx + 2}: Invalid question number '{q_num_raw}'")
                    result.skipped_answers += 1
                    continue

                # Get answer
                answer_raw = row.get(answer_col)
                if pd.isna(answer_raw):
                    result.warnings.append(f"Q{q_num}: Blank answer (skipped)")
                    result.skipped_answers += 1
                    continue

                # Normalize answer
                normalized = self._normalize_answer(str(answer_raw).strip())

                if not normalized:
                    result.warnings.append(f"Q{q_num}: Invalid answer '{answer_raw}' (skipped)")
                    result.skipped_answers += 1
                    continue

                answers[q_num] = normalized
                result.valid_answers += 1

            except Exception as e:
                result.warnings.append(f"Row {idx + 2}: Error processing answer: {str(e)}")
                result.skipped_answers += 1
                continue

        result.answers = answers
        return result

    def _normalize_answer(self, answer: str) -> Optional[str]:
        """
        Normalize answer to A/B/C/D format.

        Handles:
        - Single letters: A, a, -A-, etc
        - Multiple answers: 1,2,3,4 or A,B,C,D
        - Numbers: 1→A, 2→B, 3→C, 4→D
        - Text: "choice a" → A
        """
        answer = answer.strip().upper()

        if not answer:
            return None

        # Check for direct match (A, B, C, D)
        if answer in ["A", "B", "C", "D"]:
            return answer

        # Remove common formatting characters
        answer_clean = answer.replace("-", "").replace("(", "").replace(")", "")
        answer_clean = answer_clean.replace(".", "").replace(",", "").strip()

        # Check cleaned version
        if answer_clean in ["A", "B", "C", "D"]:
            return answer_clean

        # Check variations
        for correct_answer, variations in self.ANSWER_VARIATIONS.items():
            if answer_clean in variations:
                return correct_answer

        # Try first character if it's valid
        if answer[0] in ["A", "B", "C", "D"]:
            return answer[0]

        return None

    def validate_answers(self, total_questions: int) -> Tuple[bool, List[str]]:
        """
        Validate parsed answers.

        Args:
            total_questions: Expected total questions

        Returns:
            Tuple of (is_valid, error_list)
        """
        if not self.answers:
            return False, ["No answers found"]

        errors = []

        # Check answer count
        if len(self.answers) < total_questions * 0.5:
            errors.append(
                f"Too few answers: {len(self.answers)}/{total_questions} "
                f"({len(self.answers)/total_questions*100:.0f}%)"
            )

        # Check for missing consecutive questions
        question_numbers = sorted(self.answers.keys())
        if question_numbers:
            expected_max = max(question_numbers)
            if expected_max <= total_questions:
                missing = [
                    i for i in range(1, expected_max + 1)
                    if i not in self.answers
                ]
                if missing and len(missing) > total_questions * 0.3:
                    errors.append(f"Many missing questions: {missing[:5]}...")

        return len(errors) == 0, errors

    @property
    def answers(self) -> Dict[int, str]:
        """Legacy property access."""
        return getattr(self, "_answers", {})

    @answers.setter
    def answers(self, value: Dict[int, str]):
        """Legacy property setter."""
        self._answers = value
