"""
Tests for Metadata Completer - Handles filling metadata gaps.

Tests MetadataCompleter initialization, default metadata application,
manual metadata application, and metadata combination.
"""

import pytest
from cissp_analyzer.metadata_completer import MetadataCompleter


def test_completer_initializes():
    """Test MetadataCompleter with extraction results"""
    extraction_results = {
        "total_questions": 50,
        "extracted_count": 20,
        "confidence": 0.4,
        "gaps": [21, 22, 23],
        "extracted_metadata": {"1": {"domain": "Security"}},
        "extraction_note": "Extracted 40%",
    }

    completer = MetadataCompleter(extraction_results)
    assert completer.total_questions == 50
    assert len(completer.gaps) == 3
    assert completer.extracted_count == 20
    assert completer.extraction_coverage == 0.4


def test_completer_apply_defaults():
    """Test applying defaults to gaps (NO Ollama needed)"""
    extraction_results = {
        "total_questions": 3,
        "extracted_count": 1,
        "confidence": 0.33,
        "gaps": [2, 3],
        "extracted_metadata": {"1": {"domain": "Security"}},
        "extraction_note": "Extracted 33%",
    }

    completer = MetadataCompleter(extraction_results)
    completer.apply_defaults()
    metadata = completer.get_combined_metadata()

    assert len(metadata) == 3
    assert metadata["1"]["domain"] == "Security"
    assert metadata["2"]["domain"] == "Unmapped"
    assert metadata["2"]["topic"] == "Unmapped"
    assert metadata["3"]["domain"] == "Unmapped"
    assert metadata["3"]["difficulty"] == "Unknown"


def test_completer_apply_manual():
    """Test applying user-provided manual metadata"""
    extraction_results = {
        "total_questions": 3,
        "extracted_count": 1,
        "confidence": 0.33,
        "gaps": [2, 3],
        "extracted_metadata": {"1": {"domain": "Security"}},
        "extraction_note": "Extracted 33%",
    }

    completer = MetadataCompleter(extraction_results)
    manual_data = {
        "2": {"domain": "Access", "topic": "IAM"},
        "3": {"domain": "Crypto", "topic": "PKI"},
    }
    completer.apply_manual(manual_data)
    metadata = completer.get_combined_metadata()

    assert metadata["2"]["domain"] == "Access"
    assert metadata["2"]["topic"] == "IAM"
    assert metadata["3"]["domain"] == "Crypto"
    assert metadata["3"]["topic"] == "PKI"


def test_completer_get_options():
    """Test that completer shows available options"""
    extraction_results = {
        "total_questions": 50,
        "extracted_count": 20,
        "confidence": 0.4,
        "gaps": [21, 22, 23],
        "extracted_metadata": {},
        "extraction_note": "Extracted 40%",
    }

    completer = MetadataCompleter(extraction_results)
    options = completer.get_fallback_options()

    assert len(options) >= 2  # At least DEFAULT and MANUAL
    assert any("default" in opt.lower() for opt in options)
    assert any("manual" in opt.lower() for opt in options)


def test_completer_apply_ollama_results():
    """Test applying Ollama-generated metadata"""
    extraction_results = {
        "total_questions": 3,
        "extracted_count": 1,
        "confidence": 0.33,
        "gaps": [2, 3],
        "extracted_metadata": {"1": {"domain": "Security"}},
        "extraction_note": "Extracted 33%",
    }

    completer = MetadataCompleter(extraction_results)
    ollama_data = {
        "2": {"domain": "Network", "topic": "TCP/IP"},
        "3": {"domain": "Crypto", "topic": "Algorithms"},
    }
    completer.apply_ollama_results(ollama_data)
    metadata = completer.get_combined_metadata()

    assert metadata["2"]["domain"] == "Network"
    assert metadata["3"]["domain"] == "Crypto"
    assert completer.completion_method == "ai"


def test_completer_get_summary():
    """Test summary generation"""
    extraction_results = {
        "total_questions": 10,
        "extracted_count": 6,
        "confidence": 0.6,
        "gaps": [7, 8, 9, 10],
        "extracted_metadata": {str(i): {"domain": f"Domain{i}"} for i in range(1, 7)},
        "extraction_note": "Extracted 60%",
    }

    completer = MetadataCompleter(extraction_results)
    completer.apply_defaults()
    summary = completer.get_summary()

    assert "60%" in summary
    assert "100%" in summary  # After defaults, should be 100%
    assert "DEFAULT" in summary


def test_completer_combined_metadata_order():
    """Test that manually provided data overwrites extracted data"""
    extraction_results = {
        "total_questions": 2,
        "extracted_count": 2,
        "confidence": 1.0,
        "gaps": [],
        "extracted_metadata": {
            "1": {"domain": "Security", "topic": "OldTopic"},
            "2": {"domain": "Network"},
        },
        "extraction_note": "Extracted 100%",
    }

    completer = MetadataCompleter(extraction_results)
    manual_data = {"1": {"domain": "Security", "topic": "NewTopic"}}  # Override topic
    completer.apply_manual(manual_data)
    metadata = completer.get_combined_metadata()

    # Manual should override extracted
    assert metadata["1"]["topic"] == "NewTopic"
    assert metadata["1"]["domain"] == "Security"
    assert metadata["2"]["domain"] == "Network"


def test_completer_with_empty_extraction():
    """Test completer with zero extracted metadata"""
    extraction_results = {
        "total_questions": 5,
        "extracted_count": 0,
        "confidence": 0.0,
        "gaps": [1, 2, 3, 4, 5],
        "extracted_metadata": {},
        "extraction_note": "Extracted 0%",
    }

    completer = MetadataCompleter(extraction_results)
    completer.apply_defaults()
    metadata = completer.get_combined_metadata()

    assert len(metadata) == 5
    assert all(m["domain"] == "Unmapped" for m in metadata.values())


def test_completer_completion_method_tracking():
    """Test that completion method is tracked correctly"""
    extraction_results = {
        "total_questions": 2,
        "extracted_count": 1,
        "confidence": 0.5,
        "gaps": [2],
        "extracted_metadata": {"1": {"domain": "Security"}},
        "extraction_note": "Extracted 50%",
    }

    completer = MetadataCompleter(extraction_results)
    assert completer.completion_method is None

    completer.apply_defaults()
    assert completer.completion_method == "default"

    completer2 = MetadataCompleter(extraction_results)
    completer2.apply_manual({"2": {"domain": "Network"}})
    assert completer2.completion_method == "manual"
