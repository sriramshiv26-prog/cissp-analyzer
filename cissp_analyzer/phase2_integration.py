#!/usr/bin/env python3
"""
Phase 2 Integration Module - Orchestrates complete grading pipeline.
Connects Phase 2 components with v1.0 grading system.

Data Flow:
1. PDF Upload → Extract questions → Save to QuestionDatabase
2. Load answer key → Validate against questions
3. Process student Excel → Validate → Grade → Generate reports
4. Aggregate class data → Generate class report with metrics
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from cissp_analyzer.exam_folder_manager import ExamFolderManager
from cissp_analyzer.exam_processor import ExamProcessor
from cissp_analyzer.answer_key_manager import AnswerKeyManager
from cissp_analyzer.question_database import QuestionDatabase
from cissp_analyzer.class_report_aggregator import ClassReportAggregator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase2Integration:
    """Orchestrates Phase 2 integration with v1.0 grading components."""

    def __init__(self, exam_folder: Path):
        """
        Initialize Phase 2 Integration pipeline.

        Args:
            exam_folder: Path to exam folder
        """
        self.exam_folder = Path(exam_folder)
        self.processor = ExamProcessor(exam_folder)
        self.answer_key_manager = AnswerKeyManager(exam_folder)
        self.question_db = QuestionDatabase(exam_folder)
        self.aggregator = ClassReportAggregator(exam_folder)

    def extract_and_save_questions(self, pdf_path: str) -> Dict:
        """
        Step 1: Extract questions from PDF and save to database.

        Args:
            pdf_path: Path to exam PDF

        Returns:
            Extraction result dictionary
        """
        logger.info("=" * 70)
        logger.info("PHASE 2 INTEGRATION: STEP 1 - EXTRACT QUESTIONS")
        logger.info("=" * 70)

        try:
            questions = self.question_db.extract_from_pdf(pdf_path)

            # Validate extraction
            is_valid, errors = self.question_db.validate_extraction()
            if errors:
                logger.warning(f"Validation warnings: {errors}")

            result = {
                "status": "success",
                "questions_extracted": len(questions),
                "questions_saved": self.question_db.get_question_count(),
            }

            logger.info(f"✓ Extracted {len(questions)} questions")
            return result

        except Exception as e:
            logger.error(f"✗ Question extraction failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def load_and_validate_answer_key(
        self, answer_key_path: str
    ) -> Tuple[bool, Dict]:
        """
        Step 2: Load answer key and validate against questions.

        Args:
            answer_key_path: Path to answer key file (Excel or JSON)

        Returns:
            Tuple of (success, details)
        """
        logger.info("=" * 70)
        logger.info("PHASE 2 INTEGRATION: STEP 2 - LOAD ANSWER KEY")
        logger.info("=" * 70)

        try:
            # Load answer key
            file_path = Path(answer_key_path)
            if file_path.suffix.lower() == ".xlsx":
                answer_key = self.answer_key_manager.load_from_excel(answer_key_path)
            elif file_path.suffix.lower() == ".json":
                answer_key = self.answer_key_manager.load_from_json(answer_key_path)
            else:
                raise ValueError(f"Unsupported format: {file_path.suffix}")

            # Validate against questions
            total_questions = self.question_db.get_question_count()
            is_valid, errors = self.answer_key_manager.validate_against_questions(
                answer_key, total_questions
            )

            result = {
                "answer_keys_loaded": len(answer_key),
                "total_questions": total_questions,
                "validation_passed": is_valid,
                "validation_errors": errors,
            }

            if is_valid:
                logger.info(f"✓ Answer key validated successfully")
            else:
                logger.warning(f"⚠️  Validation issues: {errors}")

            return is_valid, result

        except Exception as e:
            logger.error(f"✗ Answer key loading failed: {str(e)}")
            return False, {"error": str(e)}

    def process_student_answers(self) -> Dict:
        """
        Step 3: Process all new student answer sheets.
        Grade using answer key and generate individual reports.

        Returns:
            Processing summary
        """
        logger.info("=" * 70)
        logger.info("PHASE 2 INTEGRATION: STEP 3 - PROCESS STUDENT ANSWERS")
        logger.info("=" * 70)

        try:
            # Load answer key first
            if not self.processor.load_answer_key():
                logger.warning(
                    "No answer key loaded; reports will not include grades"
                )

            # Process all new files
            result = self.processor.process_new_files()

            summary = {
                "status": "success",
                "processed": len(result.get("processed", [])),
                "failed": len(result.get("failed", [])),
                "skipped": len(result.get("skipped", [])),
                "details": result,
            }

            logger.info(f"✓ Processed {summary['processed']} students")
            if summary["failed"] > 0:
                logger.warning(f"✗ Failed: {summary['failed']}")

            return summary

        except Exception as e:
            logger.error(f"✗ Student processing failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

    def generate_class_report(self) -> Tuple[bool, Dict]:
        """
        Step 4: Generate class-level report from individual reports.

        Returns:
            Tuple of (success, details)
        """
        logger.info("=" * 70)
        logger.info("PHASE 2 INTEGRATION: STEP 4 - GENERATE CLASS REPORT")
        logger.info("=" * 70)

        try:
            # Validate before aggregation
            is_valid, error_msg = self.aggregator.validate_before_aggregation()
            if not is_valid:
                logger.error(f"✗ Validation failed: {error_msg}")
                return False, {"error": error_msg}

            # Generate metrics
            metrics = self.aggregator.generate_class_metrics()

            # Generate report
            report_path = self.aggregator.generate_class_report()

            result = {
                "status": "success",
                "report_path": str(report_path),
                "metrics": {
                    "total_students": metrics.get("total_students", 0),
                    "average_score": metrics.get("average_score", 0),
                    "pass_rate": metrics.get("pass_rate", 0),
                    "grading_used": metrics.get("grading_used", False),
                },
            }

            logger.info(f"✓ Class report generated: {report_path}")
            logger.info(f"  Average score: {metrics['average_score']:.1f}%")
            logger.info(f"  Pass rate: {metrics['pass_rate']:.1f}%")

            return True, result

        except Exception as e:
            logger.error(f"✗ Class report generation failed: {str(e)}")
            return False, {"error": str(e)}

    def run_full_pipeline(
        self, pdf_path: str, answer_key_path: str
    ) -> Dict:
        """
        Run complete Phase 2 Integration pipeline.

        Steps:
        1. Extract questions from PDF
        2. Load and validate answer key
        3. Process all student answer sheets
        4. Generate class report

        Args:
            pdf_path: Path to exam PDF
            answer_key_path: Path to answer key file

        Returns:
            Complete pipeline results
        """
        logger.info("\n")
        logger.info("╔" + "=" * 68 + "╗")
        logger.info("║ PHASE 2 INTEGRATION - COMPLETE PIPELINE" + " " * 28 + "║")
        logger.info("╚" + "=" * 68 + "╝\n")

        results = {
            "step_1_extract_questions": self.extract_and_save_questions(pdf_path),
        }

        if results["step_1_extract_questions"].get("status") != "success":
            logger.error("Pipeline failed at Step 1")
            return results

        is_key_valid, key_result = self.load_and_validate_answer_key(
            answer_key_path
        )
        results["step_2_load_answer_key"] = key_result

        if not is_key_valid:
            logger.warning("Answer key validation failed; continuing without grading")

        results["step_3_process_students"] = self.process_student_answers()

        success, report_result = self.generate_class_report()
        results["step_4_class_report"] = report_result

        # Summary
        logger.info("\n")
        logger.info("╔" + "=" * 68 + "╗")
        logger.info("║ PHASE 2 INTEGRATION - PIPELINE COMPLETE" + " " * 28 + "║")
        logger.info("╚" + "=" * 68 + "╝\n")

        results["overall_status"] = "success" if success else "partial"
        return results

    def display_results(self, results: Dict) -> str:
        """
        Format results for display.

        Args:
            results: Results dictionary from pipeline

        Returns:
            Formatted results string
        """
        output = "\n" + "=" * 70 + "\n"
        output += "PHASE 2 INTEGRATION RESULTS\n"
        output += "=" * 70 + "\n\n"

        # Step 1
        step1 = results.get("step_1_extract_questions", {})
        output += f"Step 1: Extract Questions\n"
        output += f"  Status: {step1.get('status', 'unknown').upper()}\n"
        if step1.get("status") == "success":
            output += f"  Questions: {step1.get('questions_extracted')}\n"

        # Step 2
        step2 = results.get("step_2_load_answer_key", {})
        output += f"\nStep 2: Load Answer Key\n"
        output += f"  Answer keys: {step2.get('answer_keys_loaded', 0)}\n"
        output += f"  Validation: {'✓ PASSED' if step2.get('validation_passed') else '⚠️  WARNINGS'}\n"

        # Step 3
        step3 = results.get("step_3_process_students", {})
        output += f"\nStep 3: Process Students\n"
        output += f"  Processed: {step3.get('processed', 0)}\n"
        output += f"  Failed: {step3.get('failed', 0)}\n"
        output += f"  Skipped: {step3.get('skipped', 0)}\n"

        # Step 4
        step4 = results.get("step_4_class_report", {})
        output += f"\nStep 4: Class Report\n"
        metrics = step4.get("metrics", {})
        output += f"  Total students: {metrics.get('total_students', 0)}\n"
        output += f"  Average score: {metrics.get('average_score', 0):.1f}%\n"
        output += f"  Pass rate: {metrics.get('pass_rate', 0):.1f}%\n"
        if metrics.get("grading_used"):
            output += f"  ✓ v1.0 Grading Integration: ACTIVE\n"

        output += "\n" + "=" * 70 + "\n"
        return output
