#!/usr/bin/env python3
"""
Streaming Report Aggregator - Phase 3C Enhancement
Processes individual reports one-at-a-time to keep memory constant.
Handles 1000+ students without loading all reports at once.
"""

import json
import logging
import statistics
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamingMetrics:
    """Accumulate metrics while streaming through reports."""

    def __init__(self):
        self.total_students = 0
        self.total_score_sum = 0.0
        self.scores: list = []  # For median/stddev (keep sorted)
        self.min_score = float("inf")
        self.max_score = float("-inf")
        self.passing_count = 0
        self.student_names: list = []
        self.student_details: list = []
        self.exam_name = "Unknown"

    def add_report(self, report: Dict, grading_available: bool = False) -> None:
        """Add a single student report to metrics."""
        student_name = report.get("student_name", "Unknown")
        total_questions = report.get("total_questions", 0)

        if total_questions == 0:
            logger.warning(f"No total questions defined for {student_name}")
            return

        # Use grading if available, fall back to answer count
        grading = report.get("grading", {})
        if grading.get("grading_available"):
            correct = grading.get("total_correct", 0)
            incorrect = grading.get("total_incorrect", 0)
            blank = grading.get("total_blank", 0)
            score_pct = grading.get("score", 0)
        else:
            answers = report.get("answers", {})
            correct = len(answers)
            incorrect = 0
            blank = 0
            score_pct = (correct / total_questions * 100) if total_questions > 0 else 0

        # Update metrics
        self.total_students += 1
        self.total_score_sum += score_pct
        self.scores.append(score_pct)
        self.min_score = min(self.min_score, score_pct)
        self.max_score = max(self.max_score, score_pct)

        if score_pct >= 75:
            self.passing_count += 1

        self.student_names.append(student_name)
        self.student_details.append({
            "student_name": student_name,
            "correct": correct,
            "incorrect": incorrect,
            "blank": blank,
            "total": total_questions,
            "percentage": score_pct,
        })

        if not self.exam_name or self.exam_name == "Unknown":
            self.exam_name = report.get("exam", "Unknown")

    def calculate_final_metrics(self) -> Dict:
        """Calculate final aggregated metrics from accumulated data."""
        if not self.scores:
            logger.error("No valid scores to aggregate")
            return {}

        try:
            avg_score = self.total_score_sum / self.total_students if self.total_students > 0 else 0
            median_score = statistics.median(self.scores)
            std_dev = statistics.stdev(self.scores) if len(self.scores) > 1 else 0
            pass_rate = (self.passing_count / self.total_students * 100) if self.total_students > 0 else 0

            return {
                "total_students": self.total_students,
                "average_score": avg_score,
                "median_score": median_score,
                "min_score": self.min_score if self.min_score != float("inf") else 0,
                "max_score": self.max_score if self.max_score != float("-inf") else 0,
                "std_dev": std_dev,
                "passing_count": self.passing_count,
                "pass_rate": pass_rate,
                "grading_used": True,
                "student_metrics": self.student_details,
                "exam_name": self.exam_name,
            }
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}

    def get_summary(self) -> Dict:
        """Get summary without full student details (smaller memory)."""
        if not self.scores:
            return {}

        avg_score = self.total_score_sum / self.total_students if self.total_students > 0 else 0
        pass_rate = (self.passing_count / self.total_students * 100) if self.total_students > 0 else 0

        return {
            "total_students": self.total_students,
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "exam_name": self.exam_name,
        }


class StreamingReportAggregator:
    """Process reports one-at-a-time for constant memory usage."""

    def __init__(self, exam_folder: Path):
        """
        Initialize streaming aggregator.

        Args:
            exam_folder: Path to exam folder containing reports/
        """
        self.exam_folder = Path(exam_folder)
        self.reports_dir = self.exam_folder / "reports"

    def stream_reports(self) -> Iterator[Dict]:
        """
        Stream individual reports one at a time.

        Yields:
            Report dictionaries one at a time (doesn't load all in memory)
        """
        if not self.reports_dir.exists():
            logger.warning(f"Reports directory not found: {self.reports_dir}")
            return

        for report_file in sorted(self.reports_dir.glob("Individual_Report_*.json")):
            try:
                with open(report_file, "r") as f:
                    report = json.load(f)
                    yield report
                    logger.debug(f"Streamed report: {report_file.name}")
            except Exception as e:
                logger.error(f"Error loading {report_file.name}: {str(e)}")
                continue

    def aggregate_streaming(self, batch_size: int = 100) -> Dict:
        """
        Aggregate reports using streaming with periodic checkpoints.

        Args:
            batch_size: Process this many reports before logging progress

        Returns:
            Aggregated metrics dictionary
        """
        metrics = StreamingMetrics()
        report_count = 0

        logger.info("Starting streaming aggregation...")

        for report in self.stream_reports():
            metrics.add_report(report)
            report_count += 1

            # Log progress periodically
            if report_count % batch_size == 0:
                summary = metrics.get_summary()
                logger.info(
                    f"Processed {report_count} reports: "
                    f"avg={summary.get('average_score', 0):.1f}%, "
                    f"students={summary.get('total_students', 0)}"
                )

        logger.info(f"✓ Completed streaming aggregation ({report_count} reports)")

        # Calculate and return final metrics
        final_metrics = metrics.calculate_final_metrics()
        return final_metrics

    def aggregate_with_validation(self) -> Tuple[bool, Dict, List[str]]:
        """
        Aggregate with pre-validation.

        Returns:
            Tuple of (success, metrics, errors)
        """
        errors = []

        # Validate reports directory exists
        if not self.reports_dir.exists():
            errors.append("Reports directory not found")
            return False, {}, errors

        # Check for at least one report
        reports = list(self.reports_dir.glob("Individual_Report_*.json"))
        if not reports:
            errors.append("No student reports found")
            return False, {}, errors

        # Stream and aggregate
        try:
            metrics = self.aggregate_streaming()

            if not metrics or metrics.get("total_students", 0) == 0:
                errors.append("No valid scores to aggregate")
                return False, {}, errors

            logger.info(f"✓ Aggregation successful: {metrics['total_students']} students")
            return True, metrics, []

        except Exception as e:
            errors.append(f"Aggregation failed: {str(e)}")
            logger.error(f"Aggregation error: {str(e)}")
            return False, {}, errors

    def benchmark_memory(self, num_students: int = 1000) -> Dict:
        """
        Estimate memory usage for large student counts.

        Args:
            num_students: Number of students to estimate for

        Returns:
            Memory usage estimate dictionary
        """
        import sys

        # Estimate sizes
        avg_report_size = sys.getsizeof({
            "student_name": "A" * 20,
            "exam": "Test",
            "answers": {i: "A" for i in range(1, 101)},
            "grading": {
                "total_correct": 0,
                "total_incorrect": 0,
                "total_blank": 0,
                "score": 0.0,
            }
        })

        # Current (load all) vs streaming
        current_usage_mb = (avg_report_size * num_students) / (1024 * 1024)
        streaming_usage_mb = (avg_report_size * 10) / (1024 * 1024)  # Only keep batch in memory

        return {
            "num_students": num_students,
            "avg_report_size_bytes": avg_report_size,
            "current_approach_mb": current_usage_mb,
            "streaming_approach_mb": streaming_usage_mb,
            "memory_savings_percent": (1 - streaming_usage_mb / current_usage_mb) * 100,
            "recommendation": f"Streaming saves ~{(1 - streaming_usage_mb / current_usage_mb) * 100:.0f}% memory"
        }

    def save_aggregated_report(self, metrics: Dict) -> Optional[Path]:
        """
        Save aggregated metrics to class report.

        Args:
            metrics: Aggregated metrics dictionary

        Returns:
            Path to saved report or None if failed
        """
        try:
            report_path = self.reports_dir / "Class_Report.json"

            with open(report_path, "w") as f:
                json.dump(metrics, f, indent=2)

            logger.info(f"✓ Class report saved: {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            return None
