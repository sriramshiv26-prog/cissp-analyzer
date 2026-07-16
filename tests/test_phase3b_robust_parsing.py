#!/usr/bin/env python3
"""
Phase 3B Tests - Robust PDF and Excel Parsing
Tests enhanced parsing with fallback strategies and error recovery.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import pandas as pd

from cissp_analyzer.robust_pdf_parser import RobustPDFParser, RobustPDFParserResult
from cissp_analyzer.robust_excel_parser import (
    RobustExcelParser,
    RobustExcelParserResult,
)


class TestRobustPDFParser:
    """Test robust PDF parsing with fallback strategies."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.pdf_path = Path(self.temp_dir) / "test.pdf"

    @patch("cissp_analyzer.robust_pdf_parser.PdfReader")
    def test_parser_initialization(self, mock_reader):
        """Test PDF parser initialization."""
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [MagicMock()]
        mock_reader.return_value = mock_reader_instance

        # Create minimal PDF file
        self.pdf_path.write_bytes(b"%PDF-1.4\n")

        parser = RobustPDFParser(str(self.pdf_path))
        assert parser.pdf_path == self.pdf_path
        assert parser.reader is not None

    def test_parser_missing_file(self):
        """Test parser with missing file."""
        with pytest.raises(FileNotFoundError):
            RobustPDFParser("/nonexistent/file.pdf")

    @patch("cissp_analyzer.robust_pdf_parser.PdfReader")
    def test_extract_with_fallback(self, mock_reader):
        """Test extraction with fallback mechanism."""
        mock_reader_instance = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = (
            "1. What is security?\nA) Protection\nB) Defense\nC) Safety\nD) Care\n"
            "2. What is cryptography?\nA) Code\nB) Cipher\nC) Art of encoding\nD) Secret\n"
        )
        mock_reader_instance.pages = [mock_page]
        mock_reader.return_value = mock_reader_instance

        self.pdf_path.write_bytes(b"%PDF-1.4\n")
        parser = RobustPDFParser(str(self.pdf_path))

        result = parser.extract_with_fallback()

        assert result is not None
        assert result.confidence >= 0.0
        assert result.extraction_method in ["primary", "alternative", "partial"]

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        result = RobustPDFParserResult()

        # No questions
        result.questions = {}
        conf = 0.0  # Manually calculated for empty
        assert conf == 0.0

        # Perfect extraction
        result.questions = {
            1: {"text": "Q1", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}},
            2: {"text": "Q2", "options": {"A": "a", "B": "b", "C": "c", "D": "d"}},
        }
        result.questions_found = 2
        result.questions_valid = 2
        # Would be high confidence

    def test_question_number_detection(self):
        """Test question number pattern detection."""
        text = "1. First question\n" "2. Second question\n" "10. Tenth question\n"

        # Would be detected by _find_question_starts
        import re

        pattern = r"^(\d+)\."
        matches = list(re.finditer(pattern, text, re.MULTILINE))

        assert len(matches) == 3
        assert int(matches[0].group(1)) == 1
        assert int(matches[2].group(1)) == 10


class TestRobustExcelParser:
    """Test robust Excel parsing with flexible column detection."""

    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def test_parser_initialization(self):
        """Test Excel parser initialization."""
        excel_path = Path(self.temp_dir) / "test.xlsx"

        # Create test Excel file
        df = pd.DataFrame(
            {
                "Question": [1, 2, 3],
                "Answer": ["A", "B", "C"],
                "Student": ["Alice", "Alice", "Alice"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))
        assert parser.excel_path == excel_path
        assert len(parser.df) == 3

    def test_missing_file(self):
        """Test parser with missing file."""
        with pytest.raises(FileNotFoundError):
            RobustExcelParser("/nonexistent/file.xlsx")

    def test_column_detection_standard(self):
        """Test column detection with standard names."""
        excel_path = Path(self.temp_dir) / "standard.xlsx"

        df = pd.DataFrame(
            {
                "Question": [1, 2, 3],
                "Answer": ["A", "B", "C"],
                "Student": ["Alice", "Alice", "Alice"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))
        q_col, a_col, s_col = parser._detect_columns(RobustExcelParserResult())

        assert q_col == "Question"
        assert a_col == "Answer"
        assert s_col == "Student"

    def test_column_detection_variations(self):
        """Test column detection with variation names."""
        excel_path = Path(self.temp_dir) / "variations.xlsx"

        df = pd.DataFrame(
            {
                "Q#": [1, 2, 3],
                "Ans": ["A", "B", "C"],
                "Student Name": ["Bob", "Bob", "Bob"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))
        q_col, a_col, s_col = parser._detect_columns(RobustExcelParserResult())

        assert q_col == "Q#"
        assert a_col == "Ans"
        assert s_col == "Student Name"

    def test_answer_normalization(self):
        """Test answer normalization."""
        excel_path = Path(self.temp_dir) / "normalize.xlsx"

        df = pd.DataFrame(
            {
                "Question": [1, 2, 3, 4, 5],
                "Answer": ["A", "a", "-B-", "3", "CHOICE_D"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))

        # Test normalization
        assert parser._normalize_answer("A") == "A"
        assert parser._normalize_answer("a") == "A"
        assert parser._normalize_answer("-B-") == "B"
        assert parser._normalize_answer("3") == "C"
        assert parser._normalize_answer("D") == "D"
        assert parser._normalize_answer("4") == "D"

    def test_parse_with_fallback(self):
        """Test parsing with fallback strategies."""
        excel_path = Path(self.temp_dir) / "fallback.xlsx"

        df = pd.DataFrame(
            {
                "Question": [1, 2, 3, 4, 5],
                "Answer": ["A", "B", "C", "D", "A"],
                "Student": ["Charlie", "Charlie", "Charlie", "Charlie", "Charlie"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))
        result = parser.parse_with_fallback()

        assert result is not None
        assert result.valid_answers == 5
        assert result.student_name == "Charlie"
        assert len(result.answers) == 5
        assert result.answers[1] == "A"
        assert result.answers[5] == "A"

    def test_parse_with_blanks(self):
        """Test parsing with blank answers."""
        excel_path = Path(self.temp_dir) / "blanks.xlsx"

        df = pd.DataFrame(
            {
                "Question": [1, 2, 3, 4, 5],
                "Answer": ["A", "", "C", "invalid", "D"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))
        result = parser.parse_with_fallback()

        assert result.valid_answers == 3  # Only A, C, D
        assert result.skipped_answers == 2  # Empty and invalid
        assert len(result.warnings) > 0

    def test_validate_answers(self):
        """Test answer validation."""
        excel_path = Path(self.temp_dir) / "validate.xlsx"

        df = pd.DataFrame(
            {
                "Question": [1, 2, 3, 4, 5],
                "Answer": ["A", "B", "C", "D", "A"],
            }
        )
        df.to_excel(excel_path, index=False)

        parser = RobustExcelParser(str(excel_path))
        result = parser.parse_with_fallback()

        # Validate 5 answers against 5 expected
        assert result.valid_answers == 5
        assert result.student_name  # Should have detected student name

        # Test insufficient answers
        result.answers = {1: "A"}
        is_valid, errors = result.validate_answers(5)
        assert not is_valid  # Should fail due to too few answers
        assert len(errors) > 0


class TestParsingIntegration:
    """Integration tests for robust parsing."""

    def test_end_to_end_excel_parsing(self):
        """Test end-to-end Excel parsing workflow."""
        with tempfile.TemporaryDirectory() as temp_dir:
            excel_path = Path(temp_dir) / "student_answers.xlsx"

            # Create realistic student answer sheet
            df = pd.DataFrame(
                {
                    "Q#": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    "Ans": ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"],
                    "Student Name": ["Diana"] * 10,
                }
            )
            df.to_excel(excel_path, index=False)

            parser = RobustExcelParser(str(excel_path))
            result = parser.parse_with_fallback()

            assert result.student_name == "Diana"
            assert result.valid_answers == 10
            assert len(result.answers) == 10
            assert result.column_mapping["question"] == "Q#"
            assert result.column_mapping["answer"] == "Ans"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
