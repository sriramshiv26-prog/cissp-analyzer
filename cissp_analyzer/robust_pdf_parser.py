#!/usr/bin/env python3
"""
Robust PDF Parser - Phase 3B Enhancement
Handles various PDF formats with error recovery and validation.
Supports fallback to manual entry if automatic extraction fails.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from pypdf import PdfReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RobustPDFParserResult:
    """Result of PDF parsing with confidence metrics."""

    def __init__(self):
        self.questions: Dict[int, Dict] = {}
        self.extraction_method: str = "unknown"
        self.confidence: float = 0.0
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.questions_found: int = 0
        self.questions_valid: int = 0
        self.missing_options: List[int] = []
        self.missing_text: List[int] = []


class RobustPDFParser:
    """Robust PDF question extraction with multiple strategies and error recovery."""

    # Question format variations
    QUESTION_PATTERNS = [
        r"^(\d+)\.\s+(.+?)$",  # "1. What is..."
        r"^Q(?:uestion)?\s*(\d+)\s*[.:\-]?\s*(.+?)$",  # "Q1: What is..."
        r"^\[(\d+)\]\s+(.+?)$",  # "[1] What is..."
        r"^#(\d+)\s+(.+?)$",  # "#1 What is..."
    ]

    OPTION_PATTERNS = [
        r"^([A-D])\)\s+(.+?)$",  # "A) Option text"
        r"^([A-D])\.\s+(.+?)$",  # "A. Option text"
        r"^([A-D])\s{2,}(.+?)$",  # "A    Option text"
        r"^\(([A-D])\)\s+(.+?)$",  # "(A) Option text"
    ]

    def __init__(self, pdf_path: str):
        """
        Initialize robust PDF parser.

        Args:
            pdf_path: Path to PDF file

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF is invalid
        """
        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            self.reader = PdfReader(str(self.pdf_path))
            self.pages = self.reader.pages

            if len(self.pages) == 0:
                raise ValueError("PDF has no pages")

            logger.info(f"✓ Loaded PDF: {self.pdf_path.name} ({len(self.pages)} pages)")

        except Exception as e:
            raise ValueError(f"Invalid PDF file: {str(e)}")

    def extract_with_fallback(self) -> RobustPDFParserResult:
        """
        Extract questions with fallback strategies.

        Tries multiple extraction methods in order:
        1. Automatic extraction (primary method)
        2. Alternative format detection
        3. Return partial results with warnings

        Returns:
            RobustPDFParserResult with questions and metadata
        """
        result = RobustPDFParserResult()

        logger.info("Starting PDF extraction with fallback strategies...")

        # Strategy 1: Try primary extraction method
        logger.info("Strategy 1: Primary extraction method...")
        questions = self._extract_primary()

        if questions:
            result.questions = questions
            result.extraction_method = "primary"
            result.questions_found = len(questions)
            result.confidence = self._calculate_confidence(result)

            if result.confidence >= 0.75:
                logger.info(
                    f"✓ Primary extraction successful ({len(questions)} questions, {result.confidence:.0%} confidence)"
                )
                return result

        # Strategy 2: Try alternative format detection
        logger.info("Strategy 2: Alternative format detection...")
        questions = self._extract_alternative()

        if questions:
            result.questions = questions
            result.extraction_method = "alternative"
            result.questions_found = len(questions)
            result.confidence = self._calculate_confidence(result)

            if result.confidence >= 0.60:
                logger.info(
                    f"✓ Alternative extraction successful ({len(questions)} questions, {result.confidence:.0%} confidence)"
                )
                return result

        # Return partial results
        result.questions = questions or {}
        result.questions_found = len(result.questions)
        result.extraction_method = "partial"
        result.confidence = self._calculate_confidence(result)

        if result.questions_found > 0:
            logger.warning(
                f"⚠️  Partial extraction: {len(questions)} questions (low confidence)"
            )
            result.warnings.append(
                f"Only {len(questions)} questions extracted. Manual review recommended."
            )
        else:
            logger.error("✗ No questions extracted. All extraction strategies failed.")
            result.issues.append(
                "Could not extract questions from PDF. Manual entry required."
            )

        return result

    def _extract_primary(self) -> Dict[int, Dict]:
        """
        Primary extraction method - handles standard numbered format.

        Returns:
            Dictionary of extracted questions
        """
        try:
            all_text = self._extract_text_from_pages()

            if not all_text:
                logger.warning("No text extracted from PDF")
                return {}

            # Find question numbers
            question_starts = self._find_question_starts(all_text)

            if not question_starts:
                logger.warning("No question numbers found")
                return {}

            # Extract questions
            questions = {}
            for q_num, start_pos in question_starts:
                question = self._extract_single_question(all_text, q_num, start_pos)
                if question:
                    questions[q_num] = question

            # If we found questions but success rate is low, try sequential fallback
            if len(questions) < len(question_starts) * 0.5:
                logger.info(
                    f"Low extraction success rate ({len(questions)}/{len(question_starts)}), "
                    f"trying sequential approach..."
                )
                sequential_questions = self._extract_sequential_questions(all_text)
                if len(sequential_questions) > len(questions):
                    questions = sequential_questions

            return questions

        except Exception as e:
            logger.error(f"Primary extraction failed: {str(e)}")
            return {}

    def _extract_sequential_questions(self, all_text: str) -> Dict[int, Dict]:
        """
        Extract questions assuming sequential numbering (1, 2, 3, ...).
        Creates minimal question objects with just the question number.
        Useful when full option extraction fails but question counting works.

        Returns:
            Dictionary of extracted questions
        """
        try:
            questions = {}
            current_q_num = 1

            # Look for sequential question patterns
            while current_q_num <= 500:
                pattern = rf"\n{current_q_num}\. "
                match = re.search(pattern, all_text)

                if match:
                    # Extract text until next question or end
                    pattern_next = rf"\n{current_q_num + 1}\. "
                    match_next = re.search(pattern_next, all_text[match.start() + 10 :])
                    end_pos = (
                        match.start() + 10 + match_next.start()
                        if match_next
                        else len(all_text)
                    )

                    q_text = all_text[match.start() + 1 : end_pos]
                    q_text = q_text[q_text.find(".") + 1 :].strip()
                    q_text = re.sub(r"\s+", " ", q_text)[:100]

                    if q_text:
                        questions[current_q_num] = {
                            "question_number": current_q_num,
                            "text": q_text,
                            "options": {},
                        }

                    current_q_num += 1
                else:
                    # No more sequential questions
                    break

            return questions

        except Exception as e:
            logger.error(f"Sequential extraction failed: {str(e)}")
            return {}

    def _extract_alternative(self) -> Dict[int, Dict]:
        """
        Alternative extraction method - handles various formats.

        Returns:
            Dictionary of extracted questions
        """
        try:
            all_text = self._extract_text_from_pages()

            if not all_text:
                return {}

            questions = {}

            # Try different question patterns
            for pattern in self.QUESTION_PATTERNS:
                matches = re.finditer(pattern, all_text, re.MULTILINE)

                for match in matches:
                    try:
                        q_num = int(match.group(1))
                        q_text = match.group(2).strip()

                        if q_text and len(q_text) > 10:  # Minimum question text length
                            if q_num not in questions:
                                # Find options following this question
                                options = self._find_options_after(
                                    all_text, match.end()
                                )
                                if len(options) >= 2:  # At least 2 options
                                    questions[q_num] = {
                                        "text": q_text,
                                        "options": options,
                                    }
                    except (ValueError, IndexError):
                        continue

            return questions

        except Exception as e:
            logger.error(f"Alternative extraction failed: {str(e)}")
            return {}

    def _extract_text_from_pages(self) -> str:
        """Extract text from all PDF pages with error handling."""
        try:
            text_parts = []

            for idx, page in enumerate(self.pages):
                try:
                    text = page.extract_text()
                    if text:
                        # Normalize text: replace tabs with newlines to improve parsing
                        text = text.replace("\t", "\n")
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(f"Error extracting page {idx + 1}: {str(e)}")
                    continue

            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            return ""

    def _find_question_starts(self, text: str) -> List[Tuple[int, int]]:
        """Find all question number positions."""
        pattern = r"^(\d+)\."
        matches = []

        for match in re.finditer(pattern, text, re.MULTILINE):
            try:
                q_num = int(match.group(1))
                matches.append((q_num, match.start()))
            except ValueError:
                continue

        return sorted(matches, key=lambda x: x[1])

    def _extract_single_question(
        self, text: str, q_num: int, start_pos: int
    ) -> Optional[Dict]:
        """Extract a single question with options."""
        try:
            # Find next question number or use text end
            next_match = re.search(r"^(\d+)\.", text[start_pos + 10 :], re.MULTILINE)
            end_pos = start_pos + 10 + next_match.start() if next_match else len(text)

            block_text = text[start_pos:end_pos]

            # Extract question text
            text_match = re.search(
                r"^\d+\.\s+(.+?)(?=^[A-D]\.|$)", block_text, re.MULTILINE | re.DOTALL
            )
            question_text = text_match.group(1).strip() if text_match else ""

            if not question_text or len(question_text) < 10:
                return None

            # Extract options
            options = {}
            for opt_letter in ["A", "B", "C", "D"]:
                pattern = rf"^{opt_letter}\.\s+(.+?)(?=^[A-D]\.|$)"
                match = re.search(pattern, block_text, re.MULTILINE | re.DOTALL)
                if match:
                    opt_text = match.group(1).strip()
                    opt_text = re.sub(r"\s+", " ", opt_text)
                    options[opt_letter] = opt_text

            # Require at least 3 valid options
            if len(options) < 3:
                return None

            return {
                "question_number": q_num,
                "text": question_text,
                "options": options,
            }

        except Exception as e:
            logger.debug(f"Error extracting Q{q_num}: {str(e)}")
            return None

    def _find_options_after(self, text: str, start_pos: int) -> Dict[str, str]:
        """Find answer options after given position."""
        options = {}
        search_text = text[start_pos : start_pos + 2000]  # Look ahead 2000 chars

        for pattern in self.OPTION_PATTERNS:
            for match in re.finditer(pattern, search_text, re.MULTILINE):
                letter = match.group(1).upper()
                option_text = match.group(2).strip()

                if letter not in options and option_text:
                    options[letter] = option_text

        return options

    def _calculate_confidence(self, result: RobustPDFParserResult) -> float:
        """Calculate confidence score for extraction result."""
        if result.questions_found == 0:
            return 0.0

        # Check for complete questions
        valid_count = 0
        for q_num, question in result.questions.items():
            # Accept questions with text (options are not required for grading)
            if question.get("text"):
                valid_count += 1

        result.questions_valid = valid_count

        # Confidence: mostly based on question count
        base_confidence = min(valid_count / result.questions_found, 1.0)

        # Only penalize missing options if we have some questions with options
        # (If all questions lack options, it's a sequential-only extraction which is valid)
        has_any_options = any(
            len(q.get("options", {})) > 0 for q in result.questions.values()
        )

        if has_any_options and result.questions_found > 0:
            avg_options = (
                sum(len(q.get("options", {})) for q in result.questions.values())
                / result.questions_found
            )

            option_confidence = min(avg_options / 4, 1.0)
            base_confidence = (base_confidence + option_confidence) / 2

        return base_confidence

    def validate_extraction(
        self, total_expected: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate extraction quality.

        Args:
            total_expected: Expected question count

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        if not self.questions:
            errors.append("No questions extracted")
            return False, errors

        if total_expected:
            coverage = len(self.questions) / total_expected * 100
            if coverage < 70:
                errors.append(
                    f"Low extraction rate: {len(self.questions)}/{total_expected} ({coverage:.0f}%)"
                )

        # Check for complete questions
        for q_num, question in self.questions.items():
            if not question.get("text"):
                errors.append(f"Q{q_num}: Missing question text")

            options = question.get("options", {})
            if len(options) < 3:
                errors.append(f"Q{q_num}: Only {len(options)} options (need ≥3)")

        is_valid = len(errors) == 0
        return is_valid, errors
