import pytest
from datetime import datetime
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentAnswer


@pytest.fixture
def mapper():
    return DomainMapper(mapping_file='data/question_domain_mapping.json')


@pytest.fixture
def engine(mapper):
    return AnalysisEngine(mapper)


def test_export_performance_as_json(engine):
    """AnalysisEngine exports performance data matching schema"""
    # Setup answer key
    answer_key = {}
    for q in range(1, 87):
        answer_key[q] = "A"
    for q in range(87, 126):
        answer_key[q] = "B"

    engine.set_answer_key(answer_key)

    # Create student answers - all correct
    answers = []
    for q in range(1, 87):
        answers.append(StudentAnswer("student1", q, "A", False))
    for q in range(87, 126):
        answers.append(StudentAnswer("student1", q, "B", False))

    # Evaluate student
    performance = engine.evaluate_student(answers, "student1")

    # Export performance data
    perf_data = engine.export_student_performance("student1", exam_number=1, exam_date="2026-06-28")

    # Verify schema
    assert perf_data["exam_number"] == 1
    assert perf_data["student_name"] == "student1"
    assert perf_data["total_questions"] == 125
    assert perf_data["total_correct"] == 125
    assert perf_data["overall_accuracy"] == 100.0
    assert perf_data["exam_date"] == "2026-06-28"

    # Verify by_domain structure
    assert "by_domain" in perf_data
    assert isinstance(perf_data["by_domain"], dict)
    for domain, stats in perf_data["by_domain"].items():
        assert "correct" in stats
        assert "total" in stats
        assert "accuracy" in stats

    # Verify by_difficulty structure
    assert "by_difficulty" in perf_data
    assert isinstance(perf_data["by_difficulty"], dict)
    for difficulty, stats in perf_data["by_difficulty"].items():
        assert "correct" in stats
        assert "total" in stats
        assert "accuracy" in stats

    # Verify by_question_type structure
    assert "by_question_type" in perf_data
    assert isinstance(perf_data["by_question_type"], dict)
    for qtype, stats in perf_data["by_question_type"].items():
        assert "correct" in stats
        assert "total" in stats
        assert "accuracy" in stats

    # Verify wrong_question_ids
    assert "wrong_question_ids" in perf_data
    assert isinstance(perf_data["wrong_question_ids"], list)
    assert len(perf_data["wrong_question_ids"]) == 0  # All correct, no wrong questions


def test_export_performance_with_some_wrong_answers(engine):
    """Test export with some incorrect answers"""
    answer_key = {}
    for q in range(1, 126):
        answer_key[q] = "A"

    engine.set_answer_key(answer_key)

    # Create answers: 100 correct, 25 wrong
    answers = []
    for q in range(1, 101):
        answers.append(StudentAnswer("student2", q, "A", False))
    for q in range(101, 126):
        answers.append(StudentAnswer("student2", q, "B", False))  # Wrong answers

    performance = engine.evaluate_student(answers, "student2")
    perf_data = engine.export_student_performance("student2", exam_number=2)

    assert perf_data["total_correct"] == 100
    assert perf_data["total_questions"] == 125
    assert perf_data["overall_accuracy"] == 80.0
    assert len(perf_data["wrong_question_ids"]) == 25
    assert perf_data["wrong_question_ids"] == list(range(101, 126))


def test_export_performance_schema_completeness(engine):
    """Verify exported schema has all required fields"""
    answer_key = {q: "A" for q in range(1, 126)}
    engine.set_answer_key(answer_key)

    answers = [StudentAnswer("test_student", q, "A", False) for q in range(1, 126)]
    engine.evaluate_student(answers, "test_student")

    perf_data = engine.export_student_performance("test_student", exam_number=1)

    # Verify all required top-level fields exist
    required_fields = [
        "exam_number",
        "student_name",
        "total_questions",
        "total_correct",
        "overall_accuracy",
        "by_domain",
        "by_difficulty",
        "by_question_type",
        "wrong_question_ids"
    ]

    for field in required_fields:
        assert field in perf_data, f"Missing required field: {field}"

    # Verify data types
    assert isinstance(perf_data["exam_number"], int)
    assert isinstance(perf_data["student_name"], str)
    assert isinstance(perf_data["total_questions"], int)
    assert isinstance(perf_data["total_correct"], int)
    assert isinstance(perf_data["overall_accuracy"], (int, float))
    assert isinstance(perf_data["by_domain"], dict)
    assert isinstance(perf_data["by_difficulty"], dict)
    assert isinstance(perf_data["by_question_type"], dict)
    assert isinstance(perf_data["wrong_question_ids"], list)


def test_export_performance_optional_date(engine):
    """Test export with and without exam_date"""
    answer_key = {q: "A" for q in range(1, 126)}
    engine.set_answer_key(answer_key)
    answers = [StudentAnswer("test_student", q, "A", False) for q in range(1, 126)]
    engine.evaluate_student(answers, "test_student")

    # Export with date
    perf_with_date = engine.export_student_performance("test_student", exam_number=1, exam_date="2026-06-28")
    assert perf_with_date["exam_date"] == "2026-06-28"

    # Export without date
    perf_without_date = engine.export_student_performance("test_student", exam_number=2)
    assert "exam_date" not in perf_without_date or perf_without_date.get("exam_date") is None
