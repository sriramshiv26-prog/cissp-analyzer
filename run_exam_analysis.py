#!/usr/bin/env python3
"""
Complete Exam Analysis Workflow
Handles: Exam setup → Answer key → Student parsing → Analysis → Reports
"""

import json
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

from exam_manager import ExamManager
from answer_key_manager import AnswerKeyManager
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentAnswer
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.class_report_gen import ClassReportGenerator


class ExamAnalyzer:
    """Complete exam analysis workflow"""

    def __init__(self, base_exam_dir="/Users/sriram/cissp-analyzer/exams"):
        self.exam_manager = ExamManager(base_exam_dir)
        self.mapper = DomainMapper()

    def run_analysis(self):
        """Main analysis workflow"""
        print("\n" + "=" * 80)
        print("CISSP EXAM ANALYSIS SYSTEM")
        print("=" * 80)

        # Step 1: Get exam name
        exam_name = self._get_exam_name()
        exam_folder = self.exam_manager.create_exam_folder(exam_name)

        # Step 2: Upload PDF
        pdf_path = self._get_pdf_path()
        if pdf_path:
            import shutil

            dest = exam_folder / "questions" / Path(pdf_path).name
            shutil.copy(pdf_path, dest)
            print(f"✓ Copied PDF: {dest.name}")

        # Step 3: Get answer key
        key_manager = AnswerKeyManager(exam_folder)
        answer_key = key_manager.load_answer_key(str(pdf_path), interactive=True)

        if not answer_key:
            print("\n✗ No answer key provided. Cannot proceed.")
            return

        print(f"\n✓ Answer key ready: {len(answer_key)} questions")

        # Step 4: Parse student answers
        print("\n" + "=" * 80)
        print("PARSING STUDENT ANSWERS")
        print("=" * 80 + "\n")

        students = self._get_student_files(exam_folder)

        if not students:
            print("\n✗ No student answer files provided.")
            return

        # Step 5: Analyze
        print("\n" + "=" * 80)
        print("ANALYZING PERFORMANCE")
        print("=" * 80 + "\n")

        engine = AnalysisEngine(self.mapper)
        engine.set_answer_key(answer_key)

        results = {}
        for student_name, answers_dict in students.items():
            student_answers = [
                StudentAnswer(student_name, q_num, ans, False)
                for q_num, ans in answers_dict.items()
            ]

            perf = engine.evaluate_student(student_answers, student_name)
            results[student_name] = perf

            print(f"✓ {student_name}: {perf.score_percentage:.1f}% ({perf.correct_count}/{perf.total_questions})")

        # Step 6: Generate reports
        print("\n" + "=" * 80)
        print("GENERATING REPORTS")
        print("=" * 80 + "\n")

        self._generate_reports(exam_folder, engine, results, students)

        # Step 7: Summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80 + "\n")

        self._print_summary(exam_folder, results)

    def _get_exam_name(self) -> str:
        """Get exam name from user"""
        print("\nEnter exam name (e.g., CISSP_July_2026):")
        name = input("> ").strip()
        if not name:
            name = f"Exam_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return name

    def _get_pdf_path(self) -> str:
        """Get PDF path from user"""
        print("\nEnter path to PDF question file (or press ENTER to skip):")
        path = input("> ").strip()
        if path and Path(path).exists():
            return path
        if path:
            print("File not found.")
        return None

    def _get_student_files(self, exam_folder: Path) -> dict:
        """Get student answer files from user"""
        print("Enter paths to student answer files (one per line, empty line to finish):")

        students = {}
        file_count = 0

        while True:
            path = input(f"File {file_count + 1}: ").strip()

            if not path:
                break

            if not Path(path).exists():
                print(f"  ✗ File not found: {path}")
                continue

            # Copy to exam folder
            dest = exam_folder / "student_answers" / Path(path).name
            import shutil

            shutil.copy(path, dest)

            # Parse
            name = self._parse_student_file(dest)
            if name:
                students[name] = self._parse_excel(dest)
                file_count += 1

        return students

    def _parse_student_file(self, file_path: Path) -> str:
        """Extract student name from file"""
        # Try to extract name from filename
        name = file_path.stem  # Remove extension
        name = name.replace("Mock Test ", "").replace("_", " ").replace("-", " ")

        print(f"  Student name (suggested: '{name}'): ", end="")
        custom_name = input().strip()

        return custom_name if custom_name else name

    def _parse_excel(self, excel_path: Path) -> dict:
        """Parse Excel student answers"""
        df = pd.read_excel(excel_path)

        # Auto-detect columns
        q_col = None
        a_col = None

        for col in df.columns:
            col_lower = col.lower()
            if "question" in col_lower or col_lower in ["q", "questions"]:
                q_col = col
            if "answer" in col_lower or col_lower in ["a", "answers"]:
                a_col = col

        if not q_col or not a_col:
            print(f"  ✗ Could not detect columns in {excel_path.name}")
            print(f"    Found: {list(df.columns)}")
            return {}

        answers = {}
        for idx, row in df.iterrows():
            q_num = int(row[q_col])
            ans = str(row[a_col]).strip() if pd.notna(row[a_col]) else ""
            answers[q_num] = ans

        return answers

    def _generate_reports(self, exam_folder: Path, engine, results: dict, students: dict):
        """Generate individual and class reports"""
        # Load answer key
        import json
        key_file = exam_folder / "answer_keys" / "answer_key.json"
        with open(key_file, 'r') as f:
            answer_key = {int(k): v for k, v in json.load(f).items()}

        # Individual reports
        for student_name, perf in results.items():
            student_answers = students.get(student_name, {})
            gen = IndividualReportGenerator(self.mapper, engine, student_answers, answer_key)
            output_file = exam_folder / "reports" / f"{student_name}_Report.xlsx"
            gen.generate(perf, output_file)
            size = output_file.stat().st_size / 1024
            print(f"✓ {student_name}_Report.xlsx ({size:.1f} KB)")

        # Class report
        try:
            gen = ClassReportGenerator(self.mapper, engine)
            class_file = exam_folder / "reports" / "Class_Report.xlsx"
            gen.generate(results, class_file)
            size = class_file.stat().st_size / 1024
            print(f"✓ Class_Report.xlsx ({size:.1f} KB)")
        except Exception as e:
            print(f"Note: Class report not available ({e})")

    def _print_summary(self, exam_folder: Path, results: dict):
        """Print analysis summary"""
        print(f"Exam Folder: {exam_folder}")
        print()
        print("Results:")
        for name in sorted(results.keys()):
            perf = results[name]
            print(f"  {name:20s}: {perf.score_percentage:5.1f}% ({perf.correct_count:3d}/{perf.total_questions})")

        print()
        print("All files saved in:")
        print(f"  {exam_folder}")

        # Show folder structure
        print("\nFolder structure:")
        print(f"  questions/ - Question PDFs")
        print(f"  answer_keys/ - Answer key (answer_key.json)")
        print(f"  student_answers/ - Student Excel files")
        print(f"  reports/ - Generated reports")


if __name__ == "__main__":
    analyzer = ExamAnalyzer()
    analyzer.run_analysis()
