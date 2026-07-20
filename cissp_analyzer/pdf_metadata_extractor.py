"""
PDF Metadata Extractor - Analyzes PDF structure to extract metadata.

Works WITHOUT Ollama. Attempts to extract domain/topic/difficulty from PDF structure
if available. Otherwise returns extraction coverage so user can choose fallback method.

Key Design:
- No external LLM calls needed
- Analyzes PDF text structure for explicit tags (e.g., [Domain: X])
- Returns confidence metrics so user knows extraction quality
- Falls back gracefully when PDF has no structured metadata
"""

import re
from pathlib import Path
from typing import Dict, List, Optional
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


class PDFMetadataExtractor:
    """Extracts whatever metadata is available from PDF structure."""

    def __init__(self, pdf_path: str):
        """
        Initialize with PDF file.

        Args:
            pdf_path: Path to the PDF file to extract from

        Raises:
            FileNotFoundError: If PDF file does not exist
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.text = self._extract_pdf_text()
        self.questions = self.extract_questions()

    def _extract_pdf_text(self) -> str:
        """
        Extract all text from PDF.

        Returns:
            Concatenated text from all PDF pages
        """
        try:
            reader = PdfReader(str(self.pdf_path))
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

    def extract_questions(self) -> List[int]:
        """
        Extract all question numbers from PDF text.

        Looks for patterns like:
        - "N. " (period followed by space)
        - "N) " (closing paren followed by space)

        Returns:
            Sorted list of unique question numbers (1-500 range)
        """
        # Pattern: "N. " or "N) " where N is a number, at start of line
        pattern = r"\n(\d+)[.\)]\s"
        questions = []

        for match in re.finditer(pattern, self.text):
            q_num = int(match.group(1))
            # Reasonable upper limit for CISSP questions
            if 1 <= q_num <= 500:
                questions.append(q_num)

        return sorted(set(questions))

    def extract(self) -> Dict:
        """
        Extract metadata from PDF structure.

        This method attempts to find structured metadata in the PDF (e.g., tags like
        [Domain: Security Architecture], [Difficulty: Hard], etc.). If the PDF doesn't
        have these tags, extraction coverage will be low, and the user should choose
        a fallback method (defaults, manual entry, or auto-generation).

        Returns:
            Dict with structure:
            {
                "total_questions": int,              # Total questions found
                "extracted_count": int,              # Questions with metadata extracted
                "confidence": float,                 # extracted_count / total_questions (0-1.0)
                "extracted_metadata": dict,          # {q_num_str: {domain, difficulty, ...}}
                "gaps": list,                        # Question numbers without metadata
                "extraction_note": str,              # Human-readable coverage message
            }
        """
        total_q = len(self.questions)
        extracted_metadata = {}

        # Attempt to extract metadata from PDF structure
        for q_num in self.questions:
            meta = self._extract_for_question(q_num)
            if meta:
                extracted_metadata[str(q_num)] = meta

        extracted_count = len(extracted_metadata)
        gaps = [q for q in self.questions if q not in extracted_metadata]
        confidence = extracted_count / total_q if total_q > 0 else 0

        coverage_pct = int(confidence * 100)
        note = f"Extracted metadata for {extracted_count}/{total_q} questions ({coverage_pct}%)"

        return {
            "total_questions": total_q,
            "extracted_count": extracted_count,
            "confidence": round(confidence, 2),
            "extracted_metadata": extracted_metadata,
            "gaps": gaps,
            "extraction_note": note,
        }

    def _extract_for_question(self, q_num: int) -> Optional[Dict]:
        """
        Attempt to extract metadata for one question.

        Looks for explicit tags in the format:
        - [Domain: X]
        - [Difficulty: Y]
        - [Topic: Z]
        - [Type: W]
        - [Context: V]

        Args:
            q_num: Question number to extract metadata for

        Returns:
            Dict with any found metadata keys, or None if nothing found
        """
        # Find question and next 500 chars of text
        q_pattern = rf"\n{q_num}[.\)]\s.{{0,500}}"
        match = re.search(q_pattern, self.text, re.DOTALL)

        if not match:
            return None

        q_text = match.group(0)
        metadata = {}

        # Look for explicit tags (case-insensitive)
        domain_match = re.search(r"\[Domain:\s*(.+?)\]", q_text, re.IGNORECASE)
        if domain_match:
            metadata["domain"] = domain_match.group(1).strip()

        difficulty_match = re.search(r"\[Difficulty:\s*(.+?)\]", q_text, re.IGNORECASE)
        if difficulty_match:
            metadata["difficulty"] = difficulty_match.group(1).strip()

        topic_match = re.search(r"\[Topic:\s*(.+?)\]", q_text, re.IGNORECASE)
        if topic_match:
            metadata["topic"] = topic_match.group(1).strip()

        type_match = re.search(r"\[Type:\s*(.+?)\]", q_text, re.IGNORECASE)
        if type_match:
            metadata["type"] = type_match.group(1).strip()

        context_match = re.search(r"\[Context:\s*(.+?)\]", q_text, re.IGNORECASE)
        if context_match:
            metadata["context"] = context_match.group(1).strip()

        return metadata if metadata else None
