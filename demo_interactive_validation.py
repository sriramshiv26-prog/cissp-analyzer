#!/usr/bin/env python3
"""
Demo: Interactive Answer Key Validation
Shows how the validator would work with user confirmation
"""

from answer_validator_interactive import InteractiveAnswerValidator
from pathlib import Path


def demo():
    """Run a demo with some sample answers"""

    # Simulated extracted answers with intentional errors for demo
    sample_answers = {
        1: "D",  # High confidence - correct
        2: "A",  # Low confidence - user might correct to B
        3: "B",  # High confidence - correct
        4: "C",  # High confidence - correct
        5: "A",  # Low confidence - user might correct to C
        # ... etc
    }

    # Simulated context from PDF
    sample_context = {
        1: "... security domain is A. Physical B. Logical C. Risk D. Governance The correct answer is D...",
        2: "... should include A. Session tokens B. User credentials C. API keys D. ... answer is B...",
        3: "... PKI is A. X.509 B. PKCS #10 C. HSM ... correct answer is B...",
        4: "... CIA triad is A. Compliance B. Config C. Confidentiality Integrity Availability correct answer is C...",
        5: "... encryption is A. Process B. Algorithm C. Mechanism The correct answer is C...",
    }

    print("\n" + "=" * 80)
    print("INTERACTIVE VALIDATOR DEMO")
    print("=" * 80)
    print("\nThis shows how the validator helps catch extraction errors.")
    print("Low-confidence answers require user confirmation.\n")

    validator = InteractiveAnswerValidator()

    # For demo, let's show what would happen
    print("Sample: 5 extracted answers")
    print("-" * 80)
    for q_num in sorted(sample_answers.keys()):
        answer = sample_answers[q_num]
        context = sample_context.get(q_num, "")
        confidence = validator.calculate_confidence(answer, context)

        confidence_bar = "█" * int(confidence * 10) + "░" * (10 - int(confidence * 10))
        status = "✓ AUTO" if confidence >= 0.75 else "⚠ REVIEW"

        print(f"Q{q_num}: {answer} [{confidence_bar}] {confidence:.0%} {status}")

    print("\n" + "-" * 80)
    print("Questions marked [REVIEW] will ask for confirmation:")
    print("  [C]onfirm | [S]kip | [A/B/C/D] to correct\n")

    print("Benefits:")
    print("  ✓ Catches extraction errors before analysis")
    print("  ✓ Shows context so you can verify")
    print("  ✓ Records all corrections for audit trail")
    print("  ✓ No false positives from high-confidence answers")
    print("  ✓ Saves validation report (validation_report.json)")


if __name__ == "__main__":
    demo()
