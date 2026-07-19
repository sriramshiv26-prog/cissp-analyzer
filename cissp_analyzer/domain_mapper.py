import json
from pathlib import Path
from typing import Optional, Dict


class DomainMapper:
    """Loads question_domain_mapping.json or exam-specific metadata.

    Backward compatible: works with or without exam_id.
    Without exam_id: loads data/question_domain_mapping.json (original CISSP data)
    With exam_id: tries data/metadata/YYYY-MM-DD/exam_id/metadata.json, falls back to default
    """

    def __init__(self, mapping_file: str = "data/question_domain_mapping.json", exam_id: Optional[str] = None):
        """
        Initialize DomainMapper.

        Args:
            mapping_file: Path to default mapping JSON (fallback)
            exam_id: Optional exam identifier for questionnaire-specific metadata
        """
        self.mapping_file = Path(mapping_file)
        self.exam_id = exam_id
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> Dict:
        """Load mapping from exam-specific path or default"""
        # Try exam-specific path first if exam_id provided
        if self.exam_id:
            exam_mapping = self._try_load_exam_mapping()
            if exam_mapping is not None:
                return exam_mapping

        # Fall back to default mapping file
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")

        with open(self.mapping_file, "r") as f:
            return json.load(f)

    def _try_load_exam_mapping(self) -> Optional[Dict]:
        """Try to load exam-specific metadata from data/metadata/YYYY-MM-DD/exam_id/"""
        metadata_base = Path("data/metadata")

        if not metadata_base.exists():
            return None

        # Search most recent date folder containing exam_id
        for date_folder in sorted(metadata_base.iterdir(), reverse=True):
            if not date_folder.is_dir():
                continue

            exam_folder = date_folder / self.exam_id
            if exam_folder.exists():
                metadata_file = exam_folder / "metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, "r") as f:
                        return json.load(f)

        return None

    def get_question_metadata(self, question_number: int) -> Optional[Dict]:
        """Get metadata for a specific question by number"""
        key = str(question_number)
        return self.mapping.get(key)

    def get_all_questions(self) -> Dict:
        """Get all question mappings"""
        return self.mapping

    def get_questions_by_domain(self, domain: str) -> list:
        """Get all questions in a specific domain"""
        return [
            (int(qnum), meta)
            for qnum, meta in self.mapping.items()
            if meta.get("domain") == domain
        ]

    def get_questions_by_topic(self, topic: str) -> list:
        """Get all questions for a specific topic"""
        return [
            (int(qnum), meta)
            for qnum, meta in self.mapping.items()
            if meta.get("topic") == topic
        ]
