from typing import List, Dict


class TrendCalculator:
    """Calculate performance trends across multiple exams"""

    def calculate_domain_trends(self, exams: List[Dict]) -> Dict[str, List[float]]:
        """
        Calculate domain accuracy trends across multiple exams.

        Args:
            exams: List of exam dictionaries, each containing "by_domain" key with domain accuracies

        Returns:
            Dictionary mapping domain names to lists of accuracy scores across exams
        """
        trends = {}

        for exam in exams:
            by_domain = exam.get("by_domain", {})
            for domain, metrics in by_domain.items():
                accuracy = metrics.get("accuracy", 0.0)
                if domain not in trends:
                    trends[domain] = []
                trends[domain].append(accuracy)

        return trends

    def calculate_difficulty_trends(self, exams: List[Dict]) -> Dict[str, List[float]]:
        """
        Calculate difficulty level accuracy trends across multiple exams.

        Args:
            exams: List of exam dictionaries, each containing "by_difficulty" key with difficulty accuracies

        Returns:
            Dictionary mapping difficulty levels to lists of accuracy scores across exams
        """
        trends = {}

        for exam in exams:
            by_difficulty = exam.get("by_difficulty", {})
            for difficulty, metrics in by_difficulty.items():
                accuracy = metrics.get("accuracy", 0.0)
                if difficulty not in trends:
                    trends[difficulty] = []
                trends[difficulty].append(accuracy)

        return trends

    def calculate_question_type_trends(self, exams: List[Dict]) -> Dict[str, List[float]]:
        """
        Calculate question type accuracy trends across multiple exams.

        Args:
            exams: List of exam dictionaries, each containing "by_question_type" key with question type accuracies

        Returns:
            Dictionary mapping question types to lists of accuracy scores across exams
        """
        trends = {}

        for exam in exams:
            by_question_type = exam.get("by_question_type", {})
            for question_type, metrics in by_question_type.items():
                accuracy = metrics.get("accuracy", 0.0)
                if question_type not in trends:
                    trends[question_type] = []
                trends[question_type].append(accuracy)

        return trends

    def detect_trend_direction(self, trend: List[float]) -> str:
        """
        Detect the direction of a trend based on first and last values.

        Logic:
        - improving: (last - first) > 0.05
        - declining: (last - first) < -0.05
        - stable: otherwise

        Args:
            trend: List of accuracy scores over time

        Returns:
            String: "improving", "declining", or "stable"
        """
        if len(trend) < 2:
            return "stable"

        diff = trend[-1] - trend[0]

        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"

    def get_momentum_score(self, previous_accuracy: float, current_accuracy: float) -> float:
        """
        Calculate momentum score between two accuracy values.

        Args:
            previous_accuracy: Accuracy from previous exam
            current_accuracy: Accuracy from current exam

        Returns:
            Float: current - previous (positive = improving, negative = declining)
        """
        return current_accuracy - previous_accuracy
