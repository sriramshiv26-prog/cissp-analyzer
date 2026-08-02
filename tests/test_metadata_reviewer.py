"""
Tests for MetadataReviewer - terminal display and inline editing.

At least 10 tests covering: init, display, edit, reviewed metadata, summary.
"""

import pytest
from cissp_analyzer.metadata_reviewer import MetadataReviewer

# --- Sample data helpers ---


def make_metadata(n=5):
    """Return metadata dict with n questions."""
    return {
        str(i): {
            "domain": f"Domain {i % 3 + 1}",
            "topic": f"Topic {i}",
            "difficulty": ["Easy", "Medium", "Hard"][i % 3],
            "question_type": "Knowledge",
            "exam_trick": "None",
        }
        for i in range(1, n + 1)
    }


# --- Initialization tests ---


def test_init_stores_metadata():
    meta = make_metadata(3)
    reviewer = MetadataReviewer(meta)
    assert len(reviewer.metadata) == 3


def test_init_edited_is_empty():
    reviewer = MetadataReviewer(make_metadata(3))
    assert reviewer.edited == {}


def test_init_does_not_mutate_original():
    meta = make_metadata(3)
    original_domain = meta["1"]["domain"]
    reviewer = MetadataReviewer(meta)
    reviewer.edit_question(1, "domain", "Changed")
    # original should be unchanged
    assert meta["1"]["domain"] == original_domain


def test_init_empty_metadata():
    reviewer = MetadataReviewer({})
    assert reviewer.metadata == {}
    assert reviewer.edited == {}


# --- Display tests ---


def test_display_summary_returns_string():
    reviewer = MetadataReviewer(make_metadata(5))
    result = reviewer.display_summary()
    assert isinstance(result, str)
    assert len(result) > 0


def test_display_summary_contains_headers():
    reviewer = MetadataReviewer(make_metadata(5))
    result = reviewer.display_summary()
    assert "Q#" in result
    assert "Domain" in result
    assert "Difficulty" in result
    assert "Topic" in result


def test_display_summary_shows_total():
    reviewer = MetadataReviewer(make_metadata(5))
    result = reviewer.display_summary()
    assert "Total questions: 5" in result


def test_display_summary_limits_to_20():
    meta = make_metadata(25)
    reviewer = MetadataReviewer(meta)
    result = reviewer.display_summary()
    assert "and 5 more" in result


def test_display_summary_shows_difficulty_breakdown():
    reviewer = MetadataReviewer(make_metadata(6))
    result = reviewer.display_summary()
    assert "Difficulty breakdown" in result


def test_display_summary_shows_domains_count():
    reviewer = MetadataReviewer(make_metadata(5))
    result = reviewer.display_summary()
    assert "Domains:" in result


# --- Edit tests ---


def test_edit_question_updates_field():
    reviewer = MetadataReviewer(make_metadata(5))
    reviewer.edit_question(1, "domain", "Cryptography")
    assert reviewer.metadata["1"]["domain"] == "Cryptography"


def test_edit_question_tracks_in_edited():
    reviewer = MetadataReviewer(make_metadata(5))
    reviewer.edit_question(2, "difficulty", "Hard")
    assert "2" in reviewer.edited
    assert reviewer.edited["2"]["difficulty"] == "Hard"


def test_edit_question_multiple_fields():
    reviewer = MetadataReviewer(make_metadata(5))
    reviewer.edit_question(1, "domain", "IAM")
    reviewer.edit_question(1, "difficulty", "Easy")
    assert reviewer.edited["1"]["domain"] == "IAM"
    assert reviewer.edited["1"]["difficulty"] == "Easy"


def test_edit_question_multiple_questions():
    reviewer = MetadataReviewer(make_metadata(5))
    reviewer.edit_question(1, "domain", "IAM")
    reviewer.edit_question(3, "domain", "Cryptography")
    assert len(reviewer.edited) == 2


def test_edit_question_invalid_q_num_raises():
    reviewer = MetadataReviewer(make_metadata(3))
    with pytest.raises(KeyError):
        reviewer.edit_question(99, "domain", "IAM")


def test_edit_question_empty_field_raises():
    reviewer = MetadataReviewer(make_metadata(3))
    with pytest.raises(ValueError):
        reviewer.edit_question(1, "", "value")


def test_edit_question_adds_new_field():
    reviewer = MetadataReviewer(make_metadata(3))
    reviewer.edit_question(1, "new_field", "new_value")
    assert reviewer.metadata["1"]["new_field"] == "new_value"


# --- get_reviewed_metadata tests ---


def test_get_reviewed_metadata_returns_dict():
    reviewer = MetadataReviewer(make_metadata(3))
    result = reviewer.get_reviewed_metadata()
    assert isinstance(result, dict)


def test_get_reviewed_metadata_includes_edits():
    reviewer = MetadataReviewer(make_metadata(3))
    reviewer.edit_question(1, "domain", "IAM")
    result = reviewer.get_reviewed_metadata()
    assert result["1"]["domain"] == "IAM"


def test_get_reviewed_metadata_is_copy():
    reviewer = MetadataReviewer(make_metadata(3))
    result = reviewer.get_reviewed_metadata()
    result["1"]["domain"] = "CHANGED"
    # reviewer's internal metadata should be unchanged
    assert reviewer.metadata["1"]["domain"] != "CHANGED"


# --- get_edit_summary tests ---


def test_get_edit_summary_no_edits():
    reviewer = MetadataReviewer(make_metadata(3))
    result = reviewer.get_edit_summary()
    assert "No edits" in result


def test_get_edit_summary_with_edits():
    reviewer = MetadataReviewer(make_metadata(3))
    reviewer.edit_question(1, "domain", "IAM")
    result = reviewer.get_edit_summary()
    assert "1 question" in result
    assert "Q1" in result
    assert "domain" in result


def test_get_edit_summary_multiple_edits():
    reviewer = MetadataReviewer(make_metadata(5))
    reviewer.edit_question(1, "domain", "IAM")
    reviewer.edit_question(2, "difficulty", "Hard")
    reviewer.edit_question(3, "domain", "Crypto")
    result = reviewer.get_edit_summary()
    assert "3 question" in result
    assert "Fields changed" in result


def test_get_edit_summary_shows_field_counts():
    reviewer = MetadataReviewer(make_metadata(3))
    reviewer.edit_question(1, "domain", "IAM")
    reviewer.edit_question(2, "domain", "Crypto")
    result = reviewer.get_edit_summary()
    assert "domain" in result
