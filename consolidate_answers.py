#!/usr/bin/env python3
"""
Consolidate Individual Student Answer Files

Combines individual student Excel files into a single consolidated file for batch analysis.

Expected input structure:
  answers/dec25_batch/
    ├── senthil_week1.xlsx
    ├── aman_week1.xlsx
    ├── praveena_week1.xlsx
    ├── thameem_week1.xlsx
    ├── kapil_week1.xlsx
    └── ...

Output structure:
  answers/dec25_batch/week1_all_students.xlsx
    └── Columns: Question | Senthil | Aman | Praveena | Thameem | Kapil

Usage:
  python3 consolidate_answers.py --batch dec25
  python3 consolidate_answers.py --batch dec25 --exam week1
  python3 consolidate_answers.py --help
"""

import sys
import json
from pathlib import Path
import pandas as pd
import openpyxl


def consolidate_batch(batch_key: str, exam: str = None):
    """Consolidate all answer files in a batch"""

    # Load roster
    try:
        with open('student_roster.json') as f:
            roster = json.load(f)
    except FileNotFoundError:
        print("❌ ERROR: student_roster.json not found")
        return False

    batch_name = f"{batch_key}_batch" if not batch_key.endswith('_batch') else batch_key
    if batch_name not in roster['batches']:
        print(f"❌ ERROR: Batch not found: {batch_name}")
        return False

    batch = roster['batches'][batch_name]
    exams = [exam] if exam else batch.get('exams', [])

    print(f"\n{'='*80}")
    print(f"CONSOLIDATING BATCH: {batch['name']}")
    print(f"Exams: {', '.join(exams)}")
    print(f"Students: {len(batch['students'])}")
    print(f"{'='*80}\n")

    for exam_name in exams:
        print(f"Processing {exam_name.upper()}...")

        # Collect all student files for this exam
        student_data = {}
        missing = []

        for student in batch['students']:
            student_name = student['name']

            if exam_name not in student.get('files', {}):
                missing.append(f"{student_name} (not registered for {exam_name})")
                continue

            file_path = student['files'][exam_name]
            if not Path(file_path).exists():
                missing.append(f"{student_name} (file not found: {file_path})")
                continue

            # Read student's answers
            try:
                df = pd.read_excel(file_path)

                # Find answer column (could be 'Answer', student name, 'Answer options', etc.)
                answer_col = None
                for col in df.columns:
                    if 'answer' in col.lower():
                        answer_col = col
                        break

                if answer_col is None and len(df.columns) > 1:
                    answer_col = df.columns[1]  # Take second column if no 'answer' found

                if answer_col is None:
                    print(f"  ⚠ {student_name}: Could not find answer column")
                    continue

                # Extract answers (should be 125 rows)
                answers = df[answer_col].values.tolist()

                # Ensure we have exactly 125 answers
                if len(answers) < 125:
                    answers.extend([''] * (125 - len(answers)))
                elif len(answers) > 125:
                    answers = answers[:125]

                student_data[student_name] = answers
                print(f"  ✓ {student_name}: {len(answers)} answers")

            except Exception as e:
                print(f"  ✗ {student_name}: ERROR - {str(e)}")
                missing.append(f"{student_name} (error reading file)")

        if missing:
            print(f"\n  ⚠ Missing or skipped:")
            for m in missing:
                print(f"    - {m}")

        # Create consolidated DataFrame
        questions = list(range(1, 126))
        consolidated_data = {'Question': questions}
        consolidated_data.update(student_data)

        df_consolidated = pd.DataFrame(consolidated_data)

        # Save to Excel
        output_file = f"answers/{batch_key}_batch/{exam_name}_all_students.xlsx"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df_consolidated.to_excel(output_file, index=False, sheet_name='Answers')
        print(f"\n  ✓ Consolidated file: {output_file}")
        print(f"    Rows: {len(df_consolidated)} | Columns: {len(df_consolidated.columns)}")
        print()

    return True


def print_help():
    """Print help message"""
    print("""
Consolidate Student Answer Files

Combines individual student Excel files into a single consolidated file
for batch analysis.

Usage:
  python3 consolidate_answers.py --batch <batch_name>
  python3 consolidate_answers.py --batch <batch_name> --exam <week>
  python3 consolidate_answers.py --help

Options:
  --batch <name>      Batch name (dec25, july26, etc)
  --exam <week>       Specific exam (week1, week2) - optional, all if not specified

Examples:
  # Consolidate entire Dec-25 batch (all exams)
  python3 consolidate_answers.py --batch dec25

  # Consolidate only Week 1
  python3 consolidate_answers.py --batch dec25 --exam week1

Output:
  answers/<batch>_batch/<exam>_all_students.xlsx
    └── Columns: Question | StudentName1 | StudentName2 | ...

Expected input structure:
  answers/<batch>_batch/
    ├── student1_week1.xlsx
    ├── student2_week1.xlsx
    ├── student1_week2.xlsx
    └── ...

Features:
  ✓ Auto-detects answer columns (handles variations)
  ✓ Standardizes to 125 questions per student
  ✓ Creates single consolidated file per exam
  ✓ Reports missing or problematic files
  ✓ Handles data quality issues gracefully
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        sys.exit(0)

    # Parse arguments
    batch_name = None
    exam_name = None

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--batch' and i + 1 < len(sys.argv):
            batch_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--exam' and i + 1 < len(sys.argv):
            exam_name = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not batch_name:
        print("Error: --batch <name> is required")
        print_help()
        sys.exit(1)

    consolidate_batch(batch_name, exam_name)
