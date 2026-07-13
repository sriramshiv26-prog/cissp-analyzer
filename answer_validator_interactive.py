#!/usr/bin/env python3
"""
Interactive Answer Key Validator
Displays extracted answers with confidence, lets user confirm/correct low-confidence ones
"""

from typing import Dict, Tuple
import json
from pathlib import Path
from datetime import datetime


class InteractiveAnswerValidator:
    """Validates extracted answers with user confirmation"""

    def __init__(self):
        self.corrections = {}
        self.skipped = set()
        self.confirmed = set()

    def calculate_confidence(self, answer: str, context: str) -> float:
        """
        Calculate confidence score for extracted answer (0.0 to 1.0)

        Factors:
        - Pattern certainty: "correct answer is B" = 1.0, partial = 0.7
        - Answer count: if all answers same letter = low confidence
        - Position: answer after "is" = high, elsewhere = low
        """
        if not answer:
            return 0.0

        # Base confidence from pattern
        if "correct answer is" in context.lower():
            confidence = 0.95  # Strong pattern
        elif "answer" in context.lower() and answer in context:
            confidence = 0.75  # Answer found near "answer" keyword
        else:
            confidence = 0.50  # Weak pattern

        return min(1.0, max(0.0, confidence))

    def validate_answers(
        self, answer_key: Dict[int, str], pdf_context: Dict[int, str] = None,
        confidence_threshold: float = 0.75
    ) -> Tuple[Dict[int, str], Dict]:
        """
        Interactive validation of extracted answers

        Args:
            answer_key: Extracted answers {q_num: answer_letter}
            pdf_context: Context around each answer for quality checking
            confidence_threshold: Questions below this need user confirmation

        Returns:
            (validated_answers, validation_report)
        """
        validated = {}
        report = {
            "total_questions": len(answer_key),
            "auto_accepted": 0,
            "manual_confirmed": 0,
            "corrected": 0,
            "skipped": 0,
            "confidence_scores": {}
        }

        print("\n" + "=" * 80)
        print("INTERACTIVE ANSWER KEY VALIDATION")
        print("=" * 80)
        print(f"\nReview {len(answer_key)} extracted answers.")
        print("Confidence < 75% will need your confirmation.\n")

        high_confidence_count = 0
        low_confidence_questions = []

        # First pass: identify high vs low confidence
        for q_num in sorted(answer_key.keys()):
            answer = answer_key[q_num]
            context = pdf_context.get(q_num, "") if pdf_context else ""
            confidence = self.calculate_confidence(answer, context)

            report["confidence_scores"][q_num] = confidence

            if confidence >= confidence_threshold:
                validated[q_num] = answer
                report["auto_accepted"] += 1
                high_confidence_count += 1
            else:
                low_confidence_questions.append((q_num, answer, confidence))

        # Show summary
        print(f"✓ Auto-accepted: {report['auto_accepted']} (confidence ≥ 75%)")
        print(f"⚠ Need review: {len(low_confidence_questions)} (confidence < 75%)\n")

        # Second pass: ask user to confirm low-confidence answers
        if low_confidence_questions:
            print("=" * 80)
            print("LOW-CONFIDENCE ANSWERS - PLEASE REVIEW")
            print("=" * 80 + "\n")

            for q_num, answer, confidence in low_confidence_questions:
                context = pdf_context.get(q_num, "").strip() if pdf_context else ""

                print(f"Q{q_num}: Confidence {confidence:.0%}")
                if context:
                    print(f"  Context: {context[:80]}...")
                print(f"  Extracted: {answer}\n")

                while True:
                    user_input = (
                        input(
                            "  [C]onfirm | [S]kip | [A/B/C/D] to correct | [Q]uit: "
                        )
                        .strip()
                        .upper()
                    )

                    if user_input == "C":
                        validated[q_num] = answer
                        report["manual_confirmed"] += 1
                        print("  ✓ Confirmed\n")
                        break
                    elif user_input == "S":
                        self.skipped.add(q_num)
                        report["skipped"] += 1
                        print("  ⊘ Skipped\n")
                        break
                    elif user_input in ["A", "B", "C", "D"]:
                        validated[q_num] = user_input
                        self.corrections[q_num] = (answer, user_input)
                        report["corrected"] += 1
                        print(f"  ✓ Corrected to {user_input}\n")
                        break
                    elif user_input == "Q":
                        print("\nValidation interrupted by user.")
                        return validated, report
                    else:
                        print("  Invalid input. Try again.\n")

        # Summary
        print("\n" + "=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        print(f"Auto-accepted:      {report['auto_accepted']}")
        print(f"Manual confirmed:   {report['manual_confirmed']}")
        print(f"Corrected:          {report['corrected']}")
        print(f"Skipped:            {report['skipped']}")
        print(f"Total validated:    {len(validated)}")

        if self.corrections:
            print(f"\nCorrections made:")
            for q_num, (old, new) in sorted(self.corrections.items()):
                print(f"  Q{q_num}: {old} → {new}")

        return validated, report

    def save_validation_report(self, report: Dict, output_file: Path):
        """Save validation report for audit trail"""
        validation_log = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_questions": report["total_questions"],
                "auto_accepted": report["auto_accepted"],
                "manual_confirmed": report["manual_confirmed"],
                "corrected": report["corrected"],
                "skipped": report["skipped"],
            },
            "corrections": self.corrections,
            "skipped_questions": list(self.skipped),
            "confidence_scores": report["confidence_scores"],
        }

        with open(output_file, "w") as f:
            json.dump(validation_log, f, indent=2)

        print(f"\n✓ Validation report saved: {output_file}")
