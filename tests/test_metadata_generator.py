"""
Tests for MetadataGenerator - full pipeline orchestrator.

At least 10 tests. Mocks PDFMetadataExtractor and OllamaAnalyzer.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from cissp_analyzer.metadata_generator import MetadataGenerator


# ---- Fixtures / Helpers ----

SAMPLE_EXTRACTION_RESULTS = {
    "total_questions": 5,
    "extracted_count": 3,
    "confidence": 0.6,
    "gaps": [4, 5],
    "extracted_metadata": {
        "1": {"domain": "IAM", "topic": "Auth", "difficulty": "Easy", "question_type": "Knowledge", "exam_trick": "None"},
        "2": {"domain": "Crypto", "topic": "AES", "difficulty": "Medium", "question_type": "Knowledge", "exam_trick": "None"},
        "3": {"domain": "Risk", "topic": "RA", "difficulty": "Hard", "question_type": "Analysis", "exam_trick": "None"},
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
        "Ollama available (model: qwen2.5-coder:7b)" if available
        else "Ollama unavailable (fallback mode)"
    )
    if batch_results is None:
        batch_results = {
            "4": {"domain": "Crypto", "topic": "PKI", "difficulty": "Hard", "question_type": "Knowledge"},
            "5": {"domain": "Risk", "topic": "BCP", "difficulty": "Medium", "question_type": "Application"},
        }
    ollama.analyze_batch.return_value = batch_results
    return ollama


# ---- Init tests ----

def test_init_sets_exam_id(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama:
        MockOllama.return_value = make_mock_ollama(available=False)
        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
    assert gen.exam_id == "exam-001"


def test_init_sets_pdf_path(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama:
        MockOllama.return_value = make_mock_ollama(available=False)
        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
    assert gen.pdf_path == "/fake/path.pdf"


def test_init_sets_output_dir(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama:
        MockOllama.return_value = make_mock_ollama(available=False)
        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
    assert gen.output_dir == tmp_path


def test_init_creates_ollama_instance(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama:
        MockOllama.return_value = make_mock_ollama()
        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
    assert MockOllama.called


# ---- run() tests ----

def test_run_defaults_returns_dict(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    assert isinstance(result, dict)
    assert "exam_id" in result
    assert "total_questions" in result
    assert "coverage" in result
    assert "method" in result
    assert "output_path" in result


def test_run_defaults_uses_defaults_method(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    assert result["method"] == "default"


def test_run_auto_with_ollama_available(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        mock_ollama = make_mock_ollama(available=True)
        MockOllama.return_value = mock_ollama
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="auto")

    assert result["method"] == "ai"
    assert mock_ollama.analyze_batch.called


def test_run_auto_without_ollama_falls_back_to_default(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="auto")

    assert result["method"] == "default"


def test_run_saves_json_file(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    output_path = Path(result["output_path"])
    assert output_path.exists()
    assert output_path.name == "metadata.json"


def test_run_json_is_valid(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    with open(result["output_path"]) as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert len(data) > 0


def test_run_output_path_structure(tmp_path):
    """Output path should be output_dir/YYYY-MM-DD/exam_id/metadata.json"""
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("my-exam", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    output_path = Path(result["output_path"])
    # Structure: tmp_path/YYYY-MM-DD/my-exam/metadata.json
    assert output_path.name == "metadata.json"
    assert output_path.parent.name == "my-exam"
    # Grandparent is a date
    date_dir = output_path.parent.parent.name
    assert len(date_dir) == 10  # YYYY-MM-DD
    assert date_dir[4] == "-"


def test_run_coverage_metric(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("exam-001", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    # 5 questions total, all should be covered after defaults applied
    assert result["total_questions"] == 5
    assert result["coverage"] == 1.0


def test_run_returns_exam_id(tmp_path):
    with patch("cissp_analyzer.metadata_generator.OllamaAnalyzer") as MockOllama, \
         patch("cissp_analyzer.metadata_generator.PDFMetadataExtractor") as MockExtractor:
        MockOllama.return_value = make_mock_ollama(available=False)
        MockExtractor.return_value = make_mock_extractor()

        gen = MetadataGenerator("my-special-exam", "/fake/path.pdf", str(tmp_path))
        result = gen.run(completion_method="defaults")

    assert result["exam_id"] == "my-special-exam"
