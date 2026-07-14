"""
Trap Category Analysis Engine for CISSP Analyzer

This module analyzes student answers against a comprehensive trap category system
to identify cognitive traps and misconceptions. It provides personalized feedback
on why students fell for specific exam traps and generates targeted study recommendations.

The 21 trap categories cover reading comprehension, logic, context understanding,
knowledge application, and test-taking psychology.

Author: CISSP Analyzer
Version: 1.0.0
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class TrapExplanation:
    """Detailed explanation of why student fell for a specific trap."""

    question_num: int
    trap_category: str
    trap_name: str
    severity: str  # "Critical", "High", "Medium", "Low"
    why_student_fell: str
    isc2_fix: str
    prevention_tip: str
    example: str
    affected_domain: int
    confidence_score: float  # 0.0-1.0, how certain we are about this trap


@dataclass
class TrapVulnerability:
    """Summarized trap vulnerability for a student."""

    trap_category: str
    trap_name: str
    frequency_count: int
    affected_questions: List[int]
    success_rate: float  # Percentage of questions with this trap the student got right
    severity: str
    is_high_priority: bool
    recommendation: str


@dataclass
class AnswerAnalysisResult:
    """Complete analysis result for a single answer."""

    question_num: int
    student_answer: str
    correct_answer: str
    is_correct: bool
    trap_category: Optional[str]
    trap_explanation: Optional[TrapExplanation]
    domain: int
    difficulty: str


class TrapAnalysisEngine:
    """
    Core engine for analyzing student answers against trap categories.

    This engine loads trap category definitions and question-to-trap mappings,
    then analyzes student answers to identify which traps each student fell for.
    It provides detailed feedback and personalized study recommendations.

    Attributes:
        trap_categories_path: Path to trap_categories_reference.json
        question_mapping_path: Path to question_domain_mapping.json
        trap_categories: Loaded trap category definitions
        question_mappings: Loaded question-to-trap and domain mappings
    """

    def __init__(
        self,
        trap_categories_path: str = None,
        question_mapping_path: str = None,
    ):
        """
        Initialize the trap analysis engine.

        Args:
            trap_categories_path: Path to trap_categories_reference.json
                Defaults to docs/trap_categories_reference.json
            question_mapping_path: Path to question_domain_mapping.json
                Defaults to data/question_domain_mapping.json
        """
        # Set default paths relative to project root
        if trap_categories_path is None:
            trap_categories_path = (
                Path(__file__).parent.parent / "docs" / "trap_categories_reference.json"
            )
        if question_mapping_path is None:
            question_mapping_path = (
                Path(__file__).parent.parent / "data" / "question_domain_mapping.json"
            )

        self.trap_categories_path = Path(trap_categories_path)
        self.question_mapping_path = Path(question_mapping_path)

        # Initialize data structures
        self.trap_categories: Dict[str, Dict] = {}
        self.question_mappings: Dict[int, Dict] = {}

        # Load trap mappings
        self._load_trap_mappings()

    def _load_trap_mappings(self) -> None:
        """
        Load trap categories and question mappings from JSON files.

        Raises:
            FileNotFoundError: If required JSON files are not found
            json.JSONDecodeError: If JSON files are malformed
        """
        try:
            # Load trap categories reference
            if not self.trap_categories_path.exists():
                raise FileNotFoundError(
                    f"Trap categories file not found: {self.trap_categories_path}"
                )

            with open(self.trap_categories_path, "r", encoding="utf-8") as f:
                trap_data = json.load(f)
                self.trap_categories = trap_data.get("categories", {})

            logger.info(f"Loaded {len(self.trap_categories)} trap categories")

            # Load question mappings
            if not self.question_mapping_path.exists():
                raise FileNotFoundError(
                    f"Question mapping file not found: {self.question_mapping_path}"
                )

            with open(self.question_mapping_path, "r", encoding="utf-8") as f:
                self.question_mappings = json.load(f)

            logger.info(f"Loaded mappings for {len(self.question_mappings)} questions")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading trap mappings: {e}")
            raise

    def load_trap_mappings(self) -> Dict[str, Dict]:
        """
        Public method to load and return trap category mappings.

        This is the primary entry point for loading trap data. Useful for
        inspection and debugging.

        Returns:
            Dictionary of trap categories with full definitions
        """
        return self.trap_categories.copy()

    def analyze_answer(
        self, question_num: int, student_answer: str, correct_answer: str
    ) -> AnswerAnalysisResult:
        """
        Analyze a single student answer against the trap category system.

        This function compares the student's answer with the correct answer,
        and if wrong, identifies which trap category likely caused the error.
        It generates detailed explanation of why the student fell for the trap.

        Args:
            question_num: Question number (1-161)
            student_answer: Student's selected answer (A, B, C, or D)
            correct_answer: Correct answer from answer key (A, B, C, or D)

        Returns:
            AnswerAnalysisResult with trap category and explanation (if answer
            is wrong)

        Example:
            >>> engine = TrapAnalysisEngine()
            >>> result = engine.analyze_answer(1, "B", "A")
            >>> if not result.is_correct:
            ...     print(f"Student fell for: {result.trap_category}")
            ...     print(result.trap_explanation.isc2_fix)
        """
        # Normalize answers (remove whitespace, uppercase)
        student_answer = str(student_answer).strip().upper()
        correct_answer = str(correct_answer).strip().upper()

        # Get question metadata
        q_data = self.question_mappings.get(str(question_num), {})
        domain = q_data.get("domain", 0)
        difficulty = q_data.get("difficulty", "Unknown")
        trap_category = q_data.get("exam_trick", None)

        # Check if answer is correct
        is_correct = student_answer == correct_answer

        # Initialize result
        result = AnswerAnalysisResult(
            question_num=question_num,
            student_answer=student_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            trap_category=None,
            trap_explanation=None,
            domain=domain,
            difficulty=difficulty,
        )

        # If answer is wrong, identify trap and generate explanation
        if not is_correct and trap_category:
            result.trap_category = trap_category
            result.trap_explanation = self._generate_trap_explanation(
                question_num, student_answer, correct_answer, trap_category, domain
            )

        return result

    def _generate_trap_explanation(
        self,
        question_num: int,
        student_answer: str,
        correct_answer: str,
        trap_category: str,
        domain: int,
    ) -> TrapExplanation:
        """
        Generate detailed explanation for why student fell for a specific trap.

        Args:
            question_num: Question number
            student_answer: Student's answer
            correct_answer: Correct answer
            trap_category: Trap category code (NEG, TOOL, ORDER, etc.)
            domain: CISSP domain (1-8)

        Returns:
            TrapExplanation with detailed feedback
        """
        trap_def = self.trap_categories.get(trap_category, {})

        # Determine severity based on trap type and question domain
        severity = self._assess_severity(trap_category, domain)

        # Generate why student fell for the trap
        why_fell = self._generate_why_fell(trap_category, trap_def, student_answer)

        # Get ISC2 fix from trap definition
        isc2_fix = trap_def.get(
            "the_fix", "Review ISC2 study materials for this concept."
        )

        # Get prevention strategy
        prevention = trap_def.get(
            "prevention_strategy", "Apply careful review before selecting answer."
        )

        # Get example
        example = trap_def.get("example_correct", "")

        # Calculate confidence score based on trap category and domain alignment
        confidence = self._calculate_confidence(trap_category, domain)

        return TrapExplanation(
            question_num=question_num,
            trap_category=trap_category,
            trap_name=trap_def.get("name", "Unknown Trap"),
            severity=severity,
            why_student_fell=why_fell,
            isc2_fix=isc2_fix,
            prevention_tip=prevention,
            example=example,
            affected_domain=domain,
            confidence_score=confidence,
        )

    def _assess_severity(self, trap_category: str, domain: int) -> str:
        """
        Assess severity of falling for a trap.

        Severity is based on:
        1. Trap difficulty rating from trap_categories_reference.json
        2. Whether the trap commonly affects this domain

        Args:
            trap_category: Trap code (NEG, TOOL, ORDER, etc.)
            domain: CISSP domain (1-8)

        Returns:
            "Critical", "High", "Medium", or "Low"
        """
        trap_def = self.trap_categories.get(trap_category, {})
        difficulty = trap_def.get("difficulty", "⭐⭐ Medium")

        if "⭐⭐⭐⭐" in difficulty:
            return "Critical"
        elif "⭐⭐⭐" in difficulty:
            return "High"
        elif "⭐⭐" in difficulty:
            return "Medium"
        else:
            return "Low"

    def _generate_why_fell(
        self, trap_category: str, trap_def: Dict, student_answer: str
    ) -> str:
        """
        Generate human-readable explanation of why student fell for trap.

        Args:
            trap_category: Trap code
            trap_def: Trap definition dictionary
            student_answer: Student's selected answer

        Returns:
            Explanation string
        """
        trap_type = trap_def.get("type", "Unknown")
        trap_desc = trap_def.get("the_trap", "")

        if trap_category == "NEG":
            return (
                f"You likely missed the negative modifier (LEAST, EXCEPT, NOT) "
                f"and selected the obvious positive answer instead of the negated one."
            )
        elif trap_category == "ORDER":
            return (
                f"You identified a correct technique, but applied it in the wrong "
                f"sequence. Process order matters in CISSP (BCP, Incident Response, etc.)."
            )
        elif trap_category == "TOOL":
            return (
                f"You chose a technically sound security control, but it's not the "
                f"best fit for this specific scenario or threat type."
            )
        elif trap_category == "ROLE":
            return (
                f"You suggested an action appropriate for a different role. "
                f"Match the authority and responsibility to the job title given."
            )
        elif trap_category == "DEFINITION":
            return (
                f"You confused two similar concepts (e.g., Authentication ≠ Authorization, "
                f"Threat ≠ Risk). Ensure you're answering what's actually being asked."
            )
        elif trap_category == "LIFECYCLE":
            return (
                f"You understand what needs to be done, but placed it at the wrong "
                f"stage in the process lifecycle (Design/Develop/Test/Deploy/Maintain)."
            )
        elif trap_category == "HIERARCHY":
            return (
                f"You assigned decision authority to the wrong person in the organization. "
                f"Different roles have different authority levels."
            )
        elif trap_category == "COMPLIANCE":
            return (
                f"You applied the wrong regulatory framework to this scenario. "
                f"Each regulation applies to specific regions, industries, or data types."
            )
        elif trap_category == "SCOPE":
            return (
                f"You applied on-premise thinking to cloud, or misidentified the shared "
                f"responsibility model boundary."
            )
        elif trap_category == "ABS":
            return (
                f"You selected an answer with absolute language (Always, Never, Completely). "
                f"In risk management, certainty is impossible—look for probabilistic answers."
            )
        elif trap_category == "VERSUS":
            return (
                f"Both your answer and the correct answer are technically true, but one is "
                f"the better practice or more specific for this context."
            )
        else:
            return (
                f"You fell for a '{trap_def.get('name', 'common')}' trap: {trap_desc}"
            )

    def _calculate_confidence(self, trap_category: str, domain: int) -> float:
        """
        Calculate confidence that this trap identification is correct.

        Confidence is higher when:
        1. Trap category is listed for this domain
        2. Trap has high frequency in actual exams
        3. Trap type matches question difficulty

        Args:
            trap_category: Trap code
            domain: CISSP domain

        Returns:
            Confidence score from 0.0 to 1.0
        """
        trap_def = self.trap_categories.get(trap_category, {})
        affected_domains = trap_def.get("affected_domains", [])
        frequency = trap_def.get("frequency", "5%")

        # Base confidence on frequency
        try:
            freq_pct = float(frequency.strip("%")) / 100
        except (ValueError, AttributeError):
            freq_pct = 0.5

        # Boost confidence if this trap affects the domain
        if domain in affected_domains:
            freq_pct += 0.15

        # Cap at 1.0
        return min(freq_pct, 1.0)

    def analyze_all_answers(
        self, answer_dict: Dict[int, str], answer_key: Dict[int, str]
    ) -> List[AnswerAnalysisResult]:
        """
        Analyze all student answers in batch.

        Batch analysis is more efficient than calling analyze_answer repeatedly,
        especially for comprehensive reports.

        Args:
            answer_dict: Dictionary mapping question numbers to student answers
                Example: {1: "A", 2: "B", 3: "C", ...}
            answer_key: Dictionary mapping question numbers to correct answers
                Example: {1: "A", 2: "A", 3: "D", ...}

        Returns:
            List of AnswerAnalysisResult objects for all questions

        Example:
            >>> answers = {1: "B", 2: "A", 3: "C"}
            >>> key = {1: "A", 2: "A", 3: "A"}
            >>> results = engine.analyze_all_answers(answers, key)
            >>> wrong_results = [r for r in results if not r.is_correct]
        """
        results = []

        for q_num, student_ans in answer_dict.items():
            correct_ans = answer_key.get(q_num, "")
            result = self.analyze_answer(q_num, student_ans, correct_ans)
            results.append(result)

        return results

    def summarize_vulnerabilities(
        self, analysis_results: List[AnswerAnalysisResult]
    ) -> List[TrapVulnerability]:
        """
        Summarize trap vulnerabilities across all student answers.

        This creates a high-level summary of which traps the student is most
        vulnerable to, ranked by frequency and severity.

        Args:
            analysis_results: List of AnswerAnalysisResult from analyze_all_answers()

        Returns:
            List of TrapVulnerability objects, sorted by severity and frequency

        Example:
            >>> results = engine.analyze_all_answers(answers, key)
            >>> vulnerabilities = engine.summarize_vulnerabilities(results)
            >>> for vuln in vulnerabilities[:5]:
            ...     print(f"{vuln.trap_name}: {vuln.frequency_count} times")
        """
        # Group by trap category
        trap_stats: Dict[str, Dict] = defaultdict(
            lambda: {
                "count": 0,
                "questions": [],
                "correct": 0,
                "name": "",
                "severity": "Low",
            }
        )

        for result in analysis_results:
            if result.trap_category and not result.is_correct:
                trap_cat = result.trap_category
                trap_stats[trap_cat]["count"] += 1
                trap_stats[trap_cat]["questions"].append(result.question_num)
                trap_stats[trap_cat]["name"] = self.trap_categories.get(
                    trap_cat, {}
                ).get("name", "Unknown")
                trap_stats[trap_cat]["severity"] = result.trap_explanation.severity

        # Build vulnerability list
        vulnerabilities = []

        for trap_cat, stats in trap_stats.items():
            if stats["count"] == 0:
                continue

            # Calculate success rate for this trap
            trap_def = self.trap_categories.get(trap_cat, {})
            success_rate = (stats["correct"] / stats["count"]) * 100

            # Determine if high priority
            is_high = trap_cat in [
                "NEG",
                "ORDER",
                "ROLE",
                "TOOL",
                "DEFINITION",
                "LIFECYCLE",
                "COMPLIANCE",
                "HIERARCHY",
            ]

            # Generate recommendation
            recommendation = self._generate_recommendation(trap_cat, stats["count"])

            vuln = TrapVulnerability(
                trap_category=trap_cat,
                trap_name=stats["name"],
                frequency_count=stats["count"],
                affected_questions=sorted(stats["questions"]),
                success_rate=success_rate,
                severity=stats["severity"],
                is_high_priority=is_high,
                recommendation=recommendation,
            )

            vulnerabilities.append(vuln)

        # Sort by: severity (High/Critical first), then frequency
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        vulnerabilities.sort(
            key=lambda v: (
                severity_order.get(v.severity, 4),
                -v.frequency_count,
            )
        )

        return vulnerabilities

    def _generate_recommendation(self, trap_category: str, frequency: int) -> str:
        """
        Generate personalized study recommendation for a trap.

        Args:
            trap_category: Trap code
            frequency: How many times student fell for this trap

        Returns:
            Actionable study recommendation string
        """
        trap_def = self.trap_categories.get(trap_category, {})
        base_strategy = trap_def.get("prevention_strategy", "Review study materials.")

        if frequency == 1:
            return f"Study this trap once: {base_strategy}"
        elif frequency <= 3:
            return f"This appears {frequency} times. {base_strategy}"
        else:
            return (
                f"High exposure ({frequency} times). PRIORITY: {base_strategy} "
                f"Create flashcards and drill this concept."
            )

    def generate_recommendations(
        self, vulnerabilities: List[TrapVulnerability]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive personalized study recommendations.

        This creates an actionable study plan targeting the student's weakest
        trap categories, prioritized by impact and frequency.

        Args:
            vulnerabilities: List of TrapVulnerability from summarize_vulnerabilities()

        Returns:
            Dictionary with:
                - study_plan: Ordered list of study priorities
                - high_priority_traps: Top 3-5 traps to focus on
                - medium_priority_traps: Next tier of traps
                - low_priority_traps: Lower-impact traps
                - total_vulnerabilities: Count of unique traps
                - primary_recommendation: One-sentence summary

        Example:
            >>> recommendations = engine.generate_recommendations(vulnerabilities)
            >>> print(recommendations["primary_recommendation"])
            >>> for item in recommendations["study_plan"][:3]:
            ...     print(f"  {item}")
        """
        if not vulnerabilities:
            return {
                "study_plan": [],
                "high_priority_traps": [],
                "medium_priority_traps": [],
                "low_priority_traps": [],
                "total_vulnerabilities": 0,
                "primary_recommendation": (
                    "Excellent! No major trap vulnerabilities detected. "
                    "Continue focused practice and review weaker domains."
                ),
            }

        # Separate by priority
        high_priority = [v for v in vulnerabilities if v.is_high_priority]
        low_priority = [v for v in vulnerabilities if not v.is_high_priority]

        # Build study plan
        study_plan = []

        # Add high priority traps
        for i, vuln in enumerate(high_priority[:5], 1):
            study_plan.append(
                f"{i}. CRITICAL: Master '{vuln.trap_name}' ({vuln.frequency_count} questions). "
                f"{vuln.recommendation}"
            )

        # Add medium-high priority
        for i, vuln in enumerate(low_priority[:5], len(high_priority) + 1):
            study_plan.append(
                f"{i}. Review '{vuln.trap_name}' ({vuln.frequency_count} times). "
                f"{vuln.recommendation}"
            )

        # Generate primary recommendation
        if high_priority:
            top_trap = high_priority[0]
            total_exposed = sum(v.frequency_count for v in vulnerabilities)
            primary = (
                f"Focus on '{top_trap.trap_name}' (caused {top_trap.frequency_count} "
                f"of {total_exposed} mistakes). "
                f"Use {top_trap.recommendation.lower()}"
            )
        else:
            primary = "Consolidate learning by drilling medium-priority traps."

        return {
            "study_plan": study_plan,
            "high_priority_traps": [
                asdict(v) for v in high_priority[:5]
            ],  # Convert to dict for JSON serialization
            "medium_priority_traps": [asdict(v) for v in low_priority[:5]],
            "total_vulnerabilities": len(vulnerabilities),
            "primary_recommendation": primary,
        }

    def get_trap_details(self, trap_category: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific trap category.

        Useful for student reference and deep learning.

        Args:
            trap_category: Trap code (NEG, TOOL, ORDER, etc.)

        Returns:
            Complete trap definition or None if not found

        Example:
            >>> trap_info = engine.get_trap_details("NEG")
            >>> print(trap_info["the_fix"])
        """
        return self.trap_categories.get(trap_category, None)

    def get_question_trap_info(self, question_num: int) -> Optional[Dict[str, Any]]:
        """
        Get trap category information for a specific question.

        Args:
            question_num: Question number (1-161)

        Returns:
            Dictionary with question metadata and trap details, or None

        Example:
            >>> info = engine.get_question_trap_info(5)
            >>> print(f"Question {info['number']} trap: {info['trap_name']}")
        """
        q_data = self.question_mappings.get(str(question_num))
        if not q_data:
            return None

        trap_cat = q_data.get("exam_trick")
        trap_def = self.trap_categories.get(trap_cat, {}) if trap_cat else {}

        return {
            "question_number": question_num,
            "domain": q_data.get("domain"),
            "topic": q_data.get("topic"),
            "difficulty": q_data.get("difficulty"),
            "question_type": q_data.get("question_type"),
            "trap_category": trap_cat,
            "trap_name": trap_def.get("name", "Unknown"),
            "trap_description": trap_def.get("the_trap", ""),
            "prevention_strategy": trap_def.get("prevention_strategy", ""),
        }

    def export_analysis_results(
        self, results: List[AnswerAnalysisResult], format: str = "json"
    ) -> str:
        """
        Export analysis results in various formats.

        Args:
            results: List of AnswerAnalysisResult objects
            format: "json", "csv", or "markdown"

        Returns:
            Formatted string (JSON, CSV, or Markdown)

        Example:
            >>> results = engine.analyze_all_answers(answers, key)
            >>> json_output = engine.export_analysis_results(results, "json")
        """
        if format == "json":
            return self._export_json(results)
        elif format == "csv":
            return self._export_csv(results)
        elif format == "markdown":
            return self._export_markdown(results)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(self, results: List[AnswerAnalysisResult]) -> str:
        """Export results as JSON."""
        output = {
            "total_questions": len(results),
            "total_correct": sum(1 for r in results if r.is_correct),
            "total_wrong": sum(1 for r in results if not r.is_correct),
            "questions": [],
        }

        for result in results:
            q_data = {
                "question_number": result.question_num,
                "student_answer": result.student_answer,
                "correct_answer": result.correct_answer,
                "is_correct": result.is_correct,
                "domain": result.domain,
                "difficulty": result.difficulty,
                "trap_category": result.trap_category,
            }

            if result.trap_explanation:
                q_data["trap_explanation"] = {
                    "trap_name": result.trap_explanation.trap_name,
                    "severity": result.trap_explanation.severity,
                    "why_student_fell": result.trap_explanation.why_student_fell,
                    "isc2_fix": result.trap_explanation.isc2_fix,
                    "prevention_tip": result.trap_explanation.prevention_tip,
                    "confidence_score": result.trap_explanation.confidence_score,
                }

            output["questions"].append(q_data)

        return json.dumps(output, indent=2)

    def _export_csv(self, results: List[AnswerAnalysisResult]) -> str:
        """Export results as CSV."""
        lines = [
            "Question,Student_Answer,Correct_Answer,Is_Correct,Domain,"
            "Difficulty,Trap_Category,Trap_Name,Severity"
        ]

        for result in results:
            trap_name = (
                result.trap_explanation.trap_name if result.trap_explanation else ""
            )
            severity = (
                result.trap_explanation.severity if result.trap_explanation else ""
            )

            line = (
                f"{result.question_num},{result.student_answer},"
                f"{result.correct_answer},{result.is_correct},"
                f"{result.domain},{result.difficulty},"
                f"{result.trap_category},{trap_name},{severity}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _export_markdown(self, results: List[AnswerAnalysisResult]) -> str:
        """Export results as Markdown."""
        md = "# Trap Analysis Report\n\n"
        md += f"**Total Questions:** {len(results)}\n"
        md += f"**Correct:** {sum(1 for r in results if r.is_correct)}\n"
        md += f"**Wrong:** {sum(1 for r in results if not r.is_correct)}\n\n"

        md += "## Detailed Results\n\n"

        for result in results:
            status = "✓ CORRECT" if result.is_correct else "✗ WRONG"
            md += f"### Question {result.question_num} - {status}\n"
            md += f"- **Student Answer:** {result.student_answer}\n"
            md += f"- **Correct Answer:** {result.correct_answer}\n"
            md += f"- **Domain:** {result.domain}\n"
            md += f"- **Difficulty:** {result.difficulty}\n"

            if result.trap_explanation:
                md += f"- **Trap:** {result.trap_explanation.trap_name}\n"
                md += f"- **Why:** {result.trap_explanation.why_student_fell}\n"
                md += f"- **Fix:** {result.trap_explanation.isc2_fix}\n"

            md += "\n"

        return md
