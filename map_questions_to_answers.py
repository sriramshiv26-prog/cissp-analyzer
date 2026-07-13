#!/usr/bin/env python3
"""
Interactive Question Bank Mapper - Link Answer Sheets to Question PDFs

Step-by-step wizard that:
1. Detects all question bank PDFs in batch directory
2. Lists all available answer sheets
3. For each PDF, asks user to select which answer sheets belong to it
4. Creates explicit mappings showing PDF → Answer Sheets
5. Saves mapping manifest for reference

This prevents confusion when multiple question banks are present.

Usage:
  python3 map_questions_to_answers.py --batch <batch_name>
  python3 map_questions_to_answers.py --batch <batch_name> --auto-match
  python3 map_questions_to_answers.py --batch <batch_name> --show-mapping
  python3 map_questions_to_answers.py --help

Examples:
  python3 map_questions_to_answers.py --batch july12
  python3 map_questions_to_answers.py --batch july12 --auto-match
  python3 map_questions_to_answers.py --batch july12 --show-mapping
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class QuestionBankMapper:
    """Interactive mapper for linking answer sheets to question banks"""

    @staticmethod
    def detect_question_banks(batch_dir: str) -> List[str]:
        """
        Detect all question bank PDFs in directory.

        Returns:
            List of PDF filenames
        """
        batch_path = Path(batch_dir)

        if not batch_path.exists():
            return []

        # Look for PDFs (typically question banks)
        pdfs = sorted([f.name for f in batch_path.glob("*.pdf")])

        return pdfs

    @staticmethod
    def detect_answer_sheets(batch_dir: str) -> List[str]:
        """
        Detect all answer sheet files in directory.

        Returns:
            List of answer sheet filenames (JSON, Excel)
        """
        batch_path = Path(batch_dir)

        if not batch_path.exists():
            return []

        # Look for answer files (JSON, Excel)
        answer_files = sorted(
            [f.name for f in batch_path.glob("*.json")]
            + [f.name for f in batch_path.glob("*.xlsx")]
            + [f.name for f in batch_path.glob("*.xls")]
        )

        return answer_files

    @staticmethod
    def suggest_matching(pdf_name: str, answer_files: List[str]) -> List[str]:
        """
        Suggest which answer files match a PDF based on filename similarity.

        Returns:
            List of likely matching answer files
        """
        from difflib import SequenceMatcher

        pdf_normalized = pdf_name.lower().replace(".pdf", "").replace("_", "")
        suggestions = []

        for answer_file in answer_files:
            answer_normalized = answer_file.lower().replace(".json", "").replace(".xlsx", "").replace(".xls", "").replace("_", "")

            # Calculate similarity
            similarity = SequenceMatcher(None, pdf_normalized, answer_normalized).ratio()

            if similarity > 0.6:  # 60% match threshold
                suggestions.append((answer_file, similarity))

        # Sort by similarity
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return [f[0] for f in suggestions]

    @staticmethod
    def interactive_mapping(batch_dir: str) -> Tuple[bool, Dict]:
        """
        Run interactive wizard to map answer sheets to question banks.

        Returns:
            Tuple of (success, mapping_dict)
        """
        mapping = {
            "batch": batch_dir,
            "created": datetime.now().isoformat(),
            "question_banks": {},
            "unmapped_answers": [],
            "notes": [],
        }

        print("\n" + "=" * 80)
        print("QUESTION BANK → ANSWER SHEET MAPPER")
        print("=" * 80)

        batch_path = Path(batch_dir)

        # Step 1: Detect PDFs
        print("\n📋 STEP 1: DETECTING QUESTION BANKS")
        print("-" * 80)

        pdfs = QuestionBankMapper.detect_question_banks(batch_dir)

        if not pdfs:
            print("✗ No PDF files found in batch directory")
            print("  Please place question bank PDFs in the batch directory first")
            return False, mapping

        print(f"\n✓ Found {len(pdfs)} question bank PDF(s):\n")
        for i, pdf in enumerate(pdfs, 1):
            print(f"  {i}. {pdf}")

        # Step 2: Detect answer sheets
        print("\n\n📄 STEP 2: DETECTING ANSWER SHEETS")
        print("-" * 80)

        answer_files = QuestionBankMapper.detect_answer_sheets(batch_dir)

        if not answer_files:
            print("✗ No answer sheet files found (JSON or Excel)")
            print("  Please place answer sheets in the batch directory")
            return False, mapping

        print(f"\n✓ Found {len(answer_files)} answer sheet(s):\n")
        for i, answer_file in enumerate(answer_files, 1):
            print(f"  {i}. {answer_file}")

        # Step 3: Interactive mapping for each PDF
        print("\n\n🔗 STEP 3: MAPPING ANSWER SHEETS TO QUESTION BANKS")
        print("-" * 80)

        mapped_answers = set()

        for pdf_idx, pdf_name in enumerate(pdfs, 1):
            print(f"\n{'='*80}")
            print(f"QUESTION BANK {pdf_idx}/{len(pdfs)}: {pdf_name}")
            print(f"{'='*80}")

            # Get suggestions
            suggestions = QuestionBankMapper.suggest_matching(pdf_name, answer_files)

            print(f"\nAnswer sheets for this question bank:")
            print(f"\n📌 Suggested matches:")
            if suggestions:
                for j, suggestion in enumerate(suggestions[:5], 1):  # Show top 5
                    print(f"   {j}. {suggestion}")
            else:
                print("   (No suggestions based on filename)")

            print(f"\n📋 All available answer sheets:")
            for j, answer_file in enumerate(answer_files, 1):
                marker = "✓" if answer_file in mapped_answers else " "
                print(f"   {j}. [{marker}] {answer_file}")

            # Ask user to select
            print(f"\n❓ Which answer sheets belong to '{pdf_name}'?")
            print(f"   Enter numbers separated by spaces (e.g., 1 2 3)")
            print(f"   Press Enter to skip: ", end="")

            try:
                selection = input().strip()

                if selection:
                    # Parse selection
                    try:
                        selected_indices = [int(x) - 1 for x in selection.split()]
                        selected_answers = [
                            answer_files[i]
                            for i in selected_indices
                            if 0 <= i < len(answer_files)
                        ]

                        if selected_answers:
                            mapping["question_banks"][pdf_name] = {
                                "answer_sheets": selected_answers,
                                "count": len(selected_answers),
                                "mapped_by": "user_interactive",
                            }

                            for answer in selected_answers:
                                mapped_answers.add(answer)

                            print(f"\n✓ Mapped {len(selected_answers)} answer sheet(s) to {pdf_name}")
                        else:
                            print(f"\n✗ Invalid selection")
                            mapping["notes"].append(f"⚠ {pdf_name}: Invalid selection")

                    except ValueError:
                        print(f"\n✗ Invalid input format")
                        mapping["notes"].append(
                            f"⚠ {pdf_name}: Invalid input, skipped"
                        )
                else:
                    print(f"  Skipped")
                    mapping["notes"].append(f"⚠ {pdf_name}: Skipped by user")

            except EOFError:
                print("\n  (No input - skipped)")
                mapping["notes"].append(f"⚠ {pdf_name}: No input, skipped")

        # Step 4: Show unmapped answers
        print(f"\n\n✓ STEP 4: MAPPING SUMMARY")
        print("-" * 80)

        unmapped = [f for f in answer_files if f not in mapped_answers]

        if unmapped:
            print(f"\n⚠️  {len(unmapped)} answer sheet(s) NOT MAPPED:")
            for answer_file in unmapped:
                print(f"   • {answer_file}")

            mapping["unmapped_answers"] = unmapped

        print(f"\n📊 Summary:")
        print(f"   Question banks: {len(pdfs)}")
        print(f"   Answer sheets: {len(answer_files)}")
        print(f"   Mapped: {len(mapped_answers)}")
        print(f"   Unmapped: {len(unmapped)}")

        return True, mapping

    @staticmethod
    def auto_match(batch_dir: str) -> Tuple[bool, Dict]:
        """
        Automatically match answer sheets to question banks by filename.

        Returns:
            Tuple of (success, mapping_dict)
        """
        mapping = {
            "batch": batch_dir,
            "created": datetime.now().isoformat(),
            "question_banks": {},
            "unmapped_answers": [],
            "notes": [],
        }

        pdfs = QuestionBankMapper.detect_question_banks(batch_dir)
        answer_files = QuestionBankMapper.detect_answer_sheets(batch_dir)

        if not pdfs or not answer_files:
            mapping["notes"].append("No PDFs or answer files found")
            return False, mapping

        mapped_answers = set()

        for pdf_name in pdfs:
            suggestions = QuestionBankMapper.suggest_matching(pdf_name, answer_files)

            if suggestions:
                mapping["question_banks"][pdf_name] = {
                    "answer_sheets": suggestions,
                    "count": len(suggestions),
                    "mapped_by": "auto_match",
                }

                for answer in suggestions:
                    mapped_answers.add(answer)

        unmapped = [f for f in answer_files if f not in mapped_answers]
        if unmapped:
            mapping["unmapped_answers"] = unmapped

        return True, mapping

    @staticmethod
    def save_mapping(batch_dir: str, mapping: Dict) -> str:
        """
        Save mapping manifest to file.

        Returns:
            Path to manifest file
        """
        batch_path = Path(batch_dir)
        manifest_file = batch_path / "ANSWER_MAPPING_MANIFEST.json"

        with open(manifest_file, "w") as f:
            json.dump(mapping, f, indent=2)

        return str(manifest_file)

    @staticmethod
    def show_mapping(batch_dir: str):
        """Show existing mapping manifest"""
        batch_path = Path(batch_dir)
        manifest_file = batch_path / "ANSWER_MAPPING_MANIFEST.json"

        if not manifest_file.exists():
            print(f"✗ No mapping found: {manifest_file}")
            return

        with open(manifest_file) as f:
            mapping = json.load(f)

        print("\n" + "=" * 80)
        print("CURRENT ANSWER MAPPING")
        print("=" * 80)
        print(f"\nBatch: {mapping['batch']}")
        print(f"Created: {mapping['created']}")

        print("\n📋 QUESTION BANKS → ANSWER SHEETS:")
        print("-" * 80)

        if mapping["question_banks"]:
            for pdf_name, details in mapping["question_banks"].items():
                print(f"\n{pdf_name}")
                print(f"  Answer sheets ({details['count']}):")
                for answer in details["answer_sheets"]:
                    print(f"    • {answer}")
        else:
            print("(No mappings)")

        if mapping["unmapped_answers"]:
            print("\n⚠️  UNMAPPED ANSWER SHEETS:")
            for answer in mapping["unmapped_answers"]:
                print(f"  • {answer}")

        if mapping["notes"]:
            print("\n📝 NOTES:")
            for note in mapping["notes"]:
                print(f"  • {note}")

        print("\n" + "=" * 80 + "\n")


def print_help():
    """Print help message"""
    print(
        """
Interactive Question Bank Mapper

Map answer sheets to question bank PDFs step-by-step.
Prevents confusion when multiple question banks are present.

Usage:
  python3 map_questions_to_answers.py --batch <name>
  python3 map_questions_to_answers.py --batch <name> --auto-match
  python3 map_questions_to_answers.py --batch <name> --show-mapping
  python3 map_questions_to_answers.py --help

Options:
  --batch <name>        Batch directory (in answers/{name}/)
  --auto-match          Auto-match by filename (no prompts)
  --show-mapping        Show existing mapping
  --help                Show this help

Examples:
  # Interactive wizard (recommended)
  python3 map_questions_to_answers.py --batch july12

  # Auto-match by filename
  python3 map_questions_to_answers.py --batch july12 --auto-match

  # View saved mapping
  python3 map_questions_to_answers.py --batch july12 --show-mapping

Workflow:
  1. Place question bank PDFs in batch directory
  2. Place answer sheets (JSON/Excel) in batch directory
  3. Run this wizard to map them
  4. Saves mapping to ANSWER_MAPPING_MANIFEST.json
  5. Other tools use this mapping for validation

Output:
  ✓ Creates ANSWER_MAPPING_MANIFEST.json showing:
    - Which question bank PDF each answer sheet belongs to
    - Count of mapped vs unmapped answers
    - Mapping method (user interactive or auto)
    - Any notes about unmapped sheets
"""
    )


if __name__ == "__main__":
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    if "--batch" in sys.argv:
        batch_idx = sys.argv.index("--batch")
        batch_name = sys.argv[batch_idx + 1]
        batch_dir = f"answers/{batch_name}"

        if "--show-mapping" in sys.argv:
            QuestionBankMapper.show_mapping(batch_dir)

        elif "--auto-match" in sys.argv:
            print(f"Auto-matching answer sheets to question banks...")
            success, mapping = QuestionBankMapper.auto_match(batch_dir)

            if success:
                # Save mapping
                manifest_file = QuestionBankMapper.save_mapping(batch_dir, mapping)
                print(f"\n✓ Mapping saved to: {manifest_file}")
                QuestionBankMapper.show_mapping(batch_dir)
            else:
                print("✗ Auto-match failed")

        else:
            # Interactive wizard
            success, mapping = QuestionBankMapper.interactive_mapping(batch_dir)

            if success:
                print("\n\n💾 SAVING MAPPING")
                print("-" * 80)

                # Save mapping
                manifest_file = QuestionBankMapper.save_mapping(batch_dir, mapping)
                print(f"✓ Mapping saved to: {manifest_file}")

                # Show summary
                QuestionBankMapper.show_mapping(batch_dir)
            else:
                print("\n✗ Mapping wizard failed")

    else:
        print_help()
        sys.exit(1)
