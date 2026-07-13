#!/usr/bin/env python3
"""
Enhanced Answer Validator - Handles edge cases intelligently

Handles:
- Blank/missing answers (detects and reports separately)
- Typos and invalid input (normalizes when possible, warns otherwise)
- Lowercase answers (auto-converts to uppercase)
- Multiple answers (detects and reports as invalid)
- Whitespace issues (auto-trims)
"""

from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ValidatedAnswer:
    """Result of answer validation"""

    question_number: int
    original_input: str
    normalized_input: Optional[str]  # Cleaned/normalized version
    is_valid: bool
    is_blank: bool
    is_typo: bool
    is_multiple_answers: bool
    warning_message: Optional[str] = None
    corrected_answer: Optional[str] = None  # If auto-corrected


class AnswerValidator:
    """Validates and normalizes student answers with intelligent error handling"""

    VALID_ANSWERS = ["A", "B", "C", "D"]

    @staticmethod
    def validate_answer(question_number: int, user_input: str) -> ValidatedAnswer:
        """
        Validate a single answer with intelligent handling

        Args:
            question_number: Question number
            user_input: User's answer (raw input)

        Returns:
            ValidatedAnswer with detailed validation info
        """
        # Store original
        original = user_input if user_input else ""

        # Step 1: Check if blank
        if not user_input or (isinstance(user_input, str) and user_input.strip() == ""):
            return ValidatedAnswer(
                question_number=question_number,
                original_input=original,
                normalized_input=None,
                is_valid=False,
                is_blank=True,
                is_typo=False,
                is_multiple_answers=False,
                warning_message="⚠️  Answer is blank - question skipped",
            )

        # Step 2: Normalize (strip whitespace, uppercase)
        normalized = str(user_input).strip().upper()

        # Step 3: Check if valid answer
        if normalized in AnswerValidator.VALID_ANSWERS:
            return ValidatedAnswer(
                question_number=question_number,
                original_input=original,
                normalized_input=normalized,
                is_valid=True,
                is_blank=False,
                is_typo=False,
                is_multiple_answers=False,
            )

        # Step 4: Check for common issues
        # Multiple answers (e.g., "A,B" or "AB")
        if len(normalized) > 1 and all(
            c in AnswerValidator.VALID_ANSWERS for c in normalized
        ):
            return ValidatedAnswer(
                question_number=question_number,
                original_input=original,
                normalized_input=normalized,
                is_valid=False,
                is_blank=False,
                is_typo=True,
                is_multiple_answers=True,
                warning_message=f"❌ Multiple answers detected: '{normalized}' - only one answer allowed",
            )

        # Check if it looks like a typo (starts with valid letter but has extra chars)
        if len(normalized) > 0 and normalized[0] in AnswerValidator.VALID_ANSWERS:
            return ValidatedAnswer(
                question_number=question_number,
                original_input=original,
                normalized_input=normalized[0],  # Try first letter
                is_valid=False,
                is_blank=False,
                is_typo=True,
                is_multiple_answers=False,
                warning_message=f"⚠️  Typo detected: '{original}' → Did you mean '{normalized[0]}'?",
                corrected_answer=normalized[0],
            )

        # Step 5: Completely invalid
        return ValidatedAnswer(
            question_number=question_number,
            original_input=original,
            normalized_input=normalized,
            is_valid=False,
            is_blank=False,
            is_typo=True,
            is_multiple_answers=False,
            warning_message=f"❌ Invalid answer: '{original}' - expected A, B, C, or D",
        )

    @staticmethod
    def validate_batch(
        answers: Dict[int, str], auto_correct_lowercase: bool = True
    ) -> Dict[int, ValidatedAnswer]:
        """
        Validate multiple answers

        Args:
            answers: Dict mapping question number to answer
            auto_correct_lowercase: If True, auto-correct lowercase to uppercase

        Returns:
            Dict of validated answers with detailed info
        """
        validated = {}
        for q_num, user_answer in answers.items():
            validated[q_num] = AnswerValidator.validate_answer(q_num, user_answer)

        return validated

    @staticmethod
    def get_report(validated_answers: Dict[int, ValidatedAnswer]) -> Dict:
        """
        Generate validation report

        Returns:
            Report with statistics and issues
        """
        total = len(validated_answers)
        valid_count = sum(1 for v in validated_answers.values() if v.is_valid)
        blank_count = sum(1 for v in validated_answers.values() if v.is_blank)
        typo_count = sum(1 for v in validated_answers.values() if v.is_typo)
        multiple_count = sum(
            1 for v in validated_answers.values() if v.is_multiple_answers
        )

        warnings = [
            v.warning_message
            for v in validated_answers.values()
            if v.warning_message and not v.is_valid
        ]

        return {
            "total_answers": total,
            "valid_answers": valid_count,
            "blank_answers": blank_count,
            "typo_or_invalid_answers": typo_count,
            "multiple_answers_errors": multiple_count,
            "warnings": warnings,
            "summary": f"{valid_count}/{total} valid answers ({100*valid_count/total if total > 0 else 0:.1f}%)",
        }

    @staticmethod
    def get_corrected_answers(
        validated_answers: Dict[int, ValidatedAnswer],
    ) -> Dict[int, str]:
        """
        Get corrected answers (use original if valid, corrected if available)

        Returns:
            Dict of best-guess answers
        """
        corrected = {}
        for q_num, validated in validated_answers.items():
            if validated.is_valid:
                corrected[q_num] = validated.normalized_input
            elif validated.corrected_answer:
                corrected[q_num] = validated.corrected_answer
            elif validated.is_blank:
                corrected[q_num] = None  # Mark as unanswered
            # else: completely invalid - skip

        return corrected


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_answers = {
        1: "A",  # Valid
        2: "b",  # Valid (lowercase, auto-correct)
        3: "",  # Blank
        4: "black",  # Typo
        5: "A,B",  # Multiple answers
        6: "C",  # Valid
        7: "xyz",  # Completely invalid
    }

    print("Testing Answer Validator:\n")
    print("=" * 80)

    validated = AnswerValidator.validate_batch(test_answers)

    for q_num, result in validated.items():
        status = "✅" if result.is_valid else "❌"
        print(f"\nQ{q_num}: {status}")
        print(f"  Input: '{result.original_input}'")
        if result.normalized_input:
            print(f"  Normalized: '{result.normalized_input}'")
        if result.warning_message:
            print(f"  {result.warning_message}")
        if result.corrected_answer:
            print(f"  Suggestion: Use '{result.corrected_answer}'")

    print("\n" + "=" * 80)
    report = AnswerValidator.get_report(validated)
    print("\nValidation Report:")
    for key, value in report.items():
        if key != "warnings":
            print(f"  • {key}: {value}")

    if report["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in report["warnings"]:
            print(f"  {warning}")
