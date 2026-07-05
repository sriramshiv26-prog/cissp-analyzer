import json
import tempfile
from pathlib import Path
import pytest
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
            "by_domain": {"Security & Risk Management": {"accuracy": 0.70}},
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
                "overall_accuracy": 0.60 + (exam_num * 0.05),
            }
            with open(student_dir / f"exam-{exam_num}_performance.json", "w") as f:
                json.dump(exam_data, f)

        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("MultiExamStudent")

        assert len(result) == 3
        assert result[0]["exam_number"] == 1
        assert result[2]["exam_number"] == 3
        assert [r["overall_accuracy"] for r in result] == [0.65, 0.70, 0.75]


def test_load_previous_exams_enforces_max_limit(caplog):
    """Verify max 10 exams, warn on excess"""
    with tempfile.TemporaryDirectory() as tmpdir:
        student_dir = Path(tmpdir) / "MaxLimitStudent"
        student_dir.mkdir()

        # Create 10 existing exam files
        for exam_num in range(1, 11):
            exam_data = {
                "exam_number": exam_num,
                "date": f"2026-06-{10+exam_num}",
                "overall_accuracy": 0.50 + (exam_num * 0.02),
            }
            with open(student_dir / f"exam-{exam_num}_performance.json", "w") as f:
                json.dump(exam_data, f)

        loader = HistoryLoader(tmpdir)

        # Save exam 11 (exceeds max limit)
        exam_11_data = {
            "exam_number": 11,
            "date": "2026-07-01",
            "overall_accuracy": 0.72,
        }
        saved_path = loader.save_exam_performance("MaxLimitStudent", 11, exam_11_data)

        # Verify warning was logged
        assert any(
            "MaxLimitStudent" in record.message and "10 exams" in record.message
            for record in caplog.records
            if record.levelname == "WARNING"
        )

        # Verify exam 11 was still saved despite warning (not a hard block)
        assert saved_path.exists()
        with open(saved_path, "r") as f:
            saved_data = json.load(f)
        assert saved_data["exam_number"] == 11
        assert saved_data["overall_accuracy"] == 0.72


def test_create_student_folder_creates_directory():
    """Verify create_student_folder creates directory and returns correct path"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # Folder should not exist initially
        student_path = Path(tmpdir) / "NewStudent"
        assert not student_path.exists()

        # Create folder
        result_path = loader.create_student_folder("NewStudent")

        # Verify folder was created
        assert student_path.exists()
        assert student_path.is_dir()

        # Verify returned path is correct
        assert result_path == student_path


def test_path_traversal_protection_create_student_folder():
    """Verify path traversal sequences are blocked in create_student_folder"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # These should raise ValueError
        traversal_attempts = [
            "../../../etc",
            "../../secret",
            "student/../../secret",
            "../secret",
            "..\\..\\secret",  # Windows path traversal
        ]

        for traversal_attempt in traversal_attempts:
            with pytest.raises(ValueError, match="path traversal"):
                loader.create_student_folder(traversal_attempt)


def test_path_traversal_protection_save_exam_performance():
    """Verify path traversal sequences are blocked in save_exam_performance"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # Test data
        exam_data = {
            "exam_number": 1,
            "date": "2026-06-26",
            "overall_accuracy": 0.65,
        }

        # These should raise ValueError
        traversal_attempts = [
            "../../../etc",
            "../../secret",
            "student/../../secret",
            "../secret",
            "..\\..\\secret",  # Windows path traversal
        ]

        for traversal_attempt in traversal_attempts:
            with pytest.raises(ValueError, match="path traversal"):
                loader.save_exam_performance(traversal_attempt, 1, exam_data)
