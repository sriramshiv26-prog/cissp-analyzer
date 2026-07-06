import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
from cissp_analyzer.models import StudentAnswer


class ExcelParser:
    """Parses student answer Excel files with support for multi-part answers"""

    @staticmethod
    def _find_column_case_insensitive(
        df_columns: List[str], target_name: str
    ) -> Optional[str]:
        """Find column name in dataframe columns (case-insensitive)"""
        for col in df_columns:
            if col.lower() == target_name.lower():
                return col
        return None

    @staticmethod
    def normalize_answer(answer_str: str) -> Optional[str]:
        """
        Normalize multi-part and single answers to consistent format.

        Handles formats like:
        - "A" → "A"
        - "1-A, 2-B, 3-C" → "1-A,2-B,3-C"
        - "1A2B3C" → "1-A,2-B,3-C"
        - "A, B, C, D" → "1-A,2-B,3-C,4-D" (positional)
        - "1B2C3A4D" → "1-B,2-C,3-A,4-D"
        """
        if not answer_str or pd.isna(answer_str):
            return None

        answer_str = str(answer_str).strip().upper()

        # Single letter answer (A, B, C, or D)
        if len(answer_str) == 1 and answer_str in "ABCD":
            return answer_str

        # Already formatted: "1-A, 2-B, 3-C" or "1-A,2-B,3-C"
        if re.match(r"^\d+-?[A-D](\s*,\s*\d+-?[A-D])*$", answer_str):
            # Normalize to "1-A,2-B,3-C" format
            parts = re.findall(r"(\d+)-?([A-D])", answer_str)
            if parts:
                normalized = ",".join([f"{num}-{letter}" for num, letter in parts])
                return normalized

        # Format: "1A2B3C4D" or "1B2C3A4D" (no separators)
        if re.match(r"^\d[A-D](\d[A-D])*$", answer_str):
            parts = re.findall(r"(\d)([A-D])", answer_str)
            if parts:
                normalized = ",".join([f"{num}-{letter}" for num, letter in parts])
                return normalized

        # Format: "A, B, C, D" or "ABCD" (positional, no numbers)
        letters = re.findall(r"[A-D]", answer_str)
        if len(letters) >= 2:  # Multi-part answer without position numbers
            normalized = ",".join(
                [f"{i+1}-{letter}" for i, letter in enumerate(letters)]
            )
            return normalized

        return answer_str

    def parse_answers(self, excel_file: str, student_name: str) -> List[StudentAnswer]:
        """
        Parse answers from Excel file for a specific student

        Expected formats:
        - Single answers: "A", "B", "C", "D"
        - Multi-part: "1-A, 2-B, 3-C", "1A2B3C", "A,B,C", "1B2C3A4D"

        Raises:
            FileNotFoundError: If Excel file doesn't exist
            ValueError: If required columns missing or data format invalid
            IOError: If Excel file is corrupted
        """
        file_path = Path(excel_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file}")

        try:
            df = pd.read_excel(excel_file)
        except Exception as exc:
            raise IOError(f"Failed to read Excel file '{excel_file}': {str(exc)}")

        df.columns = df.columns.str.strip()

        # Find question column (case-insensitive)
        question_col = self._find_column_case_insensitive(
            df.columns.tolist(), "Question"
        )
        if not question_col:
            available = ", ".join(df.columns.tolist())
            raise ValueError(
                f"Excel must have 'Question' column. Available columns: {available}"
            )

        # Find student column (case-insensitive)
        student_col = self._find_column_case_insensitive(
            df.columns.tolist(), student_name
        )
        if not student_col:
            available = ", ".join(df.columns.tolist())
            raise ValueError(
                f"Excel must have column for student '{student_name}'. "
                f"Available columns: {available}"
            )

        if df.empty:
            raise ValueError("Excel file is empty (no data rows)")

        answers = []
        for row_idx, (_, row) in enumerate(df.iterrows(), start=2):
            try:
                q_number = int(row[question_col])
            except (ValueError, TypeError):
                q_val = row[question_col]
                raise ValueError(
                    f"Invalid question number in row {row_idx}: {q_val}. "
                    "Expected integer."
                )

            raw_answer = row[student_col]

            # Normalize the answer
            selected_answer = self.normalize_answer(raw_answer)

            answer = StudentAnswer(
                student_name=student_name,
                question_number=q_number,
                selected_answer=selected_answer,
                is_correct=False,  # Will be set by analysis engine
            )
            answers.append(answer)

        if not answers:
            raise ValueError(f"No valid answers found for student '{student_name}'")

        return sorted(answers, key=lambda x: x.question_number)

    def parse_all_students(
        self, excel_file: str, student_names: List[str]
    ) -> Dict[str, List[StudentAnswer]]:
        """Parse answers for multiple students from one file"""
        result = {}
        for student_name in student_names:
            result[student_name] = self.parse_answers(excel_file, student_name)
        return result
