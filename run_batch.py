#!/usr/bin/env python3
"""
Batch runner for multiple students with config file
Usage: python3 run_batch.py [config_file]
"""

import sys
import json
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer
from cissp_analyzer.class_report_gen import ClassReportGenerator
from cissp_analyzer.domain_mapper import DomainMapper

def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else "batch_config.json"

    # Load config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)

    pdf_path = config['exam_pdf']
    answer_key_path = config['answer_key']
    output_dir = config['output_dir']
    students_list = config['students']

    print("="*70)
    print("CISSP BATCH ANALYZER - CLASS REPORT")
    print("="*70)
    print(f"PDF: {pdf_path}")
    print(f"Output: {output_dir}")
    print(f"Students: {len(students_list)}")
    print("="*70 + "\n")

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create analyzer and load answer key
    analyzer = CISSPAnalyzer()
    analyzer.set_answer_key_from_file(answer_key_path)

    # Analyze each student
    cohort_performance = []
    for student_info in students_list:
        student_name = student_info['name']
        excel_file = student_info['excel']

        print(f"Analyzing {student_name}...")

        try:
            results = analyzer.analyze(pdf_path, excel_file, [student_name], output_dir)

            # Get performance from results
            # Re-run to get performance object
            from cissp_analyzer.pdf_parser import PDFParser
            from cissp_analyzer.excel_parser import ExcelParser

            pdf_parser = PDFParser(pdf_path)
            questions = pdf_parser.extract_questions()

            excel_parser = ExcelParser()
            answers = excel_parser.parse_answers(excel_file, student_name)

            performance = analyzer.analysis_engine.evaluate_student(answers, student_name)
            cohort_performance.append(performance)

            print(f"  ✓ {student_name}: {performance.correct_count}/125 ({performance.score_percentage:.1f}%)")
        except Exception as e:
            print(f"  ✗ Error analyzing {student_name}: {e}")
            continue

    # Generate combined class report
    print(f"\nGenerating class report with {len(cohort_performance)} students...")
    mapper = DomainMapper('data/question_domain_mapping.json')
    class_gen = ClassReportGenerator(mapper)
    class_report_file = Path(output_dir) / "CISSP_Class_Analysis.xlsx"
    class_gen.generate(cohort_performance, str(class_report_file))

    print(f"✓ Class report: {class_report_file}")

    # Print summary
    print("\n" + "="*70)
    print("BATCH ANALYSIS COMPLETE!")
    print("="*70)
    print(f"\nClass Summary:")
    print(f"  Students: {len(cohort_performance)}")
    print(f"  Average: {sum(p.score_percentage for p in cohort_performance)/len(cohort_performance):.1f}%")
    print(f"  Passing (70%+): {sum(1 for p in cohort_performance if p.score_percentage >= 70)}/{len(cohort_performance)}")
    print(f"\nIndividual Scores:")
    for perf in cohort_performance:
        status = "✓ PASS" if perf.score_percentage >= 70 else "✗ NEEDS WORK"
        print(f"  {perf.student_name}: {perf.correct_count}/125 ({perf.score_percentage:.1f}%) {status}")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
