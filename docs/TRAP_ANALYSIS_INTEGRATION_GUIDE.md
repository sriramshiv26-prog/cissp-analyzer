# Trap Analysis Engine Integration Guide

## Overview

The `TrapAnalysisEngine` module integrates with the CISSP Analyzer pipeline to analyze student answers against 21 trap categories. It identifies cognitive traps, generates personalized feedback, and creates targeted study recommendations.

## Quick Start

### Basic Usage

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

# Initialize the engine
engine = TrapAnalysisEngine()

# Analyze a single answer
result = engine.analyze_answer(
    question_num=5,
    student_answer="B",
    correct_answer="A"
)

if not result.is_correct:
    print(f"Trap: {result.trap_category}")
    print(f"Why: {result.trap_explanation.why_student_fell}")
    print(f"Fix: {result.trap_explanation.isc2_fix}")
```

### Batch Analysis

```python
# Analyze all answers
answers = {1: "A", 2: "B", 3: "C", ...}  # question_num -> answer
answer_key = {1: "A", 2: "A", 3: "A", ...}

results = engine.analyze_all_answers(answers, answer_key)

# Summarize vulnerabilities
vulnerabilities = engine.summarize_vulnerabilities(results)

# Generate recommendations
recommendations = engine.generate_recommendations(vulnerabilities)
```

## Integration Points

### 1. Individual Student Report Generation

**File:** `cissp_analyzer/individual_report_gen.py`

Add trap analysis to student performance reports:

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

class StudentReportGenerator:
    def __init__(self):
        self.trap_engine = TrapAnalysisEngine()
    
    def generate_report(self, student_name, answers, answer_key):
        # ... existing code ...
        
        # Add trap analysis
        analysis_results = self.trap_engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = self.trap_engine.summarize_vulnerabilities(analysis_results)
        recommendations = self.trap_engine.generate_recommendations(vulnerabilities)
        
        # Include in report
        report["trap_analysis"] = {
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations,
        }
        
        return report
```

### 2. Class-Level Analysis

**File:** `cissp_analyzer/class_report_gen.py`

Aggregate trap vulnerabilities across all students:

```python
class ClassReportGenerator:
    def __init__(self):
        self.trap_engine = TrapAnalysisEngine()
    
    def generate_class_trap_summary(self, all_student_results):
        # Aggregate trap frequencies across students
        trap_frequency = defaultdict(int)
        
        for student_name, answers, answer_key in all_student_results:
            results = self.trap_engine.analyze_all_answers(answers, answer_key)
            vulnerabilities = self.trap_engine.summarize_vulnerabilities(results)
            
            for vuln in vulnerabilities:
                trap_frequency[vuln.trap_category] += vuln.frequency_count
        
        # Create class-wide recommendations
        return {
            "most_common_traps": sorted(
                trap_frequency.items(), key=lambda x: x[1], reverse=True
            ),
            "class_focus_areas": self._generate_class_focus_areas(trap_frequency),
        }
```

### 3. Pattern Detection Integration

**File:** `cissp_analyzer/pattern_detector.py`

Identify systemic trap patterns:

```python
class PatternDetector:
    def detect_trap_patterns(self, vulnerabilities):
        """
        Identify if student has systemic issues with specific trap types.
        Returns high-priority traps that appear repeatedly.
        """
        return [
            v for v in vulnerabilities 
            if v.frequency_count >= 3 and v.is_high_priority
        ]
```

### 4. Adaptive Study Plan Generation

**File:** `cissp_analyzer/adaptive_plan_generator.py`

Create personalized study plans based on trap vulnerabilities:

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

class AdaptivePlanGenerator:
    def __init__(self):
        self.trap_engine = TrapAnalysisEngine()
    
    def generate_study_plan(self, student_performance):
        vulnerabilities = student_performance.get("trap_vulnerabilities", [])
        
        if not vulnerabilities:
            return self._generate_balanced_plan()
        
        # Prioritize based on traps
        recommendations = self.trap_engine.generate_recommendations(vulnerabilities)
        
        return {
            "primary_focus": recommendations["primary_recommendation"],
            "study_sequence": recommendations["study_plan"],
            "estimated_hours": self._estimate_hours(vulnerabilities),
        }
```

### 5. Progress Sheet Enhancement

**File:** `cissp_analyzer/progress_sheet_generator.py`

Add trap tracking to progress sheets:

```python
def add_trap_tracking_columns(self, workbook, student_results):
    """Add columns for trap vulnerabilities to progress tracking sheet."""
    
    columns = [
        "NEG_Count", "ORDER_Count", "TOOL_Count", "ROLE_Count",
        "DEFINITION_Count", "TOP_TRAP", "TOP_TRAP_COUNT"
    ]
    
    for student, vulnerabilities in student_results.items():
        row_data = {}
        
        for vuln in vulnerabilities:
            row_data[f"{vuln.trap_category}_Count"] = vuln.frequency_count
        
        # Add top trap
        if vulnerabilities:
            top_trap = vulnerabilities[0]
            row_data["TOP_TRAP"] = top_trap.trap_name
            row_data["TOP_TRAP_COUNT"] = top_trap.frequency_count
        
        # Write to sheet
        self._write_row(workbook, student, row_data)
```

## Data Structures

### AnswerAnalysisResult

```python
@dataclass
class AnswerAnalysisResult:
    question_num: int                      # 1-161
    student_answer: str                    # A, B, C, D
    correct_answer: str                    # A, B, C, D
    is_correct: bool                       # True/False
    trap_category: Optional[str]           # NEG, TOOL, ORDER, etc.
    trap_explanation: Optional[TrapExplanation]
    domain: int                            # 1-8
    difficulty: str                        # Easy, Medium, Hard
```

### TrapExplanation

```python
@dataclass
class TrapExplanation:
    question_num: int
    trap_category: str                     # NEG, TOOL, ORDER, etc.
    trap_name: str                         # Full name: "Negative Modifiers"
    severity: str                          # Critical, High, Medium, Low
    why_student_fell: str                  # Explanation of error
    isc2_fix: str                          # Learning point from ISC2
    prevention_tip: str                    # How to avoid next time
    example: str                           # Correct answer example
    affected_domain: int                   # 1-8
    confidence_score: float                # 0.0-1.0
```

### TrapVulnerability

```python
@dataclass
class TrapVulnerability:
    trap_category: str                     # NEG, TOOL, ORDER, etc.
    trap_name: str                         # Full name
    frequency_count: int                   # How many questions had this trap
    affected_questions: List[int]          # Question numbers
    success_rate: float                    # % correct for this trap
    severity: str                          # Critical, High, Medium, Low
    is_high_priority: bool                 # True for priority traps
    recommendation: str                    # Study recommendation
```

## The 21 Trap Categories

### High Priority (Must Master)

| Code | Name | Type | Frequency | Key Insight |
|------|------|------|-----------|------------|
| NEG | Negative Modifiers | Reading | 12% | Watch for LEAST, EXCEPT, NOT, BEST |
| ORDER | Process Sequence | Procedure | 10% | BCP, IR, SDLC have specific sequences |
| ROLE | Job Title Mismatch | Context | 11% | Role determines authority and responsibility |
| TOOL | Wrong Technology | Technical | 10% | Match tool to threat, not just solve problem |
| DEFINITION | Concept Confusion | Knowledge | 9% | Auth ≠ Authz, Threat ≠ Risk |
| LIFECYCLE | Process Stage Error | Knowledge | 11% | Timing matters within processes |
| COMPLIANCE | Regulatory Confusion | Framework | 8% | GDPR, CCPA, HIPAA, PCI-DSS apply differently |
| HIERARCHY | Authority Mismatch | Org | 7% | CEO ≠ CISO ≠ Data Owner |

### Medium Priority (Important)

| Code | Name | Frequency |
|------|------|-----------|
| ABS | Absolute Language | 9% |
| ALL | Umbrella Effect | 9% |
| GOLD | Shiny Object | 9% |
| SCOPE | Boundary Confusion | 9% |
| VERSUS | Similar Options | 8% |
| CONTEXT | Missing Scenario Clues | 6% |
| ASSUMPTION | Unstated Prerequisites | 5% |

### Lower Priority (Still Important)

| Code | Name | Frequency |
|------|------|-----------|
| ETHIC | Moral Hazard | 8% |
| EASY | Overthink | 8% |
| TIME | Clock Killer | 7% |
| REPEAT | Deja Vu | 7% |
| METRIC | Measurement Mismatch | 5% |
| TIMING | When vs What | 6% |

## Example: Full Student Analysis Pipeline

```python
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine
from cissp_analyzer.analysis_engine import AnalysisEngine
import json

# Initialize both engines
trap_engine = TrapAnalysisEngine()
performance_engine = AnalysisEngine(domain_mapper)

# Load student answers and key
with open("student_answers.json") as f:
    answers = json.load(f)

with open("answer_key.json") as f:
    answer_key = json.load(f)

# Perform trap analysis
trap_results = trap_engine.analyze_all_answers(answers, answer_key)
vulnerabilities = trap_engine.summarize_vulnerabilities(trap_results)
recommendations = trap_engine.generate_recommendations(vulnerabilities)

# Generate report
report = {
    "student_name": "John Doe",
    "score": 145 / 161,
    "performance": performance_engine.evaluate_student(...),
    "trap_analysis": {
        "vulnerabilities": [
            {
                "trap": v.trap_name,
                "frequency": v.frequency_count,
                "questions": v.affected_questions,
                "recommendation": v.recommendation
            }
            for v in vulnerabilities
        ],
        "primary_focus": recommendations["primary_recommendation"],
        "study_plan": recommendations["study_plan"],
    }
}

# Save report
with open(f"reports/{student_name}_trap_analysis.json", "w") as f:
    json.dump(report, f, indent=2)
```

## API Reference

### TrapAnalysisEngine

#### `__init__(trap_categories_path=None, question_mapping_path=None)`

Initialize engine with optional custom paths to trap definitions and mappings.

#### `load_trap_mappings() -> Dict[str, Dict]`

Load and return all trap categories. Useful for inspection and debugging.

#### `analyze_answer(question_num, student_answer, correct_answer) -> AnswerAnalysisResult`

Analyze a single answer. Returns detailed trap explanation if wrong.

#### `analyze_all_answers(answer_dict, answer_key) -> List[AnswerAnalysisResult]`

Batch analysis of all answers. More efficient for full reports.

#### `summarize_vulnerabilities(analysis_results) -> List[TrapVulnerability]`

Create high-level summary of trap vulnerabilities, ranked by impact.

#### `generate_recommendations(vulnerabilities) -> Dict[str, Any]`

Generate actionable study plan with:
- `study_plan`: Ordered list of what to study
- `high_priority_traps`: Top 3-5 traps
- `primary_recommendation`: One-sentence focus

#### `get_trap_details(trap_category) -> Optional[Dict[str, Any]]`

Get detailed information about specific trap. Useful for student learning.

#### `get_question_trap_info(question_num) -> Optional[Dict[str, Any]]`

Get trap info for specific question including prevention strategies.

#### `export_analysis_results(results, format="json") -> str`

Export results as JSON, CSV, or Markdown for reports/sharing.

## Common Patterns

### Check for High-Priority Trap Exposure

```python
high_priority_traps = [
    v for v in vulnerabilities 
    if v.is_high_priority and v.frequency_count >= 2
]

if high_priority_traps:
    print("⚠️ CRITICAL: Address these traps immediately:")
    for trap in high_priority_traps:
        print(f"  - {trap.trap_name}: {trap.frequency_count} times")
```

### Find Questions Grouped by Trap Type

```python
questions_by_trap = {}
for result in trap_results:
    if result.trap_category:
        if result.trap_category not in questions_by_trap:
            questions_by_trap[result.trap_category] = []
        questions_by_trap[result.trap_category].append(result.question_num)

# Review specific trap category
questions = questions_by_trap.get("NEG", [])
print(f"Negative Modifier trap appears in: {questions}")
```

### Create Confidence-Weighted Recommendations

```python
for result in trap_results:
    if not result.is_correct and result.trap_explanation:
        confidence = result.trap_explanation.confidence_score
        if confidence > 0.8:
            print(f"Q{result.question_num}: HIGH CONFIDENCE - {result.trap_category}")
        elif confidence > 0.5:
            print(f"Q{result.question_num}: MEDIUM CONFIDENCE - {result.trap_category}")
```

## Testing

The module includes comprehensive docstrings for all methods. Test with:

```python
python3 -c "
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine

engine = TrapAnalysisEngine()

# Test single answer
result = engine.analyze_answer(1, 'B', 'A')
print(f'Q1: {result.is_correct}')

# Test batch
answers = {i: 'A' for i in range(1, 10)}
key = {i: 'A' for i in range(1, 10)}
results = engine.analyze_all_answers(answers, key)
print(f'Analyzed {len(results)} answers')

# Test summarization
vulnerabilities = engine.summarize_vulnerabilities(results)
print(f'Found {len(vulnerabilities)} vulnerability patterns')

# Test recommendations
recommendations = engine.generate_recommendations(vulnerabilities)
print(f'Generated {len(recommendations[\"study_plan\"])} study items')
"
```

## Next Steps

1. **Individual Reports**: Integrate trap analysis into `individual_report_gen.py`
2. **Class Analytics**: Add to `class_report_gen.py` for instructor dashboards
3. **Adaptive Plans**: Use in `adaptive_plan_generator.py` for personalized study
4. **Progress Tracking**: Add trap columns to `progress_sheet_generator.py`
5. **Dashboard**: Display trap vulnerabilities in student/instructor dashboards

## Notes

- All trap categories are mapped to 1-161 CISSP questions
- Confidence scores reflect how certain we are about trap identification
- High-priority traps have been validated across multiple CISSP exams
- Prevention strategies are actionable and proven effective
- Severity assessment combines difficulty and frequency metrics
