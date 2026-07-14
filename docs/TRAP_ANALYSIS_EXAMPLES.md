# Trap Analysis Engine - Usage Examples

Complete working examples for integrating trap analysis into CISSP Analyzer pipelines.

## Example 1: Basic Single Answer Analysis

**Use Case:** Check why student got a question wrong

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

engine = TrapAnalysisEngine()

# Analyze one answer
result = engine.analyze_answer(
    question_num=42,
    student_answer="C",
    correct_answer="A"
)

# Display results
print(f"Question {result.question_num}:")
print(f"  Your answer: {result.student_answer}")
print(f"  Correct: {result.correct_answer}")
print(f"  Score: {'✓ CORRECT' if result.is_correct else '✗ WRONG'}")

if result.trap_explanation:
    exp = result.trap_explanation
    print(f"\n  You fell for a TRAP: {exp.trap_name}")
    print(f"  Severity: {exp.severity}")
    print(f"  Why: {exp.why_student_fell}")
    print(f"  \n  ISC2 Fix: {exp.isc2_fix}")
    print(f"  Prevention: {exp.prevention_tip}")
    print(f"  \n  Confidence: {exp.confidence_score:.0%}")
```

## Example 2: Batch Analysis for Student Report

**Use Case:** Analyze complete exam and generate report

```python
import json
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

# Load student answers and key
with open("student_exam_answers.json") as f:
    student_answers = json.load(f)  # {1: "A", 2: "B", ...}

with open("answer_key.json") as f:
    answer_key = json.load(f)  # {1: "A", 2: "A", ...}

# Analyze
engine = TrapAnalysisEngine()
results = engine.analyze_all_answers(student_answers, answer_key)

# Summary stats
total = len(results)
correct = sum(1 for r in results if r.is_correct)
wrong = total - correct
score = (correct / total) * 100

print(f"Exam Results: {correct}/{total} ({score:.1f}%)")
print(f"Wrong answers: {wrong}")

# Identify trap patterns
wrong_results = [r for r in results if not r.is_correct and r.trap_explanation]
print(f"\nWrong answers with trap identification: {len(wrong_results)}")

for result in wrong_results[:5]:
    exp = result.trap_explanation
    print(f"  Q{result.question_num}: {exp.trap_name} (Severity: {exp.severity})")
```

## Example 3: Generate Study Plan from Vulnerabilities

**Use Case:** Create personalized study recommendations

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

engine = TrapAnalysisEngine()

# Analyze (from previous example)
results = engine.analyze_all_answers(student_answers, answer_key)

# Get vulnerabilities
vulnerabilities = engine.summarize_vulnerabilities(results)

# Generate study plan
plan = engine.generate_recommendations(vulnerabilities)

# Display
print(f"PERSONALIZED STUDY PLAN")
print(f"=" * 60)
print(f"\nPrimary Focus: {plan['primary_recommendation']}")

print(f"\nHigh Priority Traps ({len(plan['high_priority_traps'])})")
for trap in plan['high_priority_traps']:
    print(f"  • {trap['trap_name']} ({trap['frequency_count']} questions)")

print(f"\nStudy Sequence:")
for i, item in enumerate(plan['study_plan'], 1):
    print(f"  {item}")

print(f"\nTotal Vulnerabilities: {plan['total_vulnerabilities']}")
```

## Example 4: Integrate into Student Report Generator

**Use Case:** Add trap analysis to existing report generation

```python
from pathlib import Path
import json
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine
from cissp_analyzer.analysis_engine import AnalysisEngine

class EnhancedStudentReportGenerator:
    def __init__(self):
        self.trap_engine = TrapAnalysisEngine()
        self.performance_engine = AnalysisEngine(domain_mapper)
    
    def generate_full_report(self, student_name, answers, answer_key):
        """Generate comprehensive report with trap analysis."""
        
        # Standard performance analysis
        student_performance = self.performance_engine.evaluate_student(
            answers, student_name
        )
        
        # NEW: Trap analysis
        trap_results = self.trap_engine.analyze_all_answers(answers, answer_key)
        trap_vulnerabilities = self.trap_engine.summarize_vulnerabilities(trap_results)
        trap_recommendations = self.trap_engine.generate_recommendations(
            trap_vulnerabilities
        )
        
        # Build report
        report = {
            "student_name": student_name,
            "score": {
                "correct": student_performance.correct_count,
                "total": student_performance.total_questions,
                "percentage": student_performance.score_percentage,
            },
            "performance_by_domain": student_performance.by_domain,
            "performance_by_difficulty": student_performance.by_difficulty,
            
            # NEW: Trap analysis section
            "trap_analysis": {
                "vulnerabilities": [
                    {
                        "trap_name": v.trap_name,
                        "frequency": v.frequency_count,
                        "severity": v.severity,
                        "affected_questions": v.affected_questions,
                        "recommendation": v.recommendation,
                        "is_high_priority": v.is_high_priority,
                    }
                    for v in trap_vulnerabilities
                ],
                "study_plan": trap_recommendations["study_plan"],
                "primary_focus": trap_recommendations["primary_recommendation"],
            }
        }
        
        return report

# Usage
generator = EnhancedStudentReportGenerator()
report = generator.generate_full_report(
    "John Doe",
    student_answers,
    answer_key
)

# Save report
with open(f"reports/{report['student_name']}_complete_analysis.json", "w") as f:
    json.dump(report, f, indent=2)
```

## Example 5: Class-Level Trap Analysis

**Use Case:** Analyze all students to find common class-wide issues

```python
from collections import defaultdict
import json
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

class ClassTrapAnalyzer:
    def __init__(self):
        self.trap_engine = TrapAnalysisEngine()
    
    def analyze_class(self, all_student_data):
        """
        Analyze all students to find class-wide trap patterns.
        
        Args:
            all_student_data: List of (name, answers_dict, answer_key_dict)
        """
        
        # Track vulnerabilities across students
        trap_frequency = defaultdict(int)
        trap_names = {}
        affected_students = defaultdict(list)
        
        for student_name, answers, answer_key in all_student_data:
            # Analyze this student
            results = self.trap_engine.analyze_all_answers(answers, answer_key)
            vulnerabilities = self.trap_engine.summarize_vulnerabilities(results)
            
            # Aggregate trap data
            for vuln in vulnerabilities:
                trap_category = vuln.trap_category
                trap_frequency[trap_category] += vuln.frequency_count
                trap_names[trap_category] = vuln.trap_name
                affected_students[trap_category].append({
                    "student": student_name,
                    "frequency": vuln.frequency_count,
                })
        
        # Sort by frequency
        sorted_traps = sorted(
            trap_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Generate report
        report = {
            "class_size": len(all_student_data),
            "most_common_traps": [
                {
                    "rank": i + 1,
                    "trap_category": cat,
                    "trap_name": trap_names[cat],
                    "total_frequency": freq,
                    "affected_students": affected_students[cat],
                    "avg_per_student": freq / len(all_student_data),
                }
                for i, (cat, freq) in enumerate(sorted_traps[:10])
            ],
            "recommendations": self._generate_class_recommendations(sorted_traps),
        }
        
        return report
    
    def _generate_class_recommendations(self, sorted_traps):
        """Generate class-wide study recommendations."""
        top_3 = sorted_traps[:3]
        
        return f"Class focus: Master {top_3[0][0]}, {top_3[1][0]}, {top_3[2][0]}. " \
               f"These three account for {sum(f for _, f in top_3)} " \
               f"mistakes across the class."

# Usage
analyzer = ClassTrapAnalyzer()

all_students = [
    ("Alice", alice_answers, answer_key),
    ("Bob", bob_answers, answer_key),
    ("Charlie", charlie_answers, answer_key),
]

class_report = analyzer.analyze_class(all_students)

print("CLASS TRAP ANALYSIS")
for trap_info in class_report["most_common_traps"]:
    print(f"{trap_info['rank']}. {trap_info['trap_name']} "
          f"({trap_info['total_frequency']} total)")

print(f"\nRecommendation: {class_report['recommendations']}")
```

## Example 6: Track Student Progress Over Multiple Exams

**Use Case:** Monitor improvement in trap vulnerabilities

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine
import json

class ProgressTracker:
    def __init__(self):
        self.trap_engine = TrapAnalysisEngine()
    
    def track_trap_progress(self, student_name, exam_history):
        """
        Track how student's trap vulnerabilities improve over time.
        
        Args:
            student_name: Student name
            exam_history: List of (exam_date, answers, answer_key)
        """
        
        progress = {
            "student": student_name,
            "exams": []
        }
        
        for exam_date, answers, answer_key in exam_history:
            # Analyze this exam
            results = self.trap_engine.analyze_all_answers(answers, answer_key)
            vulnerabilities = self.trap_engine.summarize_vulnerabilities(results)
            
            # Extract key metrics
            exam_analysis = {
                "date": exam_date,
                "score": sum(1 for r in results if r.is_correct) / len(results) * 100,
                "unique_traps_hit": len(vulnerabilities),
                "top_3_traps": [
                    {
                        "trap": v.trap_name,
                        "frequency": v.frequency_count,
                        "severity": v.severity,
                    }
                    for v in vulnerabilities[:3]
                ]
            }
            
            progress["exams"].append(exam_analysis)
        
        # Analyze progression
        progress["improvement"] = self._analyze_improvement(progress["exams"])
        
        return progress
    
    def _analyze_improvement(self, exams):
        """Calculate improvement metrics."""
        if len(exams) < 2:
            return "Insufficient data"
        
        first_score = exams[0]["score"]
        last_score = exams[-1]["score"]
        improvement = last_score - first_score
        
        first_traps = exams[0]["unique_traps_hit"]
        last_traps = exams[-1]["unique_traps_hit"]
        trap_reduction = first_traps - last_traps
        
        return {
            "score_improvement": f"{improvement:+.1f}%",
            "trap_reduction": f"{trap_reduction} fewer trap types",
            "trend": "positive" if improvement > 0 else "negative",
        }

# Usage
tracker = ProgressTracker()

exam_history = [
    ("2026-06-01", june_answers, answer_key),
    ("2026-06-15", mid_june_answers, answer_key),
    ("2026-07-01", july_answers, answer_key),
]

progress = tracker.track_trap_progress("Jane Doe", exam_history)

print("PROGRESS TRACKING")
for exam in progress["exams"]:
    print(f"\n{exam['date']}: {exam['score']:.1f}%")
    print(f"  Unique traps: {exam['unique_traps_hit']}")
    for trap in exam["top_3_traps"]:
        print(f"    - {trap['trap']}: {trap['frequency']}x")

print(f"\nImprovement: {progress['improvement']['score_improvement']}")
print(f"Trap reduction: {progress['improvement']['trap_reduction']}")
```

## Example 7: Export and Share Reports

**Use Case:** Create shareable reports for students and instructors

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

engine = TrapAnalysisEngine()
results = engine.analyze_all_answers(answers, answer_key)

# Create different formats for different audiences

# For students: Markdown (readable, actionable)
md_report = engine.export_analysis_results(results, "markdown")
with open("student_report.md", "w") as f:
    f.write(md_report)

# For instructors: CSV (spreadsheet analysis)
csv_report = engine.export_analysis_results(results, "csv")
with open("instructor_analysis.csv", "w") as f:
    f.write(csv_report)

# For systems: JSON (structured, machine-readable)
json_report = engine.export_analysis_results(results, "json")
with open("trap_analysis_data.json", "w") as f:
    f.write(json_report)

print("✓ Reports generated:")
print("  - student_report.md (for student review)")
print("  - instructor_analysis.csv (for spreadsheet tools)")
print("  - trap_analysis_data.json (for system integration)")
```

## Example 8: Real-Time Feedback During Practice

**Use Case:** Provide immediate feedback as student answers questions

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

class PracticeFeedback:
    def __init__(self):
        self.engine = TrapAnalysisEngine()
        self.questions_answered = 0
        self.traps_identified = []
    
    def check_answer(self, question_num, student_answer, correct_answer):
        """Provide immediate feedback on one answer."""
        
        result = self.engine.analyze_answer(
            question_num,
            student_answer,
            correct_answer
        )
        
        self.questions_answered += 1
        
        # Provide feedback
        if result.is_correct:
            print(f"✓ Question {question_num} - CORRECT!")
        else:
            print(f"✗ Question {question_num} - Incorrect")
            
            if result.trap_explanation:
                exp = result.trap_explanation
                self.traps_identified.append(exp.trap_category)
                
                print(f"\n  You fell for the '{exp.trap_name}' trap")
                print(f"  {exp.why_student_fell}")
                print(f"\n  Remember: {exp.isc2_fix}")
                print(f"\n  Next time: {exp.prevention_tip}")
            else:
                print("  Review your understanding of this topic")
    
    def session_summary(self):
        """Provide summary of practice session."""
        print("\n" + "=" * 60)
        print("PRACTICE SESSION SUMMARY")
        print("=" * 60)
        print(f"Questions answered: {self.questions_answered}")
        
        if self.traps_identified:
            from collections import Counter
            trap_counts = Counter(self.traps_identified)
            
            print(f"\nTraps encountered: {len(trap_counts)} unique types")
            for trap, count in trap_counts.most_common(3):
                trap_info = self.engine.get_trap_details(trap)
                print(f"  • {trap_info['name']}: {count} times")

# Usage during practice session
feedback = PracticeFeedback()

feedback.check_answer(1, "B", "A")  # Wrong, might show trap
feedback.check_answer(2, "A", "A")  # Correct
feedback.check_answer(3, "C", "D")  # Wrong, might show trap

feedback.session_summary()
```

## Example 9: Detailed Trap Reference for Study

**Use Case:** Help student understand and avoid specific traps

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

engine = TrapAnalysisEngine()

# Get details about a trap the student struggled with
trap_category = "NEG"  # From student's vulnerability list
trap_info = engine.get_trap_details(trap_category)

# Generate study material
print(f"STUDY GUIDE: {trap_info['name'].upper()}")
print("=" * 60)
print(f"Type: {trap_info['type']}")
print(f"Difficulty: {trap_info['difficulty']}")
print(f"Frequency on CISSP: {trap_info['frequency']}")

print(f"\nThe Trap:")
print(f"  {trap_info['the_trap']}")

print(f"\nHow to Avoid:")
print(f"  {trap_info['prevention_strategy']}")

print(f"\nISC2 Principle:")
print(f"  {trap_info['isc2_principle']}")

print(f"\nExample (WRONG):")
print(f"  {trap_info['example_trap']}")

print(f"\nExample (CORRECT):")
print(f"  {trap_info['example_correct']}")

print(f"\nThe Fix:")
print(f"  {trap_info['the_fix']}")

# Find all questions with this trap
print(f"\nPractice Questions with this trap:")
q_nums = [
    q_num for q_num, q_data in engine.question_mappings.items()
    if q_data.get("exam_trick") == trap_category
]
print(f"  Questions: {q_nums[:10]}")  # Show first 10
```

## Example 10: Integration with Dashboard

**Use Case:** Add trap data to web dashboard

```python
import json
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

class DashboardDataGenerator:
    def __init__(self):
        self.engine = TrapAnalysisEngine()
    
    def get_dashboard_data(self, student_name, answers, answer_key):
        """Generate JSON data for dashboard."""
        
        # Analyze
        results = self.engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = self.engine.summarize_vulnerabilities(results)
        recommendations = self.engine.generate_recommendations(vulnerabilities)
        
        # Format for dashboard
        dashboard_data = {
            "student": student_name,
            "metrics": {
                "score": f"{sum(1 for r in results if r.is_correct)}/{len(results)}",
                "trap_vulnerabilities": len(vulnerabilities),
                "high_priority_count": len(recommendations["high_priority_traps"]),
            },
            "charts": {
                "trap_severity": self._get_severity_distribution(vulnerabilities),
                "trap_frequency": self._get_frequency_distribution(vulnerabilities),
            },
            "recommendations": recommendations,
        }
        
        return dashboard_data
    
    def _get_severity_distribution(self, vulnerabilities):
        """Get severity breakdown for chart."""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for v in vulnerabilities:
            counts[v.severity] += 1
        return counts
    
    def _get_frequency_distribution(self, vulnerabilities):
        """Get top 5 traps by frequency."""
        return [
            {"name": v.trap_name, "count": v.frequency_count}
            for v in vulnerabilities[:5]
        ]

# Usage
generator = DashboardDataGenerator()
data = generator.get_dashboard_data("John Doe", answers, answer_key)

# Send to dashboard
print(json.dumps(data, indent=2))
```

---

All these examples demonstrate different use cases for the `TrapAnalysisEngine`. Choose the pattern that best fits your integration point!
