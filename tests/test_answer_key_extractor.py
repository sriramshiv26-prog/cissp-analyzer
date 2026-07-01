import json
import pytest
from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor


class TestAnswerKeyExtractor:
    """Tests for PDF answer key extraction with answer text."""

    def test_extract_answers_with_full_text(self):
        """Test extraction includes both letter and answer text."""
        pdf_text = """
        Question 1: What encryption method uses symmetric keys?
        A) RSA
        B) AES
        C) ECC

        Answer Key:
        1: B - AES is a symmetric encryption algorithm
        2: A - Asymmetric encryption...
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)

        # Should return both letter and context text
        assert result["1"]["letter"] == "B"
        assert "AES" in result["1"]["text"]
        assert "symmetric" in result["1"]["text"]

    def test_extract_answers_letter_only_fallback(self):
        """Test extraction gracefully handles letter-only format."""
        pdf_text = """
        Answer Key:
        1: B
        2: A
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)

        assert result["1"]["letter"] == "B"
        assert result["1"]["text"] == ""  # No text provided

    def test_extract_answers_multiline_answer_text(self):
        """Test extraction handles multi-line answer explanations."""
        pdf_text = """
        Answers:
        1: C - The correct answer involves:
           - Understanding cryptography
           - Symmetric key exchange
           - AES-256 implementation
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)

        assert result["1"]["letter"] == "C"
        assert "cryptography" in result["1"]["text"]

    def test_extract_answers_complex_format(self):
        """Test extraction from exam with detailed answer explanations."""
        pdf_text = """
        Question 1: Which domain addresses access control?
        A) Asset Management
        B) Access Control and Identity Management
        C) Cryptography

        ANSWERS:
        1: B - Access Control and Identity Management (ACIM) deals with
           authentication, authorization, and accountability controls
           including role-based access, policies, and identity verification
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)

        assert result["1"]["letter"] == "B"
        assert "Access Control" in result["1"]["text"]
        assert "Identity Management" in result["1"]["text"]

    def test_validate_answer_format(self):
        """Test that answer letter is A-E."""
        extractor = AnswerKeyExtractor()
        assert extractor._is_valid_answer("A") is True
        assert extractor._is_valid_answer("E") is True
        assert extractor._is_valid_answer("F") is False

    def test_extract_from_file_not_found(self):
        """Test that missing file raises FileNotFoundError."""
        extractor = AnswerKeyExtractor()
        with pytest.raises(FileNotFoundError, match="PDF not found"):
            extractor.extract_from_file("/nonexistent/path.pdf")

    def test_save_empty_answers_raises_error(self):
        """Test that saving with no answers raises ValueError."""
        extractor = AnswerKeyExtractor()
        with pytest.raises(ValueError, match="No answers to save"):
            extractor.save_as_json("output.json")

    def test_get_answer_letters_only(self):
        """Test backward compatibility method returns letters only."""
        extractor = AnswerKeyExtractor()
        extractor.answers = {
            "1": {"letter": "A", "text": "explanation"},
            "2": {"letter": "B", "text": ""},
        }
        letters = extractor.get_answer_letters_only()

        assert letters == {"1": "A", "2": "B"}
        assert "text" not in str(letters)

    def test_save_as_json_creates_file(self, tmp_path):
        """Test that save_as_json creates JSON file with correct content."""
        extractor = AnswerKeyExtractor()
        extractor.answers = {"1": {"letter": "A", "text": "first answer"}}

        output_file = tmp_path / "answers.json"
        extractor.save_as_json(str(output_file), include_text=True)

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert data == {"1": {"letter": "A", "text": "first answer"}}
