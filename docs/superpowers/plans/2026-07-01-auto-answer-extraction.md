# Auto-Answer Key Extraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable automatic extraction of answer keys from Q&A PDFs with smart domain/topic mapping that considers both question AND answer keywords for accurate classification.

**Architecture:** Create `AnswerKeyExtractor` to parse PDFs and extract questions + full answer text. Build `AnswerContextMapper` to enhance domain classification by analyzing answer keywords/context alongside question text. Integrate into `interactive_cli.py` workflow. Existing 7-sheet report unchanged.

**Tech Stack:** pypdf (already in requirements.txt), pathlib, json, logging, re (regex)

**CRITICAL CAVEAT:** Domain/topic mapping MUST consider both:
- Question text keywords (current behavior)
- Answer text keywords (NEW - this caveat)
- Combined context for higher accuracy classification

---

## File Structure

**New Files:**
- `cissp_analyzer/answer_key_extractor.py` - Answer + answer text extraction
- `cissp_analyzer/answer_context_mapper.py` - Enhance domain mapping with answer context
- `tests/test_answer_key_extractor.py` - Answer extraction tests
- `tests/test_answer_context_mapper.py` - Context mapping tests

**Modified Files:**
- `cissp_analyzer/interactive_cli.py` - Integrate auto-extraction workflow
- `cissp_analyzer/pdf_parser.py` - Optional enhancement for answer text integration

**Unchanged Files:**
- `cissp_analyzer/main.py` - No changes
- `data/question_domain_mapping.json` - Enhanced with answer context at runtime

---

## Task 1: Create AnswerKeyExtractor with Answer Text

**Files:**
- Create: `cissp_analyzer/answer_key_extractor.py`
- Test: `tests/test_answer_key_extractor.py`

- [ ] **Step 1: Write failing tests for answer extraction with text**

Create `tests/test_answer_key_extractor.py`:

```python
import pytest
from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor


class TestAnswerKeyExtractor:
    """Tests for PDF answer key extraction with answer text."""

    def test_extract_answers_with_full_text(self):
        """Test extraction includes both letter and answer text."""
        pdf_text = """
        Question 1: What encryption method uses symmetric keys?
        A) RSA
        B) AES
        C) ECC
        
        Answer Key:
        1: B - AES is a symmetric encryption algorithm
        2: A - Asymmetric encryption...
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)
        
        # Should return both letter and context text
        assert result["1"]["letter"] == "B"
        assert "AES" in result["1"]["text"]
        assert "symmetric" in result["1"]["text"]

    def test_extract_answers_letter_only_fallback(self):
        """Test extraction gracefully handles letter-only format."""
        pdf_text = """
        Answer Key:
        1: B
        2: A
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)
        
        assert result["1"]["letter"] == "B"
        assert result["1"]["text"] == ""  # No text provided

    def test_extract_answers_multiline_answer_text(self):
        """Test extraction handles multi-line answer explanations."""
        pdf_text = """
        Answers:
        1: C - The correct answer involves:
           - Understanding cryptography
           - Symmetric key exchange
           - AES-256 implementation
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)
        
        assert result["1"]["letter"] == "C"
        assert "cryptography" in result["1"]["text"]

    def test_extract_answers_complex_format(self):
        """Test extraction from exam with detailed answer explanations."""
        pdf_text = """
        Question 1: Which domain addresses access control?
        A) Asset Management
        B) Access Control and Identity Management
        C) Cryptography
        
        ANSWERS:
        1: B - Access Control and Identity Management (ACIM) deals with 
           authentication, authorization, and accountability controls
           including role-based access, policies, and identity verification
        """
        extractor = AnswerKeyExtractor()
        result = extractor.extract_answers(pdf_text)
        
        assert result["1"]["letter"] == "B"
        assert "Access Control" in result["1"]["text"]
        assert "Identity Management" in result["1"]["text"]

    def test_validate_answer_format(self):
        """Test that answer letter is A-E."""
        extractor = AnswerKeyExtractor()
        assert extractor._is_valid_answer("A") is True
        assert extractor._is_valid_answer("E") is True
        assert extractor._is_valid_answer("F") is False
```

- [ ] **Step 2: Run test to verify all fail**

```bash
cd /Users/sriram/cissp-analyzer
python3 -m pytest tests/test_answer_key_extractor.py -v
```

Expected: `ModuleNotFoundError: No module named 'cissp_analyzer.answer_key_extractor'`

- [ ] **Step 3: Write the AnswerKeyExtractor implementation**

Create `cissp_analyzer/answer_key_extractor.py`:

```python
#!/usr/bin/env python3
"""
Answer Key Extractor - Extracts answer keys + answer text from Q&A PDFs.

Supports multiple answer section formats:
- "Answer Key:" with letter only (1: A)
- "Answer Key:" with explanations (1: A - explanation text)
- "ANSWERS:" / "Solutions:" / "Answers:" formats
- Multi-line answer explanations

Returns both answer letter (for grading) and answer text (for domain mapping).
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Any
from pypdf import PdfReader


logger = logging.getLogger(__name__)


class AnswerKeyExtractor:
    """Extract answer keys with answer text from PDF documents."""

    # Answer section markers (case-insensitive)
    ANSWER_MARKERS = [
        r'answer\s*key',
        r'answers:',
        r'solutions:',
        r'^answers$',
    ]

    # Answer patterns: "1: A", "1) A", "Q1: A", with optional explanation
    # Captures: (question_num, answer_letter, optional_explanation)
    ANSWER_PATTERNS = [
        r'^\s*(?:Q|Question)?\s*(\d+)\s*[:)]\s*([A-E])(?:\s*[-–]\s*(.+))?$',
        r'(\d+)\s*[:)]\s*([A-E])(?:\s*[-–]\s*(.+))?',
    ]

    def __init__(self):
        """Initialize the extractor."""
        self.answers: Dict[str, Dict[str, Any]] = {}

    def extract_from_file(self, pdf_path: str) -> Dict[str, Dict[str, Any]]:
        """Extract answer key from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary mapping question number to {letter, text}
            Example: {"1": {"letter": "A", "text": "RSA is asymmetric..."}}

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF is invalid or corrupted
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return self.extract_answers(text)
        except Exception as e:
            raise ValueError(f"Failed to read PDF {pdf_path}: {str(e)}")

    def extract_answers(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extract answers from PDF text.

        Returns both answer letter and answer text/explanation for context.

        Args:
            text: Full text extracted from PDF

        Returns:
            Dictionary: {"1": {"letter": "A", "text": "explanation..."}, ...}
        """
        self.answers = {}

        # Find answer section start
        answer_section = self._find_answer_section(text)
        if not answer_section:
            logger.warning("No answer section found in PDF")
            return {}

        # Extract all answer pairs including text
        self._extract_answer_pairs(answer_section)

        logger.info(f"Extracted {len(self.answers)} answers with text from PDF")
        return self.answers

    def _find_answer_section(self, text: str) -> Optional[str]:
        """Find the answer section of the PDF text.

        Looks for markers like "Answer Key:", "ANSWERS:", etc.

        Args:
            text: Full PDF text

        Returns:
            Text starting from answer marker, or None if not found
        """
        lines = text.split('\n')

        for i, line in enumerate(lines):
            for marker in self.ANSWER_MARKERS:
                if re.search(marker, line, re.IGNORECASE):
                    # Return from this line onwards
                    return '\n'.join(lines[i:])

        # If no marker found, assume last 50% of document is answers
        mid = len(lines) // 2
        return '\n'.join(lines[mid:])

    def _extract_answer_pairs(self, text: str) -> None:
        """Extract answer pairs with explanations from text.

        Args:
            text: Answer section text
        """
        lines = text.split('\n')
        buffer_text = ""  # For multi-line answers

        for line in lines:
            line = line.strip()
            if not line:
                buffer_text = ""
                continue

            # Try each pattern
            for pattern in self.ANSWER_PATTERNS:
                matches = re.finditer(pattern, line, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    question_num = match.group(1)
                    answer_letter = match.group(2).upper()
                    answer_text = match.group(3) if len(match.groups()) > 2 else ""

                    if self._is_valid_answer(answer_letter):
                        self.answers[question_num] = {
                            "letter": answer_letter,
                            "text": (answer_text or "").strip()
                        }
                        buffer_text = ""
                        break  # Found answer, move to next line

            # If line continues previous answer (indented), append to text
            if line.startswith(("  ", "\t", "-", "•")) and self.answers:
                # Get last answer's question number
                last_q = list(self.answers.keys())[-1]
                if self.answers[last_q]["text"]:
                    self.answers[last_q]["text"] += " " + line.strip(" -•")
                else:
                    self.answers[last_q]["text"] = line.strip(" -•")

    def _is_valid_answer(self, answer: str) -> bool:
        """Validate that answer is a single letter A-E.

        Args:
            answer: Answer string to validate

        Returns:
            True if valid, False otherwise
        """
        return len(answer) == 1 and answer in ['A', 'B', 'C', 'D', 'E']

    def get_answer_letters_only(self) -> Dict[str, str]:
        """Return only answer letters (for compatibility with existing code).

        Returns:
            Dictionary: {"1": "A", "2": "B", ...}
        """
        return {q_num: data["letter"] for q_num, data in self.answers.items()}

    def save_as_json(self, output_path: str, include_text: bool = True) -> None:
        """Save extracted answers as JSON file.

        Args:
            output_path: Path to save JSON file
            include_text: If True, save full answer text; if False, letters only

        Raises:
            ValueError: If no answers to save
        """
        if not self.answers:
            raise ValueError("No answers extracted to save")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if include_text:
            # Save with full answer text (for domain mapping)
            data = self.answers
        else:
            # Save letters only (for backward compatibility)
            data = self.get_answer_letters_only()

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved answer key to {output_path}")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_answer_key_extractor.py -v
```

Expected: `5+ tests PASSED`

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/answer_key_extractor.py tests/test_answer_key_extractor.py
git commit -m "feat: extract answer keys with answer text for context mapping"
```

---

## Task 2: Create Answer Context Mapper (Domain Classification Enhancement)

**Files:**
- Create: `cissp_analyzer/answer_context_mapper.py`
- Test: `tests/test_answer_context_mapper.py`

- [ ] **Step 1: Write tests for answer-context domain mapping**

Create `tests/test_answer_context_mapper.py`:

```python
import pytest
from cissp_analyzer.answer_context_mapper import AnswerContextMapper


class TestAnswerContextMapper:
    """Tests for using answer text to enhance domain/topic classification."""

    def test_extract_keywords_from_answer_text(self):
        """Test keyword extraction from answer explanations."""
        mapper = AnswerContextMapper()
        answer_text = "AES is a symmetric encryption algorithm used for data protection"
        
        keywords = mapper.extract_keywords(answer_text)
        
        assert "AES" in keywords
        assert "symmetric" in keywords
        assert "encryption" in keywords

    def test_map_question_with_context(self):
        """Test domain mapping using both Q and A context."""
        mapper = AnswerContextMapper()
        
        question_text = "Which cryptographic method uses a shared secret key?"
        answer_text = "AES (Advanced Encryption Standard) is the symmetric encryption standard"
        
        # Should map to Cryptography domain based on both texts
        domain = mapper.map_with_context(question_text, answer_text)
        
        assert domain == "Cryptography" or "Crypt" in domain

    def test_map_access_control_question(self):
        """Test that answer context helps classify access control questions."""
        mapper = AnswerContextMapper()
        
        question = "Which component manages user privileges?"
        answer = "Role-Based Access Control (RBAC) manages permissions and access levels"
        
        domain = mapper.map_with_context(question, answer)
        
        assert "Access" in domain or "Control" in domain

    def test_map_with_question_only_fallback(self):
        """Test that empty answer text falls back to question-only mapping."""
        mapper = AnswerContextMapper()
        
        question = "What is the primary goal of asset management?"
        answer = ""
        
        domain = mapper.map_with_context(question, answer)
        
        assert domain is not None  # Should still produce a result

    def test_improve_classification_with_answer_keywords(self):
        """Test that answer keywords improve classification accuracy."""
        mapper = AnswerContextMapper()
        
        # Question is vague, but answer keywords clarify domain
        question = "This framework addresses multiple security areas"
        answer_keywords = ["authentication", "authorization", "access control", "identity management"]
        
        improved_domain = mapper.map_with_keywords(question, answer_keywords)
        
        # Should classify as Access Control/Identity Management domain
        assert improved_domain is not None

    def test_handle_conflicting_contexts(self):
        """Test behavior when question and answer suggest different domains."""
        mapper = AnswerContextMapper()
        
        # Question might suggest one domain, answer text suggests another
        question = "What principle guides security design?"
        answer = "Defense in Depth uses multiple layers of cryptographic controls"
        
        # Should integrate both for most accurate classification
        result = mapper.map_with_context(question, answer)
        
        assert result is not None

    def test_extract_domain_keywords_from_answer(self):
        """Test that domain-specific keywords are extracted from answers."""
        mapper = AnswerContextMapper()
        
        domain_keywords = {
            "Cryptography": ["AES", "RSA", "encryption", "cipher", "hash"],
            "Access Control": ["RBAC", "authorization", "permissions", "roles"],
            "Governance": ["policy", "compliance", "standards", "risk"],
        }
        
        answer_text = "RBAC provides role-based authorization and permission management"
        
        detected_domains = mapper.detect_domains_from_text(answer_text, domain_keywords)
        
        assert "Access Control" in detected_domains
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_answer_context_mapper.py -v
```

Expected: `ModuleNotFoundError: No module named 'cissp_analyzer.answer_context_mapper'`

- [ ] **Step 3: Write the AnswerContextMapper implementation**

Create `cissp_analyzer/answer_context_mapper.py`:

```python
#!/usr/bin/env python3
"""
Answer Context Mapper - Enhance domain/topic mapping using answer text.

When classifying questions by domain, consider BOTH:
1. Question text keywords (what's being asked)
2. Answer text keywords (what the correct answer emphasizes)

This improves accuracy especially for ambiguous questions where the
answer clarifies the intended domain/topic.

Example:
  Q: "What is important in security?"
  A: "AES encryption is critical for protecting data"
  → Classified as Cryptography (not Generic Security)
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import re


logger = logging.getLogger(__name__)


class AnswerContextMapper:
    """Enhance question-to-domain mapping using answer text context."""

    # CISSP domain keywords for classification
    DOMAIN_KEYWORDS = {
        "Security and Risk Management": [
            "risk", "threat", "vulnerability", "governance", "policy",
            "compliance", "regulation", "audit", "assessment", "management",
            "asset management", "security program"
        ],
        "Access Control and Identity Management": [
            "access control", "authentication", "authorization", "identity",
            "rbac", "abac", "role", "permission", "privilege", "accountability",
            "user", "credential", "password", "mfa", "multi-factor"
        ],
        "Cryptography": [
            "encryption", "cipher", "aes", "rsa", "hash", "signature",
            "symmetric", "asymmetric", "cryptographic", "key", "ssl", "tls",
            "certificate", "digital signature", "ecc"
        ],
        "Physical and Environmental Security": [
            "physical", "environment", "facility", "building", "access point",
            "badge", "biometric", "surveillance", "cctv", "locks", "guards",
            "location", "perimeter"
        ],
        "Communication and Network Security": [
            "network", "protocol", "firewall", "intrusion", "detection",
            "vpn", "wan", "lan", "router", "switch", "dns", "dhcp",
            "communication", "osi model", "tcp", "ip", "packet", "snmp"
        ],
        "System and Application Security": [
            "application", "system", "patch", "update", "vulnerability",
            "exploit", "malware", "virus", "antivirus", "endpoint", "code",
            "secure coding", "input validation", "buffer overflow"
        ],
        "Security Assessment and Testing": [
            "assessment", "testing", "penetration", "pentest", "scan",
            "vulnerability assessment", "security test", "audit", "review",
            "evaluation", "metrics", "benchmark"
        ],
        "Security Operations": [
            "incident", "response", "monitoring", "logging", "siem",
            "detection", "investigation", "forensics", "recovery", "disaster",
            "continuity", "backup", "alert", "alarm"
        ],
        "Software Development Security": [
            "development", "sdlc", "secure coding", "code review", "testing",
            "deployment", "repository", "version control", "agile", "waterfall"
        ],
        "Cloud Security": [
            "cloud", "aws", "azure", "gcp", "saas", "paas", "iaas",
            "virtualization", "container", "docker", "kubernetes", "serverless"
        ],
    }

    def __init__(self, mapping_file: Optional[str] = None):
        """Initialize the mapper.

        Args:
            mapping_file: Optional JSON file with custom domain keyword mappings
        """
        self.domain_keywords = self.DOMAIN_KEYWORDS.copy()
        if mapping_file and Path(mapping_file).exists():
            self._load_custom_mappings(mapping_file)

    def _load_custom_mappings(self, mapping_file: str) -> None:
        """Load custom domain keyword mappings from JSON file.

        Args:
            mapping_file: Path to JSON file with custom mappings
        """
        try:
            with open(mapping_file) as f:
                custom = json.load(f)
                self.domain_keywords.update(custom)
                logger.info(f"Loaded custom domain mappings from {mapping_file}")
        except Exception as e:
            logger.warning(f"Failed to load custom mappings: {e}")

    def map_with_context(self, question_text: str, answer_text: str) -> Optional[str]:
        """Map question to domain using both question and answer text.

        Args:
            question_text: The question being asked
            answer_text: The answer text/explanation

        Returns:
            Best matching domain name, or None if no match
        """
        combined_text = f"{question_text} {answer_text}"
        return self._classify_text(combined_text)

    def map_with_keywords(self, question_text: str, answer_keywords: List[str]) -> Optional[str]:
        """Map question using question text and explicit answer keywords.

        Args:
            question_text: The question being asked
            answer_keywords: Keywords extracted from answer

        Returns:
            Best matching domain name, or None if no match
        """
        combined_text = f"{question_text} {' '.join(answer_keywords)}"
        return self._classify_text(combined_text)

    def detect_domains_from_text(self, text: str, domain_keywords: Optional[Dict] = None) -> List[str]:
        """Detect all matching domains in text.

        Args:
            text: Text to analyze
            domain_keywords: Optional custom keyword mappings

        Returns:
            List of matching domain names, sorted by confidence
        """
        if domain_keywords is None:
            domain_keywords = self.domain_keywords

        text_lower = text.lower()
        scores = {}

        for domain, keywords in domain_keywords.items():
            score = 0
            for keyword in keywords:
                # Count keyword occurrences (whole word match)
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                score += matches
            
            if score > 0:
                scores[domain] = score

        # Sort by score descending
        sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [domain for domain, _ in sorted_domains]

    def extract_keywords(self, text: str) -> Set[str]:
        """Extract important keywords from answer text.

        Args:
            text: Answer text to analyze

        Returns:
            Set of extracted keywords
        """
        # Remove common words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "is", "are", "be", "been", "being", "have", "has",
            "do", "does", "did", "will", "would", "could", "should", "may",
            "might", "must", "can", "that", "this", "these", "those", "which"
        }

        # Split and filter
        words = text.lower().split()
        keywords = set()

        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s-]', '', word)
            
            # Keep words > 3 chars that aren't stop words
            if len(clean_word) > 3 and clean_word not in stop_words:
                keywords.add(clean_word)

        return keywords

    def _classify_text(self, text: str) -> Optional[str]:
        """Classify text to best matching domain.

        Args:
            text: Text to classify

        Returns:
            Best matching domain name, or None
        """
        matching_domains = self.detect_domains_from_text(text)
        
        if matching_domains:
            return matching_domains[0]  # Return highest scoring domain
        
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_answer_context_mapper.py -v
```

Expected: `7+ tests PASSED`

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/answer_context_mapper.py tests/test_answer_context_mapper.py
git commit -m "feat: add AnswerContextMapper for enhanced domain classification"
```

---

## Task 3: Integrate Answer Context into PDF Parser

**Files:**
- Modify: `cissp_analyzer/pdf_parser.py`

- [ ] **Step 1: Write test for enhanced PDF parsing with answer context**

Add to `tests/test_pdf_parser.py`:

```python
def test_extract_questions_with_answer_context():
    """Test that PDF parser can leverage answer context for classification."""
    from cissp_analyzer.pdf_parser import PDFParser
    from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor
    from cissp_analyzer.answer_context_mapper import AnswerContextMapper
    
    # This is integration test
    # Parser extracts Q text + Q domain
    # But domain mapping should ALSO consider A text
    
    pdf_text = """
    Question 1: What controls data access?
    A) Physical security
    B) Role-Based Access Control
    C) Encryption standards
    
    Answer Key:
    1: B - RBAC is part of Access Control and Identity Management domain
    """
    
    # Extract both Q and A
    parser = PDFParser()
    questions = parser.extract_text_from_pdf_string(pdf_text)
    
    extractor = AnswerKeyExtractor()
    answers = extractor.extract_answers(pdf_text)
    
    # Mapper should use both Q and A text
    mapper = AnswerContextMapper()
    q_text = questions.get("1", "")
    a_text = answers.get("1", {}).get("text", "")
    
    domain = mapper.map_with_context(q_text, a_text)
    
    # Should classify correctly as Access Control
    assert "Access" in domain or "Control" in domain
```

- [ ] **Step 2: Update PDF parser to support answer context**

Modify `cissp_analyzer/pdf_parser.py` - add new method after existing extraction:

```python
def extract_with_answer_context(self, pdf_path: str, answer_extractor=None):
    """Extract questions AND use answer text to enhance domain classification.
    
    Args:
        pdf_path: Path to PDF file
        answer_extractor: Optional AnswerKeyExtractor instance
        
    Returns:
        Dictionary with questions, answers, and enhanced domain context
    """
    from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor
    from cissp_analyzer.answer_context_mapper import AnswerContextMapper
    
    # Extract questions (existing)
    questions = self.extract_questions(pdf_path)
    
    # Extract answers with text
    if answer_extractor is None:
        answer_extractor = AnswerKeyExtractor()
    
    try:
        answers = answer_extractor.extract_from_file(pdf_path)
    except Exception as e:
        logger.warning(f"Could not extract answers: {e}")
        answers = {}
    
    # Map using answer context
    mapper = AnswerContextMapper()
    enhanced_context = {}
    
    for q_num, q_text in questions.items():
        answer_data = answers.get(q_num, {})
        answer_text = answer_data.get("text", "")
        
        # Get answer-context-aware domain suggestion
        suggested_domain = mapper.map_with_context(q_text, answer_text)
        
        enhanced_context[q_num] = {
            "question": q_text,
            "answer_letter": answer_data.get("letter"),
            "answer_text": answer_text,
            "suggested_domain": suggested_domain
        }
    
    return enhanced_context
```

- [ ] **Step 3: Run tests to verify integration**

```bash
python3 -m pytest tests/test_pdf_parser.py tests/test_answer_context_mapper.py -v
```

Expected: All tests PASSED

- [ ] **Step 4: Commit**

```bash
git add cissp_analyzer/pdf_parser.py tests/test_pdf_parser.py
git commit -m "feat: enhance PDF parser to use answer context for domain classification"
```

---

## Task 4: Integrate with Interactive CLI

**Files:**
- Modify: `cissp_analyzer/interactive_cli.py`

- [ ] **Step 1: Update get_answer_key() to support answer context**

Modify `cissp_analyzer/interactive_cli.py` (replace the `get_answer_key()` function):

```python
def get_answer_key() -> Optional[str]:
    """Prompt for answer key with auto-extraction and answer context support.

    Returns:
        Path to answer key JSON, or "__AUTO_EXTRACT__" marker, or None
    """
    from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor

    print("\n" + Colors.header("-" * 70))
    print(Colors.header("STEP 2: ANSWER KEY (Optional)"))
    print(Colors.header("-" * 70))
    print("Do you have an answer key file? (JSON format)")
    print("Format: {'1': 'A', '2': 'B', ...}")
    print("OR: We can auto-extract answers from the exam PDF")
    print("(Auto-extract also uses answer text to improve domain classification)")

    answer_key = prompt("Path to answer key (optional)", required=False)

    if answer_key:
        if validate_file(answer_key):
            print(Colors.success(f"Answer key found: {answer_key}"))
            return answer_key
        else:
            print(Colors.warning(f"File not found: {answer_key}"))
            if prompt_yes_no("Try auto-extract instead?", default=True):
                return "__AUTO_EXTRACT__"
            else:
                return get_answer_key()
    else:
        if prompt_yes_no("Auto-extract answers from PDF?", default=True):
            return "__AUTO_EXTRACT__"
        else:
            print(Colors.info("Will attempt extraction from PDF"))
            return None
```

- [ ] **Step 2: Update run_analysis() to use answer context**

Modify the answer key loading section in `run_analysis()` function (around line 288):

```python
        # Load or auto-extract answer key
        if answer_key == "__AUTO_EXTRACT__":
            print(Colors.info("Auto-extracting answers with domain context enhancement..."))
            extractor = AnswerKeyExtractor()
            try:
                extracted_answers = extractor.extract_from_file(pdf)
                if extracted_answers:
                    print(Colors.success(f"Extracted {len(extracted_answers)} answers from PDF"))
                    
                    # Also extract answer text for domain mapping enhancement
                    print(Colors.info("Enhancing domain classification using answer keywords..."))
                    from cissp_analyzer.answer_context_mapper import AnswerContextMapper
                    mapper = AnswerContextMapper()
                    
                    # Count domain hints from answer text
                    domain_hints = {}
                    for q_num, ans_data in extracted_answers.items():
                        ans_text = ans_data.get("text", "")
                        if ans_text:
                            keywords = mapper.extract_keywords(ans_text)
                            domain = mapper.map_with_keywords("", list(keywords))
                            if domain:
                                domain_hints[q_num] = domain
                    
                    if domain_hints:
                        print(Colors.info(f"Domain context identified from {len(domain_hints)} answer texts"))
                    
                    # Save with full answer text (for domain mapping)
                    temp_key_path = Path(output) / ".answer_key_temp.json"
                    extractor.save_as_json(str(temp_key_path), include_text=True)
                    
                    # Load letter-only version for existing analyzer
                    letters_only = extractor.get_answer_letters_only()
                    analyzer.set_answer_key_from_dict(letters_only)
                    answer_key = str(temp_key_path)
                else:
                    print(Colors.warning("No answers found in PDF, continuing without key"))
            except Exception as e:
                print(Colors.warning(f"Auto-extraction failed: {str(e)}, continuing without key"))
```

- [ ] **Step 3: Run full test suite**

```bash
python3 -m pytest tests/ -v --tb=short
```

Expected: 
- ✅ 73+ existing tests PASSED
- ✅ 20+ new tests PASSED (extractor + mapper)
- ✅ 0 failures

- [ ] **Step 4: Commit**

```bash
git add cissp_analyzer/interactive_cli.py
git commit -m "feat: integrate answer context mapping into interactive workflow"
```

---

## Task 5: End-to-End Testing with Answer Context

**Files:**
- No file creation (testing only)

- [ ] **Step 1: Test auto-extract with Week 1 data**

```bash
cd /Users/sriram/cissp-analyzer
python3 analyze.py
# Exam: 1
# PDF: test_pdfs/week1_exam.pdf
# Auto-extract: y
# Add 5 students
# Output: week1_results_with_context
# Run: y
```

Expected:
- ✅ PDF reads successfully
- ✅ Auto-extraction finds answers WITH text
- ✅ Domain context extracted from answer keywords
- ✅ Reports generated with improved domain accuracy

- [ ] **Step 2: Verify answer text was extracted**

```bash
cat week1_results_with_context/.answer_key_temp.json | head -20
```

Expected: JSON shows both letter and text for each answer

- [ ] **Step 3: Test Week 2 multi-exam tracking**

```bash
python3 analyze.py
# Exam: 2
# PDF: test_pdfs/week2_exam.pdf
# Auto-extract: y
# Add same 5 students
# Output: week2_results_with_context
# Run: y
```

Expected:
- ✅ Week 2 analysis completes
- ✅ Progress calculations use context-aware domain mapping
- ✅ Adaptive recommendations more accurate (based on real domain classification)

- [ ] **Step 4: Verify domain mapping improvement**

Compare individual reports from Week 1 and Week 2:
- Check that domain assignments match expected CISSP domains
- Verify that answer text keywords influenced classifications
- Check that adaptive recommendations reference correct domains

- [ ] **Step 5: Run final test suite**

```bash
python3 -m pytest tests/ -v --tb=short -k "answer_key or context_mapper"
```

Expected: All 20+ new tests PASSED

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "test: validate auto-extract with answer context on real Week 1 and Week 2 data"
```

---

## Summary

**Total Tasks:** 5  
**New Files:** 4 (answer extractor, mapper, 2 test files)  
**Modified Files:** 2 (pdf_parser, interactive_cli)  
**Estimated Time:** 3-4 hours  
**Cost:** $0 (pure local text parsing)

**CRITICAL ENHANCEMENT:** 
✅ Domain/topic mapping now considers BOTH question text AND answer keywords
✅ Answer text is extracted alongside answer letters
✅ AnswerContextMapper intelligently combines contexts
✅ Improved accuracy for ambiguous questions

**What Gets Delivered:**
1. ✅ `AnswerKeyExtractor` with answer text extraction (200+ lines)
2. ✅ `AnswerContextMapper` for smart domain classification (250+ lines)
3. ✅ Enhanced PDF parser with context support
4. ✅ Integrated CLI workflow with answer context
5. ✅ 20+ comprehensive tests
6. ✅ 6 focused commits

**Success Criteria:**
- ✅ Extract answer letters AND answer text from PDFs
- ✅ Use answer keywords to improve domain classification
- ✅ Ambiguous questions classified correctly via answer context
- ✅ Multi-exam tracking benefits from accurate domain mapping
- ✅ All 93+ tests passing (73 existing + 20 new)
- ✅ Real Week 1/Week 2 data validates improvements

---

Plan complete and saved to `docs/superpowers/plans/2026-07-01-auto-answer-extraction.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - Fresh subagent per task, two-stage review (spec compliance, then code quality)

**2. Inline Execution** - Execute tasks directly in this session with checkpoints

Which approach?