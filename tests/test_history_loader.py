import json
import tempfile
from pathlib import Path
from cissp_analyzer.history_loader import HistoryLoader


def test_load_previous_exams_returns_empty_when_no_history():
    """First-time student: no previous exams"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("NewStudent")
        assert result == []


def test_load_previous_exams_single_exam():
    """Student with one previous exam"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock exam-1_performance.json
        student_dir = Path(tmpdir) / "ExistingStudent"
        student_dir.mkdir()

        exam_data = {
            "exam_number": 1,
            "date": "2026-06-26",
            "student_name": "ExistingStudent",
            "overall_accuracy": 0.65,
            "by_domain": {
                "Security & Risk Management": {"accuracy": 0.70}
            }
        }

        with open(student_dir / "exam-1_performance.json", "w") as f:
            json.dump(exam_data, f)

        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("ExistingStudent")

        assert len(result) == 1
        assert result[0]["exam_number"] == 1
        assert result[0]["overall_accuracy"] == 0.65


def test_load_previous_exams_multiple_exams():
    """Student with multiple exams - verify order"""
    with tempfile.TemporaryDirectory() as tmpdir:
        student_dir = Path(tmpdir) / "MultiExamStudent"
        student_dir.mkdir()

        for exam_num in [1, 2, 3]:
            exam_data = {
                "exam_number": exam_num,
                "date": f"2026-06-{25+exam_num}",
                "overall_accuracy": 0.60 + (exam_num * 0.05)
            }
            with open(student_dir / f"exam-{exam_num}_performance.json", "w") as f:
                json.dump(exam_data, f)

        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("MultiExamStudent")

        assert len(result) == 3
        assert result[0]["exam_number"] == 1
        assert result[2]["exam_number"] == 3
        assert [r["overall_accuracy"] for r in result] == [0.65, 0.70, 0.75]


def test_load_previous_exams_enforces_max_limit():
    """Verify max 10 exams, warn on excess"""
    # This will be tested after warnings are added in Task 2
    pass
