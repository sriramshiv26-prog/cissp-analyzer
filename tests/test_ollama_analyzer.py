"""
Tests for OllamaAnalyzer - optional Ollama enrichment with runtime detection.

At least 12 tests. Mocks HTTP calls — does not require Ollama running.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, call
from cissp_analyzer.ollama_analyzer import OllamaAnalyzer


# ---- Helpers ----

def make_ollama_tags_response(status=200):
    """Create a mock /api/tags response."""
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def make_ollama_generate_response(content: dict):
    """Create a mock /api/generate response with JSON content."""
    resp = MagicMock()
    resp.status = 200
    resp.read.return_value = json.dumps({"response": json.dumps(content)}).encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def make_ollama_generate_raw_response(raw_text: str):
    """Create a mock /api/generate response with raw text."""
    resp = MagicMock()
    resp.read.return_value = json.dumps({"response": raw_text}).encode()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


# ---- Init tests ----

def test_init_default_model():
    with patch("urllib.request.urlopen", side_effect=Exception("no ollama")):
        analyzer = OllamaAnalyzer()
    assert analyzer.model == OllamaAnalyzer.DEFAULT_MODEL


def test_init_custom_model():
    with patch("urllib.request.urlopen", side_effect=Exception("no ollama")):
        analyzer = OllamaAnalyzer(model="custom-model:latest")
    assert analyzer.model == "custom-model:latest"


def test_init_available_when_ollama_running():
    mock_resp = make_ollama_tags_response(200)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        analyzer = OllamaAnalyzer()
    assert analyzer.available is True


def test_init_unavailable_when_ollama_down():
    with patch("urllib.request.urlopen", side_effect=Exception("connection refused")):
        analyzer = OllamaAnalyzer()
    assert analyzer.available is False


# ---- _check_ollama tests ----

def test_check_ollama_returns_true_on_200():
    mock_resp = make_ollama_tags_response(200)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        analyzer = OllamaAnalyzer.__new__(OllamaAnalyzer)
        analyzer.model = OllamaAnalyzer.DEFAULT_MODEL
        result = analyzer._check_ollama()
    assert result is True


def test_check_ollama_returns_false_on_exception():
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        analyzer = OllamaAnalyzer.__new__(OllamaAnalyzer)
        analyzer.model = OllamaAnalyzer.DEFAULT_MODEL
        result = analyzer._check_ollama()
    assert result is False


# ---- analyze_question tests ----

def test_analyze_question_success():
    tags_resp = make_ollama_tags_response(200)
    gen_resp = make_ollama_generate_response({
        "domain": "Security and Risk Management",
        "topic": "Risk assessment",
        "difficulty": "Medium",
        "question_type": "Analysis",
    })

    def side_effect(req, timeout=None):
        if "tags" in req.full_url:
            return tags_resp
        return gen_resp

    with patch("urllib.request.urlopen", side_effect=side_effect):
        analyzer = OllamaAnalyzer()

    with patch("urllib.request.urlopen", return_value=gen_resp):
        result = analyzer.analyze_question(1, "What is risk management?")

    assert result is not None
    assert result["domain"] == "Security and Risk Management"
    assert result["difficulty"] == "Medium"
    assert result["question_type"] == "Analysis"


def test_analyze_question_returns_none_when_unavailable():
    with patch("urllib.request.urlopen", side_effect=Exception("no ollama")):
        analyzer = OllamaAnalyzer()

    result = analyzer.analyze_question(1, "What is AES?")
    assert result is None


def test_analyze_question_parse_failure_returns_none():
    tags_resp = make_ollama_tags_response(200)
    gen_resp = make_ollama_generate_raw_response("This is not JSON at all")

    def side_effect(req, timeout=None):
        if "tags" in req.full_url:
            return tags_resp
        return gen_resp

    with patch("urllib.request.urlopen", side_effect=side_effect):
        analyzer = OllamaAnalyzer()

    with patch("urllib.request.urlopen", return_value=gen_resp):
        result = analyzer.analyze_question(1, "What is RSA?")

    assert result is None


def test_analyze_question_missing_keys_returns_none():
    tags_resp = make_ollama_tags_response(200)
    # Response missing required keys
    gen_resp = make_ollama_generate_response({"domain": "IAM"})

    def side_effect(req, timeout=None):
        if "tags" in req.full_url:
            return tags_resp
        return gen_resp

    with patch("urllib.request.urlopen", side_effect=side_effect):
        analyzer = OllamaAnalyzer()

    with patch("urllib.request.urlopen", return_value=gen_resp):
        result = analyzer.analyze_question(1, "What is RBAC?")

    assert result is None


def test_analyze_question_handles_json_embedded_in_text():
    """Test that JSON can be extracted from text with extra content around it."""
    tags_resp = make_ollama_tags_response(200)
    json_content = {
        "domain": "Cryptography",
        "topic": "Symmetric encryption",
        "difficulty": "Easy",
        "question_type": "Knowledge",
    }
    # Simulate text around JSON
    raw = f"Here is the classification:\n{json.dumps(json_content)}\nDone."
    gen_resp = make_ollama_generate_raw_response(raw)

    def side_effect(req, timeout=None):
        if "tags" in req.full_url:
            return tags_resp
        return gen_resp

    with patch("urllib.request.urlopen", side_effect=side_effect):
        analyzer = OllamaAnalyzer()

    with patch("urllib.request.urlopen", return_value=gen_resp):
        result = analyzer.analyze_question(5, "What is AES-256?")

    assert result is not None
    assert result["domain"] == "Cryptography"


# ---- analyze_batch tests ----

def test_analyze_batch_unavailable_returns_empty():
    with patch("urllib.request.urlopen", side_effect=Exception("no ollama")):
        analyzer = OllamaAnalyzer()

    result = analyzer.analyze_batch({1: "Q1 text", 2: "Q2 text"})
    assert result == {}


def test_analyze_batch_success():
    tags_resp = make_ollama_tags_response(200)
    gen_resp = make_ollama_generate_response({
        "domain": "IAM",
        "topic": "Authentication",
        "difficulty": "Medium",
        "question_type": "Knowledge",
    })

    def side_effect(req, timeout=None):
        if "tags" in req.full_url:
            return tags_resp
        return gen_resp

    with patch("urllib.request.urlopen", side_effect=side_effect):
        analyzer = OllamaAnalyzer()

    with patch("urllib.request.urlopen", return_value=gen_resp):
        result = analyzer.analyze_batch({1: "Q1", 2: "Q2", 3: "Q3"})

    assert len(result) == 3
    assert "1" in result
    assert "2" in result
    assert "3" in result


def test_analyze_batch_uses_string_keys():
    tags_resp = make_ollama_tags_response(200)
    gen_resp = make_ollama_generate_response({
        "domain": "IAM",
        "topic": "Auth",
        "difficulty": "Easy",
        "question_type": "Knowledge",
    })

    def side_effect(req, timeout=None):
        if "tags" in req.full_url:
            return tags_resp
        return gen_resp

    with patch("urllib.request.urlopen", side_effect=side_effect):
        analyzer = OllamaAnalyzer()

    with patch("urllib.request.urlopen", return_value=gen_resp):
        result = analyzer.analyze_batch({42: "some question"})

    assert "42" in result
    assert 42 not in result


# ---- get_status tests ----

def test_get_status_available():
    mock_resp = make_ollama_tags_response(200)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        analyzer = OllamaAnalyzer(model="qwen2.5-coder:7b")

    status = analyzer.get_status()
    assert "available" in status
    assert "qwen2.5-coder:7b" in status


def test_get_status_unavailable():
    with patch("urllib.request.urlopen", side_effect=Exception("no ollama")):
        analyzer = OllamaAnalyzer()

    status = analyzer.get_status()
    assert "unavailable" in status
    assert "fallback" in status
