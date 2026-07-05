import pytest
from pathlib import Path
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.models import Question


@pytest.fixture
def pdf_path():
    return Path("/Users/sriram/Downloads/June 21st Test 1.Updated.pdf")


@pytest.fixture
def parser(pdf_path):
    if pdf_path.exists():
        return PDFParser(str(pdf_path))
    pytest.skip("Test PDF not found")


def test_pdf_loads(parser):
    """Test that PDF loads without error"""
    assert parser.pdf_path is not None
    assert parser.pages is not None
    assert len(parser.pages) > 0


def test_extract_questions(parser):
    """Test that questions are extracted"""
    questions = parser.extract_questions()
    assert questions is not None
    assert len(questions) == 125, f"Expected 125 questions, got {len(questions)}"


def test_question_structure(parser):
    """Test that extracted questions have correct structure"""
    questions = parser.extract_questions()
    q1 = questions[0]
    assert q1["number"] == 1
    assert "text" in q1
    assert len(q1["text"]) > 0
    assert "options" in q1
    assert len(q1["options"]) > 0


def test_extract_specific_question(parser):
    """Test extracting a specific question"""
    questions = parser.extract_questions()
    q31 = next((q for q in questions if q["number"] == 31), None)
    assert q31 is not None
    assert "text" in q31
    assert len(q31["text"]) > 0


def test_all_questions_numbered(parser):
    """Test that all questions are numbered 1-125"""
    questions = parser.extract_questions()
    numbers = sorted([q["number"] for q in questions])
    assert numbers == list(range(1, 126))


def test_extract_with_answer_context():
    """Test PDF parser uses answer context to enhance domain classification."""
    from cissp_analyzer.pdf_parser import PDFParser
    from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor

    # Sample PDF text with both questions and answers
    pdf_text = """Question 1: What controls data access?
A) Physical security
B) Role-Based Access Control
C) Encryption standards

Question 2: Which algorithm uses symmetric keys?
A) RSA
B) ECC
C) AES

Answer Key:
1: B - RBAC is part of Access Control and Identity Management domain
2: C - AES is the symmetric encryption standard
"""

    parser = PDFParser
    result = parser.extract_with_answer_context(pdf_text)

    # Should return enhanced context for each question
    assert "1" in result
    assert "2" in result

    # Question 1 should have domain suggestion from RBAC answer
    assert result["1"]["question"] == "What controls data access?"
    assert result["1"]["answer_letter"] == "B"
    assert "RBAC" in result["1"]["answer_text"]
    assert result["1"]["suggested_domain"] is not None

    # Question 2 should have domain suggestion from AES answer
    assert result["2"]["question"] == "Which algorithm uses symmetric keys?"
    assert result["2"]["answer_letter"] == "C"
    assert "AES" in result["2"]["answer_text"]
    assert result["2"]["suggested_domain"] is not None


def test_extract_with_answer_context_fallback():
    """Test that method gracefully handles PDFs with no answer key."""
    from cissp_analyzer.pdf_parser import PDFParser

    # PDF with questions but no answer section
    pdf_text = """Question 1: What is security?
A) Protection
B) Safety
C) Both
"""

    parser = PDFParser
    result = parser.extract_with_answer_context(pdf_text)

    # Should still work, just without answer text
    assert "1" in result
    assert result["1"]["question"] == "What is security?"
    assert result["1"]["answer_letter"] is None
    assert result["1"]["answer_text"] == ""
