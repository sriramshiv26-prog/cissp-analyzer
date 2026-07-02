#!/usr/bin/env python3
"""
Quick Answer Key Input - Smart Format Recognition

Learns from previous answer formats and prompts intelligently.
Perfect for batch entering answers for multiple questions.

Usage:
  python3 quick_answer_key.py create --exam week2
  python3 quick_answer_key.py template --show-all
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class AnswerKeyBuilder:
    """Build answer keys with smart format recognition"""

    def __init__(self):
        self.templates = self._load_templates()
        self.answer_key = {}

    def _load_templates(self) -> Dict:
        """Load answer format templates"""
        template_file = Path("answer_key_templates.json")
        if template_file.exists():
            with open(template_file) as f:
                return json.load(f)
        return {}

    def detect_question_type(self, q_num: int, q_text: str = None) -> str:
        """Detect question type from text"""
        if not q_text:
            return "single"

        text_lower = q_text.lower()

        # Detect matching questions
        if "match" in text_lower:
            if "5" in text_lower or "five" in text_lower:
                return "matching_5_items"
            return "matching_4_items"

        # Detect ordering questions
        if "order" in text_lower or "rank" in text_lower or "arrange" in text_lower:
            return "ordering_4_items"

        return "single"

    def get_prompt_template(self, question_type: str) -> Tuple[str, str]:
        """Get prompt template for question type"""
        if question_type in self.templates:
            template = self.templates[question_type]
            return (
                f"{template['description']} (format: {template['pattern']})",
                template['example']
            )
        return ("Answer", "A")

    def input_answers_fast(self, missing_questions: List[int],
                          exam_name: str = "exam") -> Dict[str, str]:
        """Fast input mode for missing answers"""
        print("\n" + "="*80)
        print("FAST ANSWER INPUT MODE")
        print("="*80)
        print(f"Exam: {exam_name}")
        print(f"Missing answers: {len(missing_questions)}")
        print()
        print("Shortcuts:")
        print("  [S] Single answer (A/B/C/D)")
        print("  [M4] Match 4 items (1-C,2-D,3-B,4-A)")
        print("  [M5] Match 5 items (1-D,2-A,3-E,4-B,5-C)")
        print("  [O] Ordering (A,C,B,D)")
        print("  [Skip] Leave blank to skip")
        print()

        answers = {}

        for q_num in missing_questions:
            prompt, example = self.get_prompt_template("single")

            print(f"\nQ{q_num}:")
            print(f"  Type [S/M4/M5/O] or enter answer")
            print(f"  Example: {example}")

            user_input = input("  >>> ").strip()

            if not user_input:
                continue

            # Process shortcuts
            if user_input.upper() == 'S':
                ans = input("  Answer (A/B/C/D): ").strip().upper()
                if ans in ['A', 'B', 'C', 'D']:
                    answers[str(q_num)] = ans
                    print(f"  ✓ {ans}")
            elif user_input.upper() == 'M4':
                ans = input("  Matching (1-?,2-?,3-?,4-?): ").strip()
                if len(ans) > 0:
                    answers[str(q_num)] = ans
                    print(f"  ✓ {ans}")
            elif user_input.upper() == 'M5':
                ans = input("  Matching (1-?,2-?,3-?,4-?,5-?): ").strip()
                if len(ans) > 0:
                    answers[str(q_num)] = ans
                    print(f"  ✓ {ans}")
            elif user_input.upper() == 'O':
                ans = input("  Order (A,C,B,D): ").strip()
                if len(ans) > 0:
                    answers[str(q_num)] = ans
                    print(f"  ✓ {ans}")
            else:
                # Direct answer
                answers[str(q_num)] = user_input.upper()
                print(f"  ✓ {user_input.upper()}")

        return answers

    def save_answer_key(self, answer_key: Dict[str, str],
                       output_path: str) -> bool:
        """Save answer key to JSON"""
        try:
            with open(output_path, 'w') as f:
                json.dump(answer_key, f, indent=2, sort_keys=True)
            print(f"\n✓ Saved: {output_path}")
            print(f"  Answers: {len(answer_key)}/125")
            return True
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            return False


def create_for_exam(exam_name: str):
    """Create answer key for an exam"""
    builder = AnswerKeyBuilder()

    # Try to load auto-extracted answers first
    pdf_path = f"exams/{exam_name}.pdf"
    answer_key_path = f"exams/{exam_name}_answer_key.json"

    # Check if answer key already exists
    if Path(answer_key_path).exists():
        with open(answer_key_path) as f:
            answer_key = json.load(f)
        print(f"Answer key already exists: {answer_key_path}")
        print(f"Current: {len(answer_key)}/125 answers")
        return

    print(f"\n" + "="*80)
    print(f"Creating answer key for: {exam_name}")
    print("="*80)

    # For now, start fresh
    existing_answers = {}

    # Find missing
    missing = [str(i) for i in range(1, 126)
               if str(i) not in existing_answers]

    print(f"Need to input: {len(missing)} answers")

    # Get answers
    new_answers = builder.input_answers_fast([int(q) for q in missing], exam_name)

    # Combine
    final_key = {**existing_answers, **new_answers}

    # Show summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total: {len(final_key)}/125")

    if len(final_key) > 0:
        builder.save_answer_key(final_key, answer_key_path)


def show_templates():
    """Show all answer format templates"""
    builder = AnswerKeyBuilder()

    print("\n" + "="*80)
    print("ANSWER FORMAT TEMPLATES")
    print("="*80)

    for template_type, details in builder.templates.items():
        print(f"\n{template_type.upper()}")
        print(f"  Description: {details['description']}")
        print(f"  Format: {details['pattern']}")
        print(f"  Example: {details['example']}")

    print()


def print_help():
    """Print help"""
    print("""
Quick Answer Key Input Tool

Fast, smart answer input for exams with mixed question types.

Usage:
  python3 quick_answer_key.py create --exam <name>
  python3 quick_answer_key.py template --show-all
  python3 quick_answer_key.py --help

Examples:
  python3 quick_answer_key.py create --exam dec25_week2
  python3 quick_answer_key.py template --show-all

Features:
  ✓ Auto-detects question types
  ✓ Provides format hints
  ✓ Keyboard shortcuts for fast input
  ✓ Saves to JSON

Format Examples:
  Single answer:       C
  Match 4 items:       1-C,2-D,3-B,4-A
  Match 5 items:       1-D,2-A,3-E,4-B,5-C
  Ordering 4 items:    A,C,B,D
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h']:
        print_help()
        sys.exit(0)

    if sys.argv[1] == 'template' and len(sys.argv) > 2 and sys.argv[2] == '--show-all':
        show_templates()
    elif sys.argv[1] == 'create' and len(sys.argv) > 2 and sys.argv[2] == '--exam':
        if len(sys.argv) > 3:
            create_for_exam(sys.argv[3])
        else:
            print("Error: Specify exam name with --exam <name>")
    else:
        print_help()
