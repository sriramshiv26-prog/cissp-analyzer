# CISSP Analyzer - Enhancement Code Examples

Quick implementation guides for the most valuable improvements.

---

## 1️⃣ ROBUSTNESS FIX: Input Validation Layer (5 hours)

**Create:** `cissp_analyzer/validation_engine.py`

```python
"""
Pre-flight validation for answer keys and student data
Prevents silent failures and crashes
"""

from typing import Dict, Tuple, List
from pathlib import Path

class ValidationEngine:
    """Validates input data quality before analysis"""
    
    def validate_answer_key(self, answer_key: Dict) -> Tuple[bool, List[str]]:
        """
        Validate answer key structure and content
        
        Returns: (is_valid, [warnings])
        """
        warnings = []
        
        if not answer_key:
            return False, ["Answer key is empty"]
        
        # Check expected question count
        expected_count = 162  # or 161 for your CISSP
        if len(answer_key) < expected_count * 0.9:  # Allow 10% missing
            warnings.append(
                f"Answer key has {len(answer_key)} questions, expected ~{expected_count}"
            )
        
        # Check answer format
        valid_answers = {'A', 'B', 'C', 'D'}
        invalid_answers = []
        
        for q_num, answer in answer_key.items():
            answer_clean = str(answer).strip().upper()
            if answer_clean not in valid_answers:
                invalid_answers.append((q_num, answer))
        
        if invalid_answers:
            warnings.append(
                f"Invalid answer formats: {invalid_answers[:5]} (showing first 5)"
            )
        
        return len(invalid_answers) == 0, warnings
    
    def validate_student_answers(
        self, student_answers: Dict, answer_key: Dict
    ) -> Tuple[bool, List[str]]:
        """Validate student answer sheet"""
        warnings = []
        
        # Check for unmapped questions
        unmapped = set(student_answers.keys()) - set(answer_key.keys())
        if unmapped:
            warnings.append(f"Student answered {len(unmapped)} unmapped questions")
        
        # Check for blanks
        blank_count = sum(1 for a in student_answers.values() if not a or str(a).strip() == "")
        if blank_count > len(student_answers) * 0.1:  # More than 10% blank
            warnings.append(f"Student has {blank_count} blank answers ({blank_count/len(student_answers)*100:.1f}%)")
        
        # Check for invalid formats
        invalid = []
        for q_num, answer in student_answers.items():
            if answer and str(answer).strip().upper() not in {'A', 'B', 'C', 'D'}:
                invalid.append(f"Q{q_num}: {answer}")
        
        if invalid:
            warnings.append(f"Invalid answer formats: {invalid[:5]}")
        
        return len(invalid) == 0, warnings
    
    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate human-readable validation report"""
        report = []
        report.append("\n" + "="*80)
        report.append("PRE-FLIGHT VALIDATION REPORT")
        report.append("="*80)
        
        for check_name, (is_valid, warnings) in validation_results.items():
            status = "✅ PASS" if is_valid else "⚠️  WARNINGS"
            report.append(f"\n{check_name}: {status}")
            for warning in warnings:
                report.append(f"  └─ {warning}")
        
        report.append("\n" + "="*80)
        return "\n".join(report)


# Usage in student_answer_analyzer.py
def main(answer_key_path=None, student_files=None, questionnaire_name="CISSP"):
    # ... existing code ...
    
    # NEW: Add validation before analysis
    validator = ValidationEngine()
    
    print("\n🔍 Running pre-flight validation...")
    validation_results = {
        "Answer Key": validator.validate_answer_key(answer_key),
    }
    
    for file_path in student_files:
        student_name, answers = load_student_answers_from_excel(file_path)
        is_valid, warnings = validator.validate_student_answers(answers, answer_key)
        validation_results[f"Student: {student_name}"] = (is_valid, warnings)
    
    print(validator.generate_validation_report(validation_results))
    
    # Continue with analysis...
```

---

## 2️⃣ QUICK WIN: Percentile Ranking (3 hours)

**Add to:** `cissp_analyzer/cohort_analytics.py` (new file)

```python
"""
Cohort analytics - peer comparison and benchmarking
"""

from scipy.stats import percentileofscore
from typing import Dict, List

class CohortAnalytics:
    """Analyze student performance relative to cohort"""
    
    def calculate_percentile(self, student_score: float, cohort_scores: List[float]) -> Dict:
        """
        Calculate student's percentile rank in cohort
        
        Returns: {
            "percentile": 65,  # 65th percentile
            "percentile_band": "Good",  # Excellent/Good/Average/Needs Work
            "better_than_n": 13,  # Better than 13 students
            "worse_than_n": 7    # Worse than 7 students
        }
        """
        if not cohort_scores:
            return {"error": "Empty cohort"}
        
        percentile = percentileofscore(cohort_scores, student_score)
        
        # Classify into bands
        if percentile >= 90:
            band = "Excellent"
        elif percentile >= 75:
            band = "Good"
        elif percentile >= 50:
            band = "Average"
        else:
            band = "Needs Work"
        
        better_than = sum(1 for score in cohort_scores if score < student_score)
        worse_than = sum(1 for score in cohort_scores if score > student_score)
        
        return {
            "percentile": round(percentile, 1),
            "percentile_band": band,
            "better_than_n": better_than,
            "worse_than_n": worse_than,
            "class_average": round(sum(cohort_scores) / len(cohort_scores), 1),
            "class_min": min(cohort_scores),
            "class_max": max(cohort_scores),
        }
    
    def get_peer_comparison(self, student_domain_score: float, domain: str, 
                           cohort_domain_scores: List[float]) -> Dict:
        """Compare student's domain score to peers"""
        return {
            "domain": domain,
            "your_score": student_domain_score,
            "class_average": round(sum(cohort_domain_scores) / len(cohort_domain_scores), 1),
            "top_student": max(cohort_domain_scores),
            "percentile": percentileofscore(cohort_domain_scores, student_domain_score),
            "students_higher": sum(1 for s in cohort_domain_scores if s > student_domain_score),
            "students_lower": sum(1 for s in cohort_domain_scores if s < student_domain_score),
        }


# Usage in individual report generation:
def generate_student_report_with_benchmarking(
    student_name, score, all_student_scores, domain_scores, cohort_domain_scores
):
    analytics = CohortAnalytics()
    
    # Add percentile ranking
    percentile_info = analytics.calculate_percentile(score, all_student_scores)
    
    # Report section
    report_section = f"""
PERCENTILE RANKING:
├─ You: {score:.1f}%
├─ Percentile: {percentile_info['percentile']:.0f}th ({percentile_info['percentile_band']})
├─ Better than: {percentile_info['better_than_n']} students
├─ Class Average: {percentile_info['class_average']:.1f}%
└─ Range: {percentile_info['class_min']:.1f}% - {percentile_info['class_max']:.1f}%
"""
    
    return report_section
```

---

## 3️⃣ QUICK WIN: Pass Probability (4 hours)

**Add to:** `cissp_analyzer/predictive_analytics.py` (new file)

```python
"""
Predictive analytics - estimate pass probability and readiness
"""

from typing import Dict, List
import statistics

class PredictiveAnalytics:
    """Forecast student exam readiness"""
    
    def estimate_pass_probability(
        self, current_score: float, passing_threshold: float = 75.0,
        cohort_historical_data: List[Dict] = None
    ) -> Dict:
        """
        Estimate probability student will pass
        
        Method: Find historical students with similar scores,
        check what % of them eventually passed
        
        Returns: {
            "pass_probability": 0.72,  # 72% chance
            "confidence": "high",
            "similar_students": 23,
            "passed_count": 16,
            "reasoning": "Of 23 students with similar starting scores, 16 passed"
        }
        """
        if not cohort_historical_data:
            # Fallback: Simple linear model
            # 50% threshold at passing_threshold score
            probability = (current_score - 50) / (passing_threshold - 50)
            probability = max(0, min(1, probability))  # Clamp 0-1
            
            return {
                "pass_probability": round(probability, 2),
                "confidence": "low",
                "method": "Default linear model",
                "reasoning": "No historical data available"
            }
        
        # Find similar students (within 5 points)
        similar_threshold = 5
        similar_students = [
            s for s in cohort_historical_data
            if abs(s.get("initial_score", 0) - current_score) <= similar_threshold
        ]
        
        if not similar_students:
            # No exact matches, use broader range
            similar_threshold = 15
            similar_students = [
                s for s in cohort_historical_data
                if abs(s.get("initial_score", 0) - current_score) <= similar_threshold
            ]
        
        if similar_students:
            passed = sum(
                1 for s in similar_students
                if s.get("final_score", 0) >= passing_threshold
            )
            probability = passed / len(similar_students)
            confidence = "high" if len(similar_students) >= 10 else "medium"
            
            return {
                "pass_probability": round(probability, 2),
                "confidence": confidence,
                "similar_students": len(similar_students),
                "passed_count": passed,
                "reasoning": f"Of {len(similar_students)} students with similar starting scores, "
                            f"{passed} passed ({probability*100:.0f}%)"
            }
        
        # Fallback
        return {
            "pass_probability": 0.5,
            "confidence": "very_low",
            "reasoning": "Insufficient historical data"
        }
    
    def estimate_time_to_pass(
        self, current_score: float, improvement_per_week: float,
        passing_threshold: float = 75.0
    ) -> Dict:
        """
        Estimate weeks until student reaches passing threshold
        
        Returns: {
            "weeks_to_pass": 4,
            "target_date": "2026-08-14",
            "required_improvement": 15,
            "weekly_velocity": 2.5
        }
        """
        if current_score >= passing_threshold:
            return {
                "weeks_to_pass": 0,
                "status": "Already passing",
                "current_score": current_score,
                "target": passing_threshold
            }
        
        if improvement_per_week <= 0:
            return {
                "weeks_to_pass": float('inf'),
                "status": "Not improving",
                "message": "No improvement detected. Consider changing study approach."
            }
        
        required_improvement = passing_threshold - current_score
        weeks_needed = required_improvement / improvement_per_week
        
        # Add buffer for uncertainty (20% more time)
        weeks_with_buffer = weeks_needed * 1.2
        
        from datetime import datetime, timedelta
        target_date = (datetime.now() + timedelta(weeks=weeks_with_buffer)).strftime("%Y-%m-%d")
        
        return {
            "weeks_to_pass": round(weeks_with_buffer, 1),
            "target_date": target_date,
            "required_improvement": required_improvement,
            "current_pace": improvement_per_week,
            "message": f"At your current pace (+{improvement_per_week:.1f}% per week), "
                      f"you should be ready in {weeks_with_buffer:.0f} weeks"
        }


# Usage:
def add_predictive_insights_to_report(student_report, cohort_historical):
    predictive = PredictiveAnalytics()
    
    current_score = student_report["score_percentage"]
    
    # Estimate pass probability
    pass_prob = predictive.estimate_pass_probability(
        current_score, 
        passing_threshold=75,
        cohort_historical_data=cohort_historical
    )
    
    # Estimate time to pass (assuming 2.5% improvement per exam)
    time_to_pass = predictive.estimate_time_to_pass(
        current_score,
        improvement_per_week=2.5,  # Adjust based on student's history
        passing_threshold=75
    )
    
    # Add to report
    student_report["predictive_analytics"] = {
        "pass_probability": pass_prob,
        "time_to_readiness": time_to_pass
    }
```

---

## 4️⃣ QUICK WIN: Learning Velocity (3 hours)

**Add to:** `cissp_analyzer/learning_metrics.py` (new file)

```python
"""
Learning velocity and improvement metrics
"""

from typing import List, Dict
from datetime import datetime

class LearningMetrics:
    """Track learning velocity and improvement patterns"""
    
    def calculate_velocity(
        self, exam_scores: List[float], exam_dates: List[str]
    ) -> Dict:
        """
        Calculate learning velocity (improvement per week)
        
        Args:
            exam_scores: [65.0, 68.5, 71.2, ...]
            exam_dates: ["2026-07-01", "2026-07-08", ...]
        
        Returns: {
            "velocity_per_week": 2.5,  # Improving 2.5% per week
            "trend": "improving",
            "acceleration": "stable",
            "weeks_tracked": 4
        }
        """
        if len(exam_scores) < 2:
            return {"error": "Need at least 2 exams to calculate velocity"}
        
        # Calculate time differences
        dates = [datetime.fromisoformat(d) for d in exam_dates]
        time_diffs = [(dates[i+1] - dates[i]).days / 7 for i in range(len(dates)-1)]
        
        # Calculate score differences
        score_diffs = [exam_scores[i+1] - exam_scores[i] for i in range(len(exam_scores)-1)]
        
        # Calculate velocity per week
        velocities = [score_diffs[i] / time_diffs[i] for i in range(len(score_diffs))]
        avg_velocity = sum(velocities) / len(velocities)
        
        # Determine trend
        if avg_velocity > 1.0:
            trend = "improving"
        elif avg_velocity < -0.5:
            trend = "declining"
        else:
            trend = "stable"
        
        # Determine acceleration (is velocity itself improving?)
        if len(velocities) >= 2:
            acceleration_trend = "accelerating" if velocities[-1] > velocities[0] else "decelerating"
        else:
            acceleration_trend = "unknown"
        
        return {
            "velocity_per_week": round(avg_velocity, 2),
            "trend": trend,
            "acceleration": acceleration_trend,
            "weeks_tracked": sum(time_diffs),
            "exam_count": len(exam_scores),
            "current_score": exam_scores[-1],
            "starting_score": exam_scores[0],
            "total_improvement": exam_scores[-1] - exam_scores[0]
        }
    
    def get_velocity_message(self, velocity_info: Dict) -> str:
        """Generate human-readable velocity message"""
        if velocity_info.get("velocity_per_week", 0) >= 2.0:
            return f"🚀 Excellent progress! Improving {velocity_info['velocity_per_week']:.1f}% per week"
        elif velocity_info.get("velocity_per_week", 0) >= 1.0:
            return f"📈 Good progress! Improving {velocity_info['velocity_per_week']:.1f}% per week"
        elif velocity_info.get("velocity_per_week", 0) >= 0:
            return f"➡️ Steady progress! Improving {velocity_info['velocity_per_week']:.2f}% per week"
        else:
            return f"⚠️ Declining performance. Score dropping {abs(velocity_info['velocity_per_week']):.1f}% per week"


# Usage:
def add_learning_velocity_to_report(student_exam_history):
    """
    Example: student took 4 exams over 3 weeks
    Scores: [65, 67, 69.5, 72]
    Dates: ["2026-07-01", "2026-07-08", "2026-07-15", "2026-07-22"]
    """
    metrics = LearningMetrics()
    
    velocity = metrics.calculate_velocity(
        exam_scores=student_exam_history["scores"],
        exam_dates=student_exam_history["dates"]
    )
    
    message = metrics.get_velocity_message(velocity)
    
    return {
        "learning_velocity": velocity,
        "message": message
    }
```

---

## 5️⃣ FIX: Edge Case Handling (4 hours)

**Update:** `cissp_analyzer/class_report_gen.py`

```python
# BEFORE: Can crash on empty cohort
def generate_class_summary(student_reports):
    max_score = max([r["score"] for r in student_reports])  # ❌ IndexError if empty
    
# AFTER: Safe with validation
def generate_class_summary(student_reports):
    if not student_reports:
        print("⚠️ No student reports to summarize")
        return None
    
    max_score = max([r["score"] for r in student_reports])  # ✅ Safe
    
    # ... rest of code ...


# BEFORE: Column overflow at 26+ students
def create_per_student_columns(workbook, students):
    for i, student in enumerate(students):
        col_letter = chr(65 + i)  # ❌ Breaks when i > 25 (Z is 25)
        
# AFTER: Safe with pagination
def create_per_student_columns(workbook, students):
    if len(students) > 25:
        print(f"⚠️ {len(students)} students detected")
        print(f"ℹ️  Will create multiple sheets (max 25 per sheet)")
        # Split into chunks of 25
        chunks = [students[i:i+25] for i in range(0, len(students), 25)]
        for chunk_idx, chunk in enumerate(chunks):
            sheet = workbook.create_sheet(f"Students_{chunk_idx+1}")
            # Process chunk...
    else:
        # Single sheet, no problem
        for i, student in enumerate(students):
            col_letter = chr(65 + i)  # ✅ Works for 0-25
            # Process...


# BEFORE: Division by zero possible
def calculate_accuracy(correct, total):
    return correct / total  # ❌ ZeroDivisionError if total == 0

# AFTER: Safe calculation
def calculate_accuracy(correct, total, default=0):
    if total == 0:
        return default  # Return 0 or None instead of crashing
    return (correct / total) * 100
```

---

## Integration Checklist

To implement these enhancements:

- [ ] Create `validation_engine.py` with pre-flight checks
- [ ] Create `cohort_analytics.py` with percentile ranking
- [ ] Create `predictive_analytics.py` with pass probability
- [ ] Create `learning_metrics.py` with velocity tracking
- [ ] Update `class_report_gen.py` with edge case handling
- [ ] Add validation calls to `student_answer_analyzer.py`
- [ ] Add analytics calls to `individual_report_gen.py`
- [ ] Write tests for each new module
- [ ] Update documentation

**Estimated Implementation Time:** 24-30 hours for all 5 improvements

---

## Testing the Improvements

```python
# test_enhancements.py

def test_validation_empty_answer_key():
    validator = ValidationEngine()
    is_valid, warnings = validator.validate_answer_key({})
    assert is_valid == False
    assert "empty" in warnings[0].lower()

def test_percentile_calculation():
    analytics = CohortAnalytics()
    result = analytics.calculate_percentile(75, [50, 60, 70, 75, 80, 85, 90])
    assert result["percentile"] == 50  # Median

def test_pass_probability():
    predictor = PredictiveAnalytics()
    result = predictor.estimate_pass_probability(60, 75)
    assert 0 <= result["pass_probability"] <= 1

def test_learning_velocity():
    metrics = LearningMetrics()
    result = metrics.calculate_velocity(
        [65, 68, 71, 74],
        ["2026-07-01", "2026-07-08", "2026-07-15", "2026-07-22"]
    )
    assert result["velocity_per_week"] > 0
    assert result["trend"] == "improving"
```

---

## Which to Implement First?

**Recommended Priority:**

1. **Validation Engine** (5h) - Prevents crashes
2. **Percentile Ranking** (3h) - Quick value add
3. **Pass Probability** (4h) - High student value
4. **Learning Velocity** (3h) - Motivation metric
5. **Edge Case Fixes** (4h) - Robustness

**Total: 19 hours for massive improvement**
