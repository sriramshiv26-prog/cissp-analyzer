from typing import List, Dict
from collections import defaultdict
from cissp_analyzer.models import StudentAnswer, StudentPerformance
from cissp_analyzer.domain_mapper import DomainMapper


class AnalysisEngine:
    """Core multi-dimensional analysis engine"""

    def __init__(self, domain_mapper: DomainMapper):
        self.mapper = domain_mapper
        self.answer_key = {}

    def set_answer_key(self, answer_key: Dict[int, str]):
        """Set the correct answer for each question"""
        self.answer_key = answer_key

    def evaluate_student(self, answers: List[StudentAnswer], student_name: str) -> StudentPerformance:
        """Evaluate a student's performance across all dimensions"""

        # Mark answers as correct/incorrect
        for answer in answers:
            q_num = answer.question_number
            if q_num in self.answer_key:
                answer.is_correct = (answer.selected_answer == self.answer_key[q_num])

        # Count correct/wrong
        correct_count = sum(1 for a in answers if a.is_correct)
        wrong_count = len(answers) - correct_count
        score_pct = (correct_count / len(answers)) * 100 if answers else 0

        # Get metadata for each question
        by_domain = defaultdict(lambda: {'correct': 0, 'wrong': 0})
        by_topic = defaultdict(lambda: {'correct': 0, 'wrong': 0})
        by_difficulty = defaultdict(lambda: {'correct': 0, 'wrong': 0})
        by_question_type = defaultdict(lambda: {'correct': 0, 'wrong': 0})
        by_exam_trick = defaultdict(lambda: {'correct': 0, 'wrong': 0})
        wrong_question_ids = []

        for answer in answers:
            meta = self.mapper.get_question_metadata(answer.question_number)
            if not meta:
                continue

            domain = meta.get('domain', 'Unknown')
            topic = meta.get('topic', 'Unknown')
            difficulty = meta.get('difficulty', 'Unknown')
            q_type = meta.get('question_type', 'Unknown')
            trick = meta.get('exam_trick', 'Unknown')

            if answer.is_correct:
                by_domain[domain]['correct'] += 1
                by_topic[topic]['correct'] += 1
                by_difficulty[difficulty]['correct'] += 1
                by_question_type[q_type]['correct'] += 1
                by_exam_trick[trick]['correct'] += 1
            else:
                by_domain[domain]['wrong'] += 1
                by_topic[topic]['wrong'] += 1
                by_difficulty[difficulty]['wrong'] += 1
                by_question_type[q_type]['wrong'] += 1
                by_exam_trick[trick]['wrong'] += 1
                wrong_question_ids.append(answer.question_number)

        # Calculate percentages for each dimension
        by_domain_pct = self._calculate_percentages(by_domain)
        by_topic_pct = self._calculate_percentages(by_topic)
        by_difficulty_pct = self._calculate_percentages(by_difficulty)
        by_question_type_pct = self._calculate_percentages(by_question_type)
        by_exam_trick_pct = self._calculate_percentages(by_exam_trick)

        return StudentPerformance(
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
            wrong_question_ids=wrong_question_ids
        )

    def _calculate_percentages(self, dimension_dict: Dict) -> Dict:
        """Convert correct/wrong counts to percentages"""
        result = {}
        for key, counts in dimension_dict.items():
            correct = counts['correct']
            wrong = counts['wrong']
            total = correct + wrong
            pct = (correct / total * 100) if total > 0 else 0
            result[key] = {
                'correct': correct,
                'wrong': wrong,
                'total': total,
                'percentage': round(pct, 1)
            }
        return result
