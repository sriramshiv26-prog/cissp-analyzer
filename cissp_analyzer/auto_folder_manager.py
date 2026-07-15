#!/usr/bin/env python3
"""
Auto-Folder Manager - Automatically creates output folders based on exam name/date.
No more manual folder management - system handles it all.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional
import json


class AutoFolderManager:
    """Manages automatic folder creation for exams and results"""

    def __init__(self, base_output_dir: str = "output"):
        self.base_dir = Path(base_output_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_exam_folder(
        self, exam_name: str, timestamp: Optional[str] = None
    ) -> Path:
        """
        Create folder for a new exam automatically

        Args:
            exam_name: Name of the exam (e.g., "CISSP_June_2026")
            timestamp: Optional timestamp (uses current time if None)

        Returns:
            Path to created folder
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Sanitize folder name (remove special chars)
        safe_exam_name = self._sanitize_name(exam_name)
        folder_name = f"{safe_exam_name}_{timestamp}"

        exam_folder = self.base_dir / folder_name
        exam_folder.mkdir(parents=True, exist_ok=True)

        # Create metadata file
        self._create_folder_metadata(exam_folder, exam_name)

        return exam_folder

    def create_student_report_folder(
        self, exam_folder: Path, student_name: str
    ) -> Path:
        """Create individual student folder within exam"""
        safe_student_name = self._sanitize_name(student_name)
        student_folder = exam_folder / "students" / safe_student_name
        student_folder.mkdir(parents=True, exist_ok=True)
        return student_folder

    def create_class_report_folder(self, exam_folder: Path) -> Path:
        """Create class-level reports folder"""
        class_folder = exam_folder / "class_analysis"
        class_folder.mkdir(parents=True, exist_ok=True)
        return class_folder

    def get_exam_folder_by_name(self, exam_name: str) -> Optional[Path]:
        """Find most recent exam folder by name"""
        safe_name = self._sanitize_name(exam_name)

        # Find folders matching this exam name (most recent first)
        matching_folders = sorted(
            [
                f
                for f in self.base_dir.iterdir()
                if f.is_dir() and f.name.startswith(safe_name)
            ],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        return matching_folders[0] if matching_folders else None

    def list_exam_folders(self) -> list:
        """List all exam folders with metadata"""
        exam_folders = []

        for folder in sorted(
            self.base_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True
        ):
            if not folder.is_dir():
                continue

            metadata_file = folder / ".exam_metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    exam_folders.append({"folder": str(folder), "metadata": metadata})

        return exam_folders

    def _create_folder_metadata(self, folder: Path, exam_name: str) -> None:
        """Create metadata file in exam folder"""
        metadata = {
            "exam_name": exam_name,
            "created_date": datetime.now().isoformat(),
            "folder_path": str(folder),
        }

        metadata_file = folder / ".exam_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for use as folder name"""
        # Replace spaces and special chars with underscores
        import re

        sanitized = re.sub(r"[^\w\-_]", "_", name)
        return sanitized[:50]  # Max 50 chars

    def generate_folder_structure_guide(self, exam_folder: Path) -> str:
        """Generate text guide of folder structure"""
        guide = f"""
📁 EXAM FOLDER STRUCTURE
{'='*60}

{exam_folder}/
├── README.txt                  ← You are here
├── .exam_metadata.json         ← Exam metadata (auto-created)
├── class_analysis/
│   ├── CISSP_Class_Analysis.xlsx
│   └── CISSP_Class_Summary.txt
└── students/
    ├── Student_Name_1/
    │   └── CISSP_Individual_Report_Student_Name_1.xlsx
    ├── Student_Name_2/
    │   └── CISSP_Individual_Report_Student_Name_2.xlsx
    └── ...

📝 FILE DESCRIPTIONS
{'='*60}

Individual Reports (in students/ folder):
  • Shows 9-sheet Excel with:
    - Score breakdown by domain
    - Weak topics (to study)
    - Strong topics (confident)
    - Question type analysis
    - Trap categories analysis
    - Learning velocity & trends
    - Personalized study plan

Class Report (in class_analysis/ folder):
  • Shows overall class performance:
    - Average scores by domain
    - Class-wide weak areas
    - Individual student rankings
    - Trend analysis

Metadata File (.exam_metadata.json):
  • Tracks exam information
  • Creation date
  • Folder location
  • Links to exam registry

✨ AUTO-CREATED FEATURES
{'='*60}

✓ Folders created automatically (no manual setup needed)
✓ Exam metadata tracked (for dashboard)
✓ Student folders organized per-student
✓ Class reports consolidated
✓ Timestamp included (multiple runs don't overwrite)

🎯 NEXT STEPS
{'='*60}

1. View individual student reports:
   open {exam_folder}/students/*/CISSP_Individual_Report_*.xlsx

2. View class analysis:
   open {exam_folder}/class_analysis/CISSP_Class_Analysis.xlsx

3. View exam dashboard:
   python3 run.py --dashboard

4. List all exams:
   python3 run.py --list-exams

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return guide

    def save_folder_structure_guide(self, exam_folder: Path) -> None:
        """Save folder structure guide to folder"""
        guide_file = exam_folder / "README.txt"
        with open(guide_file, "w") as f:
            f.write(self.generate_folder_structure_guide(exam_folder))
