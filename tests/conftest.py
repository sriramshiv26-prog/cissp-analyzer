"""
Pytest Configuration and Shared Fixtures for CISSP Analyzer Functional Tests

This module provides:
1. Pytest configuration and markers
2. Shared fixtures for temporary directories and test data
3. Sample student data, answer keys, and exam files
4. Test utilities for common validation tasks

Fixtures:
- temp_test_dir: Temporary directory that auto-cleans up after test
- sample_student_data: Dict with 3 sample students and their performance data
- sample_answer_key: Dict with 125 question answers (Q1-Q125)
- sample_excel_file: Excel file with student answers (125 questions, 3 students)
- sample_answer_key_file: JSON file with answer key
- sample_history_folder: Directory with previous exam performance data
- output_dir: Output directory for test results

Usage:
    pytest tests/ --fixtures                 # See all available fixtures
    pytest tests/test_xyz.py -v              # Run with verbose output
    pytest tests/test_xyz.py -v -s           # Run with print statements visible

Author: CISSP Analyzer Project
Date: 2026-07-03
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
import pandas as pd


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "functional: mark test as functional test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


# ============================================================================
# FIXTURE: temp_test_dir
# ============================================================================

@pytest.fixture
def temp_test_dir():
    """
    Create a temporary directory for test files that auto-cleans up.

    Returns:
        Path: Temporary directory path object

    Cleanup:
        Automatically removes directory and all contents after test completes

    Example:
        def test_file_creation(temp_test_dir):
            test_file = temp_test_dir / "test.txt"
            test_file.write_text("hello")
            assert test_file.exists()
            # Auto-cleanup after test
    """
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir

    # Cleanup: Remove all files and subdirectories
    import shutil
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


# ============================================================================
# FIXTURE: sample_student_data
# ============================================================================

@pytest.fixture
def sample_student_data() -> Dict[str, Dict[str, Any]]:
    """
    Provide sample student performance data for testing.

    Returns:
        Dict with 3 students (TestStudent1, TestStudent2, TestStudent3):
            - questions: Total questions (125)
            - correct: Number of correct answers
            - percentage: Percentage score
            - domain_breakdown: Performance by domain

    Example:
        def test_scoring(sample_student_data):
            student = sample_student_data["TestStudent1"]
            assert student["percentage"] == 85.6
            assert student["correct"] == 107
    """
    return {
        "TestStudent1": {
            "questions": 125,
            "correct": 107,
            "wrong": 18,
            "percentage": 85.6,
            "domain_breakdown": {
                "Security & Risk Management": {"correct": 15, "total": 17, "percentage": 88.2},
                "Asset Security": {"correct": 14, "total": 17, "percentage": 82.4},
                "Security Architecture & Engineering": {"correct": 17, "total": 18, "percentage": 94.4},
                "Communication & Network Security": {"correct": 16, "total": 18, "percentage": 88.9},
                "Identity & Access Management": {"correct": 16, "total": 18, "percentage": 88.9},
                "Security Assessment & Testing": {"correct": 15, "total": 17, "percentage": 88.2},
                "Security Operations": {"correct": 14, "total": 18, "percentage": 77.8},
            },
            "difficulty_breakdown": {
                "Easy": {"correct": 28, "total": 30, "percentage": 93.3},
                "Medium": {"correct": 54, "total": 65, "percentage": 83.1},
                "Hard": {"correct": 25, "total": 30, "percentage": 83.3},
            },
        },
        "TestStudent2": {
            "questions": 125,
            "correct": 102,
            "wrong": 23,
            "percentage": 81.6,
            "domain_breakdown": {
                "Security & Risk Management": {"correct": 14, "total": 17, "percentage": 82.4},
                "Asset Security": {"correct": 12, "total": 17, "percentage": 70.6},
                "Security Architecture & Engineering": {"correct": 15, "total": 18, "percentage": 83.3},
                "Communication & Network Security": {"correct": 15, "total": 18, "percentage": 83.3},
                "Identity & Access Management": {"correct": 15, "total": 18, "percentage": 83.3},
                "Security Assessment & Testing": {"correct": 14, "total": 17, "percentage": 82.4},
                "Security Operations": {"correct": 12, "total": 18, "percentage": 66.7},
            },
            "difficulty_breakdown": {
                "Easy": {"correct": 26, "total": 30, "percentage": 86.7},
                "Medium": {"correct": 52, "total": 65, "percentage": 80.0},
                "Hard": {"correct": 24, "total": 30, "percentage": 80.0},
            },
        },
        "TestStudent3": {
            "questions": 125,
            "correct": 97,
            "wrong": 28,
            "percentage": 77.6,
            "domain_breakdown": {
                "Security & Risk Management": {"correct": 13, "total": 17, "percentage": 76.5},
                "Asset Security": {"correct": 11, "total": 17, "percentage": 64.7},
                "Security Architecture & Engineering": {"correct": 14, "total": 18, "percentage": 77.8},
                "Communication & Network Security": {"correct": 14, "total": 18, "percentage": 77.8},
                "Identity & Access Management": {"correct": 14, "total": 18, "percentage": 77.8},
                "Security Assessment & Testing": {"correct": 13, "total": 17, "percentage": 76.5},
                "Security Operations": {"correct": 12, "total": 18, "percentage": 66.7},
            },
            "difficulty_breakdown": {
                "Easy": {"correct": 24, "total": 30, "percentage": 80.0},
                "Medium": {"correct": 50, "total": 65, "percentage": 76.9},
                "Hard": {"correct": 23, "total": 30, "percentage": 76.7},
            },
        },
    }


# ============================================================================
# FIXTURE: sample_answer_key
# ============================================================================

@pytest.fixture
def sample_answer_key() -> Dict[str, str]:
    """
    Provide sample answer key for 125 CISSP exam questions.

    Returns:
        Dict: Question number (str) -> Answer letter (str)
              {"1": "A", "2": "B", ..., "125": "D"}

    Details:
        - 125 questions (Q1-Q125)
        - Answers distributed across A, B, C, D
        - Realistic distribution for practice exams

    Example:
        def test_answer_validation(sample_answer_key):
            assert sample_answer_key["1"] == "A"
            assert len(sample_answer_key) == 125
            assert all(v in "ABCD" for v in sample_answer_key.values())
    """
    # Create a realistic answer key distribution
    answer_key = {}
    answers = ["A", "B", "C", "D"]

    # Distribute answers evenly across A, B, C, D
    for i in range(1, 126):
        answer_key[str(i)] = answers[(i - 1) % 4]

    # Override some answers to create a more realistic distribution
    answer_key["5"] = "B"
    answer_key["12"] = "C"
    answer_key["23"] = "A"
    answer_key["34"] = "D"
    answer_key["45"] = "B"
    answer_key["56"] = "C"
    answer_key["67"] = "A"
    answer_key["78"] = "D"
    answer_key["89"] = "B"
    answer_key["100"] = "C"
    answer_key["111"] = "A"
    answer_key["122"] = "D"

    return answer_key


# ============================================================================
# FIXTURE: sample_excel_file
# ============================================================================

@pytest.fixture
def sample_excel_file(temp_test_dir, sample_answer_key, sample_student_data):
    """
    Create sample Excel answer file with student responses.

    Args:
        temp_test_dir: Temporary directory from fixture
        sample_answer_key: Answer key from fixture
        sample_student_data: Student data from fixture

    Returns:
        Path: Path to created Excel file

    File Structure:
        Sheet: "Sheet1" or "Sheet1" (default)
        Columns: Question Number, TestStudent1, TestStudent2, TestStudent3
        Rows: 125 (one per question)

    Example:
        def test_excel_parsing(sample_excel_file):
            df = pd.read_excel(sample_excel_file)
            assert len(df) == 125
            assert "Question" in df.columns
    """
    # Create data structure: Question Number + 3 students
    data = {
        "Question": list(range(1, 126)),
    }

    # Add student answers (correct answers with some mistakes)
    # TestStudent1: 107 correct out of 125
    student1_answers = []
    for q in range(1, 126):
        if q in [3, 7, 15, 22, 34, 45, 56, 67, 78, 89, 95, 105, 110, 112, 115, 118, 120, 124]:
            # Wrong answer (18 wrong total)
            correct = sample_answer_key[str(q)]
            wrong_answers = [a for a in "ABCD" if a != correct]
            student1_answers.append(wrong_answers[0])
        else:
            student1_answers.append(sample_answer_key[str(q)])
    data["TestStudent1"] = student1_answers

    # TestStudent2: 102 correct out of 125
    student2_answers = []
    for q in range(1, 126):
        if q in [5, 12, 23, 34, 45, 56, 67, 78, 89, 100, 111, 122, 10, 20, 30, 40, 50, 60, 70, 80, 90, 110, 120]:
            # Wrong answer (23 wrong total)
            correct = sample_answer_key[str(q)]
            wrong_answers = [a for a in "ABCD" if a != correct]
            student2_answers.append(wrong_answers[1] if len(wrong_answers) > 1 else wrong_answers[0])
        else:
            student2_answers.append(sample_answer_key[str(q)])
    data["TestStudent2"] = student2_answers

    # TestStudent3: 97 correct out of 125
    student3_answers = []
    for q in range(1, 126):
        if q in [2, 8, 16, 24, 32, 42, 52, 62, 72, 82, 92, 102, 112, 6, 11, 18, 28, 38, 48, 58, 68, 85, 96, 107, 119, 123, 125]:
            # Wrong answer (28 wrong total)
            correct = sample_answer_key[str(q)]
            wrong_answers = [a for a in "ABCD" if a != correct]
            student3_answers.append(wrong_answers[2] if len(wrong_answers) > 2 else wrong_answers[0])
        else:
            student3_answers.append(sample_answer_key[str(q)])
    data["TestStudent3"] = student3_answers

    # Create DataFrame and save to Excel
    df = pd.DataFrame(data)
    excel_path = temp_test_dir / "sample_answers.xlsx"
    df.to_excel(excel_path, index=False, sheet_name="Sheet1")

    return excel_path


# ============================================================================
# FIXTURE: sample_answer_key_file
# ============================================================================

@pytest.fixture
def sample_answer_key_file(temp_test_dir, sample_answer_key):
    """
    Create sample answer key JSON file.

    Args:
        temp_test_dir: Temporary directory from fixture
        sample_answer_key: Answer key data from fixture

    Returns:
        Path: Path to created answer_key.json file

    File Format:
        JSON dict: {"1": "A", "2": "B", ..., "125": "D"}

    Example:
        def test_answer_key_loading(sample_answer_key_file):
            with open(sample_answer_key_file) as f:
                key = json.load(f)
            assert len(key) == 125
            assert key["1"] == "A"
    """
    answer_key_path = temp_test_dir / "answer_key.json"

    with open(answer_key_path, 'w') as f:
        json.dump(sample_answer_key, f, indent=2)

    return answer_key_path


# ============================================================================
# FIXTURE: sample_history_folder
# ============================================================================

@pytest.fixture
def sample_history_folder(temp_test_dir):
    """
    Create sample student history folder with previous exam performance.

    Args:
        temp_test_dir: Temporary directory from fixture

    Returns:
        Path: Path to students/ directory containing history files

    Structure:
        students/
            TestStudent2/
                exam-1_performance.json (previous exam data)

    File Content (exam-1_performance.json):
        {
            "student_name": "TestStudent2",
            "exam_date": "2026-06-15",
            "score_percentage": 65.5,
            "correct": 82,
            "total": 125
        }

    Example:
        def test_history_loading(sample_history_folder):
            history_file = sample_history_folder / "TestStudent2" / "exam-1_performance.json"
            assert history_file.exists()
    """
    history_dir = temp_test_dir / "students"
    history_dir.mkdir(exist_ok=True)

    # Create student2 history (previous exam performance)
    student2_dir = history_dir / "TestStudent2"
    student2_dir.mkdir(exist_ok=True)

    previous_exam_data = {
        "student_name": "TestStudent2",
        "exam_date": "2026-06-15",
        "exam_type": "Practice",
        "score_percentage": 65.5,
        "correct": 82,
        "total": 125,
        "by_domain": {
            "Security & Risk Management": {"correct": 10, "total": 17, "percentage": 58.8},
            "Asset Security": {"correct": 9, "total": 17, "percentage": 52.9},
            "Security Architecture & Engineering": {"correct": 11, "total": 18, "percentage": 61.1},
            "Communication & Network Security": {"correct": 11, "total": 18, "percentage": 61.1},
            "Identity & Access Management": {"correct": 12, "total": 18, "percentage": 66.7},
            "Security Assessment & Testing": {"correct": 12, "total": 17, "percentage": 70.6},
            "Security Operations": {"correct": 11, "total": 18, "percentage": 61.1},
        },
    }

    history_file = student2_dir / "exam-1_performance.json"
    with open(history_file, 'w') as f:
        json.dump(previous_exam_data, f, indent=2)

    return history_dir


# ============================================================================
# FIXTURE: output_dir
# ============================================================================

@pytest.fixture
def output_dir(temp_test_dir):
    """
    Create output directory for test results.

    Args:
        temp_test_dir: Temporary directory from fixture

    Returns:
        Path: Path to outputs/ directory

    Example:
        def test_report_generation(output_dir):
            report_file = output_dir / "performance_report.xlsx"
            # Generate report...
            assert report_file.exists()
    """
    out_dir = temp_test_dir / "outputs"
    out_dir.mkdir(exist_ok=True)
    return out_dir
