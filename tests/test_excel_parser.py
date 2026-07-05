import pytest
import pandas as pd
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.models import StudentAnswer


@pytest.fixture
def sample_answer_file(tmp_path):
    """Create a sample answer Excel file for testing"""
    data = {"Question": [1, 2, 3, 4, 5], "Student_Answer": ["A", "B", "A", "D", "C"]}
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_answers.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def parser(sample_answer_file):
    return ExcelParser()


def test_parse_student_answers(parser, sample_answer_file):
    """Test parsing student answer sheet"""
    answers = parser.parse_answers(str(sample_answer_file), "Student_Answer")
    assert len(answers) == 5
    assert all(isinstance(a, StudentAnswer) for a in answers)


def test_student_answer_structure(parser, sample_answer_file):
    """Test that student answers have correct structure"""
    answers = parser.parse_answers(str(sample_answer_file), "Student_Answer")
    answer = answers[0]
    assert answer.student_name == "Student_Answer"
    assert answer.question_number == 1
    assert answer.selected_answer == "A"


def test_parse_multiple_students(parser, tmp_path):
    """Test parsing answers from multiple students"""
    data = {
        "Question": [1, 2, 3],
        "Senthil": ["A", "B", "A"],
        "Kapil": ["B", "A", "D"],
        "Praveena": ["A", "C", "A"],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "multi_student.xlsx"
    df.to_excel(file_path, index=False)

    for student_name in ["Senthil", "Kapil", "Praveena"]:
        answers = parser.parse_answers(str(file_path), student_name)
        assert len(answers) == 3
        assert all(a.student_name == student_name for a in answers)
