#!/usr/bin/env python3
"""
Exam Registry - Tracks all uploaded question banks and their metadata.
Allows system to auto-create folders and manage multiple exams.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class ExamRegistry:
    """Manages registered exams and their metadata"""

    REGISTRY_FILE = Path("data/exam_registry.json")

    def __init__(self):
        """Initialize registry, create if doesn't exist"""
        self.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.exams = self._load_registry()

    def _load_registry(self) -> Dict:
        """Load registry from file"""
        if self.REGISTRY_FILE.exists():
            with open(self.REGISTRY_FILE) as f:
                return json.load(f)
        return {"exams": {}, "last_updated": None}

    def _save_registry(self) -> None:
        """Save registry to file"""
        self.exams["last_updated"] = datetime.now().isoformat()
        with open(self.REGISTRY_FILE, "w") as f:
            json.dump(self.exams, f, indent=2)

    def register_exam(
        self,
        exam_name: str,
        question_bank_path: str,
        num_questions: int,
        description: str = "",
    ) -> str:
        """
        Register a new exam

        Args:
            exam_name: Name of the exam (e.g., "CISSP_June_2026")
            question_bank_path: Path to question bank JSON
            num_questions: Number of questions
            description: Optional description

        Returns:
            exam_id: Unique ID for this exam
        """
        # Generate unique ID
        exam_id = self._generate_exam_id(exam_name)

        self.exams["exams"][exam_id] = {
            "exam_name": exam_name,
            "exam_id": exam_id,
            "question_bank_path": question_bank_path,
            "num_questions": num_questions,
            "description": description,
            "registered_date": datetime.now().isoformat(),
            "output_folder": f"output/{exam_name}",
            "student_results": [],
            "class_results": None,
        }

        self._save_registry()
        return exam_id

    def _generate_exam_id(self, exam_name: str) -> str:
        """Generate unique exam ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_hash = hashlib.md5(exam_name.encode()).hexdigest()[:8]
        return f"{exam_name}_{timestamp}_{name_hash}"

    def get_exam(self, exam_id: str) -> Optional[Dict]:
        """Get exam by ID"""
        return self.exams["exams"].get(exam_id)

    def list_exams(self) -> List[Dict]:
        """List all registered exams"""
        return list(self.exams["exams"].values())

    def add_student_result(
        self, exam_id: str, student_name: str, report_path: str
    ) -> None:
        """Add student result to exam"""
        if exam_id in self.exams["exams"]:
            self.exams["exams"][exam_id]["student_results"].append(
                {
                    "student_name": student_name,
                    "report_path": report_path,
                    "date": datetime.now().isoformat(),
                }
            )
            self._save_registry()

    def set_class_result(self, exam_id: str, report_path: str) -> None:
        """Set class-level report for exam"""
        if exam_id in self.exams["exams"]:
            self.exams["exams"][exam_id]["class_results"] = {
                "report_path": report_path,
                "date": datetime.now().isoformat(),
            }
            self._save_registry()

    def get_exam_by_name(self, exam_name: str) -> Optional[Dict]:
        """Find exam by name (not ID)"""
        for exam in self.exams["exams"].values():
            if exam["exam_name"] == exam_name:
                return exam
        return None

    def export_summary(self) -> Dict:
        """Export summary of all exams and results"""
        summary = {
            "total_exams": len(self.exams["exams"]),
            "total_students_analyzed": 0,
            "exams": [],
        }

        for exam in self.exams["exams"].values():
            num_students = len(exam["student_results"])
            summary["total_students_analyzed"] += num_students

            summary["exams"].append(
                {
                    "exam_name": exam["exam_name"],
                    "exam_id": exam["exam_id"],
                    "num_questions": exam["num_questions"],
                    "students_analyzed": num_students,
                    "class_result": exam["class_results"] is not None,
                    "registered_date": exam["registered_date"],
                    "output_folder": exam["output_folder"],
                }
            )

        return summary
