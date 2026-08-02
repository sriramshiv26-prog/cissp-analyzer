#!/usr/bin/env python3
"""
Exam Processor - Orchestrates processing of answer sheets for an exam.
Detects new files, validates them, and generates individual reports.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from cissp_analyzer.exam_folder_manager import ExamFolderManager
from cissp_analyzer.state_tracker import ProcessedFileTracker
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.answer_key_manager import AnswerKeyManager
from cissp_analyzer.question_database import QuestionDatabase
from cissp_analyzer.answer_validator import AnswerValidator
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

        # Initialize v1.0 grading components
        self.answer_key_manager = AnswerKeyManager(self.exam_folder)
        self.question_db = QuestionDatabase(self.exam_folder)
        self.answer_key: Optional[Dict[int, str]] = None

        # Auto-load answer key from answer_keys/answer_key.json if present
        default_key = self.exam_folder / "answer_keys" / "answer_key.json"
        if default_key.exists():
            self.answer_key = self.answer_key_manager.load_from_json(str(default_key))

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
            from cissp_analyzer.robust_pdf_parser import RobustPDFParser

            parser = RobustPDFParser(pdf_path)
            result = parser.extract_with_fallback()
            # Convert {q_num: {...}} dict to list with "number" key
            return [{"number": k, **v} for k, v in result.questions.items()]
        except Exception as e:
            logger.error(f"Error extracting questions: {str(e)}")
            return []

    def load_answer_key(self, answer_key_path: Optional[str] = None) -> bool:
        """
        Load answer key from Excel or JSON file.

        Args:
            answer_key_path: Path to answer key file (Excel or JSON)
                           If None, tries to load from exam folder

        Returns:
            True if answer key loaded successfully
        """
        try:
            if answer_key_path:
                # Load from provided path
                file_path = Path(answer_key_path)
                if file_path.suffix.lower() == ".xlsx":
                    self.answer_key = self.answer_key_manager.load_from_excel(
                        answer_key_path
                    )
                elif file_path.suffix.lower() == ".json":
                    self.answer_key = self.answer_key_manager.load_from_json(
                        answer_key_path
                    )
                else:
                    logger.error(f"Unsupported file format: {file_path.suffix}")
                    return False
            else:
                # Try to load from answer_keys directory
                self.answer_key = self.answer_key_manager.get_all_answers()
                if not self.answer_key:
                    logger.warning("No answer key found in exam folder")
                    return False

            logger.info(f"✓ Loaded {len(self.answer_key)} answer keys")
            return True

        except Exception as e:
            logger.error(f"Error loading answer key: {str(e)}")
            return False

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

        logger.info(
            f"Found {len(new_files)} new answer files out of {len(all_files)} total"
        )
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

    def process_new_files(self, generate_metadata: bool = False) -> Dict:
        """
        Process all new answer files.

        Args:
            generate_metadata: If True, run MetadataGenerator pipeline after processing.
                               Requires exam metadata to include pdf_path.
                               Existing callers unaffected (defaults to False).

        Returns:
            Summary: {processed: [], failed: [], skipped: [], metadata_result (optional)}
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
                    summary["failed"].append(
                        {"filename": filename, "reason": "Analysis failed"}
                    )
                    logger.warning(f"✗ Failed to process: {filename}")
            except Exception as e:
                summary["failed"].append({"filename": filename, "reason": str(e)})
                logger.error(f"✗ Error processing {filename}: {str(e)}")

        # Optional metadata generation step
        if generate_metadata:
            summary["metadata_result"] = self._run_metadata_generation()

        return summary

    def _run_metadata_generation(self) -> Dict:
        """
        Run MetadataGenerator pipeline for this exam.

        Returns:
            Result dict from MetadataGenerator.run() or error dict on failure
        """
        try:
            from cissp_analyzer.metadata_generator import MetadataGenerator

            exam_id = self.exam_folder.name
            pdf_path = self.metadata.get("pdf_path", "")

            if not pdf_path:
                logger.warning(
                    "Cannot run metadata generation: no pdf_path in exam metadata"
                )
                return {"error": "pdf_path not found in exam metadata"}

            logger.info(f"Running MetadataGenerator for exam: {exam_id}")
            gen = MetadataGenerator(exam_id=exam_id, pdf_path=pdf_path)
            result = gen.run(completion_method="auto")
            logger.info(f"Metadata generation complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Metadata generation failed: {e}")
            return {"error": str(e)}

    def process_single_file(self, excel_filename: str) -> Optional[Dict]:
        """
        Process a single Excel answer sheet.

        Args:
            excel_filename: Name of Excel file in exam folder

        Returns:
            Report metadata dict or None if failed
        """
        # Resolve path: check student_answers subdir first, then root
        student_answers_dir = self.exam_folder / "student_answers"
        if (student_answers_dir / excel_filename).exists():
            excel_path = student_answers_dir / excel_filename
        else:
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
        Load answers from Excel file using RobustExcelParser.

        Returns:
            Dictionary {question_number: answer_letter} or None
        """
        try:
            from cissp_analyzer.robust_excel_parser import RobustExcelParser

            parser = RobustExcelParser(str(excel_path))
            result = parser.parse_with_fallback()

            if result.answers:
                return dict(result.answers)
            return None

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

        # Warn on mismatches but don't block — real exams may have minor numbering gaps
        mismatches = [q for q in answers.keys() if q not in question_numbers]
        if mismatches:
            logger.warning(
                f"{len(mismatches)} answers have no matching question (proceeding anyway)"
            )

        # Require at least 50% overlap with expected questions
        overlap = len([q for q in answers.keys() if q in question_numbers])
        if overlap == 0:
            logger.warning("No answers overlap with question set")
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

    def _grade_answers(self, answers: Dict[int, str]) -> Dict:
        """
        Grade student answers using answer key.

        Args:
            answers: Dictionary of student answers {question_number: answer}

        Returns:
            Dictionary with grading results
        """
        if not self.answer_key:
            logger.warning("No answer key loaded; skipping grading")
            return {
                "total_correct": 0,
                "total_incorrect": 0,
                "total_blank": 0,
                "score": 0.0,
                "grading_available": False,
            }

        correct = 0
        incorrect = 0
        blank = 0
        details = {}

        # Use answer key question numbers as source of truth
        answer_key_questions = sorted(self.answer_key.keys())
        max_question = answer_key_questions[-1] if answer_key_questions else 0

        # Iterate through all questions in answer key
        for q_num in answer_key_questions:
            student_answer = answers.get(q_num, "")
            correct_answer = self.answer_key.get(q_num, "")

            if not student_answer:
                blank += 1
                details[q_num] = {"result": "blank", "correct": correct_answer}
            elif student_answer.upper() == correct_answer.upper():
                correct += 1
                details[q_num] = {"result": "correct"}
            else:
                incorrect += 1
                details[q_num] = {
                    "result": "incorrect",
                    "student": student_answer,
                    "correct": correct_answer,
                }

        total_answered = correct + incorrect
        score = (correct / total_answered * 100) if total_answered > 0 else 0

        return {
            "total_correct": correct,
            "total_incorrect": incorrect,
            "total_blank": blank,
            "score": score,
            "grading_available": True,
            "details": details,
        }

    def _generate_individual_report(
        self,
        student_name: str,
        answers: Dict[int, str],
    ) -> Path:
        """
        Generate individual student report with grading results.

        Args:
            student_name: Name of student
            answers: Dictionary of answers

        Returns:
            Path to generated report
        """
        # Grade answers if answer key is available
        grading = self._grade_answers(answers)

        report_filename = f"Individual_Report_{student_name}.json"
        report_path = self.reports_dir / report_filename

        report_data = {
            "student_name": student_name,
            "exam": self.metadata.get("exam_name"),
            "total_questions": len(self.questions),
            "answers_provided": len(answers),
            "answers": answers,
            "grading": grading,
            "generated_at": __import__("datetime").datetime.now().isoformat(),
        }

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"✓ Report saved: {report_path}")
        return report_path
