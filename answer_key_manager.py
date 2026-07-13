#!/usr/bin/env python3
"""
Interactive Answer Key Manager
Handles extraction, validation, and user confirmation for answer keys
"""

import json
import re
from pathlib import Path
from typing import Dict, Tuple, Optional
import pypdf


class ConfidenceReport:
    """Tracks answer key extraction confidence"""

    def __init__(self):
        self.total_extracted = 0
        self.pattern_matches = 0
        self.validation_issues = []
        self.warnings = []
        self.confidence_score = 0.0

    def calculate(self, extracted_count: int, expected_min: int = 50) -> float:
        """Calculate confidence score (0.0 to 1.0)"""
        if extracted_count < expected_min:
            self.warnings.append(f"Low answer count: {extracted_count} (expected >= {expected_min})")
            self.confidence_score = 0.3
        elif extracted_count >= 100:
            self.confidence_score = 0.95
        else:
            self.confidence_score = 0.7 + (extracted_count - expected_min) / 100 * 0.25

        return self.confidence_score

    def to_dict(self):
        return {
            "confidence_score": round(self.confidence_score, 2),
            "total_extracted": self.total_extracted,
            "warnings": self.warnings,
            "validation_issues": self.validation_issues,
        }


class AnswerKeyManager:
    """Manages answer key extraction with interactive fallback"""

    CONFIDENCE_THRESHOLD = 0.75  # If below this, ask user

    def __init__(self, exam_folder: Path):
        self.exam_folder = exam_folder
        self.answer_keys_dir = exam_folder / "answer_keys"
        self.answer_keys_dir.mkdir(exist_ok=True)

    def load_answer_key(
        self, pdf_path: str, interactive: bool = True
    ) -> Dict[int, str]:
        """
        Load answer key with automatic extraction + interactive fallback

        Args:
            pdf_path: Path to PDF file
            interactive: Whether to show interactive prompts

        Returns:
            Dict mapping question number to correct answer (A/B/C/D)
        """
        print("\n" + "=" * 80)
        print("ANSWER KEY MANAGER")
        print("=" * 80 + "\n")

        # Step 1: Try automatic extraction
        print("Step 1: Attempting automatic extraction from PDF...")
        print("-" * 80)
        extracted_key, report = self.extract_from_pdf(pdf_path)
        confidence = report.calculate(len(extracted_key))

        print(f"Extracted: {len(extracted_key)} answers")
        print(f"Confidence: {confidence:.0%}")

        if report.warnings:
            print("\nWarnings:")
            for warning in report.warnings:
                print(f"  ⚠️  {warning}")

        # Step 2: Check confidence
        if confidence >= self.CONFIDENCE_THRESHOLD and len(extracted_key) >= 50:
            print(f"\n✓ Confidence sufficient ({confidence:.0%}). Using extracted key.")
            self._save_answer_key(extracted_key, "automatic")
            return extracted_key

        # Step 3: Ask user to choose
        if not interactive:
            print(f"\n✗ Confidence too low ({confidence:.0%}) and interactive mode disabled.")
            return extracted_key

        print(f"\n⚠️  Confidence too low ({confidence:.0%}). Need user input.\n")
        return self._interactive_wizard(pdf_path, extracted_key, confidence)

    def extract_from_pdf(self, pdf_path: str) -> Tuple[Dict[int, str], ConfidenceReport]:
        """
        Extract answer key from PDF using robust line-by-line parsing

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (answer_key dict, confidence report)
        """
        report = ConfidenceReport()

        try:
            with open(pdf_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                all_text = ""
                for page in pdf_reader.pages:
                    all_text += page.extract_text()

            # Extract answers using regex for "correct answer is [A-D]" pattern
            import re
            answers = []

            # More robust regex: look for "correct answer is X" where X is A-D
            pattern = r"(?:correct\s+answer\s+is|answer\s+is)\s+([A-D])"
            matches = re.finditer(pattern, all_text, re.IGNORECASE)

            for match in matches:
                answers.append(match.group(1).upper())
                report.pattern_matches += 1

            # Create answer key
            answer_key = {i: ans for i, ans in enumerate(answers, 1)}
            report.total_extracted = len(answer_key)

            return answer_key, report

        except Exception as e:
            report.warnings.append(f"PDF extraction error: {str(e)}")
            return {}, report

    def _interactive_wizard(
        self, pdf_path: str, partial_key: Dict[int, str], confidence: float
    ) -> Dict[int, str]:
        """
        Interactive wizard for answer key entry/correction

        Args:
            pdf_path: Path to PDF
            partial_key: Partially extracted answer key (if any)
            confidence: Confidence score of extraction

        Returns:
            Final validated answer key
        """
        print("\n" + "=" * 80)
        print("ANSWER KEY WIZARD - SELECT YOUR OPTION")
        print("=" * 80 + "\n")

        print(f"Current Status:")
        print(f"  Extracted: {len(partial_key)} answers")
        print(f"  Confidence: {confidence:.0%}")
        print()

        print("Options:")
        print("  1) Use extracted answers (at your own risk)")
        print("  2) Upload answer_key.json file")
        print("  3) Enter answers manually (interactive Q&A)")
        print("  4) Review and correct extracted answers")
        print("  5) Skip this exam")
        print()

        choice = input("Select option (1-5): ").strip()

        if choice == "1":
            print("\n⚠️  Using extracted answers with low confidence.")
            print("     Results may be inaccurate. Verify after analysis.")
            self._save_answer_key(partial_key, "auto_low_confidence")
            return partial_key

        elif choice == "2":
            return self._load_json_upload()

        elif choice == "3":
            return self._manual_entry_wizard()

        elif choice == "4":
            return self._review_and_correct(partial_key)

        elif choice == "5":
            print("\nSkipping this exam.")
            return {}

        else:
            print("Invalid option. Try again.")
            return self._interactive_wizard(pdf_path, partial_key, confidence)

    def _load_json_upload(self) -> Dict[int, str]:
        """
        Load answer key from JSON file upload

        Returns:
            Answer key dictionary
        """
        print("\n" + "-" * 80)
        print("UPLOAD ANSWER KEY (JSON Format)")
        print("-" * 80 + "\n")

        print("Expected JSON format:")
        print("""
{
  "1": "D",
  "2": "B",
  "3": "A",
  ...
}
or
{
  "Q1": "D",
  "Q2": "B",
  ...
}
        """)

        json_path = input("\nEnter path to answer_key.json file: ").strip()

        try:
            with open(json_path, "r") as f:
                data = json.load(f)

            # Normalize keys to integers
            answer_key = {}
            for key, value in data.items():
                # Remove 'Q' prefix if present
                clean_key = key.replace("Q", "").replace("q", "")
                q_num = int(clean_key)
                answer_key[q_num] = str(value).upper().strip()

            print(f"\n✓ Loaded {len(answer_key)} answers from JSON")
            self._save_answer_key(answer_key, "json_upload")
            return answer_key

        except Exception as e:
            print(f"\n✗ Error loading JSON: {e}")
            retry = input("Try again? (Y/N): ").strip().lower()
            if retry == "y":
                return self._load_json_upload()
            else:
                return {}

    def _manual_entry_wizard(self) -> Dict[int, str]:
        """
        Interactive Q&A for manual answer entry

        Returns:
            Answer key from user input
        """
        print("\n" + "-" * 80)
        print("MANUAL ANSWER ENTRY")
        print("-" * 80 + "\n")

        print("Enter answers one by one (type 'done' to finish)")
        print("Format: Just type A, B, C, or D")
        print()

        answer_key = {}
        q_num = 1

        while True:
            ans = input(f"Q{q_num:3d}: ").strip().upper()

            if ans.lower() == "done":
                break

            if ans in ["A", "B", "C", "D"]:
                answer_key[q_num] = ans
                q_num += 1
            elif ans == "SKIP":
                q_num += 1
            else:
                print("  Invalid input. Enter A, B, C, D, 'SKIP', or 'DONE'")

        print(f"\n✓ Entered {len(answer_key)} answers")
        self._save_answer_key(answer_key, "manual_entry")
        return answer_key

    def _review_and_correct(self, partial_key: Dict[int, str]) -> Dict[int, str]:
        """
        Review extracted answers and allow corrections

        Args:
            partial_key: Extracted answer key to review

        Returns:
            Corrected answer key
        """
        print("\n" + "-" * 80)
        print("REVIEW AND CORRECT EXTRACTED ANSWERS")
        print("-" * 80 + "\n")

        print("Review answers. To change, type new answer (A/B/C/D).")
        print("Press ENTER to keep current answer. Type 'done' to finish.\n")

        corrected_key = partial_key.copy()

        for q_num in sorted(partial_key.keys()):
            current = partial_key[q_num]
            correction = input(f"Q{q_num:3d}: {current} → ").strip().upper()

            if correction == "DONE":
                break
            elif correction in ["A", "B", "C", "D"]:
                corrected_key[q_num] = correction
            elif correction == "":
                # Keep current
                pass
            else:
                print("  Invalid input. Keeping original.")

        print(f"\n✓ Reviewed {len(corrected_key)} answers")
        self._save_answer_key(corrected_key, "manual_review")
        return corrected_key

    def _save_answer_key(
        self, answer_key: Dict[int, str], method: str = "unknown"
    ) -> Path:
        """
        Save answer key to exam folder

        Args:
            answer_key: Answer key dictionary
            method: How it was obtained (for tracking)

        Returns:
            Path to saved answer key file
        """
        output_file = self.answer_keys_dir / "answer_key.json"

        # Convert to string keys for JSON
        json_data = {str(k): v for k, v in answer_key.items()}

        with open(output_file, "w") as f:
            json.dump(json_data, f, indent=2)

        # Save metadata
        metadata = {
            "method": method,
            "total_answers": len(answer_key),
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

        metadata_file = self.answer_keys_dir / "answer_key_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✓ Saved to: {output_file}")
        return output_file

    def get_answer_key(self) -> Optional[Dict[int, str]]:
        """Load existing answer key from exam folder"""
        key_file = self.answer_keys_dir / "answer_key.json"

        if not key_file.exists():
            return None

        with open(key_file, "r") as f:
            data = json.load(f)
            # Convert string keys back to integers
            return {int(k): v for k, v in data.items()}
