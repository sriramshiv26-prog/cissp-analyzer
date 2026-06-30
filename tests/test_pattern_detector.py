import pytest
from cissp_analyzer.pattern_detector import PatternDetector


@pytest.fixture
def detector():
    """Create a PatternDetector instance for testing"""
    return PatternDetector()


@pytest.fixture
def sample_questions():
    """Create sample question data matching question_domain_mapping.json structure"""
    return {
        1: {"domain": 1, "topic": "Cryptography", "subtopic": "Kerberos",
            "difficulty": "Hard", "question_type": "Application", "exam_trick": "BEST"},
        2: {"domain": 1, "topic": "Cryptography", "subtopic": "Kerberos",
            "difficulty": "Hard", "question_type": "Application", "exam_trick": "BEST"},
        3: {"domain": 1, "topic": "Cryptography", "subtopic": "Kerberos",
            "difficulty": "Hard", "question_type": "Application", "exam_trick": "BEST"},

        4: {"domain": 1, "topic": "Cryptography", "subtopic": "SAML",
            "difficulty": "Medium", "question_type": "Scenario", "exam_trick": "NOT"},
        5: {"domain": 1, "topic": "Cryptography", "subtopic": "SAML",
            "difficulty": "Medium", "question_type": "Scenario", "exam_trick": "NOT"},
        6: {"domain": 1, "topic": "Cryptography", "subtopic": "SAML",
            "difficulty": "Medium", "question_type": "Application", "exam_trick": "BEST"},

        7: {"domain": 1, "topic": "Cryptography", "subtopic": "OAuth",
            "difficulty": "Medium", "question_type": "Scenario", "exam_trick": "NOT"},
        8: {"domain": 1, "topic": "Cryptography", "subtopic": "OAuth",
            "difficulty": "Medium", "question_type": "Scenario", "exam_trick": "NOT"},
        9: {"domain": 1, "topic": "Cryptography", "subtopic": "OAuth",
            "difficulty": "Medium", "question_type": "Application", "exam_trick": "BEST"},
    }


def test_detect_all_wrong_pattern(detector, sample_questions):
    """Test detection of 'all wrong' pattern for Kerberos subtopic"""
    # Create performance data: student got Kerberos questions wrong (q1, q2, q3)
    questions = [sample_questions[i] for i in [1, 2, 3]]
    # wrong_question_ids uses array indices [0, 1, 2] for questions at positions 0, 1, 2
    wrong_question_ids = [0, 1, 2]

    # Call detect_topic_pattern for Kerberos
    result = detector.detect_topic_pattern(questions, wrong_question_ids, "Kerberos")

    # Assertions
    assert result["topic"] == "Kerberos"
    assert result["correct"] == 0
    assert result["total"] == 3
    assert result["accuracy"] == 0.0
    assert result["all_wrong"] is True
    assert result["all_correct"] is False
    assert "ALL WRONG" in result["insight"]


def test_detect_weakness_by_question_type(detector, sample_questions):
    """Test detection of weakness by question type (Scenario vs Application)"""
    # SAML: q4,q5 are Scenario (wrong), q6 is Application (correct)
    questions = [sample_questions[i] for i in [4, 5, 6]]
    # wrong_question_ids uses array indices [0, 1] for questions at positions 0,1
    wrong_question_ids = [0, 1]

    result = detector.detect_topic_pattern(questions, wrong_question_ids, "SAML")

    # Assertions
    assert result["topic"] == "SAML"
    assert result["correct"] == 1
    assert result["total"] == 3
    assert result["accuracy"] == pytest.approx(0.333, abs=0.01)
    assert result["all_wrong"] is False
    assert result["all_correct"] is False

    # Check weakness_by_type structure
    assert "weakness_by_type" in result
    assert isinstance(result["weakness_by_type"], dict)
    assert "Scenario" in result["weakness_by_type"]
    # Scenario: 0/2 correct
    assert result["weakness_by_type"]["Scenario"]["accuracy"] == 0.0
    # Application: 1/1 correct
    assert result["weakness_by_type"]["Application"]["accuracy"] == 1.0

    # Insight should mention Scenario weakness
    assert "Scenario" in result["insight"]


def test_detect_trick_keyword_pattern(detector, sample_questions):
    """Test detection of weakness by exam trick keywords"""
    # OAuth: q7,q8 are NOT keyword (wrong), q9 is BEST keyword (correct)
    questions = [sample_questions[i] for i in [7, 8, 9]]
    # wrong_question_ids uses array indices [0, 1] for questions at positions 0,1
    wrong_question_ids = [0, 1]

    result = detector.detect_topic_pattern(questions, wrong_question_ids, "OAuth")

    # Assertions
    assert result["topic"] == "OAuth"
    assert result["correct"] == 1
    assert result["total"] == 3
    assert result["accuracy"] == pytest.approx(0.333, abs=0.01)

    # Check weakness_by_trick structure
    assert "weakness_by_trick" in result
    assert isinstance(result["weakness_by_trick"], dict)
    assert "NOT" in result["weakness_by_trick"]
    # NOT keyword: 0/2 correct
    assert result["weakness_by_trick"]["NOT"]["accuracy"] == 0.0
    # BEST keyword: 1/1 correct
    assert result["weakness_by_trick"]["BEST"]["accuracy"] == 1.0

    # Insight should mention NOT keyword as issue
    assert "NOT" in result["insight"]


def test_invalid_question_indices_raise_error(detector, sample_questions):
    """Test that out-of-bounds indices raise ValueError"""
    questions = [sample_questions[i] for i in [1, 2, 3]]

    # Index 999 is out of bounds (only 3 questions at indices 0-2)
    with pytest.raises(ValueError, match="Invalid question indices"):
        detector.detect_topic_pattern(questions, [999], "Kerberos")

    # Mix of valid and invalid indices
    with pytest.raises(ValueError, match="Invalid question indices"):
        detector.detect_topic_pattern(questions, [0, 1, 999], "Kerberos")
