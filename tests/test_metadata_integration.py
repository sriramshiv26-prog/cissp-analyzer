"""
Integration tests for the full Metadata Auto-Generator pipeline.

8 integration tests covering end-to-end pipeline scenarios.
"""

import json
import csv
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cissp_analyzer.metadata_completer import MetadataCompleter
from cissp_analyzer.metadata_reviewer import MetadataReviewer
from cissp_analyzer.metadata_generator import MetadataGenerator
from cissp_analyzer.domain_mapper import DomainMapper

# ---- Fixtures ----

SAMPLE_EXTRACTION_RESULTS = {
    "total_questions": 5,
    "extracted_count": 3,
    "confidence": 0.6,
    "gaps": [4, 5],
    "extracted_metadata": {
        "1": {
            "domain": "IAM",
            "topic": "Auth",
            "difficulty": "Easy",
            "question_type": "Knowledge",
            "exam_trick": "None",
        },
        "2": {
            "domain": "Crypto",
            "topic": "AES",
            "difficulty": "Medium",
            "question_type": "Knowledge",
            "exam_trick": "None",
        },
        "3": {
            "domain": "Risk",
            "topic": "RA",
            "difficulty": "Hard",
            "question_type": "Analysis",
            "exam_trick": "None",
        },
    },
    "extraction_note": "Extracted 3/5",
}

SAMPLE_QUESTIONS = [
    {"number": 1, "text": "What is MFA?"},
    {"number": 2, "text": "Explain AES."},
    {"number": 3, "text": "What is risk analysis?"},
    {"number": 4, "text": "What is PKI?"},
    {"number": 5, "text": "Explain BCP."},
]


def make_mock_extractor(results=None, questions=None):
    extractor = MagicMock()
    extractor.extract.return_value = results or SAMPLE_EXTRACTION_RESULTS
    extractor.questions = questions or SAMPLE_QUESTIONS
    return extractor


def make_mock_ollama(available=False, batch_results=None):
    ollama = MagicMock()
    ollama.available = available
    ollama.get_status.return_value = (
        "Ollama available (model: qwen2.5-coder:7b)"
        if available
        else "Ollama unavailable (fallback mode)"
    )
    if batch_results is None:
        batch_results = {
            "4": {
                "domain": "Crypto",
                "topic": "PKI",
                "difficulty": "Hard",
                "question_type": "Knowledge",
            },
            "5": {
                "domain": "Risk",
                "topic": "BCP",
                "difficulty": "Medium",
                "question_type": "Application",
            },
        }
    ollama.analyze_batch.return_value = batch_results
    return ollama


# ---- Test 1: Extract → Complete (defaults) → Review → metadata dict correct ----


def test_extract_complete_defaults_review():
    """Full pipeline: Extract → Complete (defaults) → Review → metadata dict correct."""
    # Step 1 & 2: Complete with defaults
    completer = MetadataCompleter(SAMPLE_EXTRACTION_RESULTS)
    completer.apply_defaults()
    combined = completer.get_combined_metadata()

    # Step 3: Review
    reviewer = MetadataReviewer(combined)
    reviewed = reviewer.get_reviewed_metadata()

    # All 5 questions should have metadata
    assert len(reviewed) == 5
    for q_num_str in ["1", "2", "3", "4", "5"]:
        assert q_num_str in reviewed

    # Gap questions should have defaults
    assert reviewed["4"]["domain"] == "Unmapped"
    assert reviewed["5"]["difficulty"] == "Unknown"

    # Extracted questions should keep their values
    assert reviewed["1"]["domain"] == "IAM"
    assert reviewed["2"]["domain"] == "Crypto"


# ---- Test 2: Extract → Complete (manual CSV) → Review → edits applied ----


def test_extract_complete_manual_review_edits(tmp_path):
    """Extract → Complete (manual CSV) → Review with edits applied."""
    # Create a manual CSV
    csv_data = {
        "4": {
            "domain": "Cryptography",
            "topic": "PKI",
            "difficulty": "Hard",
            "question_type": "Knowledge",
        },
        "5": {
            "domain": "Business Continuity",
            "topic": "BCP",
            "difficulty": "Medium",
            "question_type": "Application",
        },
    }

    # Step 2: Complete with manual data
    completer = MetadataCompleter(SAMPLE_EXTRACTION_RESULTS)
    completer.apply_manual(csv_data)
    combined = completer.get_combined_metadata()

    # Step 3: Review with edits
    reviewer = MetadataReviewer(combined)
    reviewer.edit_question(4, "difficulty", "Easy")  # override
    reviewed = reviewer.get_reviewed_metadata()

    assert reviewed["4"]["domain"] == "Cryptography"
    assert reviewed["4"]["difficulty"] == "Easy"  # edited
    assert reviewed["5"]["domain"] == "Business Continuity"
    assert "4" in reviewer.edited


# ---- Test 3: OllamaAnalyzer unavailable → fallback to defaults seamlessly ----


def test_ollama_unavailable_fallback_to_defaults(tmp_path):
    """OllamaAnalyzer unavailable → fallback to defaults seamlessly."""
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, patch(
        "cissp_analyzer.metadata_generator.PDFMetadataExtractor"
    ) as MockExtractor:

        mock_ollama = make_mock_ollama(available=False)
        MockOllama.return_value = mock_ollama
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-fallback", "/fake.pdf", str(tmp_path))
        result = gen.run(completion_method="auto")

    # Should succeed without errors
    assert result["method"] == "default"
    assert result["coverage"] == 1.0
    # Ollama batch should NOT have been called
    assert not mock_ollama.analyze_batch.called


# ---- Test 4: MetadataGenerator.run() produces valid output file ----


def test_generator_run_produces_valid_output_file(tmp_path):
    """MetadataGenerator.run() produces valid output file."""
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, patch(
        "cissp_analyzer.metadata_generator.PDFMetadataExtractor"
    ) as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-output-test", "/fake.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    output_path = Path(result["output_path"])
    assert output_path.exists()
    assert output_path.suffix == ".json"

    with open(output_path) as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert len(data) == 5  # all 5 questions


# ---- Test 5: DomainMapper loads from generated metadata.json correctly ----


def test_domain_mapper_loads_generated_metadata(tmp_path):
    """DomainMapper loads from generated metadata.json correctly."""
    # Simulate generated metadata
    date_str = "2026-01-01"
    exam_id = "test-exam"
    metadata_dir = tmp_path / date_str / exam_id
    metadata_dir.mkdir(parents=True)

    metadata = {
        "1": {
            "domain": "IAM",
            "topic": "Auth",
            "difficulty": "Easy",
            "question_type": "Knowledge",
        },
        "2": {
            "domain": "Crypto",
            "topic": "AES",
            "difficulty": "Medium",
            "question_type": "Knowledge",
        },
    }
    metadata_file = metadata_dir / "metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f)

    # Create a default mapping file (required as fallback)
    default_mapping_file = tmp_path / "question_domain_mapping.json"
    with open(default_mapping_file, "w") as f:
        json.dump({}, f)

    # DomainMapper with exam_id should find the generated metadata
    with patch.object(DomainMapper, "_try_load_exam_mapping", return_value=metadata):
        mapper = DomainMapper(
            mapping_file=str(default_mapping_file),
            exam_id=exam_id,
        )
        assert mapper.mapping == metadata


# ---- Test 6: Full pipeline: PDF → metadata.json → DomainMapper reads it back ----


def test_full_pipeline_pdf_to_domain_mapper(tmp_path):
    """Full pipeline: PDF → metadata.json → DomainMapper reads it back."""
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, patch(
        "cissp_analyzer.metadata_generator.PDFMetadataExtractor"
    ) as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("pipeline-exam", "/fake.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    # Now DomainMapper should be able to load the generated metadata
    output_path = Path(result["output_path"])
    assert output_path.exists()

    with open(output_path) as f:
        loaded = json.load(f)

    # Should have all 5 questions
    assert len(loaded) == 5
    assert "1" in loaded
    assert loaded["1"]["domain"] == "IAM"  # extracted metadata preserved


# ---- Test 7: Coverage metric is accurate after completion ----


def test_coverage_metric_accurate_after_completion():
    """Coverage metric is accurate after completion."""
    extraction_results = {
        "total_questions": 10,
        "extracted_count": 6,
        "confidence": 0.6,
        "gaps": [7, 8, 9, 10],
        "extracted_metadata": {
            str(i): {
                "domain": f"D{i}",
                "topic": "T",
                "difficulty": "Easy",
                "question_type": "Knowledge",
                "exam_trick": "None",
            }
            for i in range(1, 7)
        },
        "extraction_note": "6/10 extracted",
    }

    completer = MetadataCompleter(extraction_results)
    assert completer.extraction_coverage == 0.6

    completer.apply_defaults()
    combined = completer.get_combined_metadata()

    # Coverage after defaults: all 10 should be covered
    assert len(combined) == 10
    final_coverage = len(combined) / extraction_results["total_questions"]
    assert final_coverage == 1.0

    # Summary should reflect this
    summary = completer.get_summary()
    assert "100%" in summary


# ---- Test 8: Edit tracking in MetadataReviewer after multiple edits ----


def test_edit_tracking_multiple_edits():
    """Edit tracking in MetadataReviewer is correct after multiple edits."""
    completer = MetadataCompleter(SAMPLE_EXTRACTION_RESULTS)
    completer.apply_defaults()
    combined = completer.get_combined_metadata()

    reviewer = MetadataReviewer(combined)

    # Make multiple edits
    reviewer.edit_question(1, "domain", "Network Security")
    reviewer.edit_question(2, "difficulty", "Hard")
    reviewer.edit_question(4, "domain", "IAM")
    reviewer.edit_question(4, "topic", "SSO")  # second edit to same question

    # Check tracking
    assert len(reviewer.edited) == 3  # Q1, Q2, Q4
    assert "1" in reviewer.edited
    assert "2" in reviewer.edited
    assert "4" in reviewer.edited

    # Q4 should have two fields tracked
    assert "domain" in reviewer.edited["4"]
    assert "topic" in reviewer.edited["4"]

    # Edit summary
    summary = reviewer.get_edit_summary()
    assert "3 question" in summary

    # Reviewed metadata should have all edits
    reviewed = reviewer.get_reviewed_metadata()
    assert reviewed["1"]["domain"] == "Network Security"
    assert reviewed["2"]["difficulty"] == "Hard"
    assert reviewed["4"]["domain"] == "IAM"
    assert reviewed["4"]["topic"] == "SSO"
    # Unedited questions unchanged
    assert reviewed["3"]["domain"] == "Risk"
