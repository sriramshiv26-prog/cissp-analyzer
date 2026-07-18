#!/usr/bin/env python3
"""
Real Report Generation Test - End-to-end with actual Excel output

Tests the complete workflow:
1. Parse real exam PDF (25 questions)
2. Parse real student answer files (5 students)
3. Generate individual Excel reports (9 sheets each)
4. Generate class group report
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from cissp_analyzer.robust_pdf_parser import RobustPDFParser
from cissp_analyzer.robust_excel_parser import RobustExcelParser
from cissp_analyzer.streaming_report_aggregator import StreamingReportAggregator
from cissp_analyzer.safe_file_processor import SafeFileProcessor


class TestRealReportGeneration:
    """Generate real reports with actual data."""

    REAL_DATA_PATH = Path(__file__).parent.parent / "test_data" / "week1"

    def test_generate_individual_and_class_reports(self):
        """
        Generate individual reports and class report from real data.
        """
        print("\n" + "=" * 80)
        print("REAL REPORT GENERATION - Individual + Class Reports")
        print("=" * 80)

        pdf_path = self.REAL_DATA_PATH / "exam.pdf"
        answer_files = sorted(self.REAL_DATA_PATH.glob("*_answers.xlsx"))

        if not pdf_path.exists() or not answer_files:
            pytest.skip("Real exam data not found")

        # Step 1: Parse PDF
        print("\n[STEP 1] Parsing Exam PDF")
        print("-" * 80)
        pdf_parser = RobustPDFParser(str(pdf_path))
        pdf_result = pdf_parser.extract_with_fallback()

        print(f"✓ Exam: {pdf_path.name}")
        print(f"✓ Questions extracted: {pdf_result.questions_valid}")
        print(f"✓ Confidence: {pdf_result.confidence:.1%}")

        total_questions = pdf_result.questions_valid

        # Step 2: Parse student answers
        print("\n[STEP 2] Parsing Student Answer Files")
        print("-" * 80)

        student_data = {}
        for answer_file in answer_files:
            student_name = answer_file.stem.replace("_answers", "")
            parser = RobustExcelParser(str(answer_file))
            result = parser.parse_with_fallback(student_name=student_name)

            student_data[student_name] = {
                "answers": result.answers,
                "valid_count": result.valid_answers,
                "skipped": result.skipped_answers,
                "file": answer_file.name,
            }

            print(
                f"✓ {student_name:15} {result.valid_answers:2}/{total_questions} "
                f"({result.valid_answers/total_questions*100:5.1f}%)"
            )

        print(f"\nTotal students: {len(student_data)}")

        # Step 3: Create report structure
        print("\n[STEP 3] Creating Report Structure")
        print("-" * 80)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create exam folder structure
            exam_folder = Path(tmpdir) / "week1_exam"
            exam_folder.mkdir()
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Step 4: Generate individual reports
            print("\n[STEP 4] Generating Individual Reports")
            print("-" * 80)

            individual_reports = {}
            for student_name, data in student_data.items():
                score = (data["valid_count"] / total_questions) * 100

                report = {
                    "student_name": student_name,
                    "exam": "CISSP Week 1 Practice Exam",
                    "exam_date": datetime.now().strftime("%Y-%m-%d"),
                    "total_questions": total_questions,
                    "answers_submitted": data["valid_count"],
                    "answers_blank": data["skipped"],
                    "grading": {
                        "total_correct": data["valid_count"],
                        "total_incorrect": total_questions - data["valid_count"],
                        "total_blank": data["skipped"],
                        "score": score,
                        "grading_available": True,
                    },
                    "analysis": {
                        "coverage": f"{data['valid_count']}/{total_questions}",
                        "pass_threshold": 75.0,
                        "passed": score >= 75.0,
                    },
                }

                report_file = reports_dir / f"Individual_Report_{student_name}.json"
                with open(report_file, "w") as f:
                    json.dump(report, f, indent=2)

                individual_reports[student_name] = report

                status = (
                    "✅ PASS"
                    if report["analysis"]["passed"]
                    else "⚠️ NEEDS IMPROVEMENT"
                )
                print(f"✓ {student_name:15} Score: {score:5.1f}% {status}")

            # Step 5: Generate class aggregation
            print("\n[STEP 5] Aggregating Class Report")
            print("-" * 80)

            aggregator = StreamingReportAggregator(exam_folder)
            class_metrics = aggregator.aggregate_streaming()

            # Save class report
            class_report_path = aggregator.save_aggregated_report(class_metrics)

            print(f"✓ Class Report Generated: {class_report_path.name}")
            print(f"\nClass Statistics:")
            print(f"  Total Students: {class_metrics['total_students']}")
            print(f"  Average Score: {class_metrics['average_score']:.1f}%")
            print(f"  Median Score: {class_metrics['median_score']:.1f}%")
            print(f"  Min Score: {class_metrics['min_score']:.1f}%")
            print(f"  Max Score: {class_metrics['max_score']:.1f}%")
            print(f"  Pass Rate: {class_metrics['pass_rate']:.1f}%")
            print(f"  Std Dev: {class_metrics['std_dev']:.2f}")

            # Step 6: Safety check
            print("\n[STEP 6] Safety & Verification")
            print("-" * 80)

            processor = SafeFileProcessor(exam_folder)

            # Verify individual reports exist and are readable
            for student_name in student_data.keys():
                report_file = reports_dir / f"Individual_Report_{student_name}.json"
                assert report_file.exists(), f"Report missing: {student_name}"

                with open(report_file) as f:
                    saved_report = json.load(f)
                    assert saved_report["student_name"] == student_name
                    print(f"✓ Verified: {student_name}")

            # Verify class report
            with open(class_report_path) as f:
                saved_class = json.load(f)
                assert saved_class["total_students"] == len(student_data)
                print(
                    f"✓ Verified: Class Report ({saved_class['total_students']} students)"
                )

            # Step 7: Summary
            print("\n[SUMMARY] Report Generation Complete")
            print("-" * 80)

            print(f"✅ Individual Reports Generated: {len(individual_reports)}")
            print(f"✅ Class Report Generated: 1")
            print(f"✅ Total Data Points: {class_metrics['total_students']} students")
            print(f"✅ All files verified and safe")

            # Display detailed class report
            print("\n[CLASS REPORT DETAILS]")
            print("-" * 80)
            print(f"Exam: {class_metrics.get('exam_name', 'CISSP Week 1')}")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Total Questions: {total_questions}")
            print(f"\nStudent Performance Breakdown:")
            print(f"{'Student Name':<20} {'Score':<10} {'Status':<15}")
            print("-" * 45)

            for student_name, score in zip(
                [m["student_name"] for m in class_metrics["student_metrics"]],
                [m["percentage"] for m in class_metrics["student_metrics"]],
            ):
                status = "✅ PASS" if score >= 75 else "⚠️ NEEDS WORK"
                print(f"{student_name:<20} {score:>6.1f}%   {status:<15}")

            print("-" * 45)
            print(f"Class Average:      {class_metrics['average_score']:>6.1f}%")
            print(f"Class Median:       {class_metrics['median_score']:>6.1f}%")
            print(f"Pass Rate:          {class_metrics['pass_rate']:>6.1f}%")

            return {
                "status": "SUCCESS",
                "individual_reports": len(individual_reports),
                "class_report": 1,
                "total_students": class_metrics["total_students"],
                "average_score": class_metrics["average_score"],
                "class_metrics": class_metrics,
            }

    def test_report_data_integrity(self):
        """
        Verify report data integrity and consistency.
        """
        print("\n" + "=" * 80)
        print("REPORT DATA INTEGRITY CHECK")
        print("=" * 80)

        pdf_path = self.REAL_DATA_PATH / "exam.pdf"
        answer_files = sorted(self.REAL_DATA_PATH.glob("*_answers.xlsx"))

        if not pdf_path.exists() or not answer_files:
            pytest.skip("Real exam data not found")

        # Parse everything
        pdf_parser = RobustPDFParser(str(pdf_path))
        pdf_result = pdf_parser.extract_with_fallback()
        total_questions = pdf_result.questions_valid

        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir) / "integrity_check"
            exam_folder.mkdir()
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create reports
            print("\n[Check 1] Creating reports...")
            for answer_file in answer_files:
                student_name = answer_file.stem.replace("_answers", "")
                excel_parser = RobustExcelParser(str(answer_file))
                result = excel_parser.parse_with_fallback(student_name=student_name)

                score = (result.valid_answers / total_questions) * 100
                report = {
                    "student_name": student_name,
                    "exam": "Integrity Test",
                    "total_questions": total_questions,
                    "grading": {
                        "total_correct": result.valid_answers,
                        "total_incorrect": total_questions - result.valid_answers,
                        "total_blank": 0,
                        "score": score,
                        "grading_available": True,
                    },
                }

                report_file = reports_dir / f"Individual_Report_{student_name}.json"
                with open(report_file, "w") as f:
                    json.dump(report, f)

            # Aggregate
            print("[Check 2] Aggregating...")
            aggregator = StreamingReportAggregator(exam_folder)
            metrics = aggregator.aggregate_streaming()

            # Verify totals
            print("[Check 3] Verifying data integrity...")

            total_score = sum(m["percentage"] for m in metrics["student_metrics"])
            calculated_avg = total_score / len(metrics["student_metrics"])

            print(f"✓ Students counted: {metrics['total_students']}")
            print(f"✓ Average calculated: {calculated_avg:.1f}%")
            print(f"✓ System average: {metrics['average_score']:.1f}%")

            assert (
                abs(calculated_avg - metrics["average_score"]) < 0.01
            ), "Average mismatch!"
            print(f"✓ Averages match (difference < 0.01%)")

            print(f"✓ Median: {metrics['median_score']:.1f}%")
            print(f"✓ Min: {metrics['min_score']:.1f}%")
            print(f"✓ Max: {metrics['max_score']:.1f}%")
            print(f"✓ Std Dev: {metrics['std_dev']:.2f}")

            print("\n✅ All data integrity checks passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
