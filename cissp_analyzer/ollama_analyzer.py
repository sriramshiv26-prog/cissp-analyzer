"""
OllamaAnalyzer - Optional Ollama enrichment for CISSP question classification.

Detects if Ollama is running locally, calls it to classify questions by
domain/difficulty/type, falls back gracefully if unavailable.
"""

import json
import logging
from typing import Dict, Optional

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass

logger = logging.getLogger(__name__)

CISSP_CLASSIFY_PROMPT = """Classify this CISSP exam question. Return ONLY valid JSON, no explanation:
{{"domain": "...", "topic": "...", "difficulty": "Easy|Medium|Hard", "question_type": "Knowledge|Application|Analysis"}}

Question: {q_text}"""


class OllamaAnalyzer:
    """Optional Ollama enrichment for CISSP question classification."""

    DEFAULT_MODEL = "qwen2.5-coder:7b"
    OLLAMA_URL = "http://localhost:11434"

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize OllamaAnalyzer with auto-detection.

        Args:
            model: Ollama model name to use
        """
        self.model = model
        self.available = self._check_ollama()

    def _check_ollama(self) -> bool:
        """
        Try GET /api/tags — return True if Ollama responds within 2s.

        Returns:
            True if Ollama is running and responding
        """
        try:
            url = f"{self.OLLAMA_URL}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Send a prompt to Ollama and return the response text.

        Args:
            prompt: The prompt text

        Returns:
            Response text or None on failure
        """
        if not self.available:
            return None

        try:
            url = f"{self.OLLAMA_URL}/api/generate"
            payload = json.dumps({
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }).encode("utf-8")

            req = urllib.request.Request(
                url,
                data=payload,
                method="POST",
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "")

        except Exception as e:
            logger.warning(f"Ollama call failed: {e}")
            return None

    def analyze_question(self, q_num: int, q_text: str) -> Optional[Dict]:
        """
        Send question text to Ollama, ask it to classify.

        Args:
            q_num: Question number
            q_text: Question text

        Returns:
            Dict with {domain, topic, difficulty, question_type} or None
        """
        if not self.available:
            logger.debug(f"Ollama unavailable, skipping Q{q_num}")
            return None

        prompt = CISSP_CLASSIFY_PROMPT.format(q_text=q_text)
        response = self._call_ollama(prompt)

        if not response:
            return None

        # Parse JSON from response
        try:
            # Try to find JSON in the response
            response = response.strip()

            # Look for first { and last }
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                logger.warning(f"No JSON found in Ollama response for Q{q_num}")
                return None

            json_str = response[start:end]
            parsed = json.loads(json_str)

            # Validate required keys
            required = {"domain", "topic", "difficulty", "question_type"}
            if not required.issubset(parsed.keys()):
                logger.warning(f"Missing keys in Ollama response for Q{q_num}: {parsed.keys()}")
                return None

            return {
                "domain": str(parsed.get("domain", "Unknown")),
                "topic": str(parsed.get("topic", "Unknown")),
                "difficulty": str(parsed.get("difficulty", "Unknown")),
                "question_type": str(parsed.get("question_type", "Unknown")),
            }

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Ollama JSON for Q{q_num}: {e}")
            return None

    def analyze_batch(self, questions: Dict[int, str]) -> Dict[str, Dict]:
        """
        Analyze multiple questions.

        Args:
            questions: {q_num (int): q_text (str)}

        Returns:
            {q_num_str: metadata_dict} — skips questions where analyze_question returns None
        """
        results: Dict[str, Dict] = {}

        for q_num, q_text in questions.items():
            result = self.analyze_question(q_num, q_text)
            if result is not None:
                results[str(q_num)] = result
            else:
                logger.debug(f"Skipping Q{q_num} (no result from Ollama)")

        logger.info(f"Ollama batch: {len(results)}/{len(questions)} questions classified")
        return results

    def get_status(self) -> str:
        """
        Return human-readable status of Ollama availability.

        Returns:
            Status string
        """
        if self.available:
            return f"Ollama available (model: {self.model})"
        return "Ollama unavailable (fallback mode)"
