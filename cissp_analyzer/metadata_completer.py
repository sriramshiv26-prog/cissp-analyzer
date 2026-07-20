"""
Metadata Completer - Handles filling metadata gaps using user choice.

Works WITHOUT Ollama. User chooses:
1. DEFAULT: All gaps get "Unmapped" labels (user edits later)
2. MANUAL: User provides CSV with metadata
3. [OPTIONAL] AI: Use Ollama if available (handled by separate OllamaAnalyzer)
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MetadataCompleter:
    """Coordinates filling gaps in extracted metadata based on user choice."""

    def __init__(self, extraction_results: Dict):
        """
        Initialize with PDF extraction results.

        Args:
            extraction_results: Dict from PDFMetadataExtractor.extract()
        """
        self.total_questions = extraction_results.get("total_questions", 0)
        self.extracted_count = extraction_results.get("extracted_count", 0)
        self.extraction_coverage = extraction_results.get("confidence", 0)
        self.gaps = extraction_results.get("gaps", [])
        self.extracted_metadata = extraction_results.get("extracted_metadata", {})
        self.extraction_note = extraction_results.get("extraction_note", "")
        self.additional_metadata = {}
        self.completion_method = None

    def get_fallback_options(self) -> List[str]:
        """Get available fallback options for completing gaps"""
        missing_count = len(self.gaps)
        coverage_pct = int(self.extraction_coverage * 100)

        options = [
            f"DEFAULT: Use generic labels ({missing_count} gaps) - I'll edit later",
            f"MANUAL: Upload CSV with metadata ({missing_count} missing)",
        ]

        return options

    def apply_defaults(self) -> None:
        """
        Apply default metadata to all gap questions.

        Works without any external dependencies.
        """
        default_meta = {
            "domain": "Unmapped",
            "topic": "Unmapped",
            "difficulty": "Unknown",
            "question_type": "Unknown",
            "exam_trick": "Unknown",
        }

        for q_num in self.gaps:
            self.additional_metadata[str(q_num)] = default_meta.copy()

        self.completion_method = "default"
        logger.info(f"Applied defaults to {len(self.gaps)} gap questions")

    def apply_manual(self, csv_data: Dict[str, Dict]) -> None:
        """
        Apply manually-provided metadata from CSV.

        Args:
            csv_data: Dict of {question_number_str: metadata_dict}
        """
        self.additional_metadata.update(csv_data)
        self.completion_method = "manual"
        logger.info(f"Applied {len(csv_data)} manual entries")

    def apply_ollama_results(self, ollama_metadata: Dict[str, Dict]) -> None:
        """
        Apply results from Ollama analysis (if Ollama available).

        Args:
            ollama_metadata: Dict from OllamaAnalyzer.analyze_batch()
        """
        self.additional_metadata.update(ollama_metadata)
        self.completion_method = "ai"
        logger.info(f"Applied {len(ollama_metadata)} Ollama-generated entries")

    def get_combined_metadata(self) -> Dict[str, Dict]:
        """
        Get combined metadata (extracted + completed).

        Returns:
            Dict of {question_number_str: metadata_dict} for all questions
        """
        combined = {}

        # Add extracted metadata
        combined.update(self.extracted_metadata)

        # Add completed metadata (overwrite if already extracted)
        combined.update(self.additional_metadata)

        return combined

    def get_summary(self) -> str:
        """Get summary of completion"""
        total_after = self.extracted_count + len(self.additional_metadata)
        coverage_after = total_after / self.total_questions if self.total_questions > 0 else 0

        return f"""
Metadata Completion Summary
├─ Initial coverage: {int(self.extraction_coverage*100)}% ({self.extracted_count}/{self.total_questions})
├─ Completion method: {self.completion_method.upper() if self.completion_method else 'PENDING'}
├─ Additional entries: {len(self.additional_metadata)}
└─ Final coverage: {int(coverage_after*100)}% ({total_after}/{self.total_questions})
"""
