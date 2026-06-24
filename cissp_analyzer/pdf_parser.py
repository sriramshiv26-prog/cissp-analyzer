import re
from pathlib import Path
from pypdf import PdfReader
from typing import List, Dict, Optional


class PDFParser:
    """Extracts questions and answers from CISSP exam PDF"""

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

        # Strategy: Find all question numbers (1-125) and their positions
        # Then extract the block from number to next number or end of text
        # Only keep blocks that have all 4 options (A, B, C, D) and real question text
        # IMPORTANT: Only use the FIRST occurrence of each question number (to avoid answer key duplicates)

        question_starts = []
        seen_numbers = set()
        for i in range(1, 126):
            pattern = f'^{i}\\.'
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
            block_text = re.sub(r'^\d+\.\s+', '', block_text, count=1)

            # Extract options from this block
            options = {}

            # Find all option patterns A. B. C. D. - but only the first occurrence of each
            for option_letter in ['A', 'B', 'C', 'D']:
                pattern = fr'^{option_letter}\.\s+(.+?)(?=^[A-D]\.|$)'
                option_match = re.search(pattern, block_text, re.MULTILINE | re.DOTALL)
                if option_match:
                    opt_text = option_match.group(1).strip()
                    # Clean up whitespace
                    opt_text = re.sub(r'\s+', ' ', opt_text)
                    options[option_letter] = opt_text

            # Extract question text (everything before first option)
            text_match = re.search(r'^(.+?)(?=^[A-D]\.)', block_text, re.MULTILINE | re.DOTALL)
            if text_match:
                q_text = text_match.group(1).strip()
                q_text = re.sub(r'\s+', ' ', q_text)
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
                    '?' in q_text or
                    any(word in q_text.lower() for word in ['what', 'which', 'how', 'why', 'when', 'where', 'who', 'describe', 'explain', 'place', 'list', 'match']) or
                    q_text.endswith('.') or
                    q_text.endswith('___') or
                    q_text.endswith(':')
                )

                # Reject obvious non-questions (like table entries)
                is_table_entry = (q_text.count(' ') < 2 and len(q_text) < 20)

                if is_question and not is_table_entry:
                    questions.append({
                        'number': q_num,
                        'text': q_text,
                        'options': options
                    })

        return sorted(questions, key=lambda x: x['number'])
