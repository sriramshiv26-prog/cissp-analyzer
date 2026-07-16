#!/usr/bin/env python3
"""
Exam Processor - Orchestrates processing of answer sheets for an exam.
Detects new files, validates them, and generates individual reports.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cissp_analyzer.exam_folder_manager import ExamFolderManager
from cissp_analyzer.state_tracker import ProcessedFileTracker
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.models import StudentAnswer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExamProcessor:
    """Processes answer sheets and generates individual reports."""

    def __init__(self, exam_folder: Path):
        """
        Initialize ExamProcessor for an exam folder.

        Args:
            exam_folder: Path to exam folder created by ExamFolderManager

        Raises:
            FileNotFoundError: If exam folder or metadata not found
        """
        self.exam_folder = Path(exam_folder)
        self.exam_manager = ExamFolderManager(str(self.exam_folder.parent))
        self.state_tracker = ProcessedFileTracker(self.exam_folder)

        # Load exam metadata
        exam_id = self.exam_folder.name
        try:
            self.metadata = self.exam_manager.get_exam_metadata(exam_id)
        except FileNotFoundError:
            raise FileNotFoundError(f"Exam metadata not found for: {exam_id}")

        # Load extracted questions
        self.questions = self._load_questions()

        # Create reports directory if not exists
        self.reports_dir = self.exam_folder / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def _load_questions(self) -> List[Dict]:
        """
        Load questions from PDF.

        Returns:
            List of question dictionaries
        """
        pdf_path = self.metadata.get("pdf_path")
        if not pdf_path or not Path(pdf_path).exists():
            logger.warning(f"PDF not found: {pdf_path}")
            return []

        try:
            parser = PDFParser(pdf_path)
            return parser.extract_questions()
        except Exception as e:
            logger.error(f"Error extracting questions: {str(e)}")
            return []

    def detect_new_answer_files(self) -> List[str]:
        """
        Detect new answer files that haven't been processed.

        Returns:
            List of new Excel filenames
        """
        # Get all Excel files
        all_files = self.exam_manager.get_new_answer_files(self.exam_folder.name)

        # Filter to only unprocessed
        new_files = self.state_tracker.get_unprocessed_files(all_files)

        logger.info(f"Found {len(new_files)} new answer files out of {len(all_files)} total")
        return new_files

    def skip_already_processed(self) -> List[str]:
        """
        Get list of already processed files.

        Returns:
            List of processed filenames
        """
        history = self.state_tracker.get_processing_history()
        processed = [record["filename"] for record in history]

        if processed:
            logger.info(f"Skipping {len(processed)} already processed files")
            for filename in processed:
                logger.debug(f"  - {filename}")

        return processed

    def process_new_files(self) -> Dict:
        """
        Process all new answer files.

        Returns:
            Summary: {processed: [], failed: [], skipped: []}
        """
        new_files = self.detect_new_answer_files()

        summary: Dict = {
            "processed": [],
            "failed": [],
            "skipped": self.skip_already_processed(),
        }

        for filename in new_files:
            try:
                result = self.process_single_file(filename)
                if result:
                    summary["processed"].append(result)
                    logger.info(f"✓ Processed: {filename}")
                else:
                    summary["failed"].append({"filename": filename, "reason": "Analysis failed"})
                    logger.warning(f"✗ Failed to process: {filename}")
            except Exception as e:
                summary["failed"].append({"filename": filename, "reason": str(e)})
                logger.error(f"✗ Error processing {filename}: {str(e)}")

        return summary

    def process_single_file(self, excel_filename: str) -> Optional[Dict]:
        """
        Process a single Excel answer sheet.

        Args:
            excel_filename: Name of Excel file in exam folder

        Returns:
            Report metadata dict or None if failed
        """
        excel_path = self.exam_folder / excel_filename

        # Validate Excel file
        if not self._validate_excel_file(excel_path):
            return None

        try:
            # Extract student name from filename
            student_name = self._extract_student_name(excel_filename)

            # Load answers from Excel
            answers = self._load_answers_from_excel(excel_path)
            if not answers:
                logger.warning(f"No answers found in {excel_filename}")
                return None

            # Validate answers match questions
            if not self.validate_answers_match_questions(answers, self.questions):
                logger.warning(f"Answer validation failed for {student_name}")
                return None

            # Generate individual report
            report_path = self._generate_individual_report(student_name, answers)

            # Mark as processed
            self.state_tracker.mark_processed(
                filename=excel_filename,
                report_path=str(report_path),
            )

            return {
                "student_name": student_name,
                "filename": excel_filename,
                "report_path": str(report_path),
            }

        except Exception as e:
            logger.error(f"Error processing {excel_filename}: {str(e)}")
            return None

    def _validate_excel_file(self, excel_path: Path) -> bool:
        """Validate Excel file exists and is readable."""
        if not excel_path.exists():
            logger.error(f"File not found: {excel_path}")
            return False

        if excel_path.suffix.lower() != ".xlsx":
            logger.error(f"Not an Excel file: {excel_path}")
            return False

        return True

    def _extract_student_name(self, filename: str) -> str:
        """
        Extract student name from filename.

        Handles formats like:
        - Student_Alice.xlsx → Alice
        - Alice_answers.xlsx → Alice
        - Alice.xlsx → Alice

        Args:
            filename: Excel filename

        Returns:
            Student name
        """
        # Remove extension
        name = Path(filename).stem

        # Remove common prefixes/suffixes
        for pattern in ["student_", "answers_", "_answers", "_response"]:
            name = name.replace(pattern, "")

        return name.strip() or filename

    def _load_answers_from_excel(self, excel_path: Path) -> Optional[Dict[int, str]]:
        """
        Load answers from Excel file.

        Args:
            excel_path: Path to Excel file

        Returns:
            Dictionary {question_number: answer_letter} or None
        """
        try:
            import pandas as pd

            df = pd.read_excel(excel_path)

            # Normalize column names
            df.columns = [col.strip().lower() for col in df.columns]

            answers = {}
            for _, row in df.iterrows():
                # Look for question number column
                q_num = None
                for col in ["question", "q", "question number", "question_number"]:
                    if col in df.columns:
                        q_num = row.get(col)
                        break

                # Look for answer column
                answer = None
                for col in ["answer", "ans", "student answer", "student_answer"]:
                    if col in df.columns:
                        answer = row.get(col)
                        break

                if q_num is not None and answer is not None:
                    try:
                        q_num = int(q_num)
                        normalized = ExcelParser.normalize_answer(str(answer))
                        if normalized:
                            answers[q_num] = normalized
                    except (ValueError, TypeError):
                        continue

            return answers if answers else None

        except Exception as e:
            logger.error(f"Error loading answers from {excel_path}: {str(e)}")
            return None

    def validate_answers_match_questions(
        self,
        answers: Dict[int, str],
        questions: List[Dict],
    ) -> bool:
        """
        Validate answers match available questions.

        Args:
            answers: Dictionary {question_number: answer}
            questions: List of question dictionaries

        Returns:
            True if valid, False otherwise
        """
        if not questions:
            logger.warning("No questions available for validation")
            return False

        if not answers:
            logger.warning("No answers to validate")
            return False

        # Get question numbers from questions
        question_numbers = {q.get("number", i) for i, q in enumerate(questions)}

        # Check all answer question IDs exist in questions
        for q_num in answers.keys():
            if q_num not in question_numbers:
                logger.warning(f"Answer for non-existent question: {q_num}")
                return False

        # Validate answer formats (A-D, or multi-part)
        for q_num, answer in answers.items():
            if not self._is_valid_answer_format(answer):
                logger.warning(f"Invalid answer format for Q{q_num}: {answer}")
                return False

        return True

    def _is_valid_answer_format(self, answer: str) -> bool:
        """
        Check if answer is in valid format.

        Valid formats:
        - Single letter: A, B, C, D
        - Multi-part: 1-A,2-B,3-C

        Args:
            answer: Answer string

        Returns:
            True if valid format
        """
        import re

        if not answer:
            return False

        answer = str(answer).upper().strip()

        # Single letter
        if len(answer) == 1 and answer in "ABCD":
            return True

        # Multi-part format: 1-A,2-B,3-C
        if re.match(r"^\d+-[A-D](,\d+-[A-D])*$", answer):
            return True

        return False

    def _generate_individual_report(
        self,
        student_name: str,
        answers: Dict[int, str],
    ) -> Path:
        """
        Generate individual student report.

        Args:
            student_name: Name of student
            answers: Dictionary of answers

        Returns:
            Path to generated report
        """
        # For now, create a simple JSON report
        # This can be extended to generate Excel/PDF reports

        report_filename = f"Individual_Report_{student_name}.json"
        report_path = self.reports_dir / report_filename

        report_data = {
            "student_name": student_name,
            "exam": self.metadata.get("exam_name"),
            "total_questions": len(self.questions),
            "answers_provided": len(answers),
            "answers": answers,
            "generated_at": str(Path.cwd()),
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"Report saved: {report_path}")
        return report_path
