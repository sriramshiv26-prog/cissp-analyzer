"""
MetadataGenerator - Core orchestrator for the Metadata Auto-Generator pipeline.

Runs the full pipeline: Extract → Complete → Review → Store.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from cissp_analyzer.pdf_metadata_extractor import PDFMetadataExtractor
from cissp_analyzer.metadata_completer import MetadataCompleter
from cissp_analyzer.metadata_reviewer import MetadataReviewer
from cissp_analyzer.ollama_analyzer import OllamaAnalyzer

logger = logging.getLogger(__name__)


class MetadataGenerator:
    """Core orchestrator. Runs the full metadata pipeline: Extract → Complete → Review → Store."""

    def __init__(
        self,
        exam_id: str,
        pdf_path: str,
        output_dir: str = "data/metadata",
    ):
        """
        Initialize MetadataGenerator.

        Args:
            exam_id: Exam identifier (e.g., "cissp-2024-q1")
            pdf_path: Path to the exam PDF
            output_dir: Base directory for output metadata files
        """
        self.exam_id = exam_id
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.ollama = OllamaAnalyzer()  # auto-detects availability

    def run(self, completion_method: str = "auto") -> Dict:
        """
        Full pipeline: Extract → Complete → Review → Store.

        Args:
            completion_method: One of "auto" (use Ollama if available),
                               "manual" (prompt for CSV), or "defaults"

        Returns:
            {"exam_id", "total_questions", "coverage", "method", "output_path"}
        """
        logger.info(f"Starting MetadataGenerator pipeline for exam: {self.exam_id}")

        # Step 1: Extract
        logger.info("Step 1: Extracting metadata from PDF...")
        extractor = PDFMetadataExtractor(self.pdf_path)
        extraction_results = extractor.extract()

        # Step 2: Complete
        logger.info("Step 2: Completing metadata gaps...")
        completer = MetadataCompleter(extraction_results)

        method_used = completion_method

        if completion_method == "auto":
            if self.ollama.available:
                logger.info(f"Ollama available — using AI completion ({self.ollama.get_status()})")
                # Get question texts for gaps
                questions_for_ollama = self._get_questions_for_gaps(
                    extractor, completer.gaps
                )
                ollama_results = self.ollama.analyze_batch(questions_for_ollama)
                if ollama_results:
                    completer.apply_ollama_results(ollama_results)
                    method_used = "ai"
                else:
                    logger.warning("Ollama returned no results, falling back to defaults")
                    completer.apply_defaults()
                    method_used = "default"
            else:
                logger.info("Ollama not available — applying defaults")
                completer.apply_defaults()
                method_used = "default"

        elif completion_method == "manual":
            csv_path = input("Enter path to metadata CSV: ").strip()
            csv_data = self._load_csv_metadata(csv_path)
            completer.apply_manual(csv_data)
            method_used = "manual"

        else:
            # "defaults" or any other value
            completer.apply_defaults()
            method_used = "default"

        combined_metadata = completer.get_combined_metadata()

        # Step 3: Review
        logger.info("Step 3: Reviewing metadata...")
        reviewer = MetadataReviewer(combined_metadata)
        summary = reviewer.display_summary()
        logger.info(f"Metadata summary:\n{summary}")
        reviewed_metadata = reviewer.get_reviewed_metadata()

        # Step 4: Store
        logger.info("Step 4: Saving metadata...")
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = self._save_metadata(reviewed_metadata, date_str)

        total_questions = extraction_results.get("total_questions", 0)
        covered = len(reviewed_metadata)
        coverage = covered / total_questions if total_questions > 0 else 0.0

        result = {
            "exam_id": self.exam_id,
            "total_questions": total_questions,
            "coverage": coverage,
            "method": method_used,
            "output_path": str(output_path),
        }

        logger.info(
            f"Pipeline complete: {covered}/{total_questions} questions "
            f"({coverage:.0%} coverage) — saved to {output_path}"
        )
        return result

    def _get_questions_for_gaps(
        self, extractor: PDFMetadataExtractor, gaps: list
    ) -> Dict[int, str]:
        """
        Get question text for gap questions to send to Ollama.

        Args:
            extractor: PDFMetadataExtractor instance
            gaps: List of question numbers missing metadata

        Returns:
            {q_num: q_text} for each gap question
        """
        questions = {}
        for q in extractor.questions:
            q_num = q.get("number")
            if q_num in gaps:
                text = q.get("text", q.get("question_text", ""))
                if text:
                    questions[q_num] = text
        return questions

    def _load_csv_metadata(self, csv_path: str) -> Dict[str, Dict]:
        """
        Load metadata from a CSV file.

        Expected CSV format:
        question_number,domain,topic,difficulty,question_type

        Args:
            csv_path: Path to CSV file

        Returns:
            Dict {q_num_str: metadata_dict}
        """
        import csv

        data: Dict[str, Dict] = {}
        path = Path(csv_path)

        if not path.exists():
            logger.error(f"CSV not found: {csv_path}")
            return data

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    q_num = str(row.get("question_number", "")).strip()
                    if q_num:
                        data[q_num] = {
                            "domain": row.get("domain", "Unknown"),
                            "topic": row.get("topic", "Unknown"),
                            "difficulty": row.get("difficulty", "Unknown"),
                            "question_type": row.get("question_type", "Unknown"),
                        }
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")

        return data

    def _save_metadata(self, metadata: Dict, date_str: str) -> Path:
        """
        Save metadata.json to output_dir/date_str/exam_id/.

        Args:
            metadata: Metadata dict to save
            date_str: Date string (YYYY-MM-DD)

        Returns:
            Path to saved metadata.json file
        """
        output_path = self.output_dir / date_str / self.exam_id
        output_path.mkdir(parents=True, exist_ok=True)

        metadata_file = output_path / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Metadata saved to: {metadata_file}")
        return metadata_file
