#!/usr/bin/env python3
"""
Exam Manager - Organizes exams into separate folders with answer keys and reports
"""

from pathlib import Path
import json
import shutil
from datetime import datetime


class ExamManager:
    """Manages exam folders, answer keys, and reports"""

    def __init__(self, base_dir="/Users/sriram/cissp-analyzer/exams"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_exam_folder(self, exam_name: str, pdf_path: str = None) -> Path:
        """
        Create a new exam folder structure

        Args:
            exam_name: Name for the exam (e.g., "CISSP_July_2026")
            pdf_path: Optional path to PDF question file

        Returns:
            Path to created exam folder
        """
        # Create exam folder
        exam_folder = self.base_dir / exam_name
        exam_folder.mkdir(exist_ok=True)

        # Create subfolders
        (exam_folder / "questions").mkdir(exist_ok=True)
        (exam_folder / "answer_keys").mkdir(exist_ok=True)
        (exam_folder / "student_answers").mkdir(exist_ok=True)
        (exam_folder / "reports").mkdir(exist_ok=True)
        (exam_folder / "logs").mkdir(exist_ok=True)

        # Copy PDF if provided
        if pdf_path and Path(pdf_path).exists():
            dest = exam_folder / "questions" / Path(pdf_path).name
            shutil.copy(pdf_path, dest)
            print(f"✓ Copied PDF to: {dest}")

        # Create metadata file
        metadata = {
            "exam_name": exam_name,
            "created": datetime.now().isoformat(),
            "structure": {
                "questions": "Question PDFs",
                "answer_keys": "Answer key JSON files",
                "student_answers": "Student answer Excel files",
                "reports": "Generated reports",
                "logs": "Analysis logs",
            },
        }

        metadata_file = exam_folder / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Created exam folder: {exam_folder}")
        return exam_folder

    def save_answer_key(
        self, exam_name: str, answer_key: dict, filename: str = "answer_key.json"
    ) -> Path:
        """Save answer key for an exam"""
        exam_folder = self.base_dir / exam_name
        key_file = exam_folder / "answer_keys" / filename

        with open(key_file, "w") as f:
            json.dump(answer_key, f, indent=2)

        print(f"✓ Saved answer key: {key_file}")
        return key_file

    def load_answer_key(self, exam_name: str) -> dict:
        """Load answer key for an exam"""
        key_file = self.base_dir / exam_name / "answer_keys" / "answer_key.json"

        if not key_file.exists():
            raise FileNotFoundError(f"Answer key not found: {key_file}")

        with open(key_file, "r") as f:
            return json.load(f)

    def copy_student_answers(self, exam_name: str, excel_path: str) -> Path:
        """Copy student answer Excel file to exam folder"""
        exam_folder = self.base_dir / exam_name
        dest = exam_folder / "student_answers" / Path(excel_path).name
        shutil.copy(excel_path, dest)
        print(f"✓ Copied: {dest}")
        return dest

    def save_report(self, exam_name: str, report_path: str) -> Path:
        """Copy generated report to exam folder"""
        exam_folder = self.base_dir / exam_name
        dest = exam_folder / "reports" / Path(report_path).name
        shutil.copy(report_path, dest)
        print(f"✓ Saved report: {dest}")
        return dest

    def list_exams(self) -> list:
        """List all exams"""
        exams = [d.name for d in self.base_dir.iterdir() if d.is_dir()]
        return sorted(exams)

    def get_exam_folder(self, exam_name: str) -> Path:
        """Get path to exam folder"""
        return self.base_dir / exam_name
