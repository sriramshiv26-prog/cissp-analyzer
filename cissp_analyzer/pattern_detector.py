"""Pattern Detection for Subtopic-Level Analysis"""

from typing import List, Dict, Any


class PatternDetector:
    """Detect learning patterns in exam data.

    Analyzes performance patterns at the subtopic level including:
    - All wrong vs mixed accuracy patterns
    - Weakness by question type
    - Weakness by exam trick keywords
    - Human-readable insights
    """

    def detect_topic_pattern(
        self, questions: List[Dict[str, Any]], wrong_question_ids: List[int], topic: str
    ) -> Dict[str, Any]:
        """Analyze patterns for a specific topic/subtopic.

        Args:
            questions: List of question metadata dicts with keys:
                      domain, topic, subtopic, difficulty, question_type, exam_trick
            wrong_question_ids: List of indices (0-based) into questions array that were wrong
            topic: The topic/subtopic name being analyzed

        Returns:
            Dictionary with keys:
            - topic: The topic/subtopic name
            - correct: Number of correct answers
            - total: Total number of questions
            - accuracy: Percentage accuracy (0.0 to 1.0)
            - all_wrong: Boolean, True if 0% accuracy
            - all_correct: Boolean, True if 100% accuracy
            - weakness_by_type: Dict of accuracy by question_type
            - weakness_by_trick: Dict of accuracy by exam_trick
            - insight: Human-readable insight string

        Raises:
            ValueError: If wrong_question_ids contains out-of-bounds indices
        """
        if not questions:
            return {
                "topic": topic,
                "correct": 0,
                "total": 0,
                "accuracy": 0.0,
                "all_wrong": True,
                "all_correct": False,
                "weakness_by_type": {},
                "weakness_by_trick": {},
                "insight": "No data available",
            }

        # Validate all indices are in bounds
        total = len(questions)
        valid_indices = set(range(total))
        invalid_indices = [
            idx for idx in wrong_question_ids if idx not in valid_indices
        ]

        if invalid_indices:
            raise ValueError(
                f"Invalid question indices {invalid_indices} for {total} questions "
                f"in topic '{topic}'"
            )

        correct = total - len(wrong_question_ids)
        accuracy = correct / total if total > 0 else 0.0

        # Determine if all wrong or all correct
        all_wrong = correct == 0
        all_correct = correct == total

        # Analyze by question type dimension
        by_type = self._analyze_by_dimension(
            questions, wrong_question_ids, "question_type"
        )

        # Analyze by exam trick dimension
        by_trick = self._analyze_by_dimension(
            questions, wrong_question_ids, "exam_trick"
        )

        # Generate insight
        insight = self._generate_insight(
            {
                "topic": topic,
                "correct": correct,
                "total": total,
                "accuracy": accuracy,
                "all_wrong": all_wrong,
                "all_correct": all_correct,
            },
            by_type,
            by_trick,
        )

        return {
            "topic": topic,
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "all_wrong": all_wrong,
            "all_correct": all_correct,
            "weakness_by_type": by_type,
            "weakness_by_trick": by_trick,
            "insight": insight,
        }

    def _analyze_by_dimension(
        self,
        questions: List[Dict[str, Any]],
        wrong_question_ids: List[int],
        dimension: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Aggregate accuracy by a specific dimension.

        Args:
            questions: List of question metadata dicts
            wrong_question_ids: List of indices (0-based) into questions array that were wrong
            dimension: The dimension key to aggregate by (e.g., 'question_type', 'exam_trick')

        Returns:
            Dictionary mapping dimension values to accuracy metrics
            Example: {"Scenario": {"correct": 2, "total": 5, "accuracy": 0.4},
                      "Application": {"correct": 3, "total": 4, "accuracy": 0.75}}
        """
        # Create a set for faster lookup of wrong indices
        wrong_set = set(wrong_question_ids)

        # Aggregate by dimension
        dimension_stats = {}

        for idx, question in enumerate(questions):
            dim_value = question.get(dimension, "Unknown")

            if dim_value not in dimension_stats:
                dimension_stats[dim_value] = {"correct": 0, "total": 0, "accuracy": 0.0}

            dimension_stats[dim_value]["total"] += 1

            # Check if this question (by array index) was answered incorrectly
            if idx not in wrong_set:
                dimension_stats[dim_value]["correct"] += 1

        # Calculate accuracy for each dimension value
        for dim_value in dimension_stats:
            stats = dimension_stats[dim_value]
            stats["accuracy"] = (
                stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
            )

        return dimension_stats

    def _generate_insight(
        self,
        result: Dict[str, Any],
        by_type: Dict[str, Dict[str, Any]],
        by_trick: Dict[str, Dict[str, Any]],
    ) -> str:
        """Generate human-readable insight about the pattern.

        Args:
            result: Result dict with topic, correct, total, accuracy, all_wrong, all_correct
            by_type: Accuracy breakdown by question type
            by_trick: Accuracy breakdown by exam trick

        Returns:
            Human-readable insight string
        """
        topic = result.get("topic", "Unknown")
        correct = result.get("correct", 0)
        total = result.get("total", 0)
        accuracy = result.get("accuracy", 0.0)
        all_wrong = result.get("all_wrong", False)
        all_correct = result.get("all_correct", False)

        # Handle all correct case
        if all_correct:
            return f"{topic}: MASTERED ({correct}/{total}) - excellent work"

        # Handle all wrong case
        if all_wrong:
            return f"{topic}: ALL WRONG ({correct}/{total}) - need fundamental review"

        # Find weakest dimension by type
        weakest_type = None
        weakest_type_accuracy = 1.0
        if by_type:
            for type_name, stats in by_type.items():
                if stats["accuracy"] < weakest_type_accuracy:
                    weakest_type_accuracy = stats["accuracy"]
                    weakest_type = type_name

        # Find weakest dimension by trick
        weakest_trick = None
        weakest_trick_accuracy = 1.0
        if by_trick:
            for trick_name, stats in by_trick.items():
                if stats["accuracy"] < weakest_trick_accuracy:
                    weakest_trick_accuracy = stats["accuracy"]
                    weakest_trick = trick_name

        # Generate insight based on patterns
        accuracy_percent = round(accuracy * 100)

        # Primary insight based on type weakness
        if weakest_type and weakest_type_accuracy == 0.0:
            if weakest_trick and weakest_trick_accuracy == 0.0:
                return (
                    f"{topic}: {accuracy_percent}% accuracy - weakness in {weakest_type} "
                    f"questions with {weakest_trick} keyword"
                )
            return f"{topic}: {accuracy_percent}% accuracy - weakness in {weakest_type} questions"

        # Secondary insight based on trick weakness
        if weakest_trick and weakest_trick_accuracy == 0.0:
            return f"{topic}: {accuracy_percent}% accuracy - {weakest_trick} keyword is the issue"

        # Default insight
        return (
            f"{topic}: {accuracy_percent}% accuracy - mixed performance across subtopic"
        )
