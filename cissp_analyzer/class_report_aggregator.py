#!/usr/bin/env python3
"""
Class Report Aggregator - Aggregates individual student reports into class-level metrics.
Validates data consistency and generates class reports.
"""

import json
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from cissp_analyzer.exam_folder_manager import ExamFolderManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassReportAggregator:
    """Aggregates individual student reports into class metrics."""

    def __init__(self, exam_folder: Path):
        """
        Initialize ClassReportAggregator.

        Args:
            exam_folder: Path to exam folder containing reports/
        """
        self.exam_folder = Path(exam_folder)
        self.reports_dir = self.exam_folder / "reports"

        # Load exam metadata
        exam_id = self.exam_folder.name
        self.exam_manager = ExamFolderManager(str(self.exam_folder.parent))
        try:
            self.metadata = self.exam_manager.get_exam_metadata(exam_id)
        except FileNotFoundError:
            self.metadata = {}

    def get_all_student_reports(self) -> List[Dict]:
        """
        Load all student report files.

        Returns:
            List of student report dictionaries
        """
        if not self.reports_dir.exists():
            logger.warning(f"Reports directory not found: {self.reports_dir}")
            return []

        reports = []
        for report_file in self.reports_dir.glob("Individual_Report_*.json"):
            try:
                with open(report_file, "r") as f:
                    report = json.load(f)
                    reports.append(report)
                    logger.info(f"Loaded report: {report_file.name}")
            except Exception as e:
                logger.error(f"Error loading {report_file.name}: {str(e)}")

        return reports

    def validate_before_aggregation(self) -> Tuple[bool, str]:
        """
        Validate reports before aggregation.

        Checks:
        - Reports exist
        - All students have same number of questions answered
        - No duplicate student names

        Returns:
            (is_valid, error_message)
        """
        reports = self.get_all_student_reports()

        # Check reports exist
        if not reports:
            return False, "No student reports found"

        # Check for duplicate student names
        student_names = [r.get("student_name") for r in reports]
        duplicates = [name for name in student_names if student_names.count(name) > 1]
        if duplicates:
            return False, f"Duplicate student names found: {duplicates}"

        # Check all have same number of questions (or at least similar)
        question_counts = [len(r.get("answers", {})) for r in reports]
        if question_counts and min(question_counts) != max(question_counts):
            logger.warning(
                f"Students answered different numbers of questions: {set(question_counts)}"
            )
            # Don't fail, just warn - students might skip questions

        logger.info(f"Validation passed for {len(reports)} reports")
        return True, ""

    def generate_class_metrics(self) -> Dict:
        """
        Calculate class-level metrics from all student reports.
        Uses graded results if available, falls back to answer count.

        Returns:
            Dictionary with aggregated metrics
        """
        reports = self.get_all_student_reports()

        if not reports:
            logger.error("No reports to aggregate")
            return {}

        # Calculate per-student metrics
        student_metrics = []
        all_scores = []
        grading_available = False

        for report in reports:
            student_name = report.get("student_name", "Unknown")
            total_questions = report.get("total_questions", 0)

            if total_questions == 0:
                logger.warning(f"No total questions defined for {student_name}")
                continue

            # Try to use grading results first (Phase 2 Integration)
            grading = report.get("grading", {})
            if grading.get("grading_available"):
                correct = grading.get("total_correct", 0)
                incorrect = grading.get("total_incorrect", 0)
                blank = grading.get("total_blank", 0)
                score_pct = grading.get("score", 0)
                grading_available = True
            else:
                # Fall back to counting answers (original Phase 2 behavior)
                answers = report.get("answers", {})
                correct = len(answers)
                incorrect = 0
                blank = 0
                score_pct = (
                    (correct / total_questions * 100) if total_questions > 0 else 0
                )

            student_metrics.append(
                {
                    "student_name": student_name,
                    "correct": correct,
                    "incorrect": incorrect,
                    "blank": blank,
                    "total": total_questions,
                    "percentage": score_pct,
                }
            )

            all_scores.append(score_pct)

        # Calculate aggregate metrics
        if not all_scores:
            logger.error("No valid scores to aggregate")
            return {}

        passing_count = sum(1 for score in all_scores if score >= 75)

        metrics = {
            "total_students": len(student_metrics),
            "average_score": statistics.mean(all_scores),
            "median_score": statistics.median(all_scores),
            "min_score": min(all_scores),
            "max_score": max(all_scores),
            "std_dev": statistics.stdev(all_scores) if len(all_scores) > 1 else 0,
            "passing_count": passing_count,
            "pass_rate": (
                (passing_count / len(student_metrics) * 100) if student_metrics else 0
            ),
            "grading_used": grading_available,
            "student_metrics": student_metrics,
            "exam_name": self.metadata.get("exam_name", "Unknown"),
        }

        logger.info(f"Generated metrics for {len(student_metrics)} students")
        logger.info(f"Class average: {metrics['average_score']:.1f}%")
        logger.info(f"Pass rate: {metrics['pass_rate']:.1f}%")
        if grading_available:
            logger.info(f"✓ Using v1.0 grading integration")

        return metrics

    def generate_class_report(self) -> Optional[Path]:
        """
        Generate class-level report using existing ClassReportGenerator.

        Returns:
            Path to generated report file or None if failed
        """
        # Validate before generating
        is_valid, error_msg = self.validate_before_aggregation()
        if not is_valid:
            logger.error(f"Validation failed: {error_msg}")
            return None

        try:
            # For now, save metrics as JSON
            # This can be extended to generate Excel/PDF reports
            report_filename = "Class_Report.json"
            report_path = self.reports_dir / report_filename

            # Get previous metrics if report exists
            previous_metrics = self._load_previous_metrics(report_path)

            # Generate new metrics
            metrics = self.generate_class_metrics()
            with open(report_path, "w") as f:
                json.dump(metrics, f, indent=2)

            # Log changes if there was a previous report
            if previous_metrics:
                self._log_report_changes(previous_metrics, metrics)

            logger.info(f"Class report generated: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Error generating class report: {str(e)}")
            return None

    def _load_previous_metrics(self, report_path: Path) -> Optional[Dict]:
        """
        Load previous class report metrics if it exists.

        Args:
            report_path: Path to the class report file

        Returns:
            Previous metrics dict or None if file doesn't exist
        """
        if not report_path.exists():
            return None

        try:
            with open(report_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load previous metrics: {str(e)}")
            return None

    def _log_report_changes(self, previous: Dict, current: Dict) -> None:
        """
        Log changes between previous and current class report.

        Args:
            previous: Previous metrics dictionary
            current: Current metrics dictionary
        """
        prev_students = previous.get("total_students", 0)
        curr_students = current.get("total_students", 0)
        student_delta = curr_students - prev_students

        if student_delta != 0:
            logger.info(f"📊 Class Report Updated:")
            logger.info(
                f"   Students: {prev_students} → {curr_students} "
                f"({student_delta:+d})"
            )

        prev_avg = previous.get("average_score", 0)
        curr_avg = current.get("average_score", 0)
        avg_delta = curr_avg - prev_avg

        logger.info(
            f"   Average Score: {prev_avg:.1f}% → {curr_avg:.1f}% "
            f"({avg_delta:+.1f}%)"
        )

        prev_pass = previous.get("pass_rate", 0)
        curr_pass = current.get("pass_rate", 0)
        pass_delta = curr_pass - prev_pass

        logger.info(
            f"   Pass Rate: {prev_pass:.1f}% → {curr_pass:.1f}% "
            f"({pass_delta:+.1f}%)"
        )

        if student_delta > 0:
            new_students = [
                s
                for s in current.get("student_metrics", [])
                if s["student_name"]
                not in [p["student_name"] for p in previous.get("student_metrics", [])]
            ]
            if new_students:
                logger.info(f"   New students added:")
                for student in new_students:
                    logger.info(
                        f"     • {student['student_name']}: "
                        f"{student['correct']}/{student['total']} "
                        f"({student['percentage']:.1f}%)"
                    )

    def get_report_changes(
        self, report_path: Path, current_metrics: Dict
    ) -> Optional[str]:
        """
        Get formatted summary of changes since last report generation.

        Args:
            report_path: Path to the previous class report
            current_metrics: Current metrics dictionary

        Returns:
            Formatted change summary or None if no previous report
        """
        previous_metrics = self._load_previous_metrics(report_path)
        if not previous_metrics:
            return None

        prev_students = previous_metrics.get("total_students", 0)
        curr_students = current_metrics.get("total_students", 0)
        student_delta = curr_students - prev_students

        prev_avg = previous_metrics.get("average_score", 0)
        curr_avg = current_metrics.get("average_score", 0)
        avg_delta = curr_avg - prev_avg

        prev_pass = previous_metrics.get("pass_rate", 0)
        curr_pass = current_metrics.get("pass_rate", 0)
        pass_delta = curr_pass - prev_pass

        # Get new students
        new_students = []
        if student_delta > 0:
            prev_names = {
                p["student_name"] for p in previous_metrics.get("student_metrics", [])
            }
            new_students = [
                s
                for s in current_metrics.get("student_metrics", [])
                if s["student_name"] not in prev_names
            ]

        # Format changes
        changes = "\n" + "=" * 70 + "\n"
        changes += "📊 Class Report Updated\n"
        changes += "=" * 70 + "\n\n"

        changes += f"Students: {prev_students} → {curr_students}"
        if student_delta != 0:
            changes += f" ({student_delta:+d})"
        changes += "\n"

        changes += f"Average Score: {prev_avg:.1f}% → {curr_avg:.1f}%"
        if avg_delta != 0:
            changes += f" ({avg_delta:+.1f}%)"
        changes += "\n"

        changes += f"Pass Rate: {prev_pass:.1f}% → {curr_pass:.1f}%"
        if pass_delta != 0:
            changes += f" ({pass_delta:+.1f}%)"
        changes += "\n"

        if new_students:
            changes += "\n📝 New Students Added:\n"
            for student in new_students:
                changes += (
                    f"  • {student['student_name']:20} "
                    f"{student['correct']:3}/{student['total']:3} "
                    f"({student['percentage']:5.1f}%)\n"
                )

        changes += "=" * 70 + "\n"

        return changes

    def show_preview(self, metrics: Dict) -> str:
        """
        Generate formatted preview of class metrics.

        Args:
            metrics: Metrics dictionary from generate_class_metrics()

        Returns:
            Formatted preview string
        """
        if not metrics:
            return "No metrics available"

        preview = "\n"
        preview += "=" * 70 + "\n"
        preview += f"Class Report Preview - {metrics.get('exam_name', 'Unknown')}\n"
        preview += "=" * 70 + "\n\n"

        preview += f"Students Analyzed: {metrics.get('total_students', 0)}\n"
        preview += f"Average Score: {metrics.get('average_score', 0):.1f}%\n"
        preview += f"Median Score: {metrics.get('median_score', 0):.1f}%\n"
        preview += f"Score Range: {metrics.get('min_score', 0):.1f}% - {metrics.get('max_score', 0):.1f}%\n"
        preview += f"Std Dev: {metrics.get('std_dev', 0):.1f}%\n\n"

        preview += f"Pass Rate (>75%): {metrics.get('pass_rate', 0):.1f}% "
        preview += f"({metrics.get('passing_count', 0)}/{metrics.get('total_students', 0)} students)\n\n"

        # Show individual student scores
        if metrics.get("student_metrics"):
            preview += "Student Scores:\n"
            preview += "-" * 70 + "\n"
            for student in sorted(
                metrics["student_metrics"],
                key=lambda x: x["percentage"],
                reverse=True,
            ):
                status = "✓ PASS" if student["percentage"] >= 75 else "✗ FAIL"
                # Show detailed breakdown if grading used
                if metrics.get("grading_used"):
                    preview += (
                        f"  {student['student_name']:25} "
                        f"✓{student['correct']:2} ✗{student['incorrect']:2} "
                        f"({student['percentage']:5.1f}%) {status}\n"
                    )
                else:
                    preview += (
                        f"  {student['student_name']:30} "
                        f"{student['correct']:3}/{student['total']:3} "
                        f"({student['percentage']:5.1f}%) {status}\n"
                    )

        preview += "=" * 70 + "\n\n"

        return preview

    def export_metrics_summary(self, output_file: Path) -> bool:
        """
        Export metrics summary to JSON file.

        Args:
            output_file: Path to output JSON file

        Returns:
            True if successful
        """
        try:
            metrics = self.generate_class_metrics()
            if not metrics:
                logger.error("No metrics to export")
                return False

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(metrics, f, indent=2)

            logger.info(f"Metrics exported to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
            return False
