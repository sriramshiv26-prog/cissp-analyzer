#!/usr/bin/env python3
"""
Exam Question & Answer Key Validator

Validates that exam PDFs have:
- Complete questions (125 total)
- Complete answer key (125 total)
- Proper format and alignment
- No mismatches or missing data

Must be run BEFORE student answer analysis!
"""

import json
import re
from pathlib import Path
from typing import Tuple, Dict
from pypdf import PdfReader


class ExamValidator:
    """Validates exam PDFs for completeness and correctness"""

    EXPECTED_QUESTIONS = 125
    VALID_ANSWERS = ["A", "B", "C", "D"]

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.issues: list = []
        self.warnings: list = []
        self.questions: Dict[int, str] = {}
        self.answer_key: Dict[int, str] = {}

    def extract_questions(self) -> Dict[int, str]:
        """Extract questions from PDF"""
        if not self.pdf_path.exists():
            self.issues.append(f"PDF not found: {self.pdf_path}")
            return {}

        try:
            reader = PdfReader(str(self.pdf_path))
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text() + "\n"

            # Extract questions: "1. What is..." format
            questions = {}

            for line in all_text.split("\n"):
                # Match: "123. Question text here"
                match = re.match(r"^(\d+)\.\s+(.+?)(?:\nA\.|$)", line, re.MULTILINE)
                if match:
                    q_num = int(match.group(1))
                    q_text = match.group(2).strip()[:100]  # First 100 chars
                    if 1 <= q_num <= self.EXPECTED_QUESTIONS:
                        questions[q_num] = q_text

            self.questions = questions
            return questions

        except Exception as e:
            self.issues.append(f"Error extracting questions: {str(e)}")
            return {}

    def extract_answer_key(self) -> Dict[int, str]:
        """Extract answer key from PDF"""
        if not self.pdf_path.exists():
            self.issues.append(f"PDF not found: {self.pdf_path}")
            return {}

        try:
            reader = PdfReader(str(self.pdf_path))
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text() + "\n"

            # Extract answers: "123. A. Explanation..." format
            answers = {}
            pattern = r"^(\d+)\.\s+([A-D])\."

            for line in all_text.split("\n"):
                match = re.match(pattern, line.strip())
                if match:
                    q_num = int(match.group(1))
                    answer = match.group(2)
                    if 1 <= q_num <= self.EXPECTED_QUESTIONS:
                        answers[q_num] = answer

            self.answer_key = answers
            return answers

        except Exception as e:
            self.issues.append(f"Error extracting answer key: {str(e)}")
            return {}

    def validate_questions(self) -> bool:
        """Validate question completeness"""
        print("\n📋 VALIDATING QUESTIONS")
        print("-" * 80)

        if not self.questions:
            self.issues.append("No questions extracted from PDF")
            return False

        # Check count
        if len(self.questions) < self.EXPECTED_QUESTIONS:
            missing = [
                i
                for i in range(1, self.EXPECTED_QUESTIONS + 1)
                if i not in self.questions
            ]
            missing_count = self.EXPECTED_QUESTIONS - len(self.questions)
            missing_preview = missing[:10]
            missing_more = "..." if len(missing) > 10 else ""
            self.issues.append(
                f"Missing {missing_count} questions: {missing_preview}{missing_more}"
            )
            print(
                f"✗ Only {len(self.questions)}/{self.EXPECTED_QUESTIONS} questions found"
            )
            return False

        if len(self.questions) == self.EXPECTED_QUESTIONS:
            print(f"✓ All {self.EXPECTED_QUESTIONS} questions extracted")
            return True

        return False

    def validate_answer_key(self) -> bool:
        """Validate answer key completeness"""
        print("\n🔑 VALIDATING ANSWER KEY")
        print("-" * 80)

        if not self.answer_key:
            self.issues.append("No answer key extracted from PDF")
            return False

        # Check count
        if len(self.answer_key) < self.EXPECTED_QUESTIONS:
            missing = [
                i
                for i in range(1, self.EXPECTED_QUESTIONS + 1)
                if i not in self.answer_key
            ]
            missing_count = self.EXPECTED_QUESTIONS - len(self.answer_key)
            missing_preview = missing[:10]
            missing_more = "..." if len(missing) > 10 else ""
            self.issues.append(
                f"Missing {missing_count} answers: {missing_preview}{missing_more}"
            )
            print(
                f"✗ Only {len(self.answer_key)}/{self.EXPECTED_QUESTIONS} answers found"
            )
            print(f"  Missing: {missing[:10]}{'...' if len(missing) > 10 else ''}")
            return False

        if len(self.answer_key) == self.EXPECTED_QUESTIONS:
            print(f"✓ All {self.EXPECTED_QUESTIONS} answers extracted")
            return True

        return False

    def validate_answer_format(self) -> bool:
        """Validate all answers are A/B/C/D"""
        print("\n✓ VALIDATING ANSWER FORMAT")
        print("-" * 80)

        invalid = []
        for q_num, answer in self.answer_key.items():
            if answer not in self.VALID_ANSWERS:
                invalid.append((q_num, answer))

        if invalid:
            self.issues.append(
                f"Invalid answer formats: {invalid[:5]}{'...' if len(invalid) > 5 else ''}"
            )
            print(f"✗ {len(invalid)} invalid answers found:")
            for q_num, ans in invalid[:10]:
                print(f"  Q{q_num}: '{ans}' (expected A/B/C/D)")
            return False

        print("✓ All answers are valid (A/B/C/D)")
        return True

    def validate_alignment(self) -> bool:
        """Validate questions and answers align"""
        print("\n⚙️  VALIDATING ALIGNMENT")
        print("-" * 80)

        # Both must have same count
        if len(self.questions) != len(self.answer_key):
            q_count = len(self.questions)
            a_count = len(self.answer_key)
            self.issues.append(
                f"Question/Answer mismatch: {q_count} questions vs {a_count} answers"
            )
            print("✗ Question/Answer count mismatch:")
            print(f"  Questions: {len(self.questions)}")
            print(f"  Answers:   {len(self.answer_key)}")
            return False

        # Check for gaps
        q_nums = set(self.questions.keys())
        a_nums = set(self.answer_key.keys())

        if q_nums != a_nums:
            missing_in_answers = q_nums - a_nums
            missing_in_questions = a_nums - q_nums
            if missing_in_answers:
                self.warnings.append(
                    f"Answers missing for: {sorted(missing_in_answers)[:10]}"
                )
            if missing_in_questions:
                self.warnings.append(
                    f"Questions missing for: {sorted(missing_in_questions)[:10]}"
                )

        if not self.warnings:
            print("✓ Questions and answers perfectly aligned")
            return True

        return len(self.issues) == 0

    def validate(self) -> Tuple[bool, Dict]:
        """Run complete validation"""
        print("\n" + "=" * 80)
        print("EXAM PDF VALIDATION")
        print("=" * 80)
        print(f"File: {self.pdf_path.name}")

        # Extract
        self.extract_questions()
        self.extract_answer_key()

        # Validate
        self.validate_questions()
        self.validate_answer_key()
        self.validate_answer_format()
        self.validate_alignment()

        # Summary
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        if self.issues:
            print("\n❌ CRITICAL ISSUES (must fix):")
            for issue in self.issues:
                print(f"   • {issue}")

        if self.warnings:
            print("\n⚠️  WARNINGS (should review):")
            for warning in self.warnings:
                print(f"   • {warning}")

        is_valid = len(self.issues) == 0

        print()
        if is_valid:
            print("✅ EXAM VALIDATED - Ready for student analysis")
        else:
            print("❌ EXAM VALIDATION FAILED - Fix issues before processing")

        print("=" * 80 + "\n")

        return is_valid, {
            "valid": is_valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "questions_found": len(self.questions),
            "answers_found": len(self.answer_key),
            "questions": self.questions,
            "answer_key": self.answer_key,
        }

    def save_answer_key(self, output_path: str) -> bool:
        """Save validated answer key to JSON"""
        if len(self.answer_key) != self.EXPECTED_QUESTIONS:
            found = len(self.answer_key)
            expected = self.EXPECTED_QUESTIONS
            print(f"Cannot save incomplete answer key ({found}/{expected})")
            return False

        try:
            # Convert to string keys for JSON
            answer_key_str = {str(k): v for k, v in sorted(self.answer_key.items())}
            with open(output_path, "w") as f:
                json.dump(answer_key_str, f, indent=2)
            print(f"✓ Answer key saved to: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error saving answer key: {str(e)}")
            return False
