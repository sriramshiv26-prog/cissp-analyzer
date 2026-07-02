#!/usr/bin/env python3
"""
Create Answer Key for Exam - Interactive Input Tool

For exams with matching questions or complex answer formats,
use this to manually input answer keys.

Usage:
  python3 create_answer_key.py exams/dec25_week2.pdf
  python3 create_answer_key.py --help
"""

import sys
import json
from pathlib import Path
from cissp_analyzer.exam_validator import ExamValidator


def create_answer_key_interactive(pdf_path: str):
    """Create answer key with interactive input for complex questions"""

    print("\n" + "="*80)
    print("CREATING ANSWER KEY - INTERACTIVE MODE")
    print("="*80)

    # First, auto-extract what we can
    validator = ExamValidator(pdf_path)
    auto_answers = validator.extract_answer_key()
    auto_questions = validator.extract_questions()

    print(f"\nExam: {Path(pdf_path).name}")
    print(f"Auto-extracted: {len(auto_answers)}/125 answers")
    print()

    # Start with auto-extracted answers
    answer_key = {str(k): v for k, v in auto_answers.items()}

    # Find missing answers
    missing = [i for i in range(1, 126) if str(i) not in answer_key]

    if missing:
        print(f"⚠️  Missing {len(missing)} answers: {missing[:10]}{'...' if len(missing) > 10 else ''}")
        print()
        print("For each missing question, enter the answer:")
        print("  Single answer: A, B, C, or D")
        print("  Matching question: 1-C,2-D,3-B,4-A (format: item-answer,item-answer,...)")
        print("  Ordering: A,C,B,D (format: letter,letter,letter,letter)")
        print("  Skip: press Enter to skip (will mark as missing)")
        print()

        for q_num in missing:
            if q_num in auto_questions:
                q_text = auto_questions[q_num][:80]
                print(f"\nQ{q_num}: {q_text}...")
            else:
                print(f"\nQ{q_num}:")

            answer = input("  Answer (or press Enter to skip): ").strip().upper()

            if answer:
                answer_key[str(q_num)] = answer
                print(f"  ✓ Recorded: {answer}")
            else:
                print(f"  ⊘ Skipped")

    # Summary
    print("\n" + "="*80)
    print("ANSWER KEY SUMMARY")
    print("="*80)
    print(f"Total answers: {len(answer_key)}/125")

    if len(answer_key) == 125:
        print("✅ COMPLETE!")
    else:
        missing_count = 125 - len(answer_key)
        print(f"⚠️  Still missing: {missing_count} answers")

    print()

    # Ask to save
    if len(answer_key) > 0:
        save = input("Save answer key? (y/n): ").strip().lower()

        if save == 'y':
            exam_name = Path(pdf_path).stem
            output_file = f"exams/{exam_name}_answer_key.json"

            with open(output_file, 'w') as f:
                json.dump(answer_key, f, indent=2, sort_keys=True)

            print(f"\n✓ Saved to: {output_file}")
            print(f"  {len(answer_key)} answers")

            return True

    return False


def print_help():
    """Print help message"""
    print("""
Answer Key Creation Tool

Create answer keys for exam PDFs, including support for:
  ✓ Standard multiple choice (A/B/C/D)
  ✓ Matching questions (1-C,2-D,3-B,4-A)
  ✓ Ordering questions (A,C,B,D)
  ✓ Complex answer formats

Usage:
  python3 create_answer_key.py <pdf_path>     # Create for specific exam
  python3 create_answer_key.py --help         # Show this help

Examples:
  python3 create_answer_key.py exams/dec25_week2.pdf
  python3 create_answer_key.py exams/mock_exam.pdf

Workflow:
  1. Script auto-extracts all standard answers (A/B/C/D)
  2. For missing answers, you enter them interactively
  3. For complex questions, use appropriate format:

     Single Answer:
       C

     Matching (4 items):
       1-C,2-D,3-B,4-A

     Ordering (4 items):
       A,C,B,D

     Matching with 5 items:
       1-D,2-A,3-E,4-B,5-C

  4. Answer key saved to: exams/<exam_name>_answer_key.json

Next Steps:
  After creating answer key, run:
  python3 analyze_dec25.py (or your batch analysis script)
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print_help()
        sys.exit(0)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    success = create_answer_key_interactive(pdf_path)
    sys.exit(0 if success else 1)
