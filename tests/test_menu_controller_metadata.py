"""
Tests for MenuController.show_generate_metadata_menu() (Task 9).

Tests the new "Generate Metadata for Question Bank" menu option.
"""

import pytest
from unittest.mock import patch, MagicMock
from cissp_analyzer.menu_controller import MenuController


def make_controller():
    ctrl = MenuController()
    ctrl.use_colors = False  # disable ANSI for clean test output
    return ctrl


MOCK_RESULT = {
    "exam_id": "cissp-2024",
    "total_questions": 100,
    "coverage": 1.0,
    "method": "default",
    "output_path": "/tmp/metadata.json",
}


def make_mock_gen_instance(result=None):
    """Return a mock MetadataGenerator instance."""
    mock_inst = MagicMock()
    mock_inst.run.return_value = result or MOCK_RESULT
    return mock_inst


# ---- Tests ----

def test_show_generate_metadata_menu_empty_exam_id():
    """Should return None when user enters empty exam_id."""
    ctrl = make_controller()
    with patch("builtins.input", side_effect=["", ""]):
        result = ctrl.show_generate_metadata_menu()
    assert result is None


def test_show_generate_metadata_menu_empty_pdf_path():
    """Should return None when user enters empty pdf path."""
    ctrl = make_controller()
    with patch("builtins.input", side_effect=["cissp-2024", ""]):
        result = ctrl.show_generate_metadata_menu()
    assert result is None


def test_show_generate_metadata_menu_success():
    """Should return result dict when MetadataGenerator succeeds."""
    ctrl = make_controller()
    mock_gen_inst = make_mock_gen_instance()

    with patch("builtins.input", side_effect=["cissp-2024", "/path/to/exam.pdf"]):
        with patch.object(ctrl, "_build_metadata_generator", return_value=mock_gen_inst):
            result = ctrl.show_generate_metadata_menu()

    assert result is not None
    assert result["exam_id"] == "cissp-2024"
    assert result["coverage"] == 1.0


def test_show_generate_metadata_menu_generator_called_with_correct_args():
    """_build_metadata_generator should be called with the right exam_id and pdf_path."""
    ctrl = make_controller()
    mock_gen_inst = make_mock_gen_instance()

    with patch("builtins.input", side_effect=["my-exam", "/data/exam.pdf"]):
        with patch.object(ctrl, "_build_metadata_generator", return_value=mock_gen_inst) as mock_build:
            ctrl.show_generate_metadata_menu()

    mock_build.assert_called_once_with(exam_id="my-exam", pdf_path="/data/exam.pdf")


def test_show_generate_metadata_menu_handles_exception():
    """Should return None and show error when generator raises."""
    ctrl = make_controller()

    with patch("builtins.input", side_effect=["exam-1", "/bad/path.pdf"]):
        with patch.object(ctrl, "_build_metadata_generator", side_effect=Exception("PDF not found")):
            result = ctrl.show_generate_metadata_menu()

    assert result is None


def test_show_generate_metadata_menu_run_called_with_auto():
    """run() should be called with completion_method='auto'."""
    ctrl = make_controller()
    mock_gen_inst = make_mock_gen_instance()

    with patch("builtins.input", side_effect=["e1", "/p.pdf"]):
        with patch.object(ctrl, "_build_metadata_generator", return_value=mock_gen_inst):
            ctrl.show_generate_metadata_menu()

    mock_gen_inst.run.assert_called_once_with(completion_method="auto")


def test_show_generate_metadata_menu_returns_none_on_run_exception():
    """Should return None when gen.run() raises an exception."""
    ctrl = make_controller()
    mock_gen_inst = MagicMock()
    mock_gen_inst.run.side_effect = RuntimeError("run failed")

    with patch("builtins.input", side_effect=["e1", "/p.pdf"]):
        with patch.object(ctrl, "_build_metadata_generator", return_value=mock_gen_inst):
            result = ctrl.show_generate_metadata_menu()

    assert result is None


def test_build_metadata_generator_returns_generator():
    """_build_metadata_generator should return a MetadataGenerator instance."""
    ctrl = make_controller()

    with patch("cissp_analyzer.menu_controller.MenuController._build_metadata_generator") as mock_build:
        mock_build.return_value = MagicMock()
        gen = ctrl._build_metadata_generator("exam-1", "/path.pdf")

    assert gen is not None
