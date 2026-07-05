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
            "risk",
            "threat",
            "vulnerability",
            "governance",
            "policy",
            "compliance",
            "regulation",
            "audit",
            "assessment",
            "management",
            "asset management",
            "security program",
        ],
        "Access Control and Identity Management": [
            "access control",
            "authentication",
            "authorization",
            "identity",
            "rbac",
            "abac",
            "role",
            "permission",
            "privilege",
            "accountability",
            "user",
            "credential",
            "password",
            "mfa",
            "multi-factor",
        ],
        "Cryptography": [
            "encryption",
            "cipher",
            "aes",
            "rsa",
            "hash",
            "signature",
            "symmetric",
            "asymmetric",
            "cryptographic",
            "key",
            "ssl",
            "tls",
            "certificate",
            "digital signature",
            "ecc",
        ],
        "Physical and Environmental Security": [
            "physical",
            "environment",
            "facility",
            "building",
            "access point",
            "badge",
            "biometric",
            "surveillance",
            "cctv",
            "locks",
            "guards",
            "location",
            "perimeter",
        ],
        "Communication and Network Security": [
            "network",
            "protocol",
            "firewall",
            "intrusion",
            "detection",
            "vpn",
            "wan",
            "lan",
            "router",
            "switch",
            "dns",
            "dhcp",
            "communication",
            "osi model",
            "tcp",
            "ip",
            "packet",
            "snmp",
        ],
        "System and Application Security": [
            "application",
            "system",
            "patch",
            "update",
            "vulnerability",
            "exploit",
            "malware",
            "virus",
            "antivirus",
            "endpoint",
            "code",
            "secure coding",
            "input validation",
            "buffer overflow",
        ],
        "Security Assessment and Testing": [
            "assessment",
            "testing",
            "penetration",
            "pentest",
            "scan",
            "vulnerability assessment",
            "security test",
            "audit",
            "review",
            "evaluation",
            "metrics",
            "benchmark",
        ],
        "Security Operations": [
            "incident",
            "response",
            "monitoring",
            "logging",
            "siem",
            "detection",
            "investigation",
            "forensics",
            "recovery",
            "disaster",
            "continuity",
            "backup",
            "alert",
            "alarm",
        ],
        "Software Development Security": [
            "development",
            "sdlc",
            "secure coding",
            "code review",
            "testing",
            "deployment",
            "repository",
            "version control",
            "agile",
            "waterfall",
        ],
        "Cloud Security": [
            "cloud",
            "aws",
            "azure",
            "gcp",
            "saas",
            "paas",
            "iaas",
            "virtualization",
            "container",
            "docker",
            "kubernetes",
            "serverless",
        ],
    }

    def __init__(self, mapping_file: Optional[str] = None) -> None:
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

    def map_with_keywords(
        self, question_text: str, answer_keywords: List[str]
    ) -> Optional[str]:
        """Map question using question text and explicit answer keywords.

        Args:
            question_text: The question being asked
            answer_keywords: Keywords extracted from answer

        Returns:
            Best matching domain name, or None if no match
        """
        combined_text = f"{question_text} {' '.join(answer_keywords)}"
        return self._classify_text(combined_text)

    def detect_domains_from_text(
        self, text: str, domain_keywords: Optional[Dict] = None
    ) -> List[str]:
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
                pattern = r"\b" + re.escape(keyword) + r"\b"
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
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "is",
            "are",
            "be",
            "been",
            "being",
            "have",
            "has",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "that",
            "this",
            "these",
            "those",
            "which",
        }

        # Split and filter
        words = text.lower().split()
        keywords = set()

        for word in words:
            # Remove punctuation
            clean_word = re.sub(r"[^\w\s-]", "", word)

            # Keep words >= 3 chars that aren't stop words
            # Also keep uppercase acronyms (e.g., AES, RSA)
            if len(clean_word) >= 3 and clean_word not in stop_words:
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
