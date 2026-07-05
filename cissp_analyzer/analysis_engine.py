from typing import List, Dict, Optional
from collections import defaultdict
from cissp_analyzer.models import StudentAnswer, StudentPerformance
from cissp_analyzer.domain_mapper import DomainMapper


class AnalysisEngine:
    """Core multi-dimensional analysis engine"""

    def __init__(self, domain_mapper: DomainMapper):
        self.mapper = domain_mapper
        self.answer_key: Dict[int, str] = {}
        self.student_results: Dict[str, Dict] = {}  # Store results for each student

    def set_answer_key(self, answer_key: Dict[int, str]):
        """Set the correct answer for each question"""
        self.answer_key = answer_key

    def evaluate_student(
        self, answers: List[StudentAnswer], student_name: str
    ) -> StudentPerformance:
        """Evaluate a student's performance across all dimensions"""

        # Mark answers as correct/incorrect
        for answer in answers:
            q_num = answer.question_number
            if q_num in self.answer_key:
                answer.is_correct = answer.selected_answer == self.answer_key[q_num]

        # Count correct/wrong
        correct_count = sum(1 for a in answers if a.is_correct)
        wrong_count = len(answers) - correct_count
        score_pct = (correct_count / len(answers)) * 100 if answers else 0

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
        )

        # Store results for later export
        self.student_results[student_name] = {
            "performance": performance,
            "answers": answers,
            "by_domain": by_domain_pct,
            "by_difficulty": by_difficulty_pct,
            "by_question_type": by_question_type_pct,
            "wrong_question_ids": wrong_question_ids,
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
