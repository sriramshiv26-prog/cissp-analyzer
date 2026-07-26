"""
Metadata Reviewer - Display metadata in terminal and allow inline edits.

Allows users to review extracted/completed metadata before saving,
with support for editing individual question fields.
"""

from typing import Dict, List, Optional


class MetadataReviewer:
    """Display metadata to the user in the terminal and allow inline edits."""

    VALID_DIFFICULTIES = {"Easy", "Medium", "Hard", "Unknown"}
    VALID_QUESTION_TYPES = {"Knowledge", "Application", "Analysis", "Unknown"}

    def __init__(self, metadata: Dict[str, Dict]):
        """
        Initialize with metadata dict.

        Args:
            metadata: {q_num_str: {domain, topic, difficulty, ...}}
        """
        # Deep copy to avoid mutating the original
        self.metadata = {k: dict(v) for k, v in metadata.items()}
        self.edited: Dict[str, Dict[str, str]] = {}  # {q_num_str: {field: new_value}}

    def display_summary(self) -> str:
        """
        Print table: Q# | Domain | Difficulty | Topic — first 20 rows + totals.

        Returns:
            Formatted table string
        """
        lines = []
        lines.append("-" * 80)
        lines.append(f"{'Q#':<6} {'Domain':<30} {'Difficulty':<12} {'Topic':<28}")
        lines.append("-" * 80)

        # Sort by question number
        sorted_keys = sorted(self.metadata.keys(), key=lambda x: int(x) if x.isdigit() else 0)
        display_keys = sorted_keys[:20]

        for q_num_str in display_keys:
            meta = self.metadata[q_num_str]
            domain = str(meta.get("domain", "Unknown"))[:29]
            difficulty = str(meta.get("difficulty", "Unknown"))[:11]
            topic = str(meta.get("topic", "Unknown"))[:27]
            lines.append(f"{q_num_str:<6} {domain:<30} {difficulty:<12} {topic:<28}")

        lines.append("-" * 80)

        total = len(self.metadata)
        shown = len(display_keys)
        remaining = total - shown

        if remaining > 0:
            lines.append(f"  ... and {remaining} more questions (showing first 20 of {total})")

        # Totals
        domain_counts: Dict[str, int] = {}
        difficulty_counts: Dict[str, int] = {}
        for meta in self.metadata.values():
            d = str(meta.get("domain", "Unknown"))
            diff = str(meta.get("difficulty", "Unknown"))
            domain_counts[d] = domain_counts.get(d, 0) + 1
            difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

        lines.append(f"\nTotal questions: {total}")
        lines.append(f"Domains: {len(domain_counts)} unique")
        lines.append(f"Difficulty breakdown: {dict(sorted(difficulty_counts.items()))}")
        lines.append(f"Questions edited: {len(self.edited)}")

        return "\n".join(lines)

    def edit_question(self, q_num: int, field: str, value: str) -> None:
        """
        Update a single field for a question, track in self.edited.

        Args:
            q_num: Question number (int)
            field: Field to update (domain, topic, difficulty, etc.)
            value: New value for the field

        Raises:
            KeyError: If question number not found in metadata
            ValueError: If field or value is invalid
        """
        q_num_str = str(q_num)

        if q_num_str not in self.metadata:
            raise KeyError(f"Question {q_num} not found in metadata")

        if not field or not field.strip():
            raise ValueError("Field name cannot be empty")

        # Apply the edit
        self.metadata[q_num_str][field] = value

        # Track the edit
        if q_num_str not in self.edited:
            self.edited[q_num_str] = {}
        self.edited[q_num_str][field] = value

    def get_reviewed_metadata(self) -> Dict[str, Dict]:
        """
        Return metadata with edits applied.

        Returns:
            Dict of {q_num_str: metadata_dict} with all edits applied
        """
        return {k: dict(v) for k, v in self.metadata.items()}

    def get_edit_summary(self) -> str:
        """
        Return summary: N questions edited, which fields changed.

        Returns:
            Formatted summary string
        """
        if not self.edited:
            return "No edits made."

        n = len(self.edited)
        lines = [f"{n} question(s) edited:"]

        # Collect all changed fields
        all_fields: Dict[str, int] = {}
        for q_num_str, changes in sorted(self.edited.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0):
            field_list = ", ".join(f"{f}={v!r}" for f, v in changes.items())
            lines.append(f"  Q{q_num_str}: {field_list}")
            for field in changes:
                all_fields[field] = all_fields.get(field, 0) + 1

        lines.append(f"\nFields changed: {dict(sorted(all_fields.items()))}")
        return "\n".join(lines)
