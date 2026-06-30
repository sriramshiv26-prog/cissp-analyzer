import pytest
from cissp_analyzer.adaptive_plan_generator import AdaptivePlanGenerator


@pytest.fixture
def generator():
    return AdaptivePlanGenerator()


@pytest.fixture
def current_exam():
    """Current exam with performance by domain"""
    return {
        "exam_name": "Practice Test 3",
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.75},
            "Asset Security": {"accuracy": 0.68},
            "Communication & Network Security": {"accuracy": 0.55},
            "Identity & Access Management": {"accuracy": 0.62},
            "Software Development Security": {"accuracy": 0.48},
            "Security Assessment & Testing": {"accuracy": 0.70},
            "Security Operations": {"accuracy": 0.65},
            "Software Development Security": {"accuracy": 0.58}
        }
    }


@pytest.fixture
def previous_exam():
    """Previous exam for momentum calculation"""
    return {
        "exam_name": "Practice Test 2",
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.70},
            "Asset Security": {"accuracy": 0.65},
            "Communication & Network Security": {"accuracy": 0.50},
            "Identity & Access Management": {"accuracy": 0.58},
            "Software Development Security": {"accuracy": 0.42},
            "Security Assessment & Testing": {"accuracy": 0.68},
            "Security Operations": {"accuracy": 0.60},
            "Software Development Security": {"accuracy": 0.52}
        }
    }


def test_generate_study_plan_sheet(generator, current_exam, previous_exam):
    """Generate Adaptive Study Plan sheet with recommendations"""
    worksheet = generator.generate_sheet(current_exam, previous_exam)

    # Verify worksheet is created
    assert worksheet is not None

    # Verify sheet has content
    assert worksheet.max_row > 0

    # Collect all cell values
    values_set = set()
    values_list = []
    for row in worksheet.iter_rows(values_only=True):
        for cell in row:
            if cell is not None:
                values_set.add(cell)
                values_list.append(cell)

    # Verify Priority 1 section exists
    values_text = ' '.join(str(v) for v in values_list)
    assert 'Priority 1' in values_text or 'priority 1' in values_text.lower()

    # Verify Priority 2 section exists
    assert 'Priority 2' in values_text or 'priority 2' in values_text.lower()

    # Verify sheet has meaningful content
    assert len(values_set) > 5


def test_study_plan_includes_focus_areas(generator, current_exam, previous_exam):
    """Study plan includes actionable focus areas for weak domains"""
    worksheet = generator.generate_sheet(current_exam, previous_exam)

    # Collect all cell values
    values_set = set()
    for row in worksheet.iter_rows(values_only=True):
        for cell in row:
            if cell is not None:
                values_set.add(cell)

    # Verify weak domain (Communication & Network Security) appears
    # or verify "focus" keywords exist
    values_text = ' '.join(str(v) for v in values_set)

    # Check for actionable content keywords
    assert any(keyword in values_text.lower() for keyword in [
        'focus', 'review', 'practice', 'study', 'strengthen', 'improve'
    ])


def test_study_plan_with_single_exam(generator, current_exam):
    """Study plan works with only current exam (no previous)"""
    worksheet = generator.generate_sheet(current_exam, previous_exam=None)

    # Verify worksheet is created
    assert worksheet is not None
    assert worksheet.max_row > 0

    # Verify content exists
    values_set = set()
    for row in worksheet.iter_rows(values_only=True):
        for cell in row:
            if cell is not None:
                values_set.add(cell)

    # Verify priorities exist
    values_text = ' '.join(str(v) for v in values_set)
    assert 'Priority' in values_text


def test_study_plan_includes_strengths_section(generator, current_exam, previous_exam):
    """Study plan includes Strengths to Maintain section"""
    worksheet = generator.generate_sheet(current_exam, previous_exam)

    # Collect all cell values
    values_list = []
    for row in worksheet.iter_rows(values_only=True):
        for cell in row:
            if cell is not None:
                values_list.append(cell)

    values_text = ' '.join(str(v) for v in values_list)

    # Verify strengths section exists
    assert 'Strengths' in values_text or 'strength' in values_text.lower()
