import re
import logging
from pathlib import Path
from pypdf import PdfReader
from typing import List, Dict, Any


class PDFParser:
    """Extracts questions and answers from CISSP exam PDF"""

    QUESTION_INDICATOR_WORDS = [
        "what",
        "which",
        "how",
        "why",
        "when",
        "where",
        "who",
        "describe",
        "explain",
        "place",
        "list",
        "match",
    ]

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.reader = PdfReader(str(self.pdf_path))
        self.pages = self.reader.pages

    def extract_questions(self) -> List[Dict]:
        """Extract all questions from the PDF"""
        questions = []

        # Extract all text from PDF
        all_text = ""
        for page in self.pages:
            all_text += page.extract_text()

        # Strategy: Find all question numbers (dynamic, not hardcoded to 125)
        # 1. First find all question numbers that exist in the PDF
        # 2. Then extract the block from number to next number or end of text
        # 3. Only keep blocks that have all 4 options (A, B, C, D) and real question text
        # IMPORTANT: Only use the FIRST occurrence of each question number
        # (to avoid answer key duplicates)

        # Find all question numbers in the PDF dynamically
        question_pattern = r"^(\d+)\."
        all_matches = re.finditer(question_pattern, all_text, re.MULTILINE)
        found_numbers = sorted(set(int(m.group(1)) for m in all_matches))

        # If no numbers found, assume it's a numbered document but check up to 250 to be safe
        if not found_numbers:
            found_numbers = list(range(1, 251))

        question_starts = []
        seen_numbers = set()
        for i in found_numbers:
            pattern = f"^{i}\\."
            match = re.search(pattern, all_text, re.MULTILINE)
            if match and i not in seen_numbers:
                question_starts.append((i, match.start()))
                seen_numbers.add(i)

        # Sort by position
        question_starts.sort(key=lambda x: x[1])

        # Process each question
        for idx, (q_num, start_pos) in enumerate(question_starts):
            # End position is the start of next question or end of text
            if idx + 1 < len(question_starts):
                end_pos = question_starts[idx + 1][1]
            else:
                end_pos = len(all_text)

            block_text = all_text[start_pos:end_pos]

            # Remove the question number from the start
            block_text = re.sub(r"^\d+\.\s+", "", block_text, count=1)

            # Extract options from this block
            options = {}

            # Find all option patterns A. B. C. D. - but only the first occurrence of each
            for option_letter in ["A", "B", "C", "D"]:
                pattern = rf"^{option_letter}\.\s+(.+?)(?=^[A-D]\.|$)"
                option_match = re.search(pattern, block_text, re.MULTILINE | re.DOTALL)
                if option_match:
                    opt_text = option_match.group(1).strip()
                    # Clean up whitespace
                    opt_text = re.sub(r"\s+", " ", opt_text)
                    options[option_letter] = opt_text

            # Extract question text (everything before first option)
            text_match = re.search(
                r"^(.+?)(?=^[A-D]\.)", block_text, re.MULTILINE | re.DOTALL
            )
            if text_match:
                q_text = text_match.group(1).strip()
                q_text = re.sub(r"\s+", " ", q_text)
            else:
                continue

            # Filter: Only include if we have all 4 options
            # Quality checks:
            # 1. Question text should be substantial (> 10 chars)
            # 2. Should either have a '?' OR contain question words OR end with a blank/colon
            # 3. Should not be just table entries like "ARP Description"
            if len(options) == 4 and len(q_text) > 10:
                # Check if it looks like a real question
                is_question = (
                    "?" in q_text
                    or any(
                        word in q_text.lower() for word in self.QUESTION_INDICATOR_WORDS
                    )
                    or q_text.endswith(".")
                    or q_text.endswith("___")
                    or q_text.endswith(":")
                )

                # Reject obvious non-questions (like table entries)
                is_table_entry = q_text.count(" ") < 2 and len(q_text) < 20

                if is_question and not is_table_entry:
                    questions.append(
                        {"number": q_num, "text": q_text, "options": options}
                    )

        return sorted(questions, key=lambda x: x["number"])

    @staticmethod
    def extract_with_answer_context(pdf_text: str) -> Dict[str, Dict[str, Any]]:
        """Extract questions with enhanced domain context from answer text.

        Combines question extraction with answer key extraction and domain mapping
        to provide intelligent domain classification for each question.

        Args:
            pdf_text: Full text extracted from PDF (or raw PDF text string)

        Returns:
            Dictionary mapping question number to enriched context:
            {
                "1": {
                    "question": "What is X?",
                    "answer_letter": "A",
                    "answer_text": "Full answer explanation",
                    "suggested_domain": "Domain Name"
                },
                ...
            }
        """
        from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor
        from cissp_analyzer.answer_context_mapper import AnswerContextMapper

        logger = logging.getLogger(__name__)

        # Extract questions from text
        logger.info("Extracting questions from PDF text...")
        questions = PDFParser._extract_questions_from_text(pdf_text)

        logger.info("Extracting answers from PDF text...")
        answer_extractor = AnswerKeyExtractor()
        try:
            answers = answer_extractor.extract_answers(pdf_text)
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to extract answers: {e}")
            answers = {}

        # Map using answer context
        logger.info("Mapping domains using answer context...")
        mapper = AnswerContextMapper()
        enhanced_context = {}

        for q_num, q_text in questions.items():
            answer_data = answers.get(q_num, {})
            answer_letter = answer_data.get("letter")
            answer_text = answer_data.get("text", "")

            # Get answer-context-aware domain suggestion
            suggested_domain = None
            if answer_text:
                suggested_domain = mapper.map_with_context(q_text, answer_text)
            elif q_text:
                # Fallback to question-only if no answer text
                suggested_domain = mapper.map_with_context(q_text, "")

            enhanced_context[q_num] = {
                "question": q_text,
                "answer_letter": answer_letter,
                "answer_text": answer_text,
                "suggested_domain": suggested_domain,
            }

        logger.info(f"Enhanced {len(enhanced_context)} questions with domain context")
        return enhanced_context

    @staticmethod
    def _extract_questions_from_text(text: str) -> Dict[str, str]:
        """Extract questions from text (not PDF file).

        Simpler version that extracts question text only from raw text.

        Args:
            text: Raw text content

        Returns:
            Dictionary mapping question number to question text
        """
        questions = {}

        # Look for pattern: "Question N: ..." or "N. ..." or "N) ..."
        # First try explicit "Question N:" pattern - match until next Question or option pattern
        pattern1 = r"Question\s+(\d+)\s*:\s*([^\n]+?)(?=\n\s*[A-D]\)|$)"
        matches = re.finditer(pattern1, text, re.IGNORECASE | re.MULTILINE)

        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            # Clean up multi-line questions
            q_text = re.sub(r"\s+", " ", q_text)
            if q_text and len(q_text) > 5:
                questions[q_num] = q_text

        # If no "Question N:" pattern found, try "N. " or "N) " pattern
        if not questions:
            pattern2 = r"^(\d+)\)\s+(.+?)(?=^[A-D]\)|^\d+\)|$)"
            matches = re.finditer(pattern2, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                q_num = match.group(1)
                q_text = match.group(2).strip()
                # Extract only the question part (before options)
                q_text = re.split(r"\n\s*[A-D]\)", q_text)[0].strip()
                q_text = re.sub(r"\s+", " ", q_text)
                if q_text and len(q_text) > 5:
                    questions[q_num] = q_text

        return questions
