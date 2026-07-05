import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union
from pypdf import PdfReader

logger = logging.getLogger(__name__)


class AnswerKeyExtractor:
    """Extracts answer keys from PDF files with full answer text.

    This class extracts answers in the format:
    {"1": {"letter": "A", "text": "Full answer explanation"}, ...}

    It handles various answer key formats:
    - "1: B - AES is a symmetric encryption algorithm"
    - "1: B"
    - Multi-line answer explanations
    """

    # Valid answer letters
    VALID_ANSWERS = {"A", "B", "C", "D", "E"}

    def __init__(self) -> None:
        """Initialize the AnswerKeyExtractor."""
        self.answers: Dict[str, Dict[str, str]] = {}

    def extract_from_file(self, pdf_path: str) -> Dict[str, Dict[str, str]]:
        """Extract answer key from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with format: {"1": {"letter": "A", "text": "..."}, ...}

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF cannot be read or no answers found
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            reader = PdfReader(str(pdf_file))
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text()
        except Exception as e:
            raise ValueError(f"Failed to read PDF {pdf_path}: {str(e)}")

        return self.extract_answers(all_text)

    def extract_answers(self, text: str) -> Dict[str, Dict[str, str]]:
        """Extract answer key from text.

        Args:
            text: Text content from PDF or document

        Returns:
            Dictionary with format: {"1": {"letter": "A", "text": "..."}, ...}
        """
        self.answers = {}

        # Find the answer section
        answer_section = self._find_answer_section(text)
        if not answer_section:
            logger.warning("No answer section found in text")
            return self.answers

        # Extract answer pairs
        self._extract_answer_pairs(answer_section)

        return self.answers

    def _find_answer_section(self, text: str) -> Optional[str]:
        """Find the answer section in the text.

        Args:
            text: Full text content

        Returns:
            Answer section text, or None if not found
        """
        # Look for common answer section markers
        patterns = [
            r"(?:Answer\s*Key|ANSWER\s*KEY|Answers|ANSWERS)[:\s]+(.*?)(?:\n\n|$)",
            r"(?:KEY|Key)[:\s]+(.*?)(?:\n\n|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1)

        # If no explicit section marker, try to find answer patterns anywhere
        # Look for pattern like "1: B" or "1: B - text"
        if re.search(r"^\d+\s*:\s*[A-E]", text, re.MULTILINE):
            return text

        return None

    def _extract_answer_pairs(self, text: str) -> None:
        """Extract question-answer pairs from answer section text.

        Handles formats like:
        - "1: B"
        - "1: B - AES is symmetric"
        - Multi-line explanations with leading whitespace

        Args:
            text: Answer section text
        """
        # Pattern to match "Q: LETTER" with optional text after dash
        # Key: capture everything until next question number or end
        pattern = r"^(\d+)\s*:\s*([A-E])(?:\s*-\s*([^\n]*(?:\n(?!^\d+\s*:)[^\n]*)*))?(?=^\d+\s*:|$)"

        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)

        for match in matches:
            q_num = match.group(1)
            letter = match.group(2)
            explanation = match.group(3) if match.group(3) else ""

            # Clean up explanation text
            if explanation:
                # Remove leading/trailing whitespace
                explanation = explanation.strip()
                # Split into lines and clean each line
                lines = explanation.split("\n")
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line:
                        cleaned_lines.append(line)
                # Join lines with space
                explanation = " ".join(cleaned_lines)
                # Remove trailing continuation markers if any
                if explanation.endswith("."):
                    explanation = explanation[:-1].strip()

            if self._is_valid_answer(letter):
                self.answers[q_num] = {"letter": letter, "text": explanation}

    def _is_valid_answer(self, answer: str) -> bool:
        """Validate that answer is a valid letter (A-E).

        Args:
            answer: Answer letter to validate

        Returns:
            True if valid, False otherwise
        """
        return answer.upper() in self.VALID_ANSWERS

    def get_answer_letters_only(self) -> Dict[str, str]:
        """Get only the answer letters (backward compatibility).

        Returns:
            Dictionary with format: {"1": "A", "2": "B", ...}
        """
        return {q_num: ans["letter"] for q_num, ans in self.answers.items()}

    def save_as_json(self, output_path: str, include_text: bool = True) -> None:
        """Save extracted answers to JSON file.

        Args:
            output_path: Path to save JSON file
            include_text: Whether to include answer text (default True)

        Raises:
            ValueError: If no answers have been extracted
        """
        if not self.answers:
            raise ValueError("No answers to save. Extract answers first.")

        data: Union[Dict[str, Dict[str, str]], Dict[str, str]]
        if include_text:
            data = self.answers
        else:
            data = self.get_answer_letters_only()

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved answers to {output_path}")
        except Exception as e:
            raise ValueError(f"Failed to save answers to {output_path}: {str(e)}")
