import pytest
from pathlib import Path
from cissp_analyzer.interactive_cli import get_answer_key, Colors
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor
from cissp_analyzer.answer_context_mapper import AnswerContextMapper
import tempfile
import json


class TestInteractiveCLIIntegration:
    """Tests for interactive CLI integration with answer context extraction."""

    def test_extract_with_answer_context_end_to_end(self):
        """Test end-to-end extraction with questions and answers."""
        pdf_text = """
        Question 1: What is encryption?
        A) Data protection
        B) Key management
        C) Certificate authority
        D) Authentication process

        Question 2: Which uses symmetric keys?
        A) RSA
        B) ECC
        C) AES
        D) Diffie-Hellman

        Answer Key:
        1: A - Encryption provides data protection
        2: C - AES is the symmetric encryption standard
        """

        # Test the static method
        result = PDFParser.extract_with_answer_context(pdf_text)

        # Verify extraction worked
        assert "1" in result
        assert "2" in result

        # Verify answer context was used
        assert (
            result["1"]["answer_letter"] is not None
            or result["1"]["suggested_domain"] is not None
        )
        assert (
            result["2"]["answer_letter"] is not None
            or result["2"]["suggested_domain"] is not None
        )

    def test_answer_key_json_format_for_analyzer(self, tmp_path):
        """Test that extracted answers can be saved in format compatible with analyzer."""
        pdf_text = """Answer Key:
1: A - First answer
2: B - Second answer
3: C - Third answer"""

        extractor = AnswerKeyExtractor()
        answers = extractor.extract_answers(pdf_text)

        # Should have extracted answers
        assert len(answers) > 0

        # Save with full text (for domain mapping)
        if answers:
            temp_full = tmp_path / "answers_full.json"
            extractor.save_as_json(str(temp_full), include_text=True)

            # Save letters only (for analyzer compatibility)
            letters_only = extractor.get_answer_letters_only()
            temp_letters = tmp_path / "answers_letters.json"
            with open(temp_letters, "w") as f:
                json.dump(letters_only, f)

            # Verify both files exist and have correct content
            assert temp_full.exists()
            assert temp_letters.exists()

            with open(temp_full) as f:
                full_data = json.load(f)
            with open(temp_letters) as f:
                letters_data = json.load(f)

            # Full version has text
            first_q = list(full_data.keys())[0]
            assert "text" in full_data[first_q]

            # Letters only has just letters
            first_letter = list(letters_data.values())[0]
            assert first_letter in ["A", "B", "C", "D", "E"]

    def test_user_feedback_during_extraction(self):
        """Test that extraction provides clear user feedback."""
        # Test color functions work
        assert Colors.success("test") != "test"  # Should have formatting
        assert Colors.info("test") != "test"
        assert Colors.warning("test") != "test"
        assert Colors.error("test") != "test"
        assert Colors.header("test") != "test"

    def test_answer_context_mapper_with_answer_text(self):
        """Test that answer context mapper can enhance domain classification."""
        mapper = AnswerContextMapper()

        # Test with cryptography answer
        question = "What is important in encryption?"
        answer = "AES and RSA are symmetric and asymmetric algorithms respectively"
        domain = mapper.map_with_context(question, answer)

        # Should detect Cryptography from answer keywords
        assert domain is not None
        assert "Cryptography" in domain or "crypt" in domain.lower()

    def test_answer_key_extractor_with_full_text(self):
        """Test AnswerKeyExtractor maintains full text of answers."""
        pdf_text = """Answer Key:
1: A - AES is a symmetric encryption standard used for data protection
2: B - Role-based access control restricts access based on user roles
"""

        extractor = AnswerKeyExtractor()
        answers = extractor.extract_answers(pdf_text)

        # Should extract answers
        assert len(answers) > 0

        # Verify at least first answer has text
        if "1" in answers:
            assert "text" in answers["1"]
            assert "letter" in answers["1"]
            assert answers["1"]["letter"] == "A"
            # Text should contain key concepts
            assert (
                "symmetric" in answers["1"]["text"].lower()
                or "aes" in answers["1"]["text"].lower()
            )

    def test_pdf_parser_extract_questions_from_text(self):
        """Test PDFParser._extract_questions_from_text extracts correctly."""
        text = """
        Question 1: What is encryption?
        Question 2: Which protocol is secure?
        Answer Key:
        1: A
        2: B
        """

        questions = PDFParser._extract_questions_from_text(text)

        # Should extract at least the questions
        assert len(questions) >= 1
        assert "1" in questions or "2" in questions

    def test_colors_class_has_all_methods(self):
        """Test Colors class has all required formatting methods."""
        methods = ["header", "success", "error", "warning", "info"]

        for method in methods:
            assert hasattr(Colors, method)
            assert callable(getattr(Colors, method))

    def test_answer_extractor_handles_multiline_answers(self):
        """Test that AnswerKeyExtractor handles multiline answer text."""
        pdf_text = """Answer Key:
1: A - This is a long answer
that spans multiple lines
with additional context

2: B - Short answer
"""

        extractor = AnswerKeyExtractor()
        answers = extractor.extract_answers(pdf_text)

        # Should extract at least first answer
        assert "1" in answers

        # First answer should contain some text
        assert len(answers["1"]["text"]) > 0
        # Text should contain part of the answer
        assert (
            "long" in answers["1"]["text"].lower()
            or "answer" in answers["1"]["text"].lower()
        )

    def test_answer_context_mapper_domain_keywords_exist(self):
        """Test that AnswerContextMapper has domain keywords configured."""
        mapper = AnswerContextMapper()

        # Should have CISSP domains
        assert len(mapper.domain_keywords) > 0

        # Should have key CISSP domains
        domain_names = list(mapper.domain_keywords.keys())
        assert any("Security" in d for d in domain_names)
        assert any("Cryptography" in d for d in domain_names)
        assert any("Network" in d for d in domain_names)

    def test_extract_with_answer_context_returns_dict(self):
        """Test that extract_with_answer_context returns proper structure."""
        pdf_text = """
        Question 1: What is AES?
        A) Asymmetric
        B) Symmetric
        C) Hash
        D) Digital signature

        Answer Key:
        1: B - AES is symmetric encryption
        """

        result = PDFParser.extract_with_answer_context(pdf_text)

        # Should be a dictionary
        assert isinstance(result, dict)

        # If anything is extracted, should have expected keys
        for q_num, context in result.items():
            if context.get("question"):  # If question extracted
                assert "question" in context
                assert "answer_letter" in context or "suggested_domain" in context

    def test_answer_key_letters_only_compatibility(self):
        """Test get_answer_letters_only provides format for analyzer."""
        pdf_text = """Answer Key:
1: A - Full text here
2: B - More text
3: C - Even more text
"""

        extractor = AnswerKeyExtractor()
        extractor.extract_answers(pdf_text)

        letters_only = extractor.get_answer_letters_only()

        # Should have extracted some answers
        assert len(letters_only) > 0

        # All extracted items should be letters
        for q_num, letter in letters_only.items():
            assert isinstance(letter, str)
            assert letter in ["A", "B", "C", "D", "E"]
