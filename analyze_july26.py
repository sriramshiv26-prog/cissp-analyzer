#!/usr/bin/env python3
"""
Analyze July-26 Batch - All students across all exam weeks
Usage: python3 analyze_july26.py
"""

import json
import sys
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer
from cissp_analyzer.data_quality_validator import validate_batch
from datetime import datetime

def analyze_batch(batch_key='july26_batch'):
    """Analyze entire July-26 batch."""

    with open('student_roster.json') as f:
        roster = json.load(f)

    batch = roster['batches'][batch_key]

    print(f"\n{'='*80}")
    print(f"BATCH ANALYSIS: {batch['name']}")
    print(f"{'='*80}")
    print(f"Batch ID:       {batch['id']}")
    print(f"Status:         {batch['status']}")
    print(f"Students:       {', '.join([s['name'] for s in batch['students']])}")
    print(f"Total:          {len(batch['students'])}")
    print(f"Exams:          {', '.join(batch['exams'])}")
    print(f"Started:        {batch.get('start_date', 'N/A')}")
    print(f"Time:           {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    batch_short = 'july26'

    # Validate all files before processing
    print(f"\n{'='*80}")
    print(f"PRE-ANALYSIS DATA QUALITY CHECK")
    print(f"{'='*80}\n")

    for exam in batch['exams']:
        exam_files = {}
        for student in batch['students']:
            if exam in student['files']:
                file_path = student['files'][exam]
                if Path(file_path).exists():
                    exam_files[student['name']] = file_path

        if exam_files:
            val_results = validate_batch(exam_files, f"July-26 Batch - {exam.upper()}")

            # Warn about errors but don't stop (analysis can handle some issues)
            if val_results['files_with_errors'] > 0:
                print(f"⚠️  WARNING: {val_results['files_with_errors']} file(s) have data quality issues")
                print(f"   These may affect analysis accuracy. Consider fixing them.")
                print(f"   Run: python3 auto_fix_answers.py --batch july26\n")

    for exam in batch['exams']:
        print(f"\n📊 Analyzing {exam.upper()}...")
        print(f"{'─'*80}")

        exam_pdf = f"exams/{batch_short}_{exam}.pdf"
        output_dir = f"reports/{batch_short}_results/{exam}"

        if not Path(exam_pdf).exists():
            print(f"❌ ERROR: PDF not found: {exam_pdf}")
            print(f"   Please ensure exam PDF is at: {exam_pdf}")
            continue

        student_names = []
        consolidated_file = None
        missing_files = []

        for i, student in enumerate(batch['students']):
            student_names.append(student['name'])

            if exam in student['files']:
                file_path = student['files'][exam]

                if not Path(file_path).exists():
                    missing_files.append(f"{student['name']}: {file_path}")
                    continue

        if missing_files:
            print(f"❌ Missing student answer files:")
            for missing in missing_files:
                print(f"   - {missing}")
            print(f"\n   Please copy student answer files to: answers/july26_batch/")
            continue

        # Check for consolidated file (exam-specific)
        consolidated_path = f"answers/{batch_short}_batch/{exam}_all_students.xlsx"
        if not Path(consolidated_path).exists():
            print(f"❌ Consolidated answer file not found: {consolidated_path}")
            print(f"   This file should contain all student answers combined")
            continue

        consolidated_file = consolidated_path

        print(f"   Students:  {', '.join(student_names)}")
        print(f"   PDF:       {exam_pdf}")
        print(f"   Answers:   {consolidated_file}")
        print(f"   Output:    {output_dir}")
        print(f"   Status:    Processing...\n")

        try:
            analyzer = CISSPAnalyzer(mapping_file='data/question_domain_mapping.json')
            result = analyzer.analyze(
                exam_pdf=exam_pdf,
                student_names=student_names,
                answer_excel=consolidated_file,
                output_dir=output_dir
            )

            print(f"   ✓ Analysis complete!")
            print(f"   Individual reports: {len(result.get('individual_reports', []))}")
            print(f"   Class report: 1")
            print(f"   Saved to: {output_dir}\n")

        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return False

    print(f"\n{'='*80}")
    print(f"✓ JULY-26 BATCH ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"\nResults saved to: reports/july26_results/\n")
    return True

if __name__ == '__main__':
    success = analyze_batch('july26_batch')
    sys.exit(0 if success else 1)
