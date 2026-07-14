#!/usr/bin/env python3
"""
Questionnaire Management System

Handles upload, parsing, and metadata extraction for new questionnaires.
Creates reusable metadata files for different exams/tests.

Workflow:
1. Admin uploads new questionnaire (PDF, Excel, etc.)
2. System extracts questions and answer key
3. System creates metadata: domain, section, topic, trap categories
4. Metadata stored in questionnaires/ folder
5. Student answer sheets use metadata for analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class QuestionMetadata:
    """Metadata for a single question."""

    question_num: int
    domain: int
    section: str
    topic: str
    difficulty: str
    question_type: str
    trap_category: Optional[str] = None
    explanation: Optional[str] = None


@dataclass
class QuestionnaireConfig:
    """Configuration for a questionnaire."""

    name: str
    code: str  # e.g., "CISSP_2026_JULY"
    total_questions: int
    domains: List[str]  # e.g., ["Risk Management", "Asset Security", ...]
    created_date: str
    source: str  # e.g., "ISC2 Official", "Mock Test", etc.
    description: Optional[str] = None


class QuestionnaireManager:
    """Manages questionnaire configurations and metadata."""

    def __init__(self, questionnaires_dir="questionnaires"):
        self.questionnaires_dir = Path(questionnaires_dir)
        self.questionnaires_dir.mkdir(exist_ok=True)

    def create_questionnaire(
        self,
        name: str,
        code: str,
        answer_key: Dict[int, str],
        question_metadata: List[QuestionMetadata],
        domains: List[str],
        source: str = "Custom",
        description: Optional[str] = None,
    ) -> str:
        """
        Create and save a new questionnaire configuration.

        Args:
            name: Questionnaire name (e.g., "CISSP July 2026")
            code: Unique code (e.g., "CISSP_2026_JULY")
            answer_key: Dict of {question_num: correct_answer}
            question_metadata: List of QuestionMetadata objects
            domains: List of domain names
            source: Source of questionnaire
            description: Optional description

        Returns:
            Path to questionnaire directory
        """
        q_dir = self.questionnaires_dir / code
        q_dir.mkdir(exist_ok=True)

        # Save config
        config = QuestionnaireConfig(
            name=name,
            code=code,
            total_questions=len(answer_key),
            domains=domains,
            created_date=datetime.now().isoformat(),
            source=source,
            description=description,
        )

        config_path = q_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump(asdict(config), f, indent=2)

        # Save answer key
        answer_key_path = q_dir / "answer_key.json"
        with open(answer_key_path, "w") as f:
            json.dump(answer_key, f, indent=2)

        # Save question metadata
        metadata_path = q_dir / "question_metadata.json"
        metadata_dict = {
            q.question_num: asdict(q) for q in question_metadata
        }
        with open(metadata_path, "w") as f:
            json.dump(metadata_dict, f, indent=2)

        print(f"✅ Questionnaire created: {q_dir}")
        print(f"   - Config: {config_path}")
        print(f"   - Answer key: {answer_key_path}")
        print(f"   - Metadata: {metadata_path}")

        return str(q_dir)

    def get_questionnaire(self, code: str) -> Tuple[QuestionnaireConfig, Dict, List[QuestionMetadata]]:
        """
        Load a questionnaire configuration.

        Args:
            code: Questionnaire code

        Returns:
            Tuple of (config, answer_key, metadata)
        """
        q_dir = self.questionnaires_dir / code

        # Load config
        config_path = q_dir / "config.json"
        with open(config_path) as f:
            config_data = json.load(f)
            config = QuestionnaireConfig(**config_data)

        # Load answer key
        answer_key_path = q_dir / "answer_key.json"
        with open(answer_key_path) as f:
            answer_key = json.load(f)
            # Convert keys to integers
            answer_key = {int(k): v.upper() for k, v in answer_key.items()}

        # Load metadata
        metadata_path = q_dir / "question_metadata.json"
        with open(metadata_path) as f:
            metadata_data = json.load(f)
            metadata = [QuestionMetadata(**m) for m in metadata_data.values()]

        return config, answer_key, metadata

    def list_questionnaires(self) -> List[Dict]:
        """List all available questionnaires."""
        questionnaires = []
        for q_dir in self.questionnaires_dir.iterdir():
            if q_dir.is_dir() and (q_dir / "config.json").exists():
                with open(q_dir / "config.json") as f:
                    config = json.load(f)
                    questionnaires.append(config)
        return questionnaires

    def delete_questionnaire(self, code: str) -> bool:
        """Delete a questionnaire and its metadata."""
        q_dir = self.questionnaires_dir / code
        if q_dir.exists():
            import shutil

            shutil.rmtree(q_dir)
            print(f"✅ Questionnaire deleted: {code}")
            return True
        return False


def create_template_questionnaire():
    """
    Create a template showing how to structure a new questionnaire.
    """
    template = {
        "name": "CISSP July 2026",
        "code": "CISSP_2026_JULY",
        "answer_key": {
            "1": "B",
            "2": "C",
            "3": "A",
            # ... 159 more questions
        },
        "question_metadata": [
            {
                "question_num": 1,
                "domain": 1,
                "section": "Risk Management",
                "topic": "Business Continuity Planning",
                "difficulty": "Medium",
                "question_type": "Application",
                "trap_category": "ORDER",
                "explanation": "Asks about first step in BCP - students often skip to recovery",
            },
            # ... 160 more questions
        ],
        "domains": [
            "Security & Risk Management",
            "Asset Security",
            "Security Architecture & Engineering",
            "Communication & Network Security",
            "Identity & Access Management",
            "Security Assessment & Testing",
            "Security Operations",
            "Software Development Security",
        ],
        "source": "ISC2 Official",
        "description": "Official practice assessment from ISC2",
    }

    template_path = Path("questionnaires/TEMPLATE.json")
    template_path.parent.mkdir(exist_ok=True)
    with open(template_path, "w") as f:
        json.dump(template, f, indent=2)

    print(f"✅ Template created: {template_path}")
    return template_path


if __name__ == "__main__":
    manager = QuestionnaireManager()
    print("📋 Available questionnaires:")
    for q in manager.list_questionnaires():
        print(f"  - {q['name']} ({q['code']}): {q['total_questions']} questions")
