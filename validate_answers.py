#!/usr/bin/env python3
"""
Validate Student Answer Sheets Before Analysis

Usage:
  python3 validate_answers.py                    # Validate Dec-25 batch
  python3 validate_answers.py --batch july26     # Validate July-26 batch
  python3 validate_answers.py --file path/to/file.xlsx StudentName
"""

import json
import sys
from pathlib import Path
from cissp_analyzer.data_quality_validator import AnswerSheetValidator, validate_batch

def validate_single_file():
    """Validate a single file"""
    if len(sys.argv) < 3:
        print("Usage: python3 validate_answers.py --file <filepath> <StudentName>")
        sys.exit(1)

    file_path = sys.argv[2]
    student_name = sys.argv[3]

    validator = AnswerSheetValidator()
    is_valid, issues = validator.validate_file(file_path, student_name)

    print(f"\nValidating: {file_path}")
    print(f"Student:    {student_name}")
    print(f"Status:     {'✓ PASS' if is_valid else '✗ FAIL'}\n")

    if issues:
        for issue in issues:
            print(f"  {issue}")

    if not is_valid:
        sys.exit(1)


def validate_dec25_batch():
    """Validate Dec-25 batch (default)"""
    with open('student_roster.json') as f:
        roster = json.load(f)

    batch = roster['batches']['dec25_batch']

    # Get files for both exams
    for exam in batch['exams']:
        files = {}
        for student in batch['students']:
            if exam in student['files']:
                files[student['name']] = student['files'][exam]

        results = validate_batch(files, f"DEC-25 Batch - {exam.upper()}")

        # Check if any files failed
        if results['files_with_errors'] > 0:
            print(f"\n⚠️  {results['files_with_errors']} file(s) with ERRORS - "
                  "Fix these before running analysis\n")
            sys.exit(1)


def validate_july26_batch():
    """Validate July-26 batch"""
    with open('student_roster.json') as f:
        roster = json.load(f)

    batch = roster['batches']['july26_batch']

    if not batch['students']:
        print("July-26 batch has no students yet")
        return

    # Get files for both exams
    for exam in batch['exams']:
        files = {}
        for student in batch['students']:
            if exam in student['files']:
                files[student['name']] = student['files'][exam]

        if files:
            results = validate_batch(files, f"JULY-26 Batch - {exam.upper()}")

            if results['files_with_errors'] > 0:
                print(f"\n⚠️  {results['files_with_errors']} file(s) with ERRORS\n")
                sys.exit(1)


def print_help():
    """Print help message"""
    print("""
Data Quality Validator for Answer Sheets

Usage:
  python3 validate_answers.py                      # Validate Dec-25 batch (default)
  python3 validate_answers.py --batch dec25        # Validate Dec-25 batch explicitly
  python3 validate_answers.py --batch july26       # Validate July-26 batch
  python3 validate_answers.py --file <path> <name> # Validate single file

Examples:
  python3 validate_answers.py
  python3 validate_answers.py --batch july26
  python3 validate_answers.py --file answers/dec25_batch/senthil_week1.xlsx Senthil

What gets checked:
  ✓ File structure (Question and Answer columns)
  ✓ Row count (should be 125 questions)
  ✓ Missing/NaN answers
  ✓ Invalid answer formats
  ✓ Anomalies (multi-value cells, etc.)

Exit codes:
  0 = All files valid (or only warnings)
  1 = Files have ERRORS that need fixing

Info:
  Warnings indicate issues to be aware of but files can still be analyzed
  Errors indicate issues that MUST be fixed before analysis
""")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print_help()
            sys.exit(0)
        elif sys.argv[1] == '--file':
            validate_single_file()
        elif sys.argv[1] == '--batch':
            if len(sys.argv) < 3:
                print("Usage: python3 validate_answers.py --batch <dec25|july26>")
                sys.exit(1)
            batch = sys.argv[2]
            if batch == 'dec25':
                validate_dec25_batch()
            elif batch == 'july26':
                validate_july26_batch()
            else:
                print(f"Unknown batch: {batch}")
                print("Valid batches: dec25, july26")
                sys.exit(1)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print_help()
            sys.exit(1)
    else:
        # Default: validate dec25 batch
        validate_dec25_batch()

    print("\n✓ All validations passed!\n")
