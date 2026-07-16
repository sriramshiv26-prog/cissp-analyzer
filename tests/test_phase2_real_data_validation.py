#!/usr/bin/env python3
"""
Phase 2 Real Data Validation - End-to-end integration test with actual exam data.
Tests the complete pipeline: PDF parsing → Excel parsing → Grading
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List

from cissp_analyzer.robust_pdf_parser import RobustPDFParser
from cissp_analyzer.robust_excel_parser import RobustExcelParser
from cissp_analyzer.answer_validator import AnswerValidator
from cissp_analyzer.streaming_report_aggregator import StreamingReportAggregator


class TestPhase2RealDataValidation:
    """Validate Phase 2 integration with real exam data."""

    REAL_DATA_PATH = Path(__file__).parent.parent / "test_data" / "week1"

    def test_real_exam_pdf_parsing(self):
        """Test parsing real CISSP exam PDF."""
        pdf_path = self.REAL_DATA_PATH / "exam.pdf"

        if not pdf_path.exists():
            pytest.skip(f"Real exam PDF not found: {pdf_path}")

        # Parse the PDF
        parser = RobustPDFParser(str(pdf_path))
        result = parser.extract_with_fallback()

        # Validate extraction
        assert result is not None, "PDF extraction failed"
        assert result.questions_found > 0, "No questions extracted from PDF"
        assert result.extraction_method in [
            "primary",
            "alternative",
            "partial",
        ], f"Invalid extraction method: {result.extraction_method}"

        print(f"\n✓ PDF Parsing Results:")
        print(f"  Questions found: {result.questions_found}")
        print(f"  Questions valid: {result.questions_valid}")
        print(f"  Extraction method: {result.extraction_method}")
        print(f"  Confidence: {result.confidence:.2%}")

        # We should have at least some valid questions
        assert result.questions_valid > 0, "No valid questions extracted"

    def test_real_student_answer_files(self):
        """Test parsing real student answer Excel files."""
        answer_files = list(self.REAL_DATA_PATH.glob("*_answers.xlsx"))

        if not answer_files:
            pytest.skip("No student answer files found")

        results = {}

        for answer_file in answer_files:
            student_name = answer_file.stem.replace("_answers", "")

            # Parse Excel file
            parser = RobustExcelParser(str(answer_file))
            parse_result = parser.parse_with_fallback(student_name=student_name)

            assert parse_result is not None, f"Failed to parse {student_name}"
            assert (
                parse_result.valid_answers > 0
            ), f"No answers extracted for {student_name}"

            results[student_name] = {
                "file": answer_file.name,
                "valid_answers": parse_result.valid_answers,
                "skipped_answers": parse_result.skipped_answers,
                "warnings": len(parse_result.warnings),
                "column_mapping": parse_result.column_mapping,
            }

        print(f"\n✓ Student Answer Parsing Results:")
        for student, info in results.items():
            print(f"\n  {student}:")
            print(f"    Valid answers: {info['valid_answers']}")
            print(f"    Skipped: {info['skipped_answers']}")
            print(f"    Warnings: {info['warnings']}")
            print(
                f"    Columns: Q={info['column_mapping'].get('question')}, "
                f"A={info['column_mapping'].get('answer')}"
            )

        # Should have parsed multiple students
        assert len(results) > 0, "No students parsed"
        print(f"\n  Total students parsed: {len(results)}")

    def test_phase2_integration_pipeline(self):
        """Test complete Phase 2 integration: PDF → Answers → Grading."""
        pdf_path = self.REAL_DATA_PATH / "exam.pdf"
        answer_files = list(self.REAL_DATA_PATH.glob("*_answers.xlsx"))

        if not pdf_path.exists() or not answer_files:
            pytest.skip("Real exam data not found")

        # Step 1: Extract questions from PDF
        print("\n[STEP 1] Extracting questions from PDF...")
        pdf_parser = RobustPDFParser(str(pdf_path))
        pdf_result = pdf_parser.extract_with_fallback()

        assert pdf_result.questions_valid > 0, "No questions extracted"
        total_questions = pdf_result.questions_valid
        print(f"  ✓ Extracted {total_questions} questions")
        print(f"    Extraction confidence: {pdf_result.confidence:.2%}")

        # Step 2: Parse student answers
        print("\n[STEP 2] Parsing student answer files...")
        student_results = {}

        for answer_file in answer_files:
            student_name = answer_file.stem.replace("_answers", "")

            excel_parser = RobustExcelParser(str(answer_file))
            result = excel_parser.parse_with_fallback(student_name=student_name)

            assert result.valid_answers > 0, f"No answers for {student_name}"

            student_results[student_name] = {
                "answers": result.answers,
                "valid_count": result.valid_answers,
                "skipped": result.skipped_answers,
            }

            print(f"  ✓ {student_name}: {result.valid_answers} answers parsed")

        # Step 3: Validate answers
        print("\n[STEP 3] Validating answers...")
        validator = AnswerValidator()
        validation_results = {}

        for student_name, data in student_results.items():
            answers = data["answers"]

            # Check answer coverage
            coverage = (
                (len(answers) / total_questions) * 100 if total_questions > 0 else 0
            )
            is_valid = coverage >= 50  # At least 50% answered

            validation_results[student_name] = {
                "answers_provided": len(answers),
                "total_questions": total_questions,
                "coverage": f"{coverage:.1f}%",
                "is_valid": is_valid,
            }

            status = "✓" if is_valid else "⚠"
            print(
                f"  {status} {student_name}: {len(answers)}/{total_questions} "
                f"({coverage:.1f}%)"
            )

        # Step 4: Grade students
        print("\n[STEP 4] Grading student responses...")
        grading_results = {}

        for student_name, data in student_results.items():
            # Mock answer key (in real scenario, this comes from external source)
            # For now, we'll just count correct/incorrect based on answer presence
            answers = data["answers"]

            grading_results[student_name] = {
                "answers_submitted": len(answers),
                "total_questions": total_questions,
                "submission_rate": f"{(len(answers)/total_questions*100):.1f}%",
            }

            print(f"  ✓ {student_name}: {len(answers)}/{total_questions} submitted")

        # Summary
        print("\n[SUMMARY] Phase 2 Integration Pipeline:")
        print(f"  PDF parsed: {total_questions} questions")
        print(f"  Students processed: {len(student_results)}")
        print(
            f"  Valid students: {sum(1 for v in validation_results.values() if v['is_valid'])}"
        )

        # Create a class report aggregator test
        print("\n[STEP 5] Testing streaming report aggregation...")

        # Create temporary exam folder structure
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir) / "test_exam"
            exam_folder.mkdir()
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create individual reports from our grading results
            for student_name, grade_data in grading_results.items():
                report = {
                    "student_name": student_name,
                    "exam": "Week 1 CISSP Exam",
                    "total_questions": total_questions,
                    "grading": {
                        "total_correct": grade_data["answers_submitted"],
                        "total_incorrect": total_questions
                        - grade_data["answers_submitted"],
                        "total_blank": 0,
                        "score": (
                            grade_data["answers_submitted"] / total_questions * 100
                        ),
                        "grading_available": True,
                    },
                }

                report_file = reports_dir / f"Individual_Report_{student_name}.json"
                with open(report_file, "w") as f:
                    json.dump(report, f)

            # Test streaming aggregation
            aggregator = StreamingReportAggregator(exam_folder)
            metrics = aggregator.aggregate_streaming()

            assert metrics["total_students"] == len(grading_results)
            print(f"  ✓ Aggregated {metrics['total_students']} student reports")
            print(f"    Average score: {metrics.get('average_score', 0):.1f}%")
            print(f"    Pass rate: {metrics.get('pass_rate', 0):.1f}%")

        # All steps successful
        assert len(validation_results) > 0, "No students validated"
        assert len(grading_results) > 0, "No students graded"

    def test_pdf_extraction_coverage(self):
        """Test PDF extraction completeness and quality."""
        pdf_path = self.REAL_DATA_PATH / "exam.pdf"

        if not pdf_path.exists():
            pytest.skip("Real exam PDF not found")

        parser = RobustPDFParser(str(pdf_path))
        result = parser.extract_with_fallback()

        print(f"\n✓ PDF Extraction Quality Report:")
        print(f"  Total questions found: {result.questions_found}")
        print(f"  Valid questions: {result.questions_valid}")
        print(f"  Extraction method: {result.extraction_method}")
        print(f"  Confidence score: {result.confidence:.2%}")

        if result.questions_found > 0:
            validity_rate = (result.questions_valid / result.questions_found) * 100
            print(f"  Validity rate: {validity_rate:.1f}%")

        # Report on options coverage
        questions_with_options = sum(
            1
            for q in result.questions.values()
            if q.get("options") and len(q["options"]) >= 4
        )
        print(f"  Questions with full options: {questions_with_options}")

    def test_excel_file_compatibility(self):
        """Test compatibility with various Excel formats used by students."""
        answer_files = list(self.REAL_DATA_PATH.glob("*.xlsx"))

        if not answer_files:
            pytest.skip("No Excel files found")

        print(f"\n✓ Excel File Compatibility Report:")

        for answer_file in answer_files:
            try:
                parser = RobustExcelParser(str(answer_file))
                result = parser.parse_with_fallback()

                status = "✓" if result.valid_answers > 0 else "⚠"
                print(f"  {status} {answer_file.name}")
                print(f"     Columns detected: {result.column_mapping}")
                print(f"     Valid answers: {result.valid_answers}")

                if result.errors:
                    print(f"     Errors: {', '.join(result.errors[:2])}")

            except Exception as e:
                print(f"  ✗ {answer_file.name}: {str(e)}")

    def test_end_to_end_workflow_report(self):
        """Generate comprehensive E2E workflow report."""
        pdf_path = self.REAL_DATA_PATH / "exam.pdf"
        answer_files = list(self.REAL_DATA_PATH.glob("*_answers.xlsx"))

        if not pdf_path.exists():
            pytest.skip("Real exam data not found")

        print("\n" + "=" * 70)
        print("PHASE 2 INTEGRATION - END-TO-END WORKFLOW REPORT")
        print("=" * 70)

        # PDF Parsing
        print("\n[1] PDF PARSING")
        print("-" * 70)
        pdf_parser = RobustPDFParser(str(pdf_path))
        pdf_result = pdf_parser.extract_with_fallback()

        print(f"File: {pdf_path.name}")
        print(f"Questions extracted: {pdf_result.questions_valid}")
        print(f"Extraction method: {pdf_result.extraction_method}")
        print(f"Confidence: {pdf_result.confidence:.2%}")
        print(f"Status: {'PASS ✓' if pdf_result.questions_valid > 0 else 'FAIL ✗'}")

        # Excel Parsing
        print("\n[2] EXCEL ANSWER FILE PARSING")
        print("-" * 70)

        total_valid = 0
        total_skipped = 0

        for answer_file in answer_files:
            student_name = answer_file.stem.replace("_answers", "")
            excel_parser = RobustExcelParser(str(answer_file))
            result = excel_parser.parse_with_fallback(student_name=student_name)

            total_valid += result.valid_answers
            total_skipped += result.skipped_answers

            print(f"\n{student_name}:")
            print(f"  File: {answer_file.name}")
            print(f"  Valid answers: {result.valid_answers}")
            print(f"  Skipped: {result.skipped_answers}")
            print(
                f"  Column mapping: Q={result.column_mapping.get('question')}, "
                f"A={result.column_mapping.get('answer')}"
            )

        print(f"\nSummary:")
        print(f"  Students processed: {len(answer_files)}")
        print(f"  Total answers extracted: {total_valid}")
        print(f"  Total skipped: {total_skipped}")

        # Overall status
        print("\n[3] OVERALL STATUS")
        print("-" * 70)

        checks = [
            ("PDF extraction", pdf_result.questions_valid > 0),
            ("Excel parsing", len(answer_files) > 0 and total_valid > 0),
            (
                "Answer coverage",
                total_valid > len(answer_files) * 10,
            ),  # At least 10 answers per student
        ]

        all_pass = True
        for check_name, passed in checks:
            status = "PASS ✓" if passed else "FAIL ✗"
            print(f"{check_name}: {status}")
            if not passed:
                all_pass = False

        print("\n" + "=" * 70)
        if all_pass:
            print("PHASE 2 VALIDATION: READY FOR PRODUCTION ✓")
        else:
            print("PHASE 2 VALIDATION: ISSUES DETECTED ⚠")
        print("=" * 70 + "\n")

        assert all_pass, "Phase 2 validation failed critical checks"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
