import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Optional
from cissp_analyzer.models import StudentAnswer


class ExcelParser:
    """Parses student answer Excel files with support for multi-part answers"""

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
        if len(answer_str) == 1 and answer_str in 'ABCD':
            return answer_str

        # Already formatted: "1-A, 2-B, 3-C" or "1-A,2-B,3-C"
        if re.match(r'^\d+-?[A-D](\s*,\s*\d+-?[A-D])*$', answer_str):
            # Normalize to "1-A,2-B,3-C" format
            parts = re.findall(r'(\d+)-?([A-D])', answer_str)
            if parts:
                normalized = ','.join([f"{num}-{letter}" for num, letter in parts])
                return normalized

        # Format: "1A2B3C4D" or "1B2C3A4D" (no separators)
        if re.match(r'^\d[A-D](\d[A-D])*$', answer_str):
            parts = re.findall(r'(\d)([A-D])', answer_str)
            if parts:
                normalized = ','.join([f"{num}-{letter}" for num, letter in parts])
                return normalized

        # Format: "A, B, C, D" or "ABCD" (positional, no numbers)
        letters = re.findall(r'[A-D]', answer_str)
        if len(letters) >= 2:  # Multi-part answer without position numbers
            normalized = ','.join([f"{i+1}-{letter}" for i, letter in enumerate(letters)])
            return normalized

        return answer_str

    def parse_answers(self, excel_file: str, student_name: str) -> List[StudentAnswer]:
        """
        Parse answers from Excel file for a specific student

        Expected formats:
        - Single answers: "A", "B", "C", "D"
        - Multi-part: "1-A, 2-B, 3-C", "1A2B3C", "A,B,C", "1B2C3A4D"
        """
        if not Path(excel_file).exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file}")

        df = pd.read_excel(excel_file)
        df.columns = df.columns.str.strip()

        # Verify required columns
        if 'Question' not in df.columns:
            raise ValueError("Excel must have 'Question' column")

        if student_name not in df.columns:
            raise ValueError(f"Excel must have column for student '{student_name}'")

        answers = []
        for _, row in df.iterrows():
            q_number = int(row['Question'])
            raw_answer = row[student_name]

            # Normalize the answer
            selected_answer = self.normalize_answer(raw_answer)

            answer = StudentAnswer(
                student_name=student_name,
                question_number=q_number,
                selected_answer=selected_answer,
                is_correct=False  # Will be set by analysis engine
            )
            answers.append(answer)

        return sorted(answers, key=lambda x: x.question_number)

    def parse_all_students(self, excel_file: str, student_names: List[str]) -> Dict[str, List[StudentAnswer]]:
        """Parse answers for multiple students from one file"""
        result = {}
        for student_name in student_names:
            result[student_name] = self.parse_answers(excel_file, student_name)
        return result
