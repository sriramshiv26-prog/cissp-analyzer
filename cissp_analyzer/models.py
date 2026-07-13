from dataclasses import dataclass
from typing import Optional


@dataclass
class Question:
    number: int
    text: str
    domain: str
    topic: str
    subtopic: str
    difficulty: str  # Easy, Medium, Hard
    question_type: (
        str  # Definition, Scenario, Comparison, Exception, Sequence, Managerial
    )
    exam_trick: str  # Negation, Superlative, Absolute, Scenario, Trap


@dataclass
class StudentAnswer:
    student_name: str
    question_number: int
    selected_answer: Optional[str]
    is_correct: bool


@dataclass
class QuestionAnalysis:
    question_number: int
    students_correct: int
    students_wrong: int
    success_rate: float
    common_mistakes: list


@dataclass
class StudentPerformance:
    student_name: str
    total_questions: int
    correct_count: int
    wrong_count: int
    score_percentage: float
    by_domain: dict
    by_topic: dict
    by_difficulty: dict
    by_question_type: dict
    by_exam_trick: dict
    wrong_question_ids: list
    # Validation statistics (NEW)
    blank_count: int = 0  # Blank/unanswered questions
    invalid_count: int = 0  # Typos/invalid format
    validation_warnings: list = None  # List of warning messages
