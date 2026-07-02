#!/usr/bin/env python3
"""
Validate Exam PDF - Questions & Answer Key

MUST RUN BEFORE STUDENT ANALYSIS!

Usage:
  python3 validate_exam.py exams/dec25_week1.pdf
  python3 validate_exam.py exams/dec25_week2.pdf
  python3 validate_exam.py --all
"""

import sys
from pathlib import Path
from cissp_analyzer.exam_validator import ExamValidator


def validate_single_exam(pdf_path: str) -> bool:
    """Validate a single exam PDF"""
    validator = ExamValidator(pdf_path)
    is_valid, result = validator.validate()

    if is_valid:
        # Save answer key
        exam_name = Path(pdf_path).stem
        answer_key_path = f"exams/{exam_name}_answer_key.json"
        validator.save_answer_key(answer_key_path)

    return is_valid


def validate_all_exams() -> bool:
    """Validate all exam PDFs"""
    exams_dir = Path("exams")
    pdf_files = sorted(exams_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in exams/ directory")
        return False

    print("="*80)
    print(f"VALIDATING ALL EXAMS ({len(pdf_files)} files)")
    print("="*80)

    all_valid = True
    results = {}

    for pdf_file in pdf_files:
        print()
        is_valid = validate_single_exam(str(pdf_file))
        results[pdf_file.name] = is_valid
        if not is_valid:
            all_valid = False

    # Summary
    print("\n" + "="*80)
    print("BATCH VALIDATION SUMMARY")
    print("="*80)

    for exam_name, is_valid in results.items():
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"  {exam_name}: {status}")

    print()
    if all_valid:
        print("✅ ALL EXAMS VALIDATED - Ready for student analysis")
    else:
        print("❌ SOME EXAMS FAILED - Fix issues before processing")

    print("="*80)

    return all_valid


def print_help():
    """Print help message"""
    print("""
Exam PDF Validator

IMPORTANT: Questions and Answer Keys MUST be validated before processing
student answer files. This ensures:
  ✓ All 125 questions extracted correctly
  ✓ All 125 answers extracted correctly
  ✓ No gaps or mismatches
  ✓ Answer format is valid (A/B/C/D)
  ✓ Questions and answers aligned

Usage:
  python3 validate_exam.py <pdf_path>     # Validate single exam
  python3 validate_exam.py --all          # Validate all PDFs in exams/
  python3 validate_exam.py --help         # Show this help

Examples:
  python3 validate_exam.py exams/dec25_week1.pdf
  python3 validate_exam.py exams/dec25_week2.pdf
  python3 validate_exam.py --all

Output:
  ✓ Validation report with any issues found
  ✓ Answer key JSON file (if valid)

Next Step:
  After validation passes, run student analysis:
  python3 analyze_dec25.py
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print_help()
        sys.exit(0)

    if sys.argv[1] == '--all':
        success = validate_all_exams()
    else:
        pdf_path = sys.argv[1]
        if not Path(pdf_path).exists():
            print(f"Error: File not found: {pdf_path}")
            sys.exit(1)

        success = validate_single_exam(pdf_path)

    sys.exit(0 if success else 1)
