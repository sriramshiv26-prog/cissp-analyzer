#!/usr/bin/env python3
"""
Critical Answer Verification Tool
Helps identify which answers need manual verification against PDF
"""

import json
from pathlib import Path

def verify_critical_answers():
    """Verify critical questions that may have extraction errors"""

    repo_path = Path(__file__).parent
    answer_key_path = repo_path / "exams/CISSP_July_2026/answer_keys/answer_key.json"

    with open(answer_key_path, 'r') as f:
        answer_key = json.load(f)

    # Questions that may have been corrected
    suspicious_questions = {
        144: {'topic': 'Interpreted language question'},
        147: {'topic': 'Privacy violation question'},
        156: {'topic': 'SW-CMM model question'},
        157: {'topic': 'Process/Order question'},
        158: {'topic': 'Business continuity or framework'},
        159: {'topic': 'Risk or compliance question'},
        160: {'topic': 'Framework or model question'},
        161: {'topic': 'Scenario or application question'},
        4: {'topic': 'MAD vs RTO comparison'},
        12: {'topic': 'Definition or concept'},
        17: {'topic': 'SLA application'},
    }

    print("=" * 80)
    print("CRITICAL ANSWER VERIFICATION")
    print("=" * 80)
    print("\nThese questions were identified as potentially having extraction errors:")
    print("Please verify these answers against your PDF:\n")

    for q_num in sorted(suspicious_questions.keys()):
        current = answer_key.get(str(q_num), "NOT FOUND")
        print(f"\nQ{q_num}: {suspicious_questions[q_num]['topic']}")
        print(f"  Current answer: {current}")
        print(f"  ✓ Correct? Type the letter (A/B/C/D) or press Enter to skip")

        # Interactive verification
        user_input = input("  >> ").strip().upper()

        if user_input in ['A', 'B', 'C', 'D']:
            if user_input != current:
                print(f"  ⚠️  CHANGE: {current} → {user_input}")
                answer_key[str(q_num)] = user_input
            else:
                print(f"  ✓ Confirmed: {current}")
        elif user_input == "":
            print(f"  → Skipped (keeping {current})")
        else:
            print(f"  ✗ Invalid input, skipped")

    # Save changes
    print("\n" + "=" * 80)
    save_choice = input("\nSave changes to answer key? (y/n): ").strip().lower()

    if save_choice == 'y':
        with open(answer_key_path, 'w') as f:
            json.dump(answer_key, f, indent=2)
        print("✓ Answer key updated!")
        print(f"  Saved to: {answer_key_path}")

        # Show what changed
        changes = []
        for q_num in sorted(suspicious_questions.keys()):
            with open(answer_key_path, 'r') as f:
                updated = json.load(f)
            if updated.get(str(q_num)) != answer_key.get(str(q_num)):
                changes.append(f"Q{q_num}")

        if changes:
            print(f"\n  Modified questions: {', '.join(changes)}")
    else:
        print("✗ Changes discarded")

if __name__ == "__main__":
    verify_critical_answers()
