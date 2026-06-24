import pytest
from pathlib import Path
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.models import Question


@pytest.fixture
def pdf_path():
    return Path('/Users/sriram/Downloads/June 21st Test 1.Updated.pdf')


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
    assert q1['number'] == 1
    assert 'text' in q1
    assert len(q1['text']) > 0
    assert 'options' in q1
    assert len(q1['options']) > 0


def test_extract_specific_question(parser):
    """Test extracting a specific question"""
    questions = parser.extract_questions()
    q31 = next((q for q in questions if q['number'] == 31), None)
    assert q31 is not None
    assert 'text' in q31
    assert len(q31['text']) > 0


def test_all_questions_numbered(parser):
    """Test that all questions are numbered 1-125"""
    questions = parser.extract_questions()
    numbers = sorted([q['number'] for q in questions])
    assert numbers == list(range(1, 126))
