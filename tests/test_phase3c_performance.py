#!/usr/bin/env python3
"""
Phase 3C Tests - Performance & Concurrency
Tests streaming aggregation, file locking, and safe file operations.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cissp_analyzer.streaming_report_aggregator import StreamingReportAggregator, StreamingMetrics
from cissp_analyzer.safe_file_processor import SafeFileProcessor, FileLock


class TestStreamingMetrics:
    """Test streaming metrics accumulation."""

    def setup_method(self):
        """Setup test environment."""
        self.metrics = StreamingMetrics()

    def test_add_single_report(self):
        """Test adding a single report."""
        report = {
            "student_name": "Alice",
            "exam": "Test Exam",
            "total_questions": 10,
            "grading": {
                "total_correct": 8,
                "total_incorrect": 2,
                "total_blank": 0,
                "score": 80.0,
                "grading_available": True,
            }
        }

        self.metrics.add_report(report, grading_available=True)

        assert self.metrics.total_students == 1
        assert self.metrics.scores == [80.0]
        assert self.metrics.max_score == 80.0

    def test_add_multiple_reports(self):
        """Test adding multiple reports."""
        reports = [
            {
                "student_name": f"Student{i}",
                "exam": "Test",
                "total_questions": 10,
                "grading": {
                    "total_correct": i * 10,
                    "total_incorrect": (10 - i) * 10,
                    "total_blank": 0,
                    "score": float(i * 10),
                    "grading_available": True,
                }
            }
            for i in range(1, 6)
        ]

        for report in reports:
            self.metrics.add_report(report, grading_available=True)

        assert self.metrics.total_students == 5
        assert len(self.metrics.scores) == 5
        assert self.metrics.min_score == 10.0
        assert self.metrics.max_score == 50.0

    def test_calculate_final_metrics(self):
        """Test final metric calculation."""
        # Add 5 reports: 100, 90, 80, 70, 60
        for i, score in enumerate([100, 90, 80, 70, 60], 1):
            report = {
                "student_name": f"S{i}",
                "exam": "Test",
                "total_questions": 10,
                "grading": {
                    "score": float(score),
                    "grading_available": True,
                }
            }
            self.metrics.add_report(report, grading_available=True)

        metrics = self.metrics.calculate_final_metrics()

        assert metrics["total_students"] == 5
        assert metrics["average_score"] == 80.0
        assert metrics["min_score"] == 60.0
        assert metrics["max_score"] == 100.0
        assert metrics["passing_count"] == 3  # 100, 90, 80 >= 75 (70, 60 < 75)

    def test_get_summary(self):
        """Test summary generation (memory efficient)."""
        for i in range(1, 11):
            report = {
                "student_name": f"S{i}",
                "exam": "Test",
                "total_questions": 10,
                "grading": {
                    "score": 80.0,
                    "grading_available": True,
                }
            }
            self.metrics.add_report(report, grading_available=True)

        summary = self.metrics.get_summary()

        assert summary["total_students"] == 10
        assert summary["average_score"] == 80.0
        assert "student_metrics" not in summary  # Summary doesn't include full details


class TestStreamingReportAggregator:
    """Test streaming report aggregation."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()
        self.reports_dir = self.exam_folder / "reports"
        self.reports_dir.mkdir()

    def create_test_reports(self, count: int) -> None:
        """Create test report files."""
        for i in range(1, count + 1):
            report = {
                "student_name": f"Student{i}",
                "exam": "Test Exam",
                "total_questions": 10,
                "grading": {
                    "total_correct": 8 + (i % 3),
                    "total_incorrect": 2 - (i % 3),
                    "total_blank": 0,
                    "score": 80.0 + (i % 3) * 5,
                    "grading_available": True,
                }
            }

            report_file = self.reports_dir / f"Individual_Report_Student{i}.json"
            with open(report_file, "w") as f:
                json.dump(report, f)

    def test_stream_reports(self):
        """Test streaming reports."""
        self.create_test_reports(5)

        aggregator = StreamingReportAggregator(self.exam_folder)
        reports = list(aggregator.stream_reports())

        assert len(reports) == 5
        assert reports[0]["student_name"] == "Student1"

    def test_aggregate_streaming(self):
        """Test streaming aggregation."""
        self.create_test_reports(10)

        aggregator = StreamingReportAggregator(self.exam_folder)
        metrics = aggregator.aggregate_streaming()

        assert metrics["total_students"] == 10
        assert "average_score" in metrics
        assert "pass_rate" in metrics
        assert len(metrics["student_metrics"]) == 10

    def test_aggregate_with_validation(self):
        """Test aggregation with validation."""
        self.create_test_reports(5)

        aggregator = StreamingReportAggregator(self.exam_folder)
        success, metrics, errors = aggregator.aggregate_with_validation()

        assert success is True
        assert len(errors) == 0
        assert metrics["total_students"] == 5

    def test_aggregate_no_reports(self):
        """Test aggregation with no reports."""
        aggregator = StreamingReportAggregator(self.exam_folder)
        success, metrics, errors = aggregator.aggregate_with_validation()

        assert success is False
        assert len(errors) > 0

    def test_benchmark_memory(self):
        """Test memory usage benchmark."""
        aggregator = StreamingReportAggregator(self.exam_folder)
        bench = aggregator.benchmark_memory(num_students=1000)

        assert bench["num_students"] == 1000
        assert bench["current_approach_mb"] > 0
        assert bench["streaming_approach_mb"] > 0
        assert bench["streaming_approach_mb"] < bench["current_approach_mb"]
        assert "memory_savings_percent" in bench

    def test_save_aggregated_report(self):
        """Test saving aggregated report."""
        self.create_test_reports(3)

        aggregator = StreamingReportAggregator(self.exam_folder)
        metrics = aggregator.aggregate_streaming()
        report_path = aggregator.save_aggregated_report(metrics)

        assert report_path is not None
        assert report_path.exists()

        # Verify saved report
        with open(report_path) as f:
            saved = json.load(f)
            assert saved["total_students"] == 3


class TestSafeFileProcessor:
    """Test safe file operations with locking."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()
        self.processor = SafeFileProcessor(self.exam_folder)

    def test_initialization(self):
        """Test processor initialization."""
        assert self.processor.exam_folder == self.exam_folder
        assert self.processor.lock_dir.exists()

    def test_read_with_lock(self):
        """Test reading file with lock."""
        test_file = self.exam_folder / "test.json"
        test_data = {"key": "value", "number": 42}

        with open(test_file, "w") as f:
            json.dump(test_data, f)

        result = self.processor.read_with_lock(test_file)

        assert result is not None
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_write_atomic(self):
        """Test atomic file writing."""
        test_file = self.exam_folder / "atomic.json"
        test_data = {"status": "written", "timestamp": "2024-01-01"}

        success = self.processor.write_atomic(test_file, test_data)

        assert success is True
        assert test_file.exists()

        # Verify file contents
        with open(test_file) as f:
            saved = json.load(f)
            assert saved["status"] == "written"

    def test_safe_update(self):
        """Test safe read-modify-write."""
        test_file = self.exam_folder / "update.json"
        initial_data = {"count": 0}

        with open(test_file, "w") as f:
            json.dump(initial_data, f)

        def increment(data):
            data["count"] += 1
            return data

        success = self.processor.safe_update(test_file, increment)

        assert success is True

        # Verify update
        with open(test_file) as f:
            result = json.load(f)
            assert result["count"] == 1

    def test_cleanup_locks(self):
        """Test lock cleanup."""
        # Create a stale lock file
        lock_file = self.processor.lock_dir / "stale.lock"
        lock_file.write_text("")

        # Clean up (with max_age = 0 to clean immediately)
        count = self.processor.cleanup_locks(max_age_seconds=0)

        assert count >= 1
        assert not lock_file.exists()

    def test_get_lock_status(self):
        """Test lock status reporting."""
        status = self.processor.get_lock_status()

        assert "total_locks" in status
        assert "locks" in status
        assert isinstance(status["total_locks"], int)


class TestFileLock:
    """Test FileLock context manager."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.lock_path = Path(self.temp_dir) / "test.lock"

    def test_acquire_and_release(self):
        """Test lock acquisition and release."""
        with FileLock(self.lock_path, timeout=5):
            assert self.lock_path.exists()

        # Lock should be released (file may still exist but is unlocked)

    def test_nested_locks_timeout(self):
        """Test that nested locks timeout properly."""
        # This test verifies timeout behavior with nested locks
        # (actual nested locking would need threading)
        with FileLock(self.lock_path, timeout=5):
            # Try to acquire same lock with short timeout
            try:
                with FileLock(self.lock_path, timeout=1):
                    pass  # Would block but timeout
            except TimeoutError:
                pass  # Expected


class TestPerformanceIntegration:
    """Integration tests for Phase 3C."""

    def test_large_student_batch(self):
        """Test handling 100+ students."""
        with tempfile.TemporaryDirectory() as temp_dir:
            exam_folder = Path(temp_dir) / "large_exam"
            exam_folder.mkdir()
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create 100 test reports
            for i in range(1, 101):
                report = {
                    "student_name": f"Student{i:03d}",
                    "exam": "Large Test",
                    "total_questions": 100,
                    "grading": {
                        "total_correct": 70 + (i % 30),
                        "total_incorrect": 30 - (i % 30),
                        "total_blank": 0,
                        "score": 70.0 + (i % 30),
                        "grading_available": True,
                    }
                }

                report_file = reports_dir / f"Individual_Report_Student{i:03d}.json"
                with open(report_file, "w") as f:
                    json.dump(report, f)

            # Aggregate streaming
            aggregator = StreamingReportAggregator(exam_folder)
            metrics = aggregator.aggregate_streaming(batch_size=25)

            assert metrics["total_students"] == 100
            assert 70 <= metrics["average_score"] <= 100
            assert len(metrics["student_metrics"]) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
