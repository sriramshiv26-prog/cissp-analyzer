import json
import logging
from pathlib import Path
from typing import List, Dict

# Configure logging for error reporting
logger = logging.getLogger(__name__)

# Class constant for max exams per student
MAX_EXAMS_PER_STUDENT = 10


class HistoryLoader:
    """Load and manage historical exam performance data"""

    def __init__(self, students_dir: str = "students"):
        self.students_dir = Path(students_dir)
        self.students_dir.mkdir(exist_ok=True)

    def load_previous_exams(self, student_name: str) -> List[Dict]:
        """
        Load all previous exam performance files for a student.

        Args:
            student_name: Name of the student (e.g., "Sri")

        Returns:
            List of exam performance dicts, sorted by exam_number (oldest first)
        """
        student_path = self.students_dir / student_name

        if not student_path.exists():
            return []

        exam_files = sorted(student_path.glob("exam-*_performance.json"))
        exams = []

        for exam_file in exam_files:
            try:
                with open(exam_file, 'r') as f:
                    exam_data = json.load(f)
                    exams.append(exam_data)
            except IOError as e:
                logger.warning(
                    f"Failed to read exam file {exam_file}: {e}. Skipping."
                )
            except json.JSONDecodeError as e:
                logger.warning(
                    f"Corrupted JSON in {exam_file}: {e}. Skipping."
                )

        # Sort by exam_number to handle exams 10+ correctly (not lexicographically)
        exams.sort(key=lambda x: x.get('exam_number', 0))

        return exams

    def save_exam_performance(
        self, student_name: str, exam_number: int, performance_data: Dict
    ) -> Path:
        """
        Save current exam performance to JSON file.

        Args:
            student_name: Name of student
            exam_number: Exam sequence number (1, 2, 3, ...)
            performance_data: Dict with accuracy by domain/difficulty/type

        Returns:
            Path to saved file
        """
        student_path = self.students_dir / student_name
        student_path.mkdir(parents=True, exist_ok=True)

        # Check max limit
        existing_exams = len(list(student_path.glob("exam-*_performance.json")))
        if existing_exams >= MAX_EXAMS_PER_STUDENT:
            print(
                f"Warning: Student {student_name} has {existing_exams} "
                f"exams (max {MAX_EXAMS_PER_STUDENT})."
            )
            print("   Consider archiving older exams.")

        output_file = student_path / f"exam-{exam_number}_performance.json"

        with open(output_file, 'w') as f:
            json.dump(performance_data, f, indent=2)

        return output_file

    def create_student_folder(self, student_name: str) -> Path:
        """Create student folder if it doesn't exist"""
        student_path = self.students_dir / student_name
        student_path.mkdir(parents=True, exist_ok=True)
        return student_path
