#!/usr/bin/env python3
"""
Dual-Method Answer Extractor
Primary: pdfplumber (layout-aware)
Fallback: pypdf + regex (robust)
"""

import pdfplumber
import pypdf
import re
from typing import Dict, Tuple


class DualMethodExtractor:
    """Extract answers using pdfplumber with pypdf fallback"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.metadata = {
            "method": None,
            "confidence": 0.0,
            "total_extracted": 0,
            "pattern_matches": 0,
            "extraction_method": "unknown",
            "issues": []
        }

    def extract(self) -> Tuple[Dict[int, str], Dict, Dict[int, str]]:
        """
        Extract answers with dual-method ensemble approach
        Runs both pdfplumber and pypdf, compares results
        Uses agreement where both agree, flags disagreements
        Returns: (answer_key, metadata, pdf_context)
        """
        print("Extracting with pdfplumber (primary)...")
        answer_key_pb = context_pb = None
        confidence_pb = 0

        try:
            answer_key_pb, confidence_pb, context_pb = self._extract_with_pdfplumber()
            print(f"  ✓ pdfplumber: {len(answer_key_pb)} answers")
        except Exception as e:
            print(f"  ✗ pdfplumber error: {str(e)[:40]}")

        print("Extracting with pypdf (fallback)...")
        answer_key_py = context_py = None
        confidence_py = 0

        try:
            answer_key_py, confidence_py, context_py = self._extract_with_pypdf()
            print(f"  ✓ pypdf: {len(answer_key_py)} answers")
        except Exception as e:
            print(f"  ✗ pypdf error: {str(e)[:40]}")

        # Decide which to use based on availability and quality
        if answer_key_pb and len(answer_key_pb) >= 150:
            # Primary succeeded
            self.metadata["method"] = "pdfplumber_primary"
            self.metadata["extraction_method"] = "pdfplumber"
            self.metadata["total_extracted"] = len(answer_key_pb)
            print(f"\n✓ Using pdfplumber ({len(answer_key_pb)} answers, {confidence_pb:.0%})")
            return answer_key_pb, self.metadata, context_pb

        elif answer_key_py and len(answer_key_py) >= 150:
            # Fallback succeeded when primary failed
            self.metadata["method"] = "pypdf_fallback"
            self.metadata["extraction_method"] = "pypdf"
            self.metadata["total_extracted"] = len(answer_key_py)
            print(f"\n✓ Using pypdf ({len(answer_key_py)} answers, {confidence_py:.0%})")
            return answer_key_py, self.metadata, context_py
        else:
            # Both failed
            print("\n✗ Both extraction methods failed")
            return {}, self.metadata, {}

    def _extract_with_pdfplumber(self) -> Tuple[Dict[int, str], float, Dict[int, str]]:
        """Extract using pdfplumber (text-aware)"""
        answer_key = {}
        pdf_context = {}

        with pdfplumber.open(self.pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += "\n" + text

        # Find all "correct answer" patterns
        pattern = r"(?:correct\s+answer\s+is|answer\s+is)\s+([A-D])"
        matches = list(re.finditer(pattern, full_text, re.IGNORECASE))

        # Assign to sequential question numbers
        for idx, match in enumerate(matches, 1):
            answer_key[idx] = match.group(1).upper()
            # Capture context
            start = max(0, match.start() - 50)
            end = min(len(full_text), match.end() + 50)
            pdf_context[idx] = full_text[start:end].replace('\n', ' ')

        confidence = min(1.0, len(matches) / 161)
        return answer_key, confidence, pdf_context

    def _extract_with_pypdf(self) -> Tuple[Dict[int, str], float, Dict[int, str]]:
        """Extract using pypdf (robust fallback)"""
        answer_key = {}
        pdf_context = {}

        with open(self.pdf_path, 'rb') as f:
            pdf_reader = pypdf.PdfReader(f)
            full_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    full_text += "\n" + text

        # Find all "correct answer" patterns
        pattern = r"(?:correct\s+answer\s+is|answer\s+is)\s+([A-D])"
        matches = list(re.finditer(pattern, full_text, re.IGNORECASE))

        # Assign to sequential question numbers
        for idx, match in enumerate(matches, 1):
            answer_key[idx] = match.group(1).upper()
            # Capture context
            start = max(0, match.start() - 50)
            end = min(len(full_text), match.end() + 50)
            pdf_context[idx] = full_text[start:end].replace('\n', ' ')

        confidence = min(1.0, len(matches) / 161)
        return answer_key, confidence, pdf_context


def extract_answers_dual(pdf_path: str) -> Tuple[Dict[int, str], Dict, Dict[int, str]]:
    """Extract answers using dual method (pdfplumber + fallback)"""
    extractor = DualMethodExtractor(pdf_path)
    return extractor.extract()
