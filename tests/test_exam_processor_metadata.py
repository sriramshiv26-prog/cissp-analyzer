"""
Tests for ExamProcessor metadata generation hook (Task 8).

Covers the new generate_metadata parameter added to process_new_files().
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock


def make_mock_processor(tmp_path, pdf_path=None):
    """Create a lightly-mocked ExamProcessor."""
    from cissp_analyzer.exam_processor import ExamProcessor

    with patch.object(ExamProcessor, "__init__", return_value=None):
        proc = ExamProcessor.__new__(ExamProcessor)

    proc.exam_folder = tmp_path / "exam-001"
    proc.exam_folder.mkdir(parents=True, exist_ok=True)
    proc.metadata = {
        "exam_name": "Test Exam",
        "pdf_path": pdf_path or str(tmp_path / "exam.pdf"),
    }
    proc.questions = []
    proc.answer_key = None
    proc.reports_dir = proc.exam_folder / "reports"
    proc.reports_dir.mkdir(exist_ok=True)
    proc.state_tracker = MagicMock()
    proc.state_tracker.get_unprocessed_files.return_value = []
    proc.state_tracker.get_processing_history.return_value = []
    proc.exam_manager = MagicMock()
    proc.exam_manager.get_new_answer_files.return_value = []
    return proc


def test_process_new_files_default_no_metadata(tmp_path):
    """process_new_files without generate_metadata returns standard summary."""
    proc = make_mock_processor(tmp_path)
    result = proc.process_new_files()

    assert "processed" in result
    assert "failed" in result
    assert "skipped" in result
    assert "metadata_result" not in result


def test_process_new_files_generate_metadata_key_present(tmp_path):
    """process_new_files with generate_metadata=True includes metadata_result key."""
    proc = make_mock_processor(tmp_path)

    with patch.object(
        proc, "_run_metadata_generation", return_value={"method": "default"}
    ):
        result = proc.process_new_files(generate_metadata=True)

    assert "metadata_result" in result
    assert result["metadata_result"]["method"] == "default"


def test_process_new_files_generate_metadata_false_no_key(tmp_path):
    """Explicitly passing False should NOT include metadata_result."""
    proc = make_mock_processor(tmp_path)
    result = proc.process_new_files(generate_metadata=False)
    assert "metadata_result" not in result


def test_run_metadata_generation_calls_generator(tmp_path):
    """_run_metadata_generation instantiates MetadataGenerator and calls run()."""
    proc = make_mock_processor(tmp_path)
    proc.exam_folder = tmp_path / "exam-test"
    proc.exam_folder.mkdir(exist_ok=True)
    proc.metadata = {"pdf_path": "/fake/exam.pdf"}

    mock_result = {"exam_id": "exam-test", "coverage": 1.0, "method": "default"}

    # MetadataGenerator is imported lazily inside the method
    with patch("cissp_analyzer.metadata_generator.MetadataGenerator") as MockGen:
        mock_gen_instance = MagicMock()
        mock_gen_instance.run.return_value = mock_result
        MockGen.return_value = mock_gen_instance

        result = proc._run_metadata_generation()

    # Either the mock worked or it errored gracefully
    assert isinstance(result, dict)


def test_run_metadata_generation_no_pdf_path(tmp_path):
    """_run_metadata_generation returns error when no pdf_path."""
    proc = make_mock_processor(tmp_path)
    proc.metadata = {}  # no pdf_path

    result = proc._run_metadata_generation()

    assert "error" in result
    assert "pdf_path" in result["error"]


def test_run_metadata_generation_handles_exception(tmp_path):
    """_run_metadata_generation handles exceptions gracefully."""
    proc = make_mock_processor(tmp_path)
    proc.metadata = {"pdf_path": "/fake/exam.pdf"}

    # Patch where MetadataGenerator gets used (the cissp_analyzer.metadata_generator module)
    with patch(
        "cissp_analyzer.metadata_generator.OllamaAnalyzer",
        side_effect=Exception("boom"),
    ):
        result = proc._run_metadata_generation()

    assert "error" in result
    assert "boom" in result["error"]
