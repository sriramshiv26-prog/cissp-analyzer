#!/usr/bin/env python3
"""
CISSP Analysis Tool - Command line entry point
Usage: python run.py <exam_pdf> <answers_excel> <students> <output_dir> [answer_key_json]
"""

import sys
import json
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer


def main():
    if len(sys.argv) < 5:
        print("CISSP Analysis Tool")
        print("Usage: python run.py <exam_pdf> <answers_excel> <students> <output_dir> [answer_key_json]")
        print("\nExample:")
        print("  python run.py exam.pdf answers.xlsx 'Senthil,Kapil,Praveena' ./reports/ answer_key.json")
        print("\nArguments:")
        print("  exam_pdf:        Path to exam PDF with questions")
        print("  answers_excel:   Path to Excel file with student answers")
        print("  students:        Comma-separated list of student names (must match Excel column names)")
        print("  output_dir:      Directory where reports will be saved")
        print("  answer_key_json: (Optional) Path to JSON file with answer key")
        sys.exit(1)

    exam_pdf = sys.argv[1]
    answers_excel = sys.argv[2]
    students = [s.strip() for s in sys.argv[3].split(',')]
    output_dir = sys.argv[4]
    answer_key_file = sys.argv[5] if len(sys.argv) > 5 else None

    # Validate inputs
    if not Path(exam_pdf).exists():
        print(f"Error: Exam PDF not found: {exam_pdf}")
        sys.exit(1)

    if not Path(answers_excel).exists():
        print(f"Error: Answer Excel not found: {answers_excel}")
        sys.exit(1)

    # Run analysis
    print("\n" + "=" * 60)
    print("CISSP Analysis Tool")
    print("=" * 60)
    print(f"PDF:           {exam_pdf}")
    print(f"Answers:       {answers_excel}")
    print(f"Students:      {', '.join(students)}")
    print(f"Output:        {output_dir}")
    if answer_key_file:
        print(f"Answer Key:    {answer_key_file}")
    print("=" * 60 + "\n")

    try:
        analyzer = CISSPAnalyzer()

        # Load answer key if provided
        if answer_key_file and Path(answer_key_file).exists():
            print(f"Loading answer key from {answer_key_file}...\n")
            analyzer.set_answer_key_from_file(answer_key_file)
        else:
            print("Note: No answer key provided. Set via set_answer_key_from_file().\n")

        # Run analysis
        results = analyzer.analyze(exam_pdf, answers_excel, students, output_dir)

        # Print results summary
        print("\n" + "=" * 60)
        print("Analysis Complete!")
        print("=" * 60)
        print(f"\nStudents Analyzed: {results['students_analyzed']}")
        print("\nIndividual Reports:")
        for report in results['individual_reports']:
            print(f"  - {report}")
        print(f"\nClass Report:")
        print(f"  - {results['class_report']}")
        print("\n" + "=" * 60 + "\n")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
