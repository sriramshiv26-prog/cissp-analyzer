import json
import tempfile
from pathlib import Path
from cissp_analyzer.history_loader import HistoryLoader


def test_complete_workflow_three_exams():
    """Complete workflow: analyze 3 exams, verify history and trends"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create HistoryLoader with temporary directory
        loader = HistoryLoader(tmpdir)

        # Simulate 3 exams for one student
        exam_data_list = [
            {
                "exam_number": 1,
                "date": "2026-06-20",
                "student_name": "Alice",
                "overall_accuracy": 0.60,
                "by_domain": {
                    "Security & Risk Management": {"accuracy": 0.55, "questions": 5},
                    "Asset Security": {"accuracy": 0.65, "questions": 5},
                    "Security Architecture and Engineering": {"accuracy": 0.60, "questions": 5}
                },
                "by_difficulty": {
                    "Easy": {"accuracy": 0.70, "questions": 3},
                    "Medium": {"accuracy": 0.60, "questions": 4},
                    "Hard": {"accuracy": 0.50, "questions": 3}
                }
            },
            {
                "exam_number": 2,
                "date": "2026-06-25",
                "student_name": "Alice",
                "overall_accuracy": 0.65,
                "by_domain": {
                    "Security & Risk Management": {"accuracy": 0.60, "questions": 5},
                    "Asset Security": {"accuracy": 0.70, "questions": 5},
                    "Security Architecture and Engineering": {"accuracy": 0.65, "questions": 5}
                },
                "by_difficulty": {
                    "Easy": {"accuracy": 0.75, "questions": 3},
                    "Medium": {"accuracy": 0.65, "questions": 4},
                    "Hard": {"accuracy": 0.55, "questions": 3}
                }
            },
            {
                "exam_number": 3,
                "date": "2026-06-28",
                "student_name": "Alice",
                "overall_accuracy": 0.72,
                "by_domain": {
                    "Security & Risk Management": {"accuracy": 0.70, "questions": 5},
                    "Asset Security": {"accuracy": 0.75, "questions": 5},
                    "Security Architecture and Engineering": {"accuracy": 0.72, "questions": 5}
                },
                "by_difficulty": {
                    "Easy": {"accuracy": 0.85, "questions": 3},
                    "Medium": {"accuracy": 0.72, "questions": 4},
                    "Hard": {"accuracy": 0.65, "questions": 3}
                }
            }
        ]

        # Save each exam via loader.save_exam_performance()
        saved_paths = []
        for exam_data in exam_data_list:
            exam_num = exam_data["exam_number"]
            path = loader.save_exam_performance("Alice", exam_num, exam_data)
            saved_paths.append(path)

        # Verify all exams were saved
        assert len(saved_paths) == 3
        for path in saved_paths:
            assert path.exists()

        # Load history via loader.load_previous_exams()
        history = loader.load_previous_exams("Alice")

        # Verify: len(history) == 3
        assert len(history) == 3, f"Expected 3 exams, got {len(history)}"

        # Verify: exam numbers are correct (1, 2, 3)
        exam_numbers = [exam["exam_number"] for exam in history]
        assert exam_numbers == [1, 2, 3], f"Expected exam numbers [1, 2, 3], got {exam_numbers}"

        # Verify: overall accuracy progression: 0.60 → 0.65 → 0.72
        accuracies = [exam["overall_accuracy"] for exam in history]
        assert accuracies == [0.60, 0.65, 0.72], f"Expected progression [0.60, 0.65, 0.72], got {accuracies}"

        # Verify: metadata preserved for each exam
        assert history[0]["date"] == "2026-06-20"
        assert history[1]["date"] == "2026-06-25"
        assert history[2]["date"] == "2026-06-28"

        # Verify: domain data preserved
        assert history[0]["by_domain"]["Security & Risk Management"]["accuracy"] == 0.55
        assert history[1]["by_domain"]["Asset Security"]["accuracy"] == 0.70
        assert history[2]["by_domain"]["Security Architecture and Engineering"]["accuracy"] == 0.72

        # Verify: difficulty data preserved
        assert history[0]["by_difficulty"]["Easy"]["accuracy"] == 0.70
        assert history[1]["by_difficulty"]["Medium"]["accuracy"] == 0.65
        assert history[2]["by_difficulty"]["Hard"]["accuracy"] == 0.65


def test_multi_exam_workflow_with_sorting():
    """Verify multi-exam sorting handles exams 1-10+ correctly"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # Create exams in non-sequential order (to test sorting)
        exam_order = [3, 1, 5, 2, 4]
        for exam_num in exam_order:
            exam_data = {
                "exam_number": exam_num,
                "date": f"2026-06-{20+exam_num}",
                "overall_accuracy": 0.60 + (exam_num * 0.02)
            }
            loader.save_exam_performance("Bob", exam_num, exam_data)

        # Load history and verify correct order
        history = loader.load_previous_exams("Bob")

        assert len(history) == 5
        exam_numbers = [exam["exam_number"] for exam in history]
        assert exam_numbers == [1, 2, 3, 4, 5], f"Expected sorted [1, 2, 3, 4, 5], got {exam_numbers}"


def test_multi_exam_performance_improvement_tracking():
    """Track performance improvement across multiple exams"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # Create 4 exams with improving accuracy
        for exam_num in range(1, 5):
            exam_data = {
                "exam_number": exam_num,
                "date": f"2026-06-{20+exam_num}",
                "overall_accuracy": 0.50 + (exam_num * 0.08),
                "by_domain": {
                    "Security & Risk Management": {
                        "accuracy": 0.48 + (exam_num * 0.10),
                        "questions": 10
                    },
                    "Asset Security": {
                        "accuracy": 0.52 + (exam_num * 0.07),
                        "questions": 10
                    }
                }
            }
            loader.save_exam_performance("Charlie", exam_num, exam_data)

        # Load and verify improvement
        history = loader.load_previous_exams("Charlie")

        # Calculate improvement trend
        overall_accuracies = [exam["overall_accuracy"] for exam in history]
        expected_overall = [0.58, 0.66, 0.74, 0.82]
        assert len(overall_accuracies) == len(expected_overall)
        for actual, expected in zip(overall_accuracies, expected_overall):
            assert abs(actual - expected) < 0.0001, f"Expected ~{expected}, got {actual}"

        # Verify improvement in first domain
        domain_accuracies = [
            exam["by_domain"]["Security & Risk Management"]["accuracy"]
            for exam in history
        ]
        expected_domain = [0.58, 0.68, 0.78, 0.88]
        assert len(domain_accuracies) == len(expected_domain)
        for actual, expected in zip(domain_accuracies, expected_domain):
            assert abs(actual - expected) < 0.0001, f"Expected ~{expected}, got {actual}"

        # Verify each exam improves from previous
        for i in range(1, len(overall_accuracies)):
            assert overall_accuracies[i] > overall_accuracies[i-1], \
                f"Exam {i+1} should improve over exam {i}"


def test_multi_student_multi_exam_isolation():
    """Verify exams from different students don't mix"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # Create exams for two students
        students_exams = {
            "Student1": [0.60, 0.65, 0.70],
            "Student2": [0.55, 0.62, 0.75]
        }

        for student_name, accuracies in students_exams.items():
            for exam_num, accuracy in enumerate(accuracies, 1):
                exam_data = {
                    "exam_number": exam_num,
                    "date": f"2026-06-{20+exam_num}",
                    "overall_accuracy": accuracy
                }
                loader.save_exam_performance(student_name, exam_num, exam_data)

        # Load history for each student
        history1 = loader.load_previous_exams("Student1")
        history2 = loader.load_previous_exams("Student2")

        # Verify correct exams loaded for each student
        assert len(history1) == 3
        assert len(history2) == 3

        accuracies1 = [exam["overall_accuracy"] for exam in history1]
        accuracies2 = [exam["overall_accuracy"] for exam in history2]

        assert accuracies1 == [0.60, 0.65, 0.70]
        assert accuracies2 == [0.55, 0.62, 0.75]

        # Verify no cross-contamination
        assert set(accuracies1) != set(accuracies2)


def test_multi_exam_with_missing_exam_number():
    """Handle gaps in exam sequence (e.g., exams 1, 2, 4 but no 3)"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)

        # Create exams with a gap
        exam_numbers = [1, 2, 4]  # Missing exam 3
        for exam_num in exam_numbers:
            exam_data = {
                "exam_number": exam_num,
                "date": f"2026-06-{20+exam_num}",
                "overall_accuracy": 0.60 + (exam_num * 0.05)
            }
            loader.save_exam_performance("Dana", exam_num, exam_data)

        # Load history
        history = loader.load_previous_exams("Dana")

        # Should load only the 3 exams that exist
        assert len(history) == 3
        loaded_exam_numbers = [exam["exam_number"] for exam in history]
        assert loaded_exam_numbers == [1, 2, 4]

        # Verify accuracies match expected values
        accuracies = [exam["overall_accuracy"] for exam in history]
        assert accuracies == [0.65, 0.70, 0.80]
