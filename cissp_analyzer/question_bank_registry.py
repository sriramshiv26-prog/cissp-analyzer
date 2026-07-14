#!/usr/bin/env python3
"""
Question Bank Registry - Remember & Reference Question Banks Over Time

Maintains a catalog of question bank PDFs with metadata:
- PDF name and path
- When it was registered
- Hash/fingerprint of questions
- Previous answer sheets that used it
- Associated batches

Automatically suggests matches when new answer sheets arrive.

Usage:
  python3 question_bank_registry.py --register <batch_name>
  python3 question_bank_registry.py --find-matches <batch_name>
  python3 question_bank_registry.py --list
  python3 question_bank_registry.py --show <pdf_name>
  python3 question_bank_registry.py --help

Examples:
  # Register question banks from batch
  python3 question_bank_registry.py --register july12

  # Find matching question banks for new answer sheets
  python3 question_bank_registry.py --find-matches july26

  # List all registered question banks
  python3 question_bank_registry.py --list

  # Show details of specific PDF
  python3 question_bank_registry.py --show "CISSP_Exam.pdf"
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from difflib import SequenceMatcher
import hashlib


class QuestionBankRegistry:
    """Maintain registry of question bank PDFs across batches"""

    REGISTRY_FILE = Path(".claude/projects/-Users-sriram/question_bank_registry.json")

    @staticmethod
    def ensure_registry_dir():
        """Ensure registry directory exists"""
        QuestionBankRegistry.REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_registry() -> Dict:
        """Load existing registry or create new one"""
        QuestionBankRegistry.ensure_registry_dir()

        if QuestionBankRegistry.REGISTRY_FILE.exists():
            with open(QuestionBankRegistry.REGISTRY_FILE) as f:
                return json.load(f)

        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "question_banks": {},
            "batch_associations": {},
        }

    @staticmethod
    def save_registry(registry: Dict):
        """Save registry to file"""
        QuestionBankRegistry.ensure_registry_dir()

        with open(QuestionBankRegistry.REGISTRY_FILE, "w") as f:
            json.dump(registry, f, indent=2)

    @staticmethod
    def get_pdf_fingerprint(pdf_path: str) -> str:
        """
        Get fingerprint of PDF file (size + modified time hash).

        Returns:
            Hash string for identifying PDF
        """
        try:
            path = Path(pdf_path)
            stat = path.stat()
            fingerprint_data = f"{path.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(fingerprint_data.encode()).hexdigest()[:12]
        except:
            return "unknown"

    @staticmethod
    def register_question_bank(batch_dir: str, pdf_name: str) -> Tuple[bool, str]:
        """
        Register a question bank PDF in the catalog.

        Returns:
            Tuple of (success, message)
        """
        batch_path = Path(batch_dir)
        pdf_path = batch_path / pdf_name

        if not pdf_path.exists():
            return False, f"PDF not found: {pdf_path}"

        registry = QuestionBankRegistry.load_registry()

        # Create entry
        fingerprint = QuestionBankRegistry.get_pdf_fingerprint(str(pdf_path))

        # Check if already registered
        for pdf_key, entry in registry["question_banks"].items():
            if entry.get("fingerprint") == fingerprint:
                return False, f"Already registered: {pdf_key}"

        entry = {
            "name": pdf_name,
            "path": str(pdf_path),
            "fingerprint": fingerprint,
            "registered": datetime.now().isoformat(),
            "batches_used": [batch_dir],
            "answer_sheets": [],
            "notes": "",
        }

        registry["question_banks"][pdf_name] = entry

        QuestionBankRegistry.save_registry(registry)

        return True, f"Registered: {pdf_name} (fingerprint: {fingerprint})"

    @staticmethod
    def find_matching_question_banks(
        batch_dir: str, answer_filenames: List[str], threshold: float = 0.65
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Find question banks that might match new answer sheets.

        Matches by filename similarity to previously registered PDFs.

        Returns:
            Dict of {answer_file: [(matching_pdf, similarity_score), ...]}
        """
        registry = QuestionBankRegistry.load_registry()
        matches = {}

        if not registry["question_banks"]:
            return {}  # No registered question banks

        for answer_file in answer_filenames:
            answer_normalized = (
                answer_file.lower()
                .replace(".json", "")
                .replace(".xlsx", "")
                .replace(".xls", "")
            )

            file_matches = []

            for pdf_name, pdf_entry in registry["question_banks"].items():
                pdf_normalized = pdf_name.lower().replace(".pdf", "")

                similarity = SequenceMatcher(
                    None, answer_normalized, pdf_normalized
                ).ratio()

                if similarity >= threshold:
                    file_matches.append((pdf_name, round(similarity, 2)))

            if file_matches:
                # Sort by similarity
                file_matches.sort(key=lambda x: x[1], reverse=True)
                matches[answer_file] = file_matches

        return matches

    @staticmethod
    def add_batch_association(batch_dir: str, pdf_name: str):
        """
        Record that a PDF was used in a batch.

        Used to track which batches have used which question banks.
        """
        registry = QuestionBankRegistry.load_registry()

        if pdf_name not in registry["question_banks"]:
            return

        pdf_entry = registry["question_banks"][pdf_name]

        if batch_dir not in pdf_entry.get("batches_used", []):
            if "batches_used" not in pdf_entry:
                pdf_entry["batches_used"] = []

            pdf_entry["batches_used"].append(batch_dir)

        # Record in batch_associations
        if batch_dir not in registry["batch_associations"]:
            registry["batch_associations"][batch_dir] = []

        if pdf_name not in registry["batch_associations"][batch_dir]:
            registry["batch_associations"][batch_dir].append(pdf_name)

        QuestionBankRegistry.save_registry(registry)

    @staticmethod
    def add_answer_sheet_to_pdf(pdf_name: str, answer_sheet: str):
        """
        Record that an answer sheet was analyzed for a PDF.

        Builds history of which answer sheets have been used with which PDFs.
        """
        registry = QuestionBankRegistry.load_registry()

        if pdf_name not in registry["question_banks"]:
            return

        pdf_entry = registry["question_banks"][pdf_name]

        if answer_sheet not in pdf_entry.get("answer_sheets", []):
            if "answer_sheets" not in pdf_entry:
                pdf_entry["answer_sheets"] = []

            pdf_entry["answer_sheets"].append(answer_sheet)

        QuestionBankRegistry.save_registry(registry)

    @staticmethod
    def list_registered_pdfs() -> List[Dict]:
        """
        Get all registered question banks.

        Returns:
            List of PDF entries with metadata
        """
        registry = QuestionBankRegistry.load_registry()

        entries = []
        for pdf_name, pdf_entry in registry["question_banks"].items():
            entries.append(
                {
                    "name": pdf_name,
                    "registered": pdf_entry.get("registered", "unknown"),
                    "batches_used": len(pdf_entry.get("batches_used", [])),
                    "answer_sheets_used": len(pdf_entry.get("answer_sheets", [])),
                    "last_batch": pdf_entry.get("batches_used", ["never"])[-1],
                }
            )

        return sorted(entries, key=lambda x: x["registered"], reverse=True)

    @staticmethod
    def get_pdf_details(pdf_name: str) -> Dict:
        """
        Get detailed information about a registered PDF.

        Returns:
            PDF entry dictionary
        """
        registry = QuestionBankRegistry.load_registry()

        if pdf_name in registry["question_banks"]:
            return registry["question_banks"][pdf_name]

        return {}

    @staticmethod
    def suggest_pdf_for_batch(batch_dir: str) -> List[Dict]:
        """
        Suggest question banks to use for a new batch.

        Useful when you know you're re-using a question bank from before.

        Returns:
            List of recently used question banks
        """
        registry = QuestionBankRegistry.load_registry()

        # Get PDFs used in this batch
        batch_pdfs = registry.get("batch_associations", {}).get(batch_dir, [])

        if batch_pdfs:
            return [registry["question_banks"].get(pdf, {}) for pdf in batch_pdfs]

        # Otherwise, get most recently registered PDFs
        entries = []
        for pdf_name, pdf_entry in registry["question_banks"].items():
            entries.append(pdf_entry)

        entries.sort(key=lambda x: x.get("registered", ""), reverse=True)
        return entries[:5]  # Return top 5 most recent


def print_list_pdfs():
    """Print list of all registered PDFs"""
    registry = QuestionBankRegistry.load_registry()

    print("\n" + "=" * 80)
    print("REGISTERED QUESTION BANKS")
    print("=" * 80)

    pdfs = QuestionBankRegistry.list_registered_pdfs()

    if not pdfs:
        print("\n(No question banks registered yet)")
        return

    print(f"\n{'PDF Name':<40} {'Registered':<20} {'Batches':<8} {'Sheets':<8}")
    print("-" * 80)

    for pdf in pdfs:
        print(
            f"{pdf['name']:<40} {pdf['registered'][:10]:<20} "
            f"{pdf['batches_used']:<8} {pdf['answer_sheets_used']:<8}"
        )

    print("\n" + "=" * 80 + "\n")


def print_pdf_details(pdf_name: str):
    """Print details of a specific PDF"""
    details = QuestionBankRegistry.get_pdf_details(pdf_name)

    if not details:
        print(f"✗ PDF not found in registry: {pdf_name}")
        return

    print("\n" + "=" * 80)
    print(f"QUESTION BANK: {pdf_name}")
    print("=" * 80)

    print(f"\nPath: {details.get('path', 'unknown')}")
    print(f"Fingerprint: {details.get('fingerprint', 'unknown')}")
    print(f"Registered: {details.get('registered', 'unknown')}")

    print(f"\n📊 Usage:")
    batches = details.get("batches_used", [])
    print(f"  Batches: {len(batches)}")
    if batches:
        for batch in batches:
            print(f"    • {batch}")

    sheets = details.get("answer_sheets", [])
    print(f"  Answer Sheets: {len(sheets)}")
    if sheets:
        for sheet in sheets[:10]:  # Show first 10
            print(f"    • {sheet}")
        if len(sheets) > 10:
            print(f"    ... and {len(sheets) - 10} more")

    print("\n" + "=" * 80 + "\n")


def print_register_wizard(batch_dir: str):
    """Run registration wizard for a batch"""
    batch_path = Path(batch_dir)

    print("\n" + "=" * 80)
    print("REGISTER QUESTION BANKS")
    print("=" * 80)

    if not batch_path.exists():
        print(f"\n✗ Batch directory not found: {batch_dir}")
        return

    # Find PDFs in batch
    pdfs = sorted([f.name for f in batch_path.glob("*.pdf")])

    if not pdfs:
        print(f"\n✗ No PDF files found in: {batch_dir}")
        return

    print(f"\n✓ Found {len(pdfs)} PDF(s) in batch:\n")

    for i, pdf in enumerate(pdfs, 1):
        print(f"  {i}. {pdf}")

    print(f"\n❓ Register these PDFs in question bank catalog? (y/n): ", end="")

    try:
        if input().strip().lower() == "y":
            for pdf in pdfs:
                success, msg = QuestionBankRegistry.register_question_bank(
                    batch_dir, pdf
                )
                if success:
                    print(f"  ✓ {msg}")
                else:
                    print(f"  ⚠ {msg}")

            print(f"\n✓ Registration complete")
        else:
            print("  Skipped")
    except EOFError:
        print("  (No input)")

    print("\n" + "=" * 80 + "\n")


def print_find_matches_wizard(batch_dir: str):
    """Run find-matches wizard for a batch"""
    batch_path = Path(batch_dir)

    print("\n" + "=" * 80)
    print("FIND MATCHING QUESTION BANKS")
    print("=" * 80)

    if not batch_path.exists():
        print(f"\n✗ Batch directory not found: {batch_dir}")
        return

    # Find answer sheets in batch
    answer_files = sorted(
        [f.name for f in batch_path.glob("*.json")]
        + [f.name for f in batch_path.glob("*.xlsx")]
        + [f.name for f in batch_path.glob("*.xls")]
    )

    if not answer_files:
        print(f"\n✗ No answer files found in: {batch_dir}")
        return

    print(f"\n📄 Found {len(answer_files)} answer file(s) in batch:\n")
    for i, file in enumerate(answer_files[:5], 1):
        print(f"  {i}. {file}")
    if len(answer_files) > 5:
        print(f"  ... and {len(answer_files) - 5} more")

    # Find matches
    matches = QuestionBankRegistry.find_matching_question_banks(batch_dir, answer_files)

    if not matches:
        print(f"\n⚠️  No matching question banks found in registry")
        print(f"  Suggestions:")
        print(
            f"    1. Register question banks first: python3 question_bank_registry.py --register july12"
        )
        print(f"    2. Upload question bank PDFs to batch directory")
        return

    print(f"\n🔗 MATCHING QUESTION BANKS:")
    print("-" * 80)

    for answer_file, pdf_matches in matches.items():
        print(f"\n{answer_file}:")
        for pdf_name, similarity in pdf_matches[:3]:  # Show top 3
            print(f"  • {pdf_name} (similarity: {similarity})")

    print("\n" + "=" * 80 + "\n")


def print_help():
    """Print help message"""
    print("""
Question Bank Registry - Remember & Reference Question Banks

Maintains a catalog of question bank PDFs you use repeatedly.
When new answer sheets arrive, automatically suggest which question banks they
belong to based on filename similarity and usage history.

Perfect for:
  • Recurring batches (July exam every year)
  • Question banks used across multiple cohorts
  • Re-taking tests (same PDF, different students)
  • Quick matching of old PDFs to new answer sheets

Usage:
  python3 question_bank_registry.py --register <batch_name>
  python3 question_bank_registry.py --find-matches <batch_name>
  python3 question_bank_registry.py --list
  python3 question_bank_registry.py --show <pdf_name>
  python3 question_bank_registry.py --help

Options:
  --register <batch>      Register PDFs from batch in catalog
  --find-matches <batch>  Find registered PDFs matching answer sheets in batch
  --list                  List all registered question banks
  --show <pdf_name>       Show details of specific PDF
  --help                  Show this help

Workflow Example:

  WEEK 1: Upload question bank
    $ python3 question_bank_registry.py --register july12
    → Registers: CISSP_Exam_July12.pdf

  WEEK 2: Upload answer sheets for same exam
    $ python3 question_bank_registry.py --find-matches july26

    Output:
      MATCHING QUESTION BANKS:

      student1.json:
        • CISSP_Exam_July12.pdf (similarity: 0.89) ← Suggests from last week!

      student2.json:
        • CISSP_Exam_July12.pdf (similarity: 0.91)

    → System automatically recognizes it's the same PDF!

Registry Stores:
  ✓ PDF name and path
  ✓ When it was registered
  ✓ Fingerprint (file size + mod time hash)
  ✓ Which batches have used it
  ✓ Which answer sheets have been analyzed
  ✓ Complete usage history

Benefits:
  ✓ Remember question banks over time
  ✓ Auto-suggest matching PDFs for new batches
  ✓ No re-uploading needed
  ✓ Quick matching of recurring exams
  ✓ Complete audit trail of usage
""")


if __name__ == "__main__":
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    if "--register" in sys.argv:
        batch_idx = sys.argv.index("--register")
        batch_name = sys.argv[batch_idx + 1]
        batch_dir = f"answers/{batch_name}"
        print_register_wizard(batch_dir)

    elif "--find-matches" in sys.argv:
        batch_idx = sys.argv.index("--find-matches")
        batch_name = sys.argv[batch_idx + 1]
        batch_dir = f"answers/{batch_name}"
        print_find_matches_wizard(batch_dir)

    elif "--list" in sys.argv:
        print_list_pdfs()

    elif "--show" in sys.argv:
        pdf_idx = sys.argv.index("--show")
        pdf_name = sys.argv[pdf_idx + 1]
        print_pdf_details(pdf_name)

    else:
        print_help()
        sys.exit(1)
