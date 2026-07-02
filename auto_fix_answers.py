#!/usr/bin/env python3
"""
Auto-Fix Student Answer Sheets - Correct common data quality issues

Automatically fixes:
- Column name variations (Q.NO → Question, Answer options → StudentName)
- Answer format issues (lowercase → uppercase)
- Complex answer spacing (1b, 2a, 3c → 1-B,2-A,3-C)
- Whitespace normalization

Usage:
  python3 auto_fix_answers.py --file <path> --student <name>
  python3 auto_fix_answers.py --batch <batch_name>
  python3 auto_fix_answers.py --help

Examples:
  python3 auto_fix_answers.py --file answers/dec25_batch/thameem_week2.xlsx --student Thameem
  python3 auto_fix_answers.py --batch dec25
"""

import sys
import json
from pathlib import Path
from cissp_analyzer.data_quality_validator import AnswerSheetAutoFixer


def fix_single_file(file_path: str, student_name: str = None):
    """Fix a single answer file"""
    print(f"\nAuto-fixing: {file_path}")
    print("─" * 80)

    success, output_file, fixes = AnswerSheetAutoFixer.fix_file(file_path, student_name)

    if not success:
        print(f"❌ ERROR: {fixes[0] if fixes else 'Unknown error'}")
        return False

    print(f"✓ Fixed successfully!")
    print(f"\nFixes applied:")
    for fix in fixes:
        print(f"  • {fix}")

    print(f"\nOutput file:")
    print(f"  {output_file}")
    print(f"\nReplace original file? (y/n): ", end="")

    response = input().strip().lower()
    if response == 'y':
        import shutil
        shutil.move(output_file, file_path)
        print(f"✓ Original file updated: {file_path}")
        return True
    else:
        print(f"⚠ Original file unchanged. Fixed copy saved as:")
        print(f"  {output_file}")
        return True


def fix_batch(batch_key: str):
    """Fix all answer files in a batch"""
    print(f"\n{'='*80}")
    print(f"AUTO-FIXING BATCH: {batch_key.upper()}")
    print(f"{'='*80}\n")

    try:
        with open('student_roster.json') as f:
            roster = json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: student_roster.json not found")
        return False

    batch_name = f"{batch_key}_batch" if not batch_key.endswith('_batch') else batch_key
    if batch_name not in roster['batches']:
        print(f"❌ ERROR: Batch not found: {batch_name}")
        print(f"Available batches: {', '.join(roster['batches'].keys())}")
        return False

    batch = roster['batches'][batch_name]
    total_fixed = 0
    failed = []

    for student in batch['students']:
        student_name = student['name']

        for exam, file_path in student.get('files', {}).items():
            if not Path(file_path).exists():
                print(f"⚠ SKIP: {student_name} ({exam}) - File not found: {file_path}")
                continue

            print(f"Fixing: {student_name} ({exam})")
            success, output_file, fixes = AnswerSheetAutoFixer.fix_file(file_path, student_name)

            if success and fixes:
                # Replace original
                import shutil
                shutil.move(output_file, file_path)
                print(f"  ✓ {len(fixes)} fix(es) applied and saved")
                total_fixed += 1
            elif success:
                print(f"  ✓ No issues found (file already clean)")
            else:
                print(f"  ✗ Error: {fixes[0] if fixes else 'Unknown error'}")
                failed.append(f"{student_name} ({exam})")

    print(f"\n{'='*80}")
    print(f"AUTO-FIX COMPLETE")
    print(f"{'='*80}")
    print(f"Fixed: {total_fixed} file(s)")
    if failed:
        print(f"Failed: {len(failed)} file(s)")
        for f in failed:
            print(f"  • {f}")
    print()

    return True


def print_help():
    """Print help message"""
    print("""
Auto-Fix Student Answer Sheets

Automatically corrects common data quality issues:
- Column name variations (Q.NO → Question, Answer options → StudentName)
- Answer format issues (lowercase → UPPERCASE)
- Complex answer formatting (1b, 2a, 3c → 1-B,2-A,3-C)
- Whitespace normalization

Usage:
  python3 auto_fix_answers.py --file <path> --student <name>
  python3 auto_fix_answers.py --batch <batch_name>
  python3 auto_fix_answers.py --help

Options:
  --file <path>       Path to answer Excel file
  --student <name>    Student name (for column header)
  --batch <name>      Batch name (dec25, july26, etc)

Examples:
  # Fix single file
  python3 auto_fix_answers.py --file answers/dec25_batch/thameem_week2.xlsx --student Thameem

  # Fix entire batch
  python3 auto_fix_answers.py --batch dec25

What Gets Fixed:
  ✓ Column headers standardized
  ✓ Answer values normalized to uppercase
  ✓ Complex answers formatted correctly (1-B,2-A,3-C)
  ✓ Extra whitespace removed
  ✓ Output saved as new file (backup original)

Then:
  - Review fixes in the new file
  - Confirm to overwrite original, or keep separate
  - Re-run analysis with fixed files
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)

    # Parse arguments
    file_path = None
    student_name = None
    batch_name = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--file' and i + 1 < len(sys.argv):
            file_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--student' and i + 1 < len(sys.argv):
            student_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--batch' and i + 1 < len(sys.argv):
            batch_name = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Execute
    if file_path:
        fix_single_file(file_path, student_name)
    elif batch_name:
        fix_batch(batch_name)
    else:
        print("Error: Specify --file or --batch")
        print_help()
        sys.exit(1)
