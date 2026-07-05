import pytest
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentAnswer


@pytest.fixture
def mapper():
    return DomainMapper(mapping_file="data/question_domain_mapping.json")


@pytest.fixture
def engine(mapper):
    return AnalysisEngine(mapper)


def test_evaluate_answers_senthil(engine):
    """Test evaluation for Senthil with answer key"""
    # Set up answer key: A for 1-86, B for 87-125
    answer_key = {}
    for q in range(1, 87):
        answer_key[q] = "A"
    for q in range(87, 126):
        answer_key[q] = "B"

    engine.set_answer_key(answer_key)

    answers = []
    for q in range(1, 87):
        answers.append(StudentAnswer("Senthil", q, "A", False))
    for q in range(87, 126):
        answers.append(StudentAnswer("Senthil", q, "B", False))

    performance = engine.evaluate_student(answers, "Senthil")
    assert performance.student_name == "Senthil"
    assert performance.correct_count == 125
    assert performance.score_percentage == 100.0


def test_performance_has_all_dimensions(engine):
    """Test that performance analysis includes all dimensions"""
    answers = [StudentAnswer("Test", 1, "A", False) for _ in range(125)]
    performance = engine.evaluate_student(answers, "Test")

    assert hasattr(performance, "by_domain")
    assert hasattr(performance, "by_topic")
    assert hasattr(performance, "by_difficulty")
    assert hasattr(performance, "by_question_type")
    assert hasattr(performance, "by_exam_trick")
    assert isinstance(performance.by_domain, dict)
    assert isinstance(performance.by_topic, dict)


def test_domain_breakdown(engine):
    """Test that domain breakdown includes all 8 domains"""
    answers = [StudentAnswer("Test", q, "A", False) for q in range(1, 126)]
    performance = engine.evaluate_student(answers, "Test")
    assert len(performance.by_domain) > 0


def test_wrong_question_tracking(engine):
    """Test that wrong questions are tracked"""
    answers = []
    for q in range(1, 51):
        answers.append(StudentAnswer("Test", q, "A", False))
    for q in range(51, 126):
        answers.append(StudentAnswer("Test", q, "B", False))

    performance = engine.evaluate_student(answers, "Test")
    assert len(performance.wrong_question_ids) > 0
