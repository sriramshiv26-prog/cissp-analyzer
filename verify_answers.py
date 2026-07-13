#!/usr/bin/env python3
"""
Quick Answer Verification Tool
Lets you easily check and correct extracted answers
"""

import json
from pathlib import Path
from answer_validator_interactive import InteractiveAnswerValidator


def verify_specific_questions(question_numbers: list):
    """
    Verify specific questions by number

    Args:
        question_numbers: List of question numbers to verify (e.g., [28, 147, 150])
    """
    exam_folder = Path('exams/CISSP_July_2026')

    # Load current answer key
    with open(exam_folder / 'answer_keys' / 'answer_key.json', 'r') as f:
        answer_key = json.load(f)

    # Load PDF context
    from answer_key_manager import AnswerKeyManager
    pdf_path = list(exam_folder.glob('questions/*.pdf'))[0]
    manager = AnswerKeyManager(exam_folder)
    extracted, report, pdf_context = manager.extract_from_pdf(str(pdf_path))

    # Prepare answers dict for selected questions only
    validator = InteractiveAnswerValidator()
    questions_to_verify = {}

    print("\n" + "=" * 80)
    print("ANSWER VERIFICATION TOOL")
    print("=" * 80 + "\n")

    corrections = {}

    for q_num in sorted(question_numbers):
        current = answer_key.get(str(q_num), '?')
        extracted_ans = extracted.get(q_num, '?')
        context = pdf_context.get(q_num, '')
        confidence = validator.calculate_confidence(extracted_ans, context)

        print(f"\nQ{q_num}:")
        print(f"  Current answer:  {current}")
        print(f"  Extracted:       {extracted_ans} (confidence: {confidence:.0%})")
        if context:
            print(f"  Context:         {context[:80]}...")

        while True:
            user_input = input(f"  [K]eep | [A/B/C/D] to change | [S]kip: ").strip().upper()

            if user_input == "K":
                print("  → Keeping current answer")
                break
            elif user_input == "S":
                print("  → Skipping")
                break
            elif user_input in ["A", "B", "C", "D"]:
                if user_input != current:
                    print(f"  → Changed {current} → {user_input}")
                    corrections[q_num] = user_input
                else:
                    print(f"  → No change needed")
                break
            else:
                print("  Invalid input. Try again.")

    # Apply corrections
    if corrections:
        print("\n" + "-" * 80)
        print("Applying corrections...")
        for q_num, new_ans in corrections.items():
            answer_key[str(q_num)] = new_ans
            print(f"  Q{q_num}: {new_ans}")

        # Save updated answer key
        with open(exam_folder / 'answer_keys' / 'answer_key.json', 'w') as f:
            json.dump(answer_key, f, indent=2)

        print(f"\n✓ Answer key updated with {len(corrections)} correction(s)")
        print("⚠️  Re-run analysis to update student reports:")
        print("    python3 run_exam_analysis.py")
    else:
        print("\n✓ No corrections needed")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Verify specific questions passed as arguments
        # Usage: python3 verify_answers.py 28 147 150
        question_numbers = [int(q) for q in sys.argv[1:]]
        verify_specific_questions(question_numbers)
    else:
        # Interactive mode
        print("Verify specific questions")
        print("Usage: python3 verify_answers.py <Q1> <Q2> <Q3> ...")
        print("\nExample:")
        print("  python3 verify_answers.py 28 147 150")
        print("\nThen you'll be asked to confirm or correct each answer.")
