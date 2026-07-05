import json
from pathlib import Path
from typing import Optional, Dict


class DomainMapper:
    """Loads and provides access to question_domain_mapping.json"""

    def __init__(self, mapping_file: str = "data/question_domain_mapping.json"):
        self.mapping_file = Path(mapping_file)
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> Dict:
        """Load the authoritative question mapping from JSON"""
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")

        with open(self.mapping_file, "r") as f:
            return json.load(f)

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
