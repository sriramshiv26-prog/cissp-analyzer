#!/usr/bin/env python3
"""
Regenerate all student reports with corrected answer key
Used after answer key corrections (e.g., Q144 fix)
"""

import json
import sys
from pathlib import Path
import pandas as pd
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.class_report_gen import ClassReportGenerator
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentAnswer

def parse_excel(excel_path: Path) -> dict:
    """Parse Excel student answers with intelligent column detection"""
    df = pd.read_excel(excel_path)

    q_col = None
    a_col = None

    for col in df.columns:
        col_lower = col.lower()
        if "question" in col_lower or col_lower in ["q"]:
            q_col = col
        if "answer" in col_lower or col_lower in ["a"]:
            a_col = col

    if not q_col or not a_col:
        raise ValueError(f"Could not detect columns. Found: {list(df.columns)}")

    answers = {}
    for idx, row in df.iterrows():
        try:
            q_num = int(row[q_col])
            ans = str(row[a_col]).strip() if pd.notna(row[a_col]) else ""
            answers[q_num] = ans
        except (ValueError, TypeError):
            continue

    return answers


def regenerate_all_reports():
    """Regenerate all student reports with current answer key"""

    exam_folder = Path('exams/CISSP_July_2026')
    reports_dir = exam_folder / 'reports'
    student_answers_dir = exam_folder / 'student_answers'
    answer_keys_dir = exam_folder / 'answer_keys'

    # Load answer key
    with open(answer_keys_dir / 'answer_key.json', 'r') as f:
        answer_key = json.load(f)
        answer_key = {int(k): v for k, v in answer_key.items()}

    # Initialize engine and mapper
    mapper = DomainMapper()
    engine = AnalysisEngine(mapper)
    engine.set_answer_key(answer_key)

    print("=" * 80)
    print("REPORT REGENERATION WITH CORRECTED ANSWER KEY")
    print("=" * 80)
    print(f"\nAnswer key loaded: {len(answer_key)} questions")
    print(f"Student answers folder: {student_answers_dir}")
    print(f"Reports output folder: {reports_dir}\n")

    # Find all student answer files
    student_files = list(student_answers_dir.glob('*.xlsx'))
    print(f"Found {len(student_files)} student answer files\n")

    all_results = {}
    all_students = {}

    for student_file in sorted(student_files):
        print(f"Processing: {student_file.name}")
        print("-" * 80)

        # Extract student name from filename using smarter pattern matching
        stem = student_file.stem
        # Try to find the name (usually at the end or after dashes/spaces)
        if "Senthilraj" in stem:
            student_name = "Senthilraj"
        elif "Praveena" in stem:
            student_name = "Praveena"
        elif "Aman" in stem:
            student_name = "Aman"
        elif "kapil" in stem.lower():
            student_name = "Kapil"
        else:
            # Fallback: use cleaned stem
            student_name = stem.replace("Mock Test ", "").replace("_", " ").replace("-", " ").strip()
            # Capitalize first letters
            student_name = " ".join(w.capitalize() for w in student_name.split())

        try:
            # Parse student answers
            answers_dict = parse_excel(student_file)
            print(f"  Student: {student_name}")
            print(f"  Questions answered: {len(answers_dict)}")

            # Store for report generation
            all_students[student_name] = answers_dict

            # Convert dict to StudentAnswer objects for analysis
            student_answers_list = [
                StudentAnswer(student_name, q_num, ans, False)
                for q_num, ans in answers_dict.items()
            ]

            # Run analysis
            perf = engine.evaluate_student(student_answers_list, student_name)
            all_results[student_name] = perf

            print(f"  Score: {perf.score_percentage:.1f}% ({perf.correct_count}/{perf.total_questions})")
            print(f"  Blank answers: {perf.blank_count}")
            print(f"  Invalid answers: {perf.invalid_count}\n")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}\n")
            continue

    # Generate individual reports
    print("=" * 80)
    print("GENERATING INDIVIDUAL REPORTS")
    print("=" * 80 + "\n")

    for student_name, perf in all_results.items():
        try:
            student_answers = all_students.get(student_name, {})
            gen = IndividualReportGenerator(mapper, engine, student_answers, answer_key)
            output_file = reports_dir / f"{student_name}_Report.xlsx"
            gen.generate(perf, output_file)
            size = output_file.stat().st_size / 1024
            print(f"✓ {student_name}_Report.xlsx ({size:.1f} KB)")
        except Exception as e:
            print(f"✗ Error generating report for {student_name}: {e}")

    # Generate class report
    if all_results:
        print("\n" + "=" * 80)
        print("GENERATING CLASS REPORT")
        print("=" * 80 + "\n")

        try:
            gen = ClassReportGenerator(mapper, engine)
            class_file = reports_dir / "Class_Report.xlsx"
            gen.generate(all_results, class_file)
            size = class_file.stat().st_size / 1024
            print(f"✓ Class_Report.xlsx ({size:.1f} KB)\n")
        except Exception as e:
            print(f"Note: Class report not available ({e})\n")

    print("=" * 80)
    print("✓ REGENERATION COMPLETE")
    print("=" * 80)
    print("\nAll reports have been regenerated with the corrected answer key.")
    print("Summary:")
    for name in sorted(all_results.keys()):
        perf = all_results[name]
        print(f"  {name:30s}: {perf.score_percentage:5.1f}% ({perf.correct_count:3d}/{perf.total_questions})")

if __name__ == "__main__":
    try:
        regenerate_all_reports()
    except KeyboardInterrupt:
        print("\n\nRegeneration cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
