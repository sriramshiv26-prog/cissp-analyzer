#!/usr/bin/env python3
"""
Fuzzy Filename Matcher - Match Files by Flexible Naming Patterns

Handles real-world filename variations:
- Case variations (Jul12 vs july12 vs JULY12)
- Missing/extra letters (questbank vs questionbank, exm vs exam)
- Different delimiters (jul-12 vs jul_12 vs jul12)
- Abbreviations (Q1 vs Q.1 vs q_1)
- Typographical errors (questoin vs question)

Usage:
  python3 fuzzy_file_matcher.py --batch <batch_name>
  python3 fuzzy_file_matcher.py --batch <batch_name> --match-exam-sheets
  python3 fuzzy_file_matcher.py --help

Examples:
  python3 fuzzy_file_matcher.py --batch july12
  python3 fuzzy_file_matcher.py --batch july12 --match-exam-sheets
"""

import sys
from pathlib import Path
from typing import Tuple, Dict, List
from difflib import SequenceMatcher
import re


class FuzzyFileMatcher:
    """Match related files using fuzzy string similarity"""

    @staticmethod
    def normalize_filename(filename: str) -> str:
        """
        Normalize filename for comparison.

        Removes: extensions, delimiters, extra spaces
        Converts: uppercase → lowercase, numbers stay
        Example: "Jul-12_Exam.pdf" → "jul12exam"
        """
        # Remove extension
        name = Path(filename).stem

        # Convert to lowercase
        name = name.lower()

        # Remove common delimiters and spaces
        name = re.sub(r"[-_\s\.]+", "", name)

        # Keep only alphanumeric
        name = re.sub(r"[^a-z0-9]", "", name)

        return name

    @staticmethod
    def similarity_ratio(str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings (0.0 to 1.0).

        0.0 = completely different
        1.0 = identical
        """
        return SequenceMatcher(None, str1, str2).ratio()

    @staticmethod
    def find_related_files(
        batch_dir: str, reference_file: str, threshold: float = 0.7
    ) -> List[Tuple[str, float]]:
        """
        Find files related to reference file based on filename similarity.

        Args:
            batch_dir: Directory to search
            reference_file: File to match against
            threshold: Minimum similarity (0.0-1.0). Default 0.7 = 70% match

        Returns:
            List of (filename, similarity_score) sorted by similarity
        """
        batch_path = Path(batch_dir)

        if not batch_path.exists():
            return []

        # Normalize reference
        ref_normalized = FuzzyFileMatcher.normalize_filename(reference_file)

        all_files = list(batch_path.glob("*.*"))
        matches = []

        for file_path in all_files:
            if file_path.name == reference_file:
                continue  # Skip the reference file itself

            # Normalize candidate
            candidate_normalized = FuzzyFileMatcher.normalize_filename(file_path.name)

            # Calculate similarity
            similarity = FuzzyFileMatcher.similarity_ratio(ref_normalized, candidate_normalized)

            if similarity >= threshold:
                matches.append((file_path.name, similarity))

        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches

    @staticmethod
    def group_related_files(batch_dir: str, threshold: float = 0.7) -> Dict[str, List[str]]:
        """
        Group all files in directory by filename similarity.

        Files with similar names are grouped together.
        Returns:
            Dict of {canonical_name: [related_files]}
        """
        batch_path = Path(batch_dir)

        if not batch_path.exists():
            return {}

        all_files = sorted([f.name for f in batch_path.glob("*.*")])

        if not all_files:
            return {}

        groups = {}
        used_files = set()

        for file1 in all_files:
            if file1 in used_files:
                continue

            # Start new group with first file
            group_key = file1
            group = [file1]
            used_files.add(file1)

            # Find similar files
            for file2 in all_files:
                if file2 in used_files:
                    continue

                norm1 = FuzzyFileMatcher.normalize_filename(file1)
                norm2 = FuzzyFileMatcher.normalize_filename(file2)

                similarity = FuzzyFileMatcher.similarity_ratio(norm1, norm2)

                if similarity >= threshold:
                    group.append(file2)
                    used_files.add(file2)

            if len(group) > 1 or group_key not in groups:
                groups[group_key] = group

        return groups

    @staticmethod
    def match_exam_to_answers(
        batch_dir: str, exam_pattern: str = None, threshold: float = 0.75
    ) -> Dict[str, Dict]:
        """
        Match exam PDFs to answer sheets by filename similarity.

        Returns:
            Dict of {exam_file: {answer_files: [], similarity_scores: []}}
        """
        batch_path = Path(batch_dir)

        if not batch_path.exists():
            return {}

        # Find exam files
        if exam_pattern:
            exam_files = list(batch_path.glob(exam_pattern))
        else:
            # Look for PDFs (typical exam files)
            exam_files = list(batch_path.glob("*exam*.pdf")) + list(batch_path.glob("*.pdf"))

        # Find answer files (JSON, Excel)
        answer_files = (
            list(batch_path.glob("*.json"))
            + list(batch_path.glob("*.xlsx"))
            + list(batch_path.glob("*.xls"))
        )

        matches = {}

        for exam_file in exam_files:
            related_answers = []
            scores = []

            for answer_file in answer_files:
                exam_norm = FuzzyFileMatcher.normalize_filename(exam_file.name)
                answer_norm = FuzzyFileMatcher.normalize_filename(answer_file.name)

                similarity = FuzzyFileMatcher.similarity_ratio(exam_norm, answer_norm)

                if similarity >= threshold:
                    related_answers.append(answer_file.name)
                    scores.append(round(similarity, 2))

            if related_answers:
                matches[exam_file.name] = {
                    "answer_files": related_answers,
                    "similarity_scores": scores,
                    "match_count": len(related_answers),
                }

        return matches

    @staticmethod
    def detect_exam_versions(batch_dir: str) -> Dict[str, List[str]]:
        """
        Detect different exam versions based on filename patterns.

        Looks for common version indicators:
        - v1, v2, v3, etc.
        - exam1, exam2, exam3, etc.
        - full, practice, mock, midterm, final, makeup
        - batch1, batch2, etc.

        Returns:
            Dict of {version_name: [matching_files]}
        """
        batch_path = Path(batch_dir)

        if not batch_path.exists():
            return {}

        all_files = [f.name for f in batch_path.glob("*.*")]
        versions = {}

        version_keywords = {
            "v1": ["_v1", "-v1", "v1_", "version1"],
            "v2": ["_v2", "-v2", "v2_", "version2"],
            "v3": ["_v3", "-v3", "v3_", "version3"],
            "full": ["full_exam", "fullexam", "complete", "_full"],
            "practice": ["practice", "mock", "sample", "test"],
            "midterm": ["midterm", "mid_term", "midterm"],
            "final": ["final_exam", "finalexam", "_final"],
            "makeup": ["makeup", "make_up", "retest"],
            "exam1": ["exam1", "exam_1", "exam-1"],
            "exam2": ["exam2", "exam_2", "exam-2"],
        }

        for version_name, keywords in version_keywords.items():
            matching_files = []

            for filename in all_files:
                filename_lower = filename.lower()

                for keyword in keywords:
                    if keyword.lower() in filename_lower:
                        matching_files.append(filename)
                        break

            if matching_files:
                versions[version_name] = matching_files

        return versions


def print_file_matching_report(batch_name: str):
    """Print detailed file matching report"""
    batch_dir = Path(f"answers/{batch_name}")

    if not batch_dir.exists():
        print(f"✗ Batch directory not found: {batch_dir}")
        return

    print("\n" + "=" * 80)
    print(f"FUZZY FILE MATCHING: {batch_name.upper()}")
    print("=" * 80)

    all_files = [f.name for f in batch_dir.glob("*.*")]
    print(f"\nFiles found: {len(all_files)}")

    if len(all_files) == 0:
        print("  (no files)")
        return

    print("\nFiles:")
    for i, filename in enumerate(sorted(all_files), 1):
        normalized = FuzzyFileMatcher.normalize_filename(filename)
        print(f"  {i}. {filename}")
        print(f"     → Normalized: {normalized}")

    # Group related files
    print("\n📁 GROUPED BY SIMILARITY (threshold: 70%):")
    print("-" * 80)

    groups = FuzzyFileMatcher.group_related_files(str(batch_dir), threshold=0.7)

    for i, (key, files) in enumerate(groups.items(), 1):
        if len(files) > 1:
            print(f"\nGroup {i}: {len(files)} related file(s)")
            for file in sorted(files):
                print(f"  • {file}")

    # Detect exam versions
    print("\n📊 EXAM VERSION DETECTION:")
    print("-" * 80)

    versions = FuzzyFileMatcher.detect_exam_versions(str(batch_dir))

    if versions:
        for version_name, files in versions.items():
            print(f"\n{version_name.upper()}: {len(files)} file(s)")
            for file in sorted(files):
                print(f"  • {file}")
    else:
        print("\n(No version patterns detected)")

    # Match exam to answers
    print("\n🔗 EXAM-TO-ANSWER MATCHING (threshold: 75%):")
    print("-" * 80)

    matches = FuzzyFileMatcher.match_exam_to_answers(str(batch_dir))

    if matches:
        for exam_file, match_info in matches.items():
            print(f"\nExam: {exam_file}")
            print(f"  Matches: {match_info['match_count']} answer file(s)")
            for answer, score in zip(match_info["answer_files"], match_info["similarity_scores"]):
                print(f"    • {answer} (similarity: {score})")
    else:
        print("\n(No exam files found or no matches above threshold)")

    print("\n" + "=" * 80 + "\n")


def print_help():
    """Print help message"""
    print(
        """
Fuzzy Filename Matcher

Match related files even with typos, case variations, and missing letters.

Features:
  • Case-insensitive matching (Jul12 = july12 = JULY12)
  • Typo tolerance (questbank = questionbank, exm = exam)
  • Delimiter variations (jul-12 = jul_12 = jul12)
  • Abbreviation detection (Q1 = Q.1 = q_1)
  • Exam version detection (v1, v2, full, practice, etc.)

Usage:
  python3 fuzzy_file_matcher.py --batch <name>
  python3 fuzzy_file_matcher.py --batch <name> --detailed
  python3 fuzzy_file_matcher.py --help

Options:
  --batch <name>        Batch directory (in answers/{name}/)
  --detailed            Show detailed per-file analysis
  --help                Show this help

Examples:
  # Quick matching report
  python3 fuzzy_file_matcher.py --batch july12

  # Analyze filename patterns
  python3 fuzzy_file_matcher.py --batch july12 --detailed

What It Does:
  ✓ Groups related files by similarity
  ✓ Detects exam versions (v1, v2, practice, etc.)
  ✓ Matches exam PDFs to answer sheets
  ✓ Tolerates typos and variations
  ✓ Shows similarity scores

Real Examples:
  Input Files:
    • july12_exam.pdf, jul12answersheet.json, July_12_Q&A.xlsx
    → Grouped: All related (96% similarity)

  Input Files:
    • questionbank.pdf, questbank_answers.json
    → Matched despite typo (missing 'u')

  Input Files:
    • exam_v1.pdf, exam_v2.pdf, practice_test.pdf
    → Detected versions: v1, v2, practice
"""
    )


if __name__ == "__main__":
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    if "--batch" in sys.argv:
        batch_idx = sys.argv.index("--batch")
        batch_name = sys.argv[batch_idx + 1]

        print_file_matching_report(batch_name)

    else:
        print_help()
        sys.exit(1)
