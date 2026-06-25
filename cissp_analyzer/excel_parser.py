import pandas as pd
from pathlib import Path
from typing import List, Dict
from cissp_analyzer.models import StudentAnswer


class ExcelParser:
    """Parses student answer Excel files"""

    def parse_answers(self, excel_file: str, student_name: str) -> List[StudentAnswer]:
        """
        Parse answers from Excel file for a specific student

        Expected format:
        - Column 'Question': Question numbers (1-125)
        - Column '<StudentName>': Their answers (A, B, C, D)
        """
        if not Path(excel_file).exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file}")

        df = pd.read_excel(excel_file)

        # Verify required columns
        if 'Question' not in df.columns:
            raise ValueError("Excel must have 'Question' column")

        if student_name not in df.columns:
            raise ValueError(f"Excel must have column for student '{student_name}'")

        answers = []
        for _, row in df.iterrows():
            q_number = int(row['Question'])
            selected_answer = row[student_name]

            # Handle NaN or empty answers (unanswered questions)
            if pd.isna(selected_answer):
                selected_answer = None
            else:
                selected_answer = str(selected_answer).strip().upper()

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
