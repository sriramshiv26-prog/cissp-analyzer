from typing import List, Dict, Optional
from collections import defaultdict
from cissp_analyzer.models import StudentAnswer, StudentPerformance
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.answer_validator import AnswerValidator


class AnalysisEngine:
    """Core multi-dimensional analysis engine with intelligent answer validation"""

    def __init__(self, domain_mapper: DomainMapper):
        self.mapper = domain_mapper
        self.answer_key: Dict[int, str] = {}
        self.student_results: Dict[str, Dict] = {}  # Store results for each student
        self.validator = AnswerValidator()  # Initialize answer validator

    def set_answer_key(self, answer_key: Dict[int, str]):
        """Set the correct answer for each question"""
        self.answer_key = answer_key

    def evaluate_student(
        self, answers: List[StudentAnswer], student_name: str
    ) -> StudentPerformance:
        """Evaluate a student's performance across all dimensions with answer validation"""

        # Step 1: Validate all answers for edge cases
        answer_dict = {a.question_number: a.selected_answer for a in answers}
        validated_answers = AnswerValidator.validate_batch(answer_dict)
        validation_report = AnswerValidator.get_report(validated_answers)

        # Step 2: Mark answers as correct/incorrect (using validated/normalized answers)
        blank_count = 0
        invalid_count = 0

        for answer in answers:
            q_num = answer.question_number
            validated = validated_answers.get(q_num)

            # Handle blank answers differently (don't count as wrong)
            if validated and validated.is_blank:
                answer.is_correct = False
                blank_count += 1
                # Mark as blank for later reporting
                answer.selected_answer = None
                continue

            # Handle invalid/typo answers (count as wrong, but note the issue)
            if validated and validated.is_typo:
                invalid_count += 1
                # Use corrected answer if available
                if validated.corrected_answer:
                    answer.selected_answer = validated.corrected_answer
                else:
                    answer.is_correct = False
                    continue

            # Standard comparison with normalized answer
            if q_num in self.answer_key:
                # Use normalized/corrected answer for comparison
                user_answer = (
                    validated.normalized_input
                    if validated and validated.normalized_input
                    else answer.selected_answer
                )
                answer.is_correct = user_answer == self.answer_key[q_num]

        # Step 3: Count correct/wrong (blanks and invalid count as wrong)
        correct_count = sum(1 for a in answers if a.is_correct)
        total_count = len(answers)
        wrong_count = total_count - correct_count
        score_pct = (correct_count / total_count) * 100 if total_count > 0 else 0

        # Get metadata for each question
        by_domain: defaultdict = defaultdict(lambda: {"correct": 0, "wrong": 0})
        by_topic: defaultdict = defaultdict(lambda: {"correct": 0, "wrong": 0})
        by_difficulty: defaultdict = defaultdict(lambda: {"correct": 0, "wrong": 0})
        by_question_type: defaultdict = defaultdict(lambda: {"correct": 0, "wrong": 0})
        by_exam_trick: defaultdict = defaultdict(lambda: {"correct": 0, "wrong": 0})
        wrong_question_ids = []

        for answer in answers:
            meta = self.mapper.get_question_metadata(answer.question_number)
            if not meta:
                continue

            domain = meta.get("domain", "Unknown")
            topic = meta.get("topic", "Unknown")
            difficulty = meta.get("difficulty", "Unknown")
            q_type = meta.get("question_type", "Unknown")
            trick = meta.get("exam_trick", "Unknown")

            if answer.is_correct:
                by_domain[domain]["correct"] += 1
                by_topic[topic]["correct"] += 1
                by_difficulty[difficulty]["correct"] += 1
                by_question_type[q_type]["correct"] += 1
                by_exam_trick[trick]["correct"] += 1
            else:
                by_domain[domain]["wrong"] += 1
                by_topic[topic]["wrong"] += 1
                by_difficulty[difficulty]["wrong"] += 1
                by_question_type[q_type]["wrong"] += 1
                by_exam_trick[trick]["wrong"] += 1
                wrong_question_ids.append(answer.question_number)

        # Calculate percentages for each dimension
        by_domain_pct = self._calculate_percentages(by_domain)
        by_topic_pct = self._calculate_percentages(by_topic)
        by_difficulty_pct = self._calculate_percentages(by_difficulty)
        by_question_type_pct = self._calculate_percentages(by_question_type)
        by_exam_trick_pct = self._calculate_percentages(by_exam_trick)

        performance = StudentPerformance(
            student_name=student_name,
            total_questions=len(answers),
            correct_count=correct_count,
            wrong_count=wrong_count,
            score_percentage=score_pct,
            by_domain=by_domain_pct,
            by_topic=by_topic_pct,
            by_difficulty=by_difficulty_pct,
            by_question_type=by_question_type_pct,
            by_exam_trick=by_exam_trick_pct,
            wrong_question_ids=wrong_question_ids,
            blank_count=blank_count,
            invalid_count=invalid_count,
            validation_warnings=validation_report.get("warnings", []),
        )

        # Store results for later export
        self.student_results[student_name] = {
            "performance": performance,
            "answers": answers,
            "by_domain": by_domain_pct,
            "by_difficulty": by_difficulty_pct,
            "by_question_type": by_question_type_pct,
            "wrong_question_ids": wrong_question_ids,
            "validation_report": validation_report,
            "validation_warnings": validation_report.get("warnings", []),
        }

        return performance

    def _calculate_percentages(self, dimension_dict: Dict) -> Dict:
        """Convert correct/wrong counts to percentages"""
        result = {}
        for key, counts in dimension_dict.items():
            correct = counts["correct"]
            wrong = counts["wrong"]
            total = correct + wrong
            pct = (correct / total * 100) if total > 0 else 0
            result[key] = {
                "correct": correct,
                "wrong": wrong,
                "total": total,
                "percentage": round(pct, 1),
            }
        return result

    def export_student_performance(
        self, student_name: str, exam_number: int, exam_date: Optional[str] = None
    ) -> Dict:
        """
        Export analyzed performance data in format for historical tracking.

        Args:
            student_name: Name of student
            exam_number: Which exam (1, 2, 3, ...)
            exam_date: Optional date (defaults to today if provided, else None)

        Returns:
            Dict matching exam-N_performance.json schema
        """
        results = self.student_results.get(student_name, {})
        performance = results.get("performance")

        if not performance:
            raise ValueError(f"No performance data found for student: {student_name}")

        # Extract data from stored performance
        by_domain = results.get("by_domain", {})
        by_difficulty = results.get("by_difficulty", {})
        by_question_type = results.get("by_question_type", {})
        wrong_question_ids = results.get("wrong_question_ids", [])

        # Convert percentage dict format to accuracy dict format
        domain_with_accuracy = {}
        for domain_name, stats in by_domain.items():
            domain_with_accuracy[domain_name] = {
                "correct": stats.get("correct", 0),
                "total": stats.get("total", 0),
                "accuracy": stats.get("percentage", 0) / 100,
            }

        difficulty_with_accuracy = {}
        for difficulty_name, stats in by_difficulty.items():
            difficulty_with_accuracy[difficulty_name] = {
                "correct": stats.get("correct", 0),
                "total": stats.get("total", 0),
                "accuracy": stats.get("percentage", 0) / 100,
            }

        question_type_with_accuracy = {}
        for qtype_name, stats in by_question_type.items():
            question_type_with_accuracy[qtype_name] = {
                "correct": stats.get("correct", 0),
                "total": stats.get("total", 0),
                "accuracy": stats.get("percentage", 0) / 100,
            }

        # Build return dict
        export_data = {
            "exam_number": exam_number,
            "student_name": student_name,
            "total_questions": performance.total_questions,
            "total_correct": performance.correct_count,
            "overall_accuracy": performance.score_percentage,
            "by_domain": domain_with_accuracy,
            "by_difficulty": difficulty_with_accuracy,
            "by_question_type": question_type_with_accuracy,
            "wrong_question_ids": wrong_question_ids,
        }

        # Add exam_date if provided
        if exam_date is not None:
            export_data["exam_date"] = exam_date

        return export_data
