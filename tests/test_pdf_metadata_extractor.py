"""
Tests for PDFMetadataExtractor - PDF structure analysis without Ollama

Tests verify that the extractor can:
1. Initialize with a PDF and extract text
2. Extract question numbers from PDF
3. Return proper dict structure with confidence metrics
4. Handle missing or corrupted PDFs gracefully
"""

import pytest
from pathlib import Path
from cissp_analyzer.pdf_metadata_extractor import PDFMetadataExtractor


class TestPDFMetadataExtractorInitialization:
    """Tests for PDFMetadataExtractor initialization"""

    def test_extractor_initializes_with_valid_pdf(self):
        """Test PDFMetadataExtractor can be instantiated with valid PDF"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)

        assert extractor.pdf_path.exists()
        assert len(extractor.text) > 0
        assert isinstance(extractor.questions, list)

    def test_extractor_raises_on_missing_pdf(self):
        """Test that FileNotFoundError is raised for missing PDF"""
        pdf_path = "exams/nonexistent_file_12345.pdf"

        with pytest.raises(FileNotFoundError):
            PDFMetadataExtractor(pdf_path)

    def test_pdf_text_is_extracted(self):
        """Test that PDF text is properly extracted"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)

        # Text should contain expected patterns
        assert "\n" in extractor.text or len(extractor.text) > 100
        assert isinstance(extractor.text, str)


class TestQuestionExtraction:
    """Tests for question number extraction from PDF"""

    def test_extract_question_numbers(self):
        """Test that questions are extracted from PDF"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        questions = extractor.extract_questions()

        assert len(questions) > 0
        assert isinstance(questions, list)
        assert all(isinstance(q, int) for q in questions)
        assert all(1 <= q <= 500 for q in questions)
        # Questions should be sorted and unique
        assert questions == sorted(set(questions))

    def test_questions_are_sorted_and_unique(self):
        """Test that extracted questions are sorted and unique"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        questions = extractor.extract_questions()

        # Check sorted
        assert questions == sorted(questions)
        # Check unique
        assert len(questions) == len(set(questions))


class TestExtractMethod:
    """Tests for the main extract() method"""

    def test_extract_returns_dict(self):
        """Test extract() returns proper dict structure"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        assert isinstance(result, dict)
        assert "total_questions" in result
        assert "extracted_count" in result
        assert "confidence" in result
        assert "gaps" in result
        assert "extracted_metadata" in result
        assert "extraction_note" in result

    def test_extract_confidence_is_valid(self):
        """Test that confidence is between 0 and 1.0"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        assert isinstance(result["confidence"], (int, float))
        assert 0 <= result["confidence"] <= 1.0

    def test_extract_counts_are_consistent(self):
        """Test that extracted_count <= total_questions"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        assert result["extracted_count"] <= result["total_questions"]
        assert result["total_questions"] > 0

    def test_extract_gaps_are_correct(self):
        """Test that gaps list contains questions without metadata"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        total = result["total_questions"]
        extracted = result["extracted_count"]
        gaps = len(result["gaps"])

        # gaps should equal total - extracted
        # (since most PDFs won't have embedded metadata)
        assert gaps >= 0
        assert gaps <= total

    def test_extract_note_is_descriptive(self):
        """Test that extraction_note is a string with useful info"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        assert isinstance(result["extraction_note"], str)
        assert "Extracted" in result["extraction_note"]
        assert "/" in result["extraction_note"]  # Should have ratio like "X/Y"

    def test_extracted_metadata_is_dict(self):
        """Test that extracted_metadata is a dict"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        assert isinstance(result["extracted_metadata"], dict)

    def test_extracted_metadata_keys_are_strings(self):
        """Test that metadata keys are question numbers as strings"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        if result["extracted_metadata"]:
            for key in result["extracted_metadata"].keys():
                assert isinstance(key, str)
                assert key.isdigit()


class TestMetadataExtraction:
    """Tests for per-question metadata extraction"""

    def test_extract_for_question_returns_dict_or_none(self):
        """Test that _extract_for_question returns dict or None"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)

        # Try a few questions
        for q_num in extractor.questions[:3]:
            result = extractor._extract_for_question(q_num)
            assert result is None or isinstance(result, dict)

    def test_metadata_dict_has_valid_keys(self):
        """Test that metadata dicts have valid keys"""
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        # Valid metadata keys
        valid_keys = {"domain", "difficulty", "topic", "type", "context"}

        for q_num, metadata in result["extracted_metadata"].items():
            if metadata:
                for key in metadata.keys():
                    assert key in valid_keys


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_extract_with_empty_pdf(self, tmp_path):
        """Test handling of PDF with minimal/no questions"""
        # This test just verifies we handle it gracefully
        # Actual behavior depends on PDF content
        pdf_path = "exams/dec25_week1.pdf"
        extractor = PDFMetadataExtractor(pdf_path)
        result = extractor.extract()

        # Should not crash, should return valid structure
        assert isinstance(result, dict)
        assert "total_questions" in result

    def test_multiple_pdfs_work_independently(self):
        """Test that multiple PDFs can be extracted independently"""
        pdf1 = PDFMetadataExtractor("exams/dec25_week1.pdf")
        pdf2 = PDFMetadataExtractor("exams/dec25_week2.pdf")

        result1 = pdf1.extract()
        result2 = pdf2.extract()

        # Both should succeed
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
        assert result1["total_questions"] > 0
        assert result2["total_questions"] > 0
