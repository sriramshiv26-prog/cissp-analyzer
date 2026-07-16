#!/usr/bin/env python3
"""
Answer Key Manager - Phase 2 Integration
Loads, validates, and manages answer keys for exam grading.
Supports: Excel files, JSON files, and version control.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerKeyManager:
    """Manages answer key loading, validation, and lookup for exam grading."""

    def __init__(self, exam_folder: Path):
        """
        Initialize AnswerKeyManager for an exam.

        Args:
            exam_folder: Path to exam folder
        """
        self.exam_folder = Path(exam_folder)
        self.answer_keys_dir = self.exam_folder / "answer_keys"
        self.answer_keys_dir.mkdir(exist_ok=True)
        self.current_key: Optional[Dict[int, str]] = None
        self.version = 1

    def load_from_excel(self, excel_path: str, version: int = 1) -> Dict[int, str]:
        """
        Load answer key from Excel file.

        Expected format:
        - Column headers: "Question", "Answer" OR "Q", "Ans" OR "Q#", "A"
        - Or: First column = question number, second column = answer
        - Answers: A, B, C, D (case-insensitive)

        Args:
            excel_path: Path to Excel file containing answer key
            version: Version number for this key (for multi-version exams)

        Returns:
            Dictionary mapping question number (int) to answer (str)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format is invalid or no data found
        """
        file_path = Path(excel_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            logger.info(f"Loaded Excel file: {excel_path}")
            logger.info(f"Columns: {list(df.columns)}")

            # Find question and answer columns (case-insensitive)
            question_col = self._find_column(df, ["Question", "Q", "Q#", "Qnum"])
            answer_col = self._find_column(df, ["Answer", "Ans", "A", "Correct"])

            if not question_col or not answer_col:
                # Try using first two columns
                if len(df.columns) < 2:
                    raise ValueError("Excel file must have at least 2 columns")
                question_col = df.columns[0]
                answer_col = df.columns[1]
                logger.warning(f"Using first two columns: {question_col}, {answer_col}")

            answer_key = {}
            errors = []

            for idx, row in df.iterrows():
                try:
                    q_num = int(row[question_col])
                    answer = str(row[answer_col]).strip().upper()

                    if answer not in ["A", "B", "C", "D"]:
                        errors.append(f"Q{q_num}: Invalid answer '{answer}'")
                        continue

                    answer_key[q_num] = answer

                except (ValueError, TypeError) as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")

            if not answer_key:
                raise ValueError("No valid answer key data found in Excel file")

            if errors:
                logger.warning(f"Conversion errors: {errors}")

            logger.info(f"✓ Loaded {len(answer_key)} answer keys from Excel")
            self._save_answer_key(answer_key, version, "excel")
            self.current_key = answer_key
            self.version = version
            return answer_key

        except Exception as e:
            logger.error(f"Error loading Excel file: {str(e)}")
            raise

    def load_from_json(self, json_path: str, version: int = 1) -> Dict[int, str]:
        """
        Load answer key from JSON file.

        Expected format:
        {
            "1": "A",
            "2": "B",
            ...
        }
        Or:
        {
            "Q1": "A",
            "Q2": "B",
            ...
        }

        Args:
            json_path: Path to JSON file
            version: Version number for this key

        Returns:
            Dictionary mapping question number (int) to answer (str)

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON format is invalid
        """
        file_path = Path(json_path)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            answer_key = {}
            errors = []

            for key, value in data.items():
                try:
                    # Handle both "1" and "Q1" formats
                    q_num_str = str(key).strip().upper()
                    if q_num_str.startswith("Q"):
                        q_num_str = q_num_str[1:]
                    q_num = int(q_num_str)

                    answer = str(value).strip().upper()
                    if answer not in ["A", "B", "C", "D"]:
                        errors.append(f"Q{q_num}: Invalid answer '{answer}'")
                        continue

                    answer_key[q_num] = answer

                except (ValueError, TypeError) as e:
                    errors.append(f"Key '{key}': {str(e)}")

            if not answer_key:
                raise ValueError("No valid answer key data found in JSON file")

            if errors:
                logger.warning(f"Conversion errors: {errors}")

            logger.info(f"✓ Loaded {len(answer_key)} answer keys from JSON")
            self._save_answer_key(answer_key, version, "json")
            self.current_key = answer_key
            self.version = version
            return answer_key

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {str(e)}")
            raise ValueError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            logger.error(f"Error loading JSON file: {str(e)}")
            raise

    def validate_against_questions(
        self, answer_key: Dict[int, str], total_questions: int
    ) -> Tuple[bool, List[str]]:
        """
        Validate that answer key matches the exam questions.

        Args:
            answer_key: Answer key to validate
            total_questions: Total number of questions in exam

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if answer key is empty
        if not answer_key:
            errors.append("Answer key is empty")
            return False, errors

        # Check for missing answers
        missing = []
        for q_num in range(1, total_questions + 1):
            if q_num not in answer_key:
                missing.append(q_num)

        if missing and len(missing) <= 10:
            errors.append(f"Missing answers for questions: {missing}")
        elif missing:
            errors.append(f"Missing answers for {len(missing)} questions")

        # Check for extra answers (beyond total questions)
        extra = [q for q in answer_key.keys() if q > total_questions]
        if extra and len(extra) <= 10:
            errors.append(f"Answer key has extra answers: {extra}")
        elif extra:
            errors.append(f"Answer key has {len(extra)} extra answers")

        # Check coverage
        coverage = len(answer_key) / total_questions * 100
        logger.info(
            f"Answer key coverage: {coverage:.1f}% ({len(answer_key)}/{total_questions})"
        )

        is_valid = len(errors) == 0
        return is_valid, errors

    def get_answer(self, question_number: int) -> Optional[str]:
        """
        Get answer for a specific question.

        Args:
            question_number: Question number to lookup

        Returns:
            Answer (A/B/C/D) or None if not found
        """
        if not self.current_key:
            return None
        return self.current_key.get(question_number)

    def get_all_answers(self) -> Dict[int, str]:
        """Get all loaded answer keys."""
        return self.current_key or {}

    def handle_multiple_versions(self, version: int) -> Optional[Dict[int, str]]:
        """
        Load answer key for a specific exam version.

        Args:
            version: Version number (1, 2, 3, etc.)

        Returns:
            Answer key dictionary or None if version not found
        """
        version_file = self.answer_keys_dir / f"answer_key_v{version}.json"

        if not version_file.exists():
            logger.warning(f"Version {version} not found")
            return None

        try:
            with open(version_file, "r") as f:
                data = json.load(f)
                # Convert string keys to integers
                return {int(k): v for k, v in data.items()}
        except Exception as e:
            logger.error(f"Error loading version {version}: {str(e)}")
            return None

    def _find_column(
        self, df: pd.DataFrame, possible_names: List[str]
    ) -> Optional[str]:
        """
        Find column in DataFrame by name (case-insensitive).

        Args:
            df: Pandas DataFrame
            possible_names: List of possible column names to match

        Returns:
            Column name if found, None otherwise
        """
        df_columns_lower = {col.lower(): col for col in df.columns}

        for name in possible_names:
            if name.lower() in df_columns_lower:
                return df_columns_lower[name.lower()]

        return None

    def _save_answer_key(
        self, answer_key: Dict[int, str], version: int = 1, source: str = "unknown"
    ) -> Path:
        """
        Save answer key to disk with versioning.

        Args:
            answer_key: Answer key dictionary
            version: Version number
            source: Source of answer key (excel, json, manual)

        Returns:
            Path to saved file
        """
        # Save versioned file
        version_file = self.answer_keys_dir / f"answer_key_v{version}.json"
        json_data = {str(k): v for k, v in answer_key.items()}

        with open(version_file, "w") as f:
            json.dump(json_data, f, indent=2)

        # Update current answer key link
        current_file = self.answer_keys_dir / "answer_key_current.json"
        with open(current_file, "w") as f:
            json.dump(json_data, f, indent=2)

        # Save metadata
        metadata = {
            "version": version,
            "source": source,
            "total_answers": len(answer_key),
            "created_at": __import__("datetime").datetime.now().isoformat(),
        }
        metadata_file = self.answer_keys_dir / f"answer_key_v{version}_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✓ Saved answer key v{version} to {version_file}")
        return version_file

    def list_versions(self) -> List[int]:
        """List all available answer key versions."""
        versions = []
        for file in self.answer_keys_dir.glob("answer_key_v*.json"):
            if not file.name.endswith("_metadata.json"):
                try:
                    version = int(file.stem.replace("answer_key_v", ""))
                    versions.append(version)
                except ValueError:
                    pass
        return sorted(versions)
