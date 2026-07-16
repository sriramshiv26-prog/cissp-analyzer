#!/usr/bin/env python3
"""
Phase 2 Integration Tests - End-to-end workflow testing.
Tests all Phase 2 components working together.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import Phase 2 components
from cissp_analyzer.exam_folder_manager import ExamFolderManager
from cissp_analyzer.state_tracker import ProcessedFileTracker
from cissp_analyzer.menu_controller import MenuController
from cissp_analyzer.pdf_upload_handler import PDFUploadHandler
from cissp_analyzer.exam_processor import ExamProcessor
from cissp_analyzer.class_report_aggregator import ClassReportAggregator
from cissp_analyzer.processing_validator import ProcessingValidator


class TestExamFolderManager:
    """Test exam folder management."""

    def test_create_and_list_exams(self):
        """Test creating and listing exam folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExamFolderManager(tmpdir)

            # Create mock PDF
            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n")

            # Create exam folder
            with patch.object(
                manager, "_extract_total_questions_from_pdf", return_value=100
            ):
                folder = manager.create_exam_folder("Test Exam", str(pdf_path))

            assert folder.exists()
            assert (folder / "exam.pdf").exists()
            assert (folder / ".exam_metadata.json").exists()

            # List exams
            exams = manager.list_exams()
            assert len(exams) == 1
            assert exams[0]["exam_name"] == "Test Exam"

    def test_folder_structure_validation(self):
        """Test exam folder structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExamFolderManager(tmpdir)

            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n")

            with patch.object(
                manager, "_extract_total_questions_from_pdf", return_value=50
            ):
                folder = manager.create_exam_folder("Structured Exam", str(pdf_path))

            # Verify metadata structure
            metadata = manager.get_exam_metadata(folder.name)
            assert "exam_name" in metadata
            assert "pdf_path" in metadata
            assert "created_date" in metadata
            assert "total_questions" in metadata

    def test_get_new_answer_files(self):
        """Test retrieving answer files from exam folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExamFolderManager(tmpdir)

            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n")

            with patch.object(
                manager, "_extract_total_questions_from_pdf", return_value=50
            ):
                folder = manager.create_exam_folder("File Test", str(pdf_path))

            # Create mock answer files
            (folder / "Alice.xlsx").touch()
            (folder / "Bob.xlsx").touch()
            (folder / "~temp.xlsx").touch()  # Should be skipped

            files = manager.get_new_answer_files(folder.name)
            assert len(files) == 2
            assert "Alice.xlsx" in files
            assert "Bob.xlsx" in files
            assert "~temp.xlsx" not in files


class TestStateTracker:
    """Test state tracking for processed files."""

    def test_mark_and_track_processed_files(self):
        """Test marking files as processed and retrieving history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)
            tracker = ProcessedFileTracker(exam_folder)

            # Mark files as processed
            tracker.mark_processed("Alice.xlsx", "reports/Alice_report.json")
            tracker.mark_processed("Bob.xlsx", "reports/Bob_report.json")

            # Verify tracked
            assert tracker.is_processed("Alice.xlsx")
            assert tracker.is_processed("Bob.xlsx")
            assert not tracker.is_processed("Charlie.xlsx")

    def test_detect_unprocessed_files(self):
        """Test detecting unprocessed files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)
            tracker = ProcessedFileTracker(exam_folder)

            # Mark some files as processed
            tracker.mark_processed("Alice.xlsx", "reports/Alice.json")

            # Get unprocessed from larger list
            all_files = ["Alice.xlsx", "Bob.xlsx", "Charlie.xlsx"]
            unprocessed = tracker.get_unprocessed_files(all_files)

            assert len(unprocessed) == 2
            assert "Bob.xlsx" in unprocessed
            assert "Charlie.xlsx" in unprocessed
            assert "Alice.xlsx" not in unprocessed

    def test_processing_history(self):
        """Test retrieving processing history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)
            tracker = ProcessedFileTracker(exam_folder)

            tracker.mark_processed("File1.xlsx", "reports/File1.json")
            tracker.mark_processed("File2.xlsx", "reports/File2.json")

            history = tracker.get_processing_history()
            assert len(history) == 2
            assert all("filename" in record for record in history)
            assert all("report_path" in record for record in history)
            assert all("processed_date" in record for record in history)


class TestPDFUploadHandler:
    """Test PDF upload and validation."""

    def test_validate_pdf_file(self):
        """Test PDF file validation."""
        handler = PDFUploadHandler()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create valid PDF
            pdf_path = Path(tmpdir) / "valid.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n")

            # Mock pypdf.PdfReader to accept minimal PDF
            with patch("pypdf.PdfReader") as mock_reader:
                mock_instance = MagicMock()
                mock_instance.pages = [MagicMock()]  # At least one page
                mock_reader.return_value = mock_instance

                # Should validate successfully
                assert handler.validate_pdf(str(pdf_path))

    def test_validate_pdf_not_found(self):
        """Test validation fails for missing PDF."""
        handler = PDFUploadHandler()
        assert not handler.validate_pdf("/nonexistent/file.pdf")

    def test_validate_wrong_file_type(self):
        """Test validation fails for non-PDF files."""
        handler = PDFUploadHandler()

        with tempfile.TemporaryDirectory() as tmpdir:
            txt_path = Path(tmpdir) / "test.txt"
            txt_path.write_text("Not a PDF")
            assert not handler.validate_pdf(str(txt_path))

    @patch("cissp_analyzer.pdf_upload_handler.PDFUploadHandler.prompt_exam_metadata")
    def test_metadata_collection(self, mock_prompt):
        """Test exam metadata collection."""
        handler = PDFUploadHandler()
        mock_prompt.return_value = {
            "exam_name": "CISSP_June_2026",
            "description": "Practice exam",
        }

        metadata = handler.prompt_exam_metadata()
        assert metadata["exam_name"] == "CISSP_June_2026"
        assert metadata["description"] == "Practice exam"


class TestProcessingValidator:
    """Test data validation."""

    def test_validate_answer_sheet(self):
        """Test answer sheet validation."""
        validator = ProcessingValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            import pandas as pd

            # Create valid answer sheet
            df = pd.DataFrame({"Question": [1, 2, 3], "Answer": ["A", "B", "C"]})
            excel_path = Path(tmpdir) / "answers.xlsx"
            df.to_excel(excel_path, index=False)

            is_valid, msg = validator.validate_answer_sheet(str(excel_path))
            assert is_valid

    def test_validate_answer_format(self):
        """Test answer format validation."""
        validator = ProcessingValidator()

        answers = {1: "A", 2: "B", 3: "C"}
        questions = [{"number": 1}, {"number": 2}, {"number": 3}]

        is_valid, mismatches = validator.validate_question_match(answers, questions)
        assert is_valid
        assert len(mismatches) == 0

    def test_detect_duplicate_names(self):
        """Test duplicate name detection."""
        validator = ProcessingValidator()

        names = ["Alice", "Bob", "alice", "Charlie", "Bob"]
        duplicates = validator.check_duplicate_student_names(names)

        assert len(duplicates) > 0
        assert "alice" in duplicates or "Alice" in duplicates

    def test_validate_folder_structure(self):
        """Test folder structure validation."""
        validator = ProcessingValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)

            # Create required files
            (exam_folder / "exam.pdf").write_bytes(b"%PDF-1.4\n")
            metadata = {"exam_name": "Test", "created_date": "2026-07-15"}
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))

            is_valid, msg = validator.validate_folder_structure(exam_folder)
            assert is_valid

    def test_validate_pdf(self):
        """Test PDF validation."""
        validator = ProcessingValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "test.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n")

            # Mock pypdf.PdfReader to accept minimal PDF
            with patch("pypdf.PdfReader") as mock_reader:
                mock_instance = MagicMock()
                mock_instance.pages = [MagicMock()]  # At least one page
                mock_reader.return_value = mock_instance

                is_valid, msg = validator.validate_pdf(str(pdf_path))
                assert is_valid


class TestExamProcessor:
    """Test exam processing workflow."""

    def test_detect_new_files(self):
        """Test detection of new answer files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)

            # Create exam structure
            (exam_folder / "exam.pdf").write_bytes(b"%PDF-1.4\n")
            metadata = {
                "exam_name": "Test Exam",
                "pdf_path": str(exam_folder / "exam.pdf"),
                "created_date": "2026-07-15",
            }
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))
            (exam_folder / "reports").mkdir()

            # Create answer files
            (exam_folder / "Alice.xlsx").touch()
            (exam_folder / "Bob.xlsx").touch()

            with patch.object(ExamProcessor, "_load_questions", return_value=[]):
                processor = ExamProcessor(exam_folder)
                new_files = processor.detect_new_answer_files()

                # All files are new (not processed yet)
                assert len(new_files) >= 2

    def test_skip_already_processed(self):
        """Test skipping already processed files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)

            # Create exam structure
            (exam_folder / "exam.pdf").write_bytes(b"%PDF-1.4\n")
            metadata = {
                "exam_name": "Test",
                "pdf_path": str(exam_folder / "exam.pdf"),
                "created_date": "2026-07-15",
            }
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))
            (exam_folder / "reports").mkdir()

            # Mark file as processed
            tracker = ProcessedFileTracker(exam_folder)
            tracker.mark_processed("Alice.xlsx", "reports/Alice.json")

            with patch.object(ExamProcessor, "_load_questions", return_value=[]):
                processor = ExamProcessor(exam_folder)
                skipped = processor.skip_already_processed()

                assert "Alice.xlsx" in skipped


class TestClassReportAggregator:
    """Test class-level report generation."""

    def test_load_student_reports(self):
        """Test loading individual student reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create sample reports
            for i, name in enumerate(["Alice", "Bob", "Charlie"], 1):
                report = {
                    "student_name": name,
                    "exam": "Test Exam",
                    "total_questions": 100,
                    "answers_provided": 95,
                    "answers": {j: "A" for j in range(1, 96)},
                }
                report_path = reports_dir / f"Individual_Report_{name}.json"
                report_path.write_text(json.dumps(report))

            metadata = {"exam_name": "Test Exam", "created_date": "2026-07-15"}
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))

            aggregator = ClassReportAggregator(exam_folder)
            reports = aggregator.get_all_student_reports()

            assert len(reports) == 3
            assert all(
                r.get("student_name") in ["Alice", "Bob", "Charlie"] for r in reports
            )

    def test_generate_class_metrics(self):
        """Test generating class metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create reports with varying scores
            for i, (name, correct) in enumerate(
                [("Alice", 95), ("Bob", 75), ("Charlie", 60)], 1
            ):
                report = {
                    "student_name": name,
                    "exam": "Test",
                    "total_questions": 100,
                    "answers_provided": correct,
                    "answers": {j: "A" for j in range(1, correct + 1)},
                }
                report_path = reports_dir / f"Individual_Report_{name}.json"
                report_path.write_text(json.dumps(report))

            metadata = {"exam_name": "Test Exam", "created_date": "2026-07-15"}
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))

            aggregator = ClassReportAggregator(exam_folder)
            metrics = aggregator.generate_class_metrics()

            assert metrics["total_students"] == 3
            assert 60 <= metrics["average_score"] <= 95
            assert metrics["min_score"] == 60
            assert metrics["max_score"] == 95
            assert metrics["pass_rate"] >= 0

    def test_validate_before_aggregation(self):
        """Test validation before report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create sample reports
            for name in ["Alice", "Bob"]:
                report = {
                    "student_name": name,
                    "exam": "Test",
                    "total_questions": 100,
                    "answers_provided": 95,
                    "answers": {},
                }
                report_path = reports_dir / f"Individual_Report_{name}.json"
                report_path.write_text(json.dumps(report))

            metadata = {"exam_name": "Test", "created_date": "2026-07-15"}
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))

            aggregator = ClassReportAggregator(exam_folder)
            is_valid, msg = aggregator.validate_before_aggregation()

            assert is_valid


class TestMenuController:
    """Test menu interaction."""

    def test_show_main_menu(self):
        """Test main menu display."""
        menu = MenuController()
        exams = [
            {
                "exam_name": "CISSP June 2026",
                "created_date": "2026-06-15",
                "folder_id": "cissp_20260615",
            }
        ]

        output = menu.show_main_menu(exams)
        assert "CISSP ANALYZER" in output
        assert "CISSP June 2026" in output
        assert "Upload NEW questionnaire" in output

    def test_show_success_message(self):
        """Test success message display."""
        menu = MenuController()
        # Should not raise exception
        menu.show_success_message("Test successful!")

    def test_show_error_message(self):
        """Test error message display."""
        menu = MenuController()
        # Should not raise exception
        menu.show_error_message("Test error")

    def test_show_warning_message(self):
        """Test warning message display."""
        menu = MenuController()
        # Should not raise exception
        menu.show_warning_message("Test warning")

    def test_show_info_message(self):
        """Test info message display."""
        menu = MenuController()
        # Should not raise exception
        menu.show_info_message("Test info")


class TestEndToEndWorkflow:
    """End-to-end workflow integration tests."""

    def test_complete_exam_workflow(self):
        """Test complete workflow: upload → process → report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            exam_folder = Path(tmpdir)
            reports_dir = exam_folder / "reports"
            reports_dir.mkdir()

            # Create exam metadata
            (exam_folder / "exam.pdf").write_bytes(b"%PDF-1.4\n")
            metadata = {
                "exam_name": "Test Exam",
                "pdf_path": str(exam_folder / "exam.pdf"),
                "created_date": "2026-07-15",
                "total_questions": 100,
            }
            (exam_folder / ".exam_metadata.json").write_text(json.dumps(metadata))

            # Create answer files
            import pandas as pd

            for name in ["Alice", "Bob", "Charlie"]:
                df = pd.DataFrame({"Question": range(1, 101), "Answer": ["A"] * 100})
                df.to_excel(exam_folder / f"{name}.xlsx", index=False)

            # Create reports (simulating processing)
            for name in ["Alice", "Bob", "Charlie"]:
                report = {
                    "student_name": name,
                    "exam": "Test Exam",
                    "total_questions": 100,
                    "answers_provided": 100,
                    "answers": {i: "A" for i in range(1, 101)},
                }
                (reports_dir / f"Individual_Report_{name}.json").write_text(
                    json.dumps(report)
                )

            # Test aggregation
            aggregator = ClassReportAggregator(exam_folder)
            is_valid, _ = aggregator.validate_before_aggregation()
            assert is_valid

            metrics = aggregator.generate_class_metrics()
            assert metrics["total_students"] == 3
            assert metrics["average_score"] == 100

            preview = aggregator.show_preview(metrics)
            assert "Student" in preview or "student" in preview.lower()

    def test_error_handling_missing_files(self):
        """Test error handling when required files are missing."""
        validator = ProcessingValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            exam_folder = Path(tmpdir)

            # Empty folder - missing required files
            is_valid, msg = validator.validate_folder_structure(exam_folder)
            assert not is_valid
            assert "metadata" in msg.lower() or "pdf" in msg.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
