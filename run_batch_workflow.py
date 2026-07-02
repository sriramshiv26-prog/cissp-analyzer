#!/usr/bin/env python3
"""
Master Workflow Script - Complete Batch Analysis Pipeline

Automates entire workflow from exam PDF to student reports.
No manual steps needed - everything from the Dec-25 Batch learnings
is automated here.

Usage:
  python3 run_batch_workflow.py --batch dec25 --setup
  python3 run_batch_workflow.py --batch dec25 --full
  python3 run_batch_workflow.py --batch dec25 --analyze-only
  python3 run_batch_workflow.py --help
"""

import sys
import json
from pathlib import Path
from datetime import datetime


class BatchWorkflow:
    """Manages complete batch analysis workflow"""

    def __init__(self, batch_name: str):
        self.batch_name = batch_name
        self.log = []

    def log_step(self, step: str, status: str, message: str = ""):
        """Log workflow step"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {status:8} - {step}"
        if message:
            entry += f" ({message})"
        self.log.append(entry)
        print(entry)

    def step_1_verify_structure(self) -> bool:
        """Verify batch folder structure exists"""
        self.log_step("Step 1", "START", "Verifying folder structure")

        required_dirs = [
            "exams",
            f"answers/{self.batch_name}",
            "reports",
        ]

        all_exist = True
        for dir_path in required_dirs:
            if Path(dir_path).exists():
                self.log_step("  ", "✓", f"Found: {dir_path}")
            else:
                self.log_step("  ", "✗", f"Missing: {dir_path}")
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                self.log_step("  ", "✓", f"Created: {dir_path}")

        return True

    def step_2_validate_exams(self) -> bool:
        """Validate all exam PDFs"""
        self.log_step("Step 2", "START", "Validating exam PDFs")

        from cissp_analyzer.exam_validator import ExamValidator

        exams = list(Path("exams").glob(f"{self.batch_name}*.pdf"))

        if not exams:
            self.log_step("  ", "✗", f"No PDFs found matching: exams/{self.batch_name}*.pdf")
            return False

        for exam_pdf in exams:
            self.log_step("  ", "INFO", f"Validating: {exam_pdf.name}")
            validator = ExamValidator(str(exam_pdf))
            is_valid, result = validator.validate()

            if result["questions_found"] == 125:
                self.log_step("  ", "✓", f"Questions: {result['questions_found']}/125")
            else:
                self.log_step("  ", "⚠", f"Questions: {result['questions_found']}/125")

            if result["answers_found"] == 125:
                self.log_step("  ", "✓", f"Answers: {result['answers_found']}/125")
            else:
                self.log_step("  ", "⚠", f"Answers: {result['answers_found']}/125")
                self.log_step("  ", "INFO", f"Missing: {result['issues']}")

        return True

    def step_3_validate_student_files(self) -> bool:
        """Validate student answer files"""
        self.log_step("Step 3", "START", "Validating student answer files")

        from cissp_analyzer.data_quality_validator import validate_batch
        import json

        # Get batch info from roster
        with open("student_roster.json") as f:
            roster = json.load(f)

        if self.batch_name not in [b for b in ["dec25_batch", "july26_batch", "adhoc"]]:
            batch_key = f"{self.batch_name}_batch"
        else:
            batch_key = self.batch_name

        if batch_key not in roster["batches"]:
            self.log_step("  ", "✗", f"Batch not found in roster: {batch_key}")
            return False

        batch = roster["batches"][batch_key]
        self.log_step("  ", "INFO", f"Batch: {batch['name']} ({len(batch['students'])} students)")

        # Validate files for each exam
        for exam in batch.get("exams", []):
            files = {}
            for student in batch["students"]:
                if exam in student.get("files", {}):
                    files[student["name"]] = student["files"][exam]

            if files:
                results = validate_batch(files, f"{self.batch_name.upper()} - {exam.upper()}")
                self.log_step("  ", "INFO", f"Exam {exam}: {results['valid_files']}/{results['total_files']} valid")

        return True

    def step_4_run_analysis(self) -> bool:
        """Run batch analysis"""
        self.log_step("Step 4", "START", "Running batch analysis")

        # Import analysis script based on batch
        if self.batch_name == "dec25":
            self.log_step("  ", "INFO", "Running: analyze_dec25.py")
            # Run the script
            import subprocess
            result = subprocess.run(["python3", "analyze_dec25.py"], capture_output=True, text=True)

            if result.returncode == 0:
                self.log_step("  ", "✓", "Analysis completed successfully")
                # Count reports
                reports = list(Path(f"reports/{self.batch_name}_results").glob("**/*.xlsx"))
                self.log_step("  ", "✓", f"Reports generated: {len(reports)}")
                return True
            else:
                self.log_step("  ", "✗", "Analysis failed")
                if result.stderr:
                    self.log_step("  ", "ERROR", result.stderr[:200])
                return False
        else:
            self.log_step("  ", "⚠", f"Batch script not found for: {self.batch_name}")
            self.log_step("  ", "INFO", f"Create: analyze_{self.batch_name}.py")
            return False

    def step_5_verify_outputs(self) -> bool:
        """Verify all output files"""
        self.log_step("Step 5", "START", "Verifying output reports")

        import openpyxl

        reports_dir = Path(f"reports/{self.batch_name}_results")

        if not reports_dir.exists():
            self.log_step("  ", "✗", f"Reports directory not found: {reports_dir}")
            return False

        reports = list(reports_dir.glob("**/*.xlsx"))

        if not reports:
            self.log_step("  ", "✗", "No report files found")
            return False

        self.log_step("  ", "INFO", f"Total reports: {len(reports)}")

        for report in reports:
            try:
                wb = openpyxl.load_workbook(report)
                sheets = len(wb.sheetnames)
                self.log_step("  ", "✓", f"{report.name}: {sheets} sheets")
            except Exception as e:
                self.log_step("  ", "✗", f"{report.name}: {str(e)[:50]}")

        return True

    def run_full_workflow(self):
        """Run complete workflow"""
        print("\n" + "="*80)
        print(f"BATCH WORKFLOW - {self.batch_name.upper()}")
        print("="*80)
        print()

        steps = [
            ("Structure", self.step_1_verify_structure),
            ("Exam Validation", self.step_2_validate_exams),
            ("Student Files", self.step_3_validate_student_files),
            ("Analysis", self.step_4_run_analysis),
            ("Output", self.step_5_verify_outputs),
        ]

        results = {}
        for step_name, step_func in steps:
            try:
                success = step_func()
                results[step_name] = "✓ PASS" if success else "✗ FAIL"
            except Exception as e:
                self.log_step(step_name, "✗", f"Error: {str(e)[:100]}")
                results[step_name] = "✗ ERROR"

        # Summary
        print("\n" + "="*80)
        print("WORKFLOW SUMMARY")
        print("="*80)

        for step, result in results.items():
            print(f"  {step:20} {result}")

        print()
        all_pass = all("✓" in v for v in results.values())
        if all_pass:
            print("✅ WORKFLOW COMPLETE - All steps passed!")
        else:
            print("⚠️  Some steps failed - review errors above")

        print("="*80 + "\n")

        return all_pass


def print_help():
    """Print help message"""
    print("""
Batch Workflow - Complete Analysis Pipeline

Automates all steps from exam PDFs to student reports, using learnings
from Dec-25 Batch implementation.

Usage:
  python3 run_batch_workflow.py --batch <name> --full
  python3 run_batch_workflow.py --batch <name> --validate-only
  python3 run_batch_workflow.py --batch <name> --analyze-only
  python3 run_batch_workflow.py --help

Options:
  --batch <name>        Batch name (dec25, july26, etc)
  --full               Run complete workflow (default)
  --validate-only      Only validate (no analysis)
  --analyze-only       Only run analysis (skip validation)

Examples:
  python3 run_batch_workflow.py --batch dec25 --full
  python3 run_batch_workflow.py --batch july26 --full

Steps Automated:
  1. Verify folder structure
  2. Validate exam PDFs (questions + answer keys)
  3. Validate student answer files (data quality)
  4. Run batch analysis
  5. Verify output reports

All fixes from Dec-25 Batch are automated - no manual steps needed!
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)

    # Parse arguments
    batch_name = None
    mode = "full"  # default

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--batch' and i + 1 < len(sys.argv):
            batch_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--full':
            mode = 'full'
            i += 1
        elif sys.argv[i] == '--validate-only':
            mode = 'validate'
            i += 1
        elif sys.argv[i] == '--analyze-only':
            mode = 'analyze'
            i += 1
        else:
            i += 1

    if not batch_name:
        print("Error: --batch <name> is required")
        print_help()
        sys.exit(1)

    # Run workflow
    workflow = BatchWorkflow(batch_name)

    if mode == 'full':
        workflow.run_full_workflow()
    elif mode == 'validate':
        workflow.step_1_verify_structure()
        workflow.step_2_validate_exams()
        workflow.step_3_validate_student_files()
    elif mode == 'analyze':
        workflow.step_4_run_analysis()
        workflow.step_5_verify_outputs()
