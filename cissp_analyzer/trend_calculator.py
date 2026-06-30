from typing import List, Dict


class TrendCalculator:
    """Calculate performance trends across multiple exams"""

    # Threshold for classifying trends as improving/declining (5% change = 0.05)
    TREND_THRESHOLD = 0.05

    def __init__(self, trend_threshold: float = 0.05):
        """Initialize TrendCalculator with configurable threshold.

        Args:
            trend_threshold: Minimum change (0-1) to classify as improving/declining. Default 0.05 (5%).
        """
        self.TREND_THRESHOLD = trend_threshold

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

        A trend is classified as:
        - improving: change >= TREND_THRESHOLD (default 5%)
        - declining: change <= -TREND_THRESHOLD (default -5%)
        - stable: otherwise

        Args:
            trend: List of accuracy scores over time

        Returns:
            String: "improving", "declining", or "stable"
        """
        if len(trend) < 2:
            return "stable"

        diff = trend[-1] - trend[0]

        if diff >= self.TREND_THRESHOLD:
            return "improving"
        elif diff <= -self.TREND_THRESHOLD:
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

    def calculate_priority_score(self, current_accuracy: float,
                                previous_accuracy: float = None) -> float:
        """
        Calculate domain priority score for study recommendations.

        Formula: priority_score = weakness + (momentum × 2)

        Note: Results are rounded to 10 decimal places to avoid floating-point precision issues.
        Scores should be compared with small epsilon tolerance (1e-9) rather than exact equality.

        Args:
            current_accuracy: Current exam accuracy (0-1)
            previous_accuracy: Previous exam accuracy (0-1), or None if first exam

        Returns:
            Priority score (higher = more important to study)
        """
        # weakness: how far from 100%
        weakness = (1.0 - current_accuracy) * 100.0

        # momentum: improvement/regression trend
        if previous_accuracy is None:
            momentum = 0.0
        else:
            momentum = (current_accuracy - previous_accuracy) * 100.0

        # priority = weakness + (momentum × 2)
        priority = weakness + (momentum * 2.0)

        # Round to avoid floating-point precision issues
        return round(priority, 10)

    def rank_domains_by_priority(self, current_exam: Dict,
                                previous_exam: Dict = None) -> List[Dict]:
        """
        Rank domains by priority score (weakness + momentum).

        Returns list of dicts with: domain, current_accuracy, previous_accuracy,
        momentum, priority_score, and rank (position in sorted list).
        """
        domains = []

        # Extract current exam domains
        current_by_domain = current_exam.get("by_domain", {})
        previous_by_domain = previous_exam.get("by_domain", {}) if previous_exam else {}

        for domain, metrics in current_by_domain.items():
            current_acc = metrics.get("accuracy", 0.0)
            previous_acc = previous_by_domain.get(domain, {}).get("accuracy", None)

            # Calculate momentum
            if previous_acc is None:
                momentum = 0
            else:
                momentum = (current_acc - previous_acc) * 100

            priority_score = self.calculate_priority_score(current_acc, previous_acc)

            domains.append({
                "domain": domain,
                "current_accuracy": current_acc,
                "previous_accuracy": previous_acc,
                "momentum": momentum,
                "priority_score": priority_score
            })

        # Sort by priority score descending (highest priority first)
        domains.sort(key=lambda x: x["priority_score"], reverse=True)

        # Add rank field (1-indexed position in sorted list)
        for idx, domain_dict in enumerate(domains, start=1):
            domain_dict["rank"] = idx

        return domains
