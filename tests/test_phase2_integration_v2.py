#!/usr/bin/env python3
"""
Integration tests for Phase 2 v1.0 grading integration.
Tests: AnswerKeyManager, QuestionDatabase, ExamProcessor (updated), Phase2Integration
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cissp_analyzer.answer_key_manager import AnswerKeyManager
from cissp_analyzer.question_database import QuestionDatabase
from cissp_analyzer.exam_processor import ExamProcessor
from cissp_analyzer.phase2_integration import Phase2Integration
from cissp_analyzer.exam_folder_manager import ExamFolderManager


class TestAnswerKeyManager:
    """Test Answer Key Manager integration."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()
        self.manager = AnswerKeyManager(self.exam_folder)

    def test_load_from_json(self):
        """Test loading answer key from JSON file."""
        json_file = Path(self.temp_dir) / "answer_key.json"
        answer_data = {"1": "A", "2": "B", "3": "C", "4": "D"}

        with open(json_file, "w") as f:
            json.dump(answer_data, f)

        result = self.manager.load_from_json(str(json_file))
        assert len(result) == 4
        assert result[1] == "A"
        assert result[2] == "B"

    def test_load_from_json_with_q_prefix(self):
        """Test loading JSON with Q prefix."""
        json_file = Path(self.temp_dir) / "answer_key.json"
        answer_data = {"Q1": "A", "Q2": "B", "Q3": "C"}

        with open(json_file, "w") as f:
            json.dump(answer_data, f)

        result = self.manager.load_from_json(str(json_file))
        assert len(result) == 3
        assert result[1] == "A"

    def test_validate_against_questions(self):
        """Test answer key validation."""
        answer_key = {1: "A", 2: "B", 3: "C", 4: "D", 5: "A"}
        is_valid, errors = self.manager.validate_against_questions(answer_key, 5)
        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_answers(self):
        """Test validation with missing answers."""
        answer_key = {1: "A", 2: "B"}  # Only 2 out of 5
        is_valid, errors = self.manager.validate_against_questions(answer_key, 5)
        assert is_valid is False
        assert any("Missing" in str(e) for e in errors)

    def test_get_answer(self):
        """Test getting individual answer."""
        json_file = Path(self.temp_dir) / "answer_key.json"
        answer_data = {"1": "A", "2": "B", "3": "C"}

        with open(json_file, "w") as f:
            json.dump(answer_data, f)

        self.manager.load_from_json(str(json_file))
        assert self.manager.get_answer(1) == "A"
        assert self.manager.get_answer(2) == "B"
        assert self.manager.get_answer(999) is None


class TestQuestionDatabase:
    """Test Question Database integration."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()
        self.db = QuestionDatabase(self.exam_folder)

    def test_save_and_load_questions(self):
        """Test saving and loading questions."""
        questions = {
            1: {"text": "What is CISSP?", "A": "Answer A", "B": "Answer B"},
            2: {"text": "What is security?", "A": "Answer C", "B": "Answer D"},
        }

        self.db._save_questions(questions)
        loaded = self.db.load_questions()

        assert len(loaded) == 2
        assert loaded[1]["text"] == "What is CISSP?"
        assert loaded[2]["text"] == "What is security?"

    def test_get_question(self):
        """Test retrieving specific question."""
        questions = {
            1: {"text": "Q1 text", "A": "A1", "B": "B1"},
            2: {"text": "Q2 text", "A": "A2", "B": "B2"},
        }

        self.db._save_questions(questions)
        q = self.db.get_question(1)

        assert q is not None
        assert q["text"] == "Q1 text"

    def test_get_question_count(self):
        """Test question count."""
        questions = {i: {"text": f"Q{i}", "A": "A"} for i in range(1, 51)}
        self.db._save_questions(questions)

        assert self.db.get_question_count() == 50

    def test_validate_extraction(self):
        """Test validation of extracted questions."""
        questions = {
            1: {"question_text": "Q1", "A": "A1", "B": "B1", "C": "C1", "D": "D1"}
        }
        self.db._save_questions(questions)
        is_valid, errors = self.db.validate_extraction(total_expected=1)
        assert is_valid is True


class TestExamProcessorIntegration:
    """Test ExamProcessor with v1.0 grading integration."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()

        # Create exam metadata
        exam_manager = ExamFolderManager(self.temp_dir)
        self.metadata = {
            "exam_name": "Test CISSP",
            "pdf_path": str(self.exam_folder / "test.pdf"),
            "total_questions": 5,
        }

        metadata_file = self.exam_folder / ".exam_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(self.metadata, f)

    @patch("cissp_analyzer.exam_processor.PDFParser")
    def test_load_answer_key(self, mock_parser):
        """Test loading answer key in ExamProcessor."""
        processor = ExamProcessor(self.exam_folder)

        # Create answer key file
        json_file = self.exam_folder / "answer_key.json"
        answer_data = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A"}
        with open(json_file, "w") as f:
            json.dump(answer_data, f)

        # Load the answer key
        result = processor.load_answer_key(str(json_file))
        assert result is True
        assert processor.answer_key is not None
        assert len(processor.answer_key) == 5

    @patch("cissp_analyzer.exam_processor.PDFParser")
    def test_grade_answers(self, mock_parser):
        """Test grading answers."""
        # Setup mock for PDFParser to return questions
        mock_parser_instance = MagicMock()
        mock_parser_instance.extract_questions.return_value = [
            {"question_number": i, "text": f"Q{i}"} for i in range(1, 6)
        ]
        mock_parser.return_value = mock_parser_instance

        processor = ExamProcessor(self.exam_folder)
        processor.answer_key = {1: "A", 2: "B", 3: "C", 4: "D", 5: "A"}

        # Student answers - 3 correct, 1 incorrect, 1 blank
        student_answers = {1: "A", 2: "B", 3: "X", 4: "D"}  # 5th missing (blank)

        grading = processor._grade_answers(student_answers)

        assert grading["total_correct"] == 3
        assert grading["total_incorrect"] == 1
        assert grading["total_blank"] == 1
        assert grading["grading_available"] is True


class TestPhase2Integration:
    """Test complete Phase 2 Integration pipeline."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()

        # Create exam metadata
        self.metadata = {
            "exam_name": "Test CISSP",
            "pdf_path": str(self.exam_folder / "test.pdf"),
            "total_questions": 5,
        }

        metadata_file = self.exam_folder / ".exam_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(self.metadata, f)

        self.integration = Phase2Integration(self.exam_folder)

    def test_extract_and_save_questions(self):
        """Test question extraction step."""
        with patch.object(
            self.integration.question_db, "extract_from_pdf"
        ) as mock_extract:
            mock_extract.return_value = {
                1: {"text": "Q1"},
                2: {"text": "Q2"},
            }

            result = self.integration.extract_and_save_questions("test.pdf")

            assert result["status"] == "success"
            assert result["questions_extracted"] == 2

    def test_load_and_validate_answer_key(self):
        """Test answer key loading step."""
        json_file = self.temp_dir + "/answer_key.json"
        answer_data = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A"}
        with open(json_file, "w") as f:
            json.dump(answer_data, f)

        # Mock question database to return expected count
        with patch.object(
            self.integration.question_db, "get_question_count", return_value=5
        ):
            is_valid, result = self.integration.load_and_validate_answer_key(json_file)

            assert is_valid is True
            assert result["answer_keys_loaded"] == 5
            assert result["validation_passed"] is True

    def test_display_results(self):
        """Test results display formatting."""
        test_results = {
            "step_1_extract_questions": {
                "status": "success",
                "questions_extracted": 5,
            },
            "step_2_load_answer_key": {
                "answer_keys_loaded": 5,
                "validation_passed": True,
            },
            "step_3_process_students": {"processed": 10, "failed": 0, "skipped": 0},
            "step_4_class_report": {
                "metrics": {
                    "total_students": 10,
                    "average_score": 78.5,
                    "pass_rate": 80.0,
                    "grading_used": True,
                }
            },
        }

        output = self.integration.display_results(test_results)

        assert "PHASE 2 INTEGRATION RESULTS" in output
        assert "Step 1: Extract Questions" in output
        assert "Step 2: Load Answer Key" in output
        assert "v1.0 Grading Integration: ACTIVE" in output


class TestIntegrationEndToEnd:
    """End-to-end integration tests."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.exam_folder = Path(self.temp_dir) / "test_exam"
        self.exam_folder.mkdir()

        # Create exam metadata
        self.metadata = {
            "exam_name": "Test CISSP",
            "pdf_path": str(self.exam_folder / "test.pdf"),
            "total_questions": 5,
        }

        metadata_file = self.exam_folder / ".exam_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(self.metadata, f)

    @patch("cissp_analyzer.exam_processor.PDFParser")
    def test_answer_key_to_grading_flow(self, mock_parser):
        """Test flow from answer key to grading."""
        # Setup mock for PDFParser
        mock_parser_instance = MagicMock()
        mock_parser_instance.extract_questions.return_value = [
            {"question_number": i, "text": f"Q{i}"} for i in range(1, 6)
        ]
        mock_parser.return_value = mock_parser_instance

        # Create answer key
        json_file = self.temp_dir + "/answer_key.json"
        answer_data = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "A"}
        with open(json_file, "w") as f:
            json.dump(answer_data, f)

        # Load with AnswerKeyManager
        manager = AnswerKeyManager(self.exam_folder)
        answer_key = manager.load_from_json(json_file)

        # Use in ExamProcessor for grading
        processor = ExamProcessor(self.exam_folder)
        processor.answer_key = answer_key

        student_answers = {1: "A", 2: "B", 3: "C", 4: "D", 5: "B"}
        grading = processor._grade_answers(student_answers)

        # Should be 4 correct, 1 incorrect
        assert grading["total_correct"] == 4
        assert grading["total_incorrect"] == 1
        assert grading["score"] == 80.0  # 4/5 = 80%


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
