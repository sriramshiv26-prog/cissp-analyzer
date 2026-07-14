#!/usr/bin/env python3
"""
Dual-Tier Questionnaire Processor for CISSP Analyzer
Processes questionnaires with both TIER 1 (5 categories) and TIER 2 (13 trap codes)

TIER 1: Original categorization - domain, topic, difficulty, type, exam_trick
TIER 2: Trap code detection - NEG, ABS, EASY, ROLE, SCOPE, ORDER, ALL, GOLD, ETHIC, TIME, REPEAT
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum


class TrapCode(Enum):
    """13 Trap Codes for TIER 2 Analysis"""

    NEG = "Negative Modifiers"  # NOT, EXCEPT, LEAST, NONE OF
    ABS = "Absolute Language"  # ALWAYS, NEVER, ALL, COMPLETELY, 100%
    EASY = "The Overthink"  # Simple question that looks too easy
    ROLE = "Job Title Mismatch"  # Wrong role → wrong answer
    SCOPE = "Boundary Confusion"  # IaaS/PaaS/SaaS responsibility models
    ORDER = "Process Sequence"  # FIRST, BEFORE, SEQUENCE, STEP
    ALL = "Umbrella Effect"  # Tactical answer vs strategic umbrella
    GOLD = "Shiny Object"  # Impressive but irrelevant crypto/PKI
    ETHIC = "Moral Hazard"  # Violates ISC2 Canon
    TIME = "Clock Killer"  # Long complex scenario
    REPEAT = "Deja Vu"  # Same domain appears twice


@dataclass
class Tier1Categorization:
    """TIER 1: Original 5 categories"""

    domain: int
    domain_name: str
    topic: str
    subtopic: Optional[str]
    difficulty: str
    question_type: str
    exam_trick: str


@dataclass
class Tier2TrapAnalysis:
    """TIER 2: 13 Trap Code Analysis"""

    trap_codes: List[str]
    trap_details: Dict[str, Dict]
    risk_level: str  # CRITICAL, HIGH, MEDIUM


@dataclass
class QuestionProfile:
    """Complete question profile with both tiers"""

    number: int
    text: str
    options: Dict[str, str]
    correct_answer: str
    correct_explanation: str

    tier1: Tier1Categorization
    tier2: Tier2TrapAnalysis


class TrapDetector:
    """Detects 13 trap codes in questions and answers"""

    def __init__(self):
        self.trap_patterns = {
            TrapCode.NEG: {
                "keywords": [
                    r"\bNOT\b",
                    r"\bEXCEPT\b",
                    r"\bLEAST\b",
                    r"\bNONE OF\b",
                    r"\bALL ARE.*EXCEPT\b",
                ],
                "risk": "CRITICAL",
            },
            TrapCode.ABS: {
                "keywords": [
                    r"\bALWAYS\b",
                    r"\bNEVER\b",
                    r"\bCOMPLETELY\b",
                    r"\b100%\b",
                    r"\bWILL PREVENT\b",
                ],
                "risk": "HIGH",
            },
            TrapCode.ORDER: {
                "keywords": [
                    r"\bFIRST\b",
                    r"\bBEFORE\b",
                    r"\bSEQUENCE\b",
                    r"\bSTEP\b",
                    r"\bINITIAL\b",
                ],
                "risk": "CRITICAL",
            },
            TrapCode.ROLE: {
                "keywords": [r"\b(ANALYST|MANAGER|OWNER|CUSTODIAN|CISO|DATA OWNER)\b"],
                "risk": "HIGH",
            },
            TrapCode.SCOPE: {
                "keywords": [
                    r"\b(IaaS|PAAS|SAAS|CLOUD|HYPERVISOR|SHARED RESPONSIBILITY)\b"
                ],
                "risk": "HIGH",
            },
            TrapCode.ALL: {
                "keywords": [
                    r"\b(STRATEGY|COMPREHENSIVE|FRAMEWORK|DEFENSE-IN-DEPTH|OVERALL)\b"
                ],
                "risk": "MEDIUM",
            },
            TrapCode.GOLD: {
                "keywords": [
                    r"\b(ENCRYPTION|PKI|BLOCKCHAIN|CRYPTOGRAPHY|CERTIFICATE)\b"
                ],
                "risk": "MEDIUM",
            },
            TrapCode.ETHIC: {
                "keywords": [
                    r"\b(HACK BACK|OFFENSIVE|VIGILANTE|ILLEGAL|UNAUTHORIZED)\b"
                ],
                "risk": "HIGH",
            },
        }

    def detect_traps(
        self,
        question_text: str,
        options: Dict[str, str],
        correct_answer: str,
        is_short_question: bool = False,
        position: int = 0,
    ) -> Tuple[List[str], Dict, str]:
        """
        Detect trap codes in question
        Returns: (trap_codes, trap_details, risk_level)
        """
        detected_traps = {}
        combined_text = question_text + " " + " ".join(options.values())

        # Keyword-based detection
        for trap_code, pattern_info in self.trap_patterns.items():
            for keyword_pattern in pattern_info["keywords"]:
                if re.search(keyword_pattern, combined_text, re.IGNORECASE):
                    if trap_code.name not in detected_traps:
                        detected_traps[trap_code.name] = {
                            "name": trap_code.value,
                            "risk": pattern_info["risk"],
                            "detected": True,
                            "keywords_found": [],
                        }
                    # Extract matching keywords
                    matches = re.findall(keyword_pattern, combined_text, re.IGNORECASE)
                    detected_traps[trap_code.name]["keywords_found"].extend(matches)

        # EASY trap: short question early in exam or after failure
        if is_short_question and position < 30:
            detected_traps["EASY"] = {
                "name": "The Overthink",
                "risk": "HIGH",
                "detected": True,
                "reason": "Short question early in exam",
            }

        # TIME trap: long complex scenario
        if len(question_text) > 300:
            detected_traps["TIME"] = {
                "name": "Clock Killer",
                "risk": "CRITICAL",
                "detected": True,
                "reason": "Long complex scenario (300+ chars)",
            }

        # Determine overall risk level
        if any(trap.get("risk") == "CRITICAL" for trap in detected_traps.values()):
            risk_level = "CRITICAL"
        elif any(trap.get("risk") == "HIGH" for trap in detected_traps.values()):
            risk_level = "HIGH"
        else:
            risk_level = "MEDIUM" if detected_traps else "LOW"

        trap_codes = list(detected_traps.keys())
        return trap_codes, detected_traps, risk_level


class QuestionnaireProcessor:
    """Process questionnaires with both TIER 1 and TIER 2 categorization"""

    def __init__(self, domain_mapper_path: str):
        self.domain_mapper = self._load_domain_mapper(domain_mapper_path)
        self.trap_detector = TrapDetector()
        self.previous_domains = []  # Track for REPEAT trap detection

    def _load_domain_mapper(self, path: str) -> Dict:
        """Load domain mapping from JSON"""
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Domain mapper not found at {path}")
            return {}

    def _categorize_tier1(
        self, question_num: int, question_text: str
    ) -> Tier1Categorization:
        """Apply TIER 1 categorization using domain mapper"""
        # Fetch from domain mapper if available
        q_key = f"q_{question_num}"

        if q_key in self.domain_mapper:
            q_data = self.domain_mapper[q_key]
            return Tier1Categorization(
                domain=q_data.get("domain", 0),
                domain_name=q_data.get("domain_name", "Unknown"),
                topic=q_data.get("topic", "General"),
                subtopic=q_data.get("subtopic"),
                difficulty=q_data.get("difficulty", "Medium"),
                question_type=q_data.get("question_type", "Knowledge"),
                exam_trick=q_data.get("exam_trick", "NONE"),
            )

        # Fallback: basic categorization
        return Tier1Categorization(
            domain=1,
            domain_name="Security & Risk Management",
            topic="General",
            subtopic=None,
            difficulty="Medium",
            question_type="Knowledge",
            exam_trick="NONE",
        )

    def process_question(
        self,
        question_num: int,
        question_text: str,
        options: Dict[str, str],
        correct_answer: str,
        explanation: str = "",
    ) -> QuestionProfile:
        """
        Process single question through both tiers
        """
        # TIER 1: Original categorization
        tier1 = self._categorize_tier1(question_num, question_text)

        # TIER 2: Trap code detection
        is_short = len(question_text) < 100
        trap_codes, trap_details, risk_level = self.trap_detector.detect_traps(
            question_text,
            options,
            correct_answer,
            is_short_question=is_short,
            position=question_num,
        )

        # Detect REPEAT trap
        if tier1.domain in self.previous_domains:
            trap_codes.append("REPEAT")
            trap_details["REPEAT"] = {
                "name": "Deja Vu",
                "risk": "MEDIUM",
                "detected": True,
                "reason": f"Domain {tier1.domain} appeared previously",
            }

        self.previous_domains.append(tier1.domain)

        tier2 = Tier2TrapAnalysis(
            trap_codes=trap_codes, trap_details=trap_details, risk_level=risk_level
        )

        return QuestionProfile(
            number=question_num,
            text=question_text,
            options=options,
            correct_answer=correct_answer,
            correct_explanation=explanation,
            tier1=tier1,
            tier2=tier2,
        )

    def process_questionnaire(self, questions: List[Dict]) -> Dict:
        """
        Process complete questionnaire
        Returns JSON with both tiers for all questions
        """
        processed_questions = []
        stats = {
            "total_questions": len(questions),
            "domain_distribution": {},
            "difficulty_distribution": {},
            "trap_distribution": {},
            "risk_distribution": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        }

        for i, q in enumerate(questions, 1):
            profile = self.process_question(
                question_num=q.get("number", i),
                question_text=q.get("text", ""),
                options=q.get("options", {}),
                correct_answer=q.get("correct_answer", ""),
                explanation=q.get("explanation", ""),
            )

            # Update statistics
            domain = profile.tier1.domain_name
            stats["domain_distribution"][domain] = (
                stats["domain_distribution"].get(domain, 0) + 1
            )

            difficulty = profile.tier1.difficulty
            stats["difficulty_distribution"][difficulty] = (
                stats["difficulty_distribution"].get(difficulty, 0) + 1
            )

            for trap in profile.tier2.trap_codes:
                stats["trap_distribution"][trap] = (
                    stats["trap_distribution"].get(trap, 0) + 1
                )

            stats["risk_distribution"][profile.tier2.risk_level] += 1

            # Serialize to dict
            processed_questions.append(
                {
                    "number": profile.number,
                    "text": profile.text,
                    "options": profile.options,
                    "correct_answer": profile.correct_answer,
                    "correct_explanation": profile.correct_explanation,
                    "tier1": asdict(profile.tier1),
                    "tier2": {
                        "trap_codes": profile.tier2.trap_codes,
                        "trap_details": profile.tier2.trap_details,
                        "risk_level": profile.tier2.risk_level,
                    },
                }
            )

        return {
            "metadata": {
                "total_questions": stats["total_questions"],
                "processor_version": "1.0",
                "categorization_system": "Dual-Tier (TIER 1: 5 categories + TIER 2: 13 trap codes)",
            },
            "statistics": stats,
            "questions": processed_questions,
        }


def generate_sample_output():
    """Generate sample output showing dual-tier categorization"""
    sample = {
        "question": {
            "number": 77,
            "text": "A rogue wireless device has been found on a network, and the way it was discovered is that individuals were not able to get a DHCP address. What should be done to prevent this in the future?",
            "options": {
                "A": "Turn on port authentication on the host switches.",
                "B": "Create reservation on the DHCP server.",
                "C": "Set the clients to Bootstrap Protocol (BootP).",
                "D": "Expand the reservation pool on the DHCP server.",
            },
            "correct_answer": "A",
            "explanation": "Turn on port authentication on the host switches to prevent rogue stations from connecting without proper MAC addresses.",
            "TIER_1_ORIGINAL_5_CATEGORIES": {
                "domain": 3,
                "domain_name": "Security Architecture and Engineering",
                "topic": "Network Security",
                "subtopic": "Access Control",
                "difficulty": "Medium",
                "question_type": "Application",
                "exam_trick": "BEST",
            },
            "TIER_2_NEW_13_TRAP_CODES": {
                "trap_codes": ["ROLE", "SCOPE"],
                "trap_details": {
                    "ROLE": {
                        "name": "Job Title Mismatch",
                        "risk": "HIGH",
                        "detected": True,
                        "explanation": "Question asks 'what should be done' - assumes network admin role, but answer requires understanding responsibility boundaries",
                    },
                    "SCOPE": {
                        "name": "Boundary Confusion",
                        "risk": "HIGH",
                        "detected": True,
                        "explanation": "Question context (DHCP, port authentication) tests understanding of access control scope",
                    },
                },
                "risk_level": "HIGH",
            },
        }
    }
    return sample


if __name__ == "__main__":
    # Example usage
    print("CISSP Questionnaire Processor - Dual Tier System")
    print("=" * 60)
    print("\nSample Output Structure:")
    print(json.dumps(generate_sample_output(), indent=2))
