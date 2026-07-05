import pytest
from cissp_analyzer.trend_calculator import TrendCalculator


@pytest.fixture
def calculator():
    return TrendCalculator()


def test_calculate_domain_trends_two_exams(calculator):
    """Test domain trend calculation across two exams"""
    exam1 = {
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.65},
            "Asset Security": {"accuracy": 0.70},
            "Security Architecture and Engineering": {"accuracy": 0.60},
        }
    }

    exam2 = {
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.75},
            "Asset Security": {"accuracy": 0.68},
            "Security Architecture and Engineering": {"accuracy": 0.80},
        }
    }

    exams = [exam1, exam2]
    trends = calculator.calculate_domain_trends(exams)

    # Verify structure
    assert isinstance(trends, dict)
    assert "Security & Risk Management" in trends
    assert "Asset Security" in trends
    assert "Security Architecture and Engineering" in trends

    # Verify values
    assert trends["Security & Risk Management"] == [0.65, 0.75]
    assert trends["Asset Security"] == [0.70, 0.68]
    assert trends["Security Architecture and Engineering"] == [0.60, 0.80]


def test_calculate_domain_trends_three_exams(calculator):
    """Test domain trend calculation across three exams"""
    exam1 = {
        "by_domain": {
            "Communication & Network Security": {"accuracy": 0.50},
            "Identity and Access Management (IAM)": {"accuracy": 0.55},
        }
    }

    exam2 = {
        "by_domain": {
            "Communication & Network Security": {"accuracy": 0.60},
            "Identity and Access Management (IAM)": {"accuracy": 0.65},
        }
    }

    exam3 = {
        "by_domain": {
            "Communication & Network Security": {"accuracy": 0.75},
            "Identity and Access Management (IAM)": {"accuracy": 0.70},
        }
    }

    exams = [exam1, exam2, exam3]
    trends = calculator.calculate_domain_trends(exams)

    # Verify structure
    assert len(trends) == 2
    assert "Communication & Network Security" in trends
    assert "Identity and Access Management (IAM)" in trends

    # Verify values
    assert trends["Communication & Network Security"] == [0.50, 0.60, 0.75]
    assert trends["Identity and Access Management (IAM)"] == [0.55, 0.65, 0.70]


def test_calculate_difficulty_trends(calculator):
    """Test difficulty trend calculation"""
    exam1 = {
        "by_difficulty": {
            "Easy": {"accuracy": 0.90},
            "Medium": {"accuracy": 0.65},
            "Hard": {"accuracy": 0.40},
        }
    }

    exam2 = {
        "by_difficulty": {
            "Easy": {"accuracy": 0.92},
            "Medium": {"accuracy": 0.72},
            "Hard": {"accuracy": 0.55},
        }
    }

    exams = [exam1, exam2]
    trends = calculator.calculate_difficulty_trends(exams)

    # Verify structure
    assert isinstance(trends, dict)
    assert "Easy" in trends
    assert "Medium" in trends
    assert "Hard" in trends

    # Verify values
    assert trends["Easy"] == [0.90, 0.92]
    assert trends["Medium"] == [0.65, 0.72]
    assert trends["Hard"] == [0.40, 0.55]


def test_calculate_question_type_trends(calculator):
    """Test question type trend calculation"""
    exam1 = {
        "by_question_type": {
            "Definition": {"accuracy": 0.80},
            "Scenario": {"accuracy": 0.60},
            "Comparison": {"accuracy": 0.55},
        }
    }

    exam2 = {
        "by_question_type": {
            "Definition": {"accuracy": 0.85},
            "Scenario": {"accuracy": 0.70},
            "Comparison": {"accuracy": 0.65},
        }
    }

    exams = [exam1, exam2]
    trends = calculator.calculate_question_type_trends(exams)

    # Verify structure
    assert isinstance(trends, dict)
    assert "Definition" in trends
    assert "Scenario" in trends
    assert "Comparison" in trends

    # Verify values
    assert trends["Definition"] == [0.80, 0.85]
    assert trends["Scenario"] == [0.60, 0.70]
    assert trends["Comparison"] == [0.55, 0.65]


def test_detect_trend_direction_improving(calculator):
    """Test trend direction detection for improving trend"""
    trend = [0.50, 0.60, 0.70]
    direction = calculator.detect_trend_direction(trend)
    assert direction == "improving"


def test_detect_trend_direction_declining(calculator):
    """Test trend direction detection for declining trend"""
    trend = [0.80, 0.70, 0.60]
    direction = calculator.detect_trend_direction(trend)
    assert direction == "declining"


def test_detect_trend_direction_stable(calculator):
    """Test trend direction detection for stable trend"""
    trend = [0.65, 0.66, 0.64]
    direction = calculator.detect_trend_direction(trend)
    assert direction == "stable"


def test_get_momentum_score(calculator):
    """Test momentum score calculation"""
    # Improving momentum
    score = calculator.get_momentum_score(0.60, 0.75)
    assert abs(score - 0.15) < 1e-9

    # Declining momentum
    score = calculator.get_momentum_score(0.80, 0.65)
    assert abs(score - (-0.15)) < 1e-9

    # No momentum
    score = calculator.get_momentum_score(0.70, 0.70)
    assert abs(score - 0.0) < 1e-9


def test_calculate_priority_score_with_momentum(calculator):
    """Test priority score calculation with momentum (weakness + momentum × 2)"""
    # Case 1: High weakness + positive momentum (improving)
    # weakness = (1 - 0.60) * 100 = 40
    # momentum = (0.60 - 0.50) * 100 = 10
    # priority = 40 + (10 * 2) = 60
    score = calculator.calculate_priority_score(0.60, 0.50)
    assert abs(score - 60.0) < 1e-9

    # Case 2: Low weakness + negative momentum (declining)
    # weakness = (1 - 0.85) * 100 = 15
    # momentum = (0.85 - 0.95) * 100 = -10
    # priority = 15 + (-10 * 2) = -5
    score = calculator.calculate_priority_score(0.85, 0.95)
    assert abs(score - (-5.0)) < 1e-9

    # Case 3: No history (first exam)
    # weakness = (1 - 0.70) * 100 = 30
    # momentum = 0 (no previous)
    # priority = 30 + (0 * 2) = 30
    score = calculator.calculate_priority_score(0.70, None)
    assert abs(score - 30.0) < 1e-9


def test_rank_domains_by_priority(calculator):
    """Test ranking domains by priority score (weakness + momentum)"""
    current_exam = {
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.60},
            "Asset Security": {"accuracy": 0.85},
            "Communication & Network Security": {"accuracy": 0.70},
        }
    }

    previous_exam = {
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.50},
            "Asset Security": {"accuracy": 0.95},
            "Communication & Network Security": {"accuracy": 0.65},
        }
    }

    ranked = calculator.rank_domains_by_priority(current_exam, previous_exam)

    # Verify structure
    assert isinstance(ranked, list)
    assert len(ranked) == 3

    # Verify all domains are present
    domain_names = [item["domain"] for item in ranked]
    assert "Security & Risk Management" in domain_names
    assert "Asset Security" in domain_names
    assert "Communication & Network Security" in domain_names

    # Verify scores are calculated correctly and include all required fields
    # Security & Risk Management: weakness=40, momentum=10, priority=60 (RANK 1 - HIGHEST)
    # Communication & Network Security: weakness=30, momentum=5, priority=40 (RANK 2 - MIDDLE)
    # Asset Security: weakness=15, momentum=-10, priority=-5 (RANK 3 - LOWEST)
    assert ranked[0]["domain"] == "Security & Risk Management"
    assert abs(ranked[0]["current_accuracy"] - 0.60) < 1e-9
    assert abs(ranked[0]["previous_accuracy"] - 0.50) < 1e-9
    assert abs(ranked[0]["momentum"] - 10.0) < 1e-9
    assert abs(ranked[0]["priority_score"] - 60.0) < 1e-9
    assert ranked[0]["rank"] == 1

    assert ranked[1]["domain"] == "Communication & Network Security"
    assert abs(ranked[1]["current_accuracy"] - 0.70) < 1e-9
    assert abs(ranked[1]["previous_accuracy"] - 0.65) < 1e-9
    assert abs(ranked[1]["momentum"] - 5.0) < 1e-9
    assert abs(ranked[1]["priority_score"] - 40.0) < 1e-9
    assert ranked[1]["rank"] == 2

    assert ranked[2]["domain"] == "Asset Security"
    assert abs(ranked[2]["current_accuracy"] - 0.85) < 1e-9
    assert abs(ranked[2]["previous_accuracy"] - 0.95) < 1e-9
    assert abs(ranked[2]["momentum"] - (-10.0)) < 1e-9
    assert abs(ranked[2]["priority_score"] - (-5.0)) < 1e-9
    assert ranked[2]["rank"] == 3
