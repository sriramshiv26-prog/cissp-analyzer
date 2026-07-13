import pytest
from cissp_analyzer.domain_mapper import DomainMapper


@pytest.fixture
def domain_mapper():
    return DomainMapper(mapping_file="data/question_domain_mapping.json")


def test_load_mapping(domain_mapper):
    """Test that mapping loads correctly"""
    assert domain_mapper.mapping is not None
    assert len(domain_mapper.mapping) > 0


def test_get_question_metadata(domain_mapper):
    """Test getting metadata for a specific question"""
    meta = domain_mapper.get_question_metadata(31)
    assert meta is not None
    assert "domain" in meta
    assert "topic" in meta


def test_question_31_metadata(domain_mapper):
    """Test that Q31 is correctly mapped to Asset Management"""
    meta = domain_mapper.get_question_metadata(31)
    assert meta["domain"] == 2
    assert "Asset" in meta["topic"]


def test_question_58_metadata(domain_mapper):
    """Test that Q58 is correctly mapped to Testing"""
    meta = domain_mapper.get_question_metadata(58)
    assert meta["domain"] == 6
    assert isinstance(meta["topic"], str)


def test_all_questions_have_metadata(domain_mapper):
    """Test that all mapped questions have required fields"""
    all_questions = domain_mapper.get_all_questions()
    for qnum_str, meta in all_questions.items():
        assert meta is not None, f"Question {qnum_str} missing metadata"
        assert all(k in meta for k in ["domain", "topic"])


def test_invalid_question_returns_none(domain_mapper):
    """Test that invalid question numbers return None"""
    assert domain_mapper.get_question_metadata(999) is None
