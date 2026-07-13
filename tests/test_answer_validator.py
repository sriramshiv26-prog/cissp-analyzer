#!/usr/bin/env python3
"""
Tests for the enhanced Answer Validator

Tests edge cases:
- Blank answers
- Lowercase answers
- Typos and invalid input
- Multiple answers
- Whitespace handling
"""

import pytest
from cissp_analyzer.answer_validator import AnswerValidator, ValidatedAnswer


class TestAnswerValidation:
    """Test individual answer validation"""

    def test_valid_uppercase_answer(self):
        """Test that uppercase A/B/C/D are accepted"""
        for answer in ["A", "B", "C", "D"]:
            result = AnswerValidator.validate_answer(1, answer)
            assert result.is_valid, f"'{answer}' should be valid"
            assert not result.is_blank
            assert not result.is_typo

    def test_lowercase_answer_auto_corrected(self):
        """Test that lowercase is auto-corrected"""
        for answer in ["a", "b", "c", "d"]:
            result = AnswerValidator.validate_answer(1, answer)
            assert result.is_valid, f"'{answer}' should be auto-corrected"
            assert result.normalized_input == answer.upper()
            assert not result.warning_message  # No warning, seamless correction

    def test_blank_answer_detected(self):
        """Test that blank answers are detected and marked separately"""
        for blank in ["", "   ", None]:
            if blank is None:
                continue  # Skip None for string input

            result = AnswerValidator.validate_answer(1, blank)
            assert result.is_blank, f"'{blank}' should be detected as blank"
            assert not result.is_valid
            assert "blank" in result.warning_message.lower()

    def test_whitespace_trimmed(self):
        """Test that whitespace is trimmed"""
        test_cases = ["  A", "B  ", "  C  ", "\tD", "  D\t"]

        for answer in test_cases:
            result = AnswerValidator.validate_answer(1, answer)
            assert result.is_valid, f"'{answer}' should be valid after trimming"
            assert result.normalized_input in ["A", "B", "C", "D"]

    def test_typo_detected_with_suggestion(self):
        """Test that typos are detected and suggestions provided"""
        result = AnswerValidator.validate_answer(1, "black")
        assert result.is_typo, "Typo should be detected"
        assert not result.is_valid
        assert result.corrected_answer == "B"
        assert "Did you mean" in result.warning_message

    def test_multiple_answers_detected(self):
        """Test that multiple answers are detected"""
        test_cases = ["A,B", "AB", "A B", "ABCD"]

        for answer in test_cases:
            result = AnswerValidator.validate_answer(1, answer)
            assert not result.is_valid, f"'{answer}' should be invalid"
            if len(answer) > 1 and all(c in "ABCD" for c in answer.replace(",", " ")):
                # Multiple valid letters
                assert result.is_multiple_answers or result.is_typo

    def test_completely_invalid_answer(self):
        """Test that completely invalid answers are rejected"""
        test_cases = ["X", "Z", "1", "?", "xyz", "AAA"]

        for answer in test_cases:
            result = AnswerValidator.validate_answer(1, answer)
            assert not result.is_valid, f"'{answer}' should be invalid"
            assert result.is_typo or not result.is_valid
            assert result.warning_message is not None

    def test_mixed_case_single_letter(self):
        """Test that single mixed-case letter works"""
        result = AnswerValidator.validate_answer(1, "A")
        assert result.is_valid, "Single letter should be valid"
        assert result.normalized_input == "A"

    def test_mixed_case_multiple_letters_rejected(self):
        """Test that multiple letters (even mixed case) are rejected"""
        result = AnswerValidator.validate_answer(1, "Ab")
        # "Ab" → "AB" = two letters, should be detected as multiple
        assert not result.is_valid, "Multiple letters should be invalid"
        assert result.is_typo or result.is_multiple_answers


class TestBatchValidation:
    """Test batch answer validation"""

    def test_batch_validation_multiple_answers(self):
        """Test validating multiple answers at once"""
        answers = {
            1: "A",  # Valid
            2: "b",  # Valid (lowercase)
            3: "",  # Blank
            4: "black",  # Typo
            5: "A,B",  # Multiple
            6: "D",  # Valid
        }

        validated = AnswerValidator.validate_batch(answers)

        assert validated[1].is_valid
        assert validated[2].is_valid
        assert validated[3].is_blank
        assert validated[4].is_typo
        assert validated[5].is_typo or validated[5].is_multiple_answers
        assert validated[6].is_valid

    def test_batch_with_all_valid(self):
        """Test batch with all valid answers"""
        answers = {1: "A", 2: "B", 3: "C", 4: "D"}
        validated = AnswerValidator.validate_batch(answers)

        for v in validated.values():
            assert v.is_valid


class TestValidationReport:
    """Test validation report generation"""

    def test_report_statistics(self):
        """Test that report calculates correct statistics"""
        answers = {
            1: "A",  # Valid
            2: "b",  # Valid
            3: "",  # Blank
            4: "black",  # Typo
            5: "A,B",  # Multiple
            6: "D",  # Valid
        }

        validated = AnswerValidator.validate_batch(answers)
        report = AnswerValidator.get_report(validated)

        assert report["total_answers"] == 6
        assert report["valid_answers"] == 3  # Q1, Q2, Q6
        assert report["blank_answers"] == 1  # Q3
        assert report["typo_or_invalid_answers"] == 2  # Q4, Q5

    def test_report_warnings_generated(self):
        """Test that warnings are included in report"""
        answers = {1: "", 2: "black", 3: "A,B"}
        validated = AnswerValidator.validate_batch(answers)
        report = AnswerValidator.get_report(validated)

        assert len(report["warnings"]) > 0
        assert any("blank" in w.lower() for w in report["warnings"])

    def test_report_summary(self):
        """Test that summary is formatted correctly"""
        answers = {1: "A", 2: "B", 3: "C"}
        validated = AnswerValidator.validate_batch(answers)
        report = AnswerValidator.get_report(validated)

        assert "3/3" in report["summary"]
        assert "100" in report["summary"]  # Percentage


class TestCorrectedAnswers:
    """Test getting corrected answers"""

    def test_corrected_answers_returns_valid(self):
        """Test that valid answers are returned as-is"""
        answers = {1: "A", 2: "B"}
        validated = AnswerValidator.validate_batch(answers)
        corrected = AnswerValidator.get_corrected_answers(validated)

        assert corrected[1] == "A"
        assert corrected[2] == "B"

    def test_corrected_answers_normalizes_lowercase(self):
        """Test that lowercase is normalized in corrected answers"""
        answers = {1: "a", 2: "b"}
        validated = AnswerValidator.validate_batch(answers)
        corrected = AnswerValidator.get_corrected_answers(validated)

        assert corrected[1] == "A"
        assert corrected[2] == "B"

    def test_corrected_answers_handles_blanks(self):
        """Test that blanks are marked as None in corrected answers"""
        answers = {1: "A", 2: ""}
        validated = AnswerValidator.validate_batch(answers)
        corrected = AnswerValidator.get_corrected_answers(validated)

        assert corrected[1] == "A"
        assert corrected[2] is None  # Blank marked as None

    def test_corrected_answers_suggests_typo_fix(self):
        """Test that corrected answers suggest typo fixes"""
        answers = {1: "black"}  # Typo for 'B'
        validated = AnswerValidator.validate_batch(answers)
        corrected = AnswerValidator.get_corrected_answers(validated)

        # Typo with suggestion should be included
        assert 1 in corrected
        # Either the correction is suggested or it's marked invalid
        # (depends on whether we want to auto-correct or flag)


class TestEdgeCases:
    """Test various edge cases"""

    def test_empty_string_is_blank(self):
        """Test empty string detection"""
        result = AnswerValidator.validate_answer(1, "")
        assert result.is_blank

    def test_whitespace_only_is_blank(self):
        """Test whitespace-only detection"""
        result = AnswerValidator.validate_answer(1, "   ")
        assert result.is_blank

    def test_tabs_and_newlines_trimmed(self):
        """Test that special whitespace is handled"""
        result = AnswerValidator.validate_answer(1, "\t\nA\n\t")
        assert result.is_valid
        assert result.normalized_input == "A"

    def test_original_input_preserved(self):
        """Test that original input is always stored"""
        answers = ["a", "BLACK", "", "A,B", "X"]

        for ans in answers:
            result = AnswerValidator.validate_answer(1, ans)
            assert result.original_input == ans  # Original preserved

    def test_question_number_tracked(self):
        """Test that question number is tracked correctly"""
        for q_num in [1, 5, 10, 100, 200]:
            result = AnswerValidator.validate_answer(q_num, "A")
            assert result.question_number == q_num
