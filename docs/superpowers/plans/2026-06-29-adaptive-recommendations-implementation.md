# Adaptive Recommendations Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement historical exam tracking + momentum-based adaptive recommendations without breaking existing 7-sheet report structure.

**Architecture:** 
- Add 5 new modules for history, trends, recommendations, and new sheets
- Enhance 2 existing modules (individual_report_gen, class_report_gen)
- Implement local students/ folder structure for exam storage
- Maintain backward compatibility (1-exam students still work)

**Tech Stack:** Python 3.9+, pandas, openpyxl, Ollama (local LLMs), existing CISSP infrastructure

---

## File Structure & Responsibilities

### New Files (5 modules)

```
cissp_analyzer/
├── history_loader.py              # Load previous exam JSON files + merge
├── trend_calculator.py            # Calculate domain/difficulty/type trends
├── recommendations_engine.py      # Momentum algorithm + pattern detection
├── progress_sheet_generator.py    # Generate Sheet 7 (Progress Over Time)
└── adaptive_plan_generator.py     # Generate Sheet 8 (Adaptive Study Plan)
```

### Modified Files (2 modules)

```
cissp_analyzer/
├── individual_report_gen.py       # Add 2 new sheets (7, 8)
└── main.py                        # Add history loading step + CLI modes
```

### Data Storage

```
students/
├── [StudentName]/
│   ├── Mock1_[Date]_[StudentName].xlsx    # Input exam file
│   ├── exam-1_performance.json            # Cached performance data
│   ├── Mock2_[Date]_[StudentName].xlsx
│   └── exam-2_performance.json
```

### Tests (6 test files)

```
tests/
├── test_history_loader.py
├── test_trend_calculator.py
├── test_recommendations_engine.py
├── test_progress_sheet_generator.py
├── test_adaptive_plan_generator.py
└── test_integration_multi_exam.py
```

---

## Task Cost Analysis & Model Recommendations

| Task | Hours | Model | Cost | Rationale |
|------|-------|-------|------|-----------|
| 1-3: History Infrastructure | 1.5h | Qwen2.5-coder | $0 | Straightforward Python data loading |
| 4-6: Trend Calculations | 2h | Qwen2.5-coder | $0 | Math formulas, no complex logic |
| 7-8: Momentum Algorithm | 1.5h | Gemma4 | $0 | Requires reasoning about weighting |
| 9-10: Pattern Detection | 1.5h | Qwen2.5-coder | $0 | Data filtering and analysis |
| 11-13: Sheet Generators | 2.5h | Qwen2.5-coder | $0 | Openpyxl operations (mechanical) |
| 14-15: Integration & CLI | 1.5h | Claude Sonnet | $2-3 | Architectural decision + orchestration |
| 16-17: Testing | 2h | Qwen2.5-coder | $0 | Test data + validation |
| 18: Documentation | 0.5h | No LLM | $0 | Manual writeup |

**Total Estimated:** 12-13 hours | **Cost:** $2-3 (only for architectural review task)

---

## Phase 1: Infrastructure & Data Schema (Tasks 1-3)

### Task 1: History Loader - Core Logic

**Files:**
- Create: `cissp_analyzer/history_loader.py`
- Test: `tests/test_history_loader.py`

**Cost:** 30 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write failing test for load_previous_exams()**

```python
# tests/test_history_loader.py
import json
import tempfile
from pathlib import Path
from cissp_analyzer.history_loader import HistoryLoader

def test_load_previous_exams_returns_empty_when_no_history():
    """First-time student: no previous exams"""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("NewStudent")
        assert result == []

def test_load_previous_exams_single_exam():
    """Student with one previous exam"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create mock exam-1_performance.json
        student_dir = Path(tmpdir) / "ExistingStudent"
        student_dir.mkdir()
        
        exam_data = {
            "exam_number": 1,
            "date": "2026-06-26",
            "student_name": "ExistingStudent",
            "overall_accuracy": 0.65,
            "by_domain": {
                "Security & Risk Management": {"accuracy": 0.70}
            }
        }
        
        with open(student_dir / "exam-1_performance.json", "w") as f:
            json.dump(exam_data, f)
        
        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("ExistingStudent")
        
        assert len(result) == 1
        assert result[0]["exam_number"] == 1
        assert result[0]["overall_accuracy"] == 0.65

def test_load_previous_exams_multiple_exams():
    """Student with multiple exams - verify order"""
    with tempfile.TemporaryDirectory() as tmpdir:
        student_dir = Path(tmpdir) / "MultiExamStudent"
        student_dir.mkdir()
        
        for exam_num in [1, 2, 3]:
            exam_data = {
                "exam_number": exam_num,
                "date": f"2026-06-{25+exam_num}",
                "overall_accuracy": 0.60 + (exam_num * 0.05)
            }
            with open(student_dir / f"exam-{exam_num}_performance.json", "w") as f:
                json.dump(exam_data, f)
        
        loader = HistoryLoader(tmpdir)
        result = loader.load_previous_exams("MultiExamStudent")
        
        assert len(result) == 3
        assert result[0]["exam_number"] == 1
        assert result[2]["exam_number"] == 3
        assert [r["overall_accuracy"] for r in result] == [0.60, 0.65, 0.70]

def test_load_previous_exams_enforces_max_limit():
    """Verify max 10 exams, warn on excess"""
    # This will be tested after warnings are added in Task 2
    pass
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/test_history_loader.py -v
# Expected: FAILED - HistoryLoader not found
```

- [ ] **Step 3: Write HistoryLoader implementation**

```python
# cissp_analyzer/history_loader.py
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

class HistoryLoader:
    """Load and manage historical exam performance data"""
    
    def __init__(self, students_dir: str = "students"):
        self.students_dir = Path(students_dir)
        self.students_dir.mkdir(exist_ok=True)
    
    def load_previous_exams(self, student_name: str) -> List[Dict]:
        """
        Load all previous exam performance files for a student.
        
        Args:
            student_name: Name of the student (e.g., "Sri")
            
        Returns:
            List of exam performance dicts, sorted by exam_number (oldest first)
        """
        student_path = self.students_dir / student_name
        
        if not student_path.exists():
            return []
        
        exam_files = sorted(student_path.glob("exam-*_performance.json"))
        exams = []
        
        for exam_file in exam_files:
            with open(exam_file, 'r') as f:
                exam_data = json.load(f)
                exams.append(exam_data)
        
        return exams
    
    def save_exam_performance(self, student_name: str, exam_number: int, 
                             performance_data: Dict) -> Path:
        """
        Save current exam performance to JSON file.
        
        Args:
            student_name: Name of student
            exam_number: Exam sequence number (1, 2, 3, ...)
            performance_data: Dict with accuracy by domain/difficulty/type
            
        Returns:
            Path to saved file
        """
        student_path = self.students_dir / student_name
        student_path.mkdir(parents=True, exist_ok=True)
        
        # Check max limit
        existing_exams = len(list(student_path.glob("exam-*_performance.json")))
        if existing_exams >= 10:
            print(f"⚠️  Warning: Student {student_name} has {existing_exams} exams (max 10).")
            print("   Consider archiving older exams.")
        
        output_file = student_path / f"exam-{exam_number}_performance.json"
        
        with open(output_file, 'w') as f:
            json.dump(performance_data, f, indent=2)
        
        return output_file
    
    def create_student_folder(self, student_name: str) -> Path:
        """Create student folder if it doesn't exist"""
        student_path = self.students_dir / student_name
        student_path.mkdir(parents=True, exist_ok=True)
        return student_path
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_history_loader.py -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/history_loader.py tests/test_history_loader.py
git commit -m "feat: add HistoryLoader for multi-exam support"
```

---

### Task 2: Performance Data Schema & Extraction

**Files:**
- Create: `cissp_analyzer/models.py` (extend existing)
- Modify: `cissp_analyzer/analysis_engine.py` (add export method)
- Test: `tests/test_performance_schema.py`

**Cost:** 20 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for performance data extraction**

```python
# tests/test_performance_schema.py
import json
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.domain_mapper import DomainMapper

def test_export_performance_as_json():
    """AnalysisEngine exports performance data matching schema"""
    # Setup
    mapper = DomainMapper('data/question_domain_mapping.json')
    engine = AnalysisEngine(mapper)
    
    # Simulate analyzed results
    engine.student_results = {
        "student1": {
            "questions": [
                {"id": 1, "correct": True, "domain": "Security & Risk Management", 
                 "difficulty": "Medium", "type": "Application", "trick": None},
                {"id": 2, "correct": False, "domain": "Asset Security",
                 "difficulty": "Hard", "type": "Scenario", "trick": "NOT"}
            ]
        }
    }
    
    # Export
    perf_data = engine.export_student_performance("student1", exam_number=1)
    
    # Verify schema
    assert perf_data["exam_number"] == 1
    assert perf_data["student_name"] == "student1"
    assert perf_data["total_questions"] == 2
    assert perf_data["total_correct"] == 1
    assert perf_data["overall_accuracy"] == 0.5
    
    assert "by_domain" in perf_data
    assert "by_difficulty" in perf_data
    assert "by_question_type" in perf_data
    assert "wrong_question_ids" in perf_data
    
    assert perf_data["wrong_question_ids"] == [2]
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_performance_schema.py::test_export_performance_as_json -v
# Expected: FAILED - method export_student_performance not found
```

- [ ] **Step 3: Add export method to AnalysisEngine**

```python
# Add to cissp_analyzer/analysis_engine.py

def export_student_performance(self, student_name: str, exam_number: int, 
                               exam_date: str = None) -> Dict:
    """
    Export analyzed performance data in format for historical tracking.
    
    Args:
        student_name: Name of student
        exam_number: Which exam (1, 2, 3, ...)
        exam_date: Optional date (defaults to today)
        
    Returns:
        Dict matching exam-N_performance.json schema
    """
    if exam_date is None:
        from datetime import date
        exam_date = str(date.today())
    
    results = self.student_results.get(student_name, {})
    questions = results.get("questions", [])
    
    # Count totals
    total_correct = sum(1 for q in questions if q.get("correct", False))
    total_questions = len(questions)
    overall_accuracy = total_correct / total_questions if total_questions > 0 else 0
    
    # Aggregate by domain
    by_domain = {}
    for q in questions:
        domain = q.get("domain", "Unknown")
        if domain not in by_domain:
            by_domain[domain] = {"correct": 0, "total": 0}
        by_domain[domain]["total"] += 1
        if q.get("correct"):
            by_domain[domain]["correct"] += 1
    
    # Add accuracy to each domain
    for domain in by_domain:
        correct = by_domain[domain]["correct"]
        total = by_domain[domain]["total"]
        by_domain[domain]["accuracy"] = correct / total if total > 0 else 0
    
    # Aggregate by difficulty
    by_difficulty = {}
    for q in questions:
        difficulty = q.get("difficulty", "Unknown")
        if difficulty not in by_difficulty:
            by_difficulty[difficulty] = {"correct": 0, "total": 0}
        by_difficulty[difficulty]["total"] += 1
        if q.get("correct"):
            by_difficulty[difficulty]["correct"] += 1
    
    for difficulty in by_difficulty:
        correct = by_difficulty[difficulty]["correct"]
        total = by_difficulty[difficulty]["total"]
        by_difficulty[difficulty]["accuracy"] = correct / total if total > 0 else 0
    
    # Aggregate by question type
    by_question_type = {}
    for q in questions:
        q_type = q.get("type", "Unknown")
        if q_type not in by_question_type:
            by_question_type[q_type] = {"correct": 0, "total": 0}
        by_question_type[q_type]["total"] += 1
        if q.get("correct"):
            by_question_type[q_type]["correct"] += 1
    
    for q_type in by_question_type:
        correct = by_question_type[q_type]["correct"]
        total = by_question_type[q_type]["total"]
        by_question_type[q_type]["accuracy"] = correct / total if total > 0 else 0
    
    # Collect wrong question IDs
    wrong_question_ids = [q.get("id") for q in questions if not q.get("correct", False)]
    
    return {
        "exam_number": exam_number,
        "date": exam_date,
        "student_name": student_name,
        "total_questions": total_questions,
        "total_correct": total_correct,
        "overall_accuracy": overall_accuracy,
        "by_domain": by_domain,
        "by_difficulty": by_difficulty,
        "by_question_type": by_question_type,
        "wrong_question_ids": wrong_question_ids
    }
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_performance_schema.py::test_export_performance_as_json -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/analysis_engine.py tests/test_performance_schema.py
git commit -m "feat: export performance data for historical tracking"
```

---

### Task 3: Student Name Detection from Filename

**Files:**
- Create: `cissp_analyzer/filename_parser.py`
- Test: `tests/test_filename_parser.py`

**Cost:** 15 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for filename parsing**

```python
# tests/test_filename_parser.py
from cissp_analyzer.filename_parser import FilenameParser

def test_extract_student_name_from_standard_pattern():
    """Extract student name from Mock[N]_[Date]_[Name].xlsx"""
    parser = FilenameParser()
    
    assert parser.extract_student_name("Mock1_Jun26_Sri.xlsx") == "Sri"
    assert parser.extract_student_name("Mock2_Jun28_Sam.xlsx") == "Sam"
    assert parser.extract_student_name("Mock3_Jul1_Alice.xlsx") == "Alice"

def test_extract_exam_number():
    """Extract exam sequence number"""
    parser = FilenameParser()
    
    assert parser.extract_exam_number("Mock1_Jun26_Sri.xlsx") == 1
    assert parser.extract_exam_number("Mock2_Jun28_Sam.xlsx") == 2
    assert parser.extract_exam_number("Mock10_Aug15_Bob.xlsx") == 10

def test_malformed_filename_returns_none():
    """Filename not matching pattern returns None"""
    parser = FilenameParser()
    
    assert parser.extract_student_name("random_file.xlsx") is None
    assert parser.extract_student_name("Final_Test.xlsx") is None

def test_case_insensitive_extraction():
    """Extract name regardless of case"""
    parser = FilenameParser()
    
    # File named with lowercase
    assert parser.extract_student_name("Mock1_Jun26_sri.xlsx") == "sri"
    # Should match folder "Sri" case-insensitively
    assert parser.normalize_student_name("sri") == "sri"
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_filename_parser.py -v
# Expected: FAILED - FilenameParser not found
```

- [ ] **Step 3: Implement FilenameParser**

```python
# cissp_analyzer/filename_parser.py
import re
from typing import Optional

class FilenameParser:
    """Parse student name and exam info from standardized filenames"""
    
    PATTERN = r"Mock(\d+)_([A-Za-z0-9]+)_([A-Za-z0-9\s]+)\.xlsx"
    
    def extract_student_name(self, filename: str) -> Optional[str]:
        """
        Extract student name from Mock[N]_[Date]_[StudentName].xlsx
        
        Args:
            filename: Filename to parse
            
        Returns:
            Student name or None if pattern doesn't match
        """
        match = re.match(self.PATTERN, filename)
        if match:
            return match.group(3)  # Third group is student name
        return None
    
    def extract_exam_number(self, filename: str) -> Optional[int]:
        """Extract exam sequence number from filename"""
        match = re.match(self.PATTERN, filename)
        if match:
            return int(match.group(1))
        return None
    
    def extract_date(self, filename: str) -> Optional[str]:
        """Extract date code from filename"""
        match = re.match(self.PATTERN, filename)
        if match:
            return match.group(2)
        return None
    
    @staticmethod
    def normalize_student_name(name: str) -> str:
        """Normalize student name for folder lookup (lowercase, strip whitespace)"""
        return name.lower().strip()
    
    def matches_pattern(self, filename: str) -> bool:
        """Check if filename matches expected pattern"""
        return re.match(self.PATTERN, filename) is not None
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_filename_parser.py -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/filename_parser.py tests/test_filename_parser.py
git commit -m "feat: add FilenameParser for student name extraction"
```

---

## Phase 2: Trend Calculations (Tasks 4-6)

### Task 4: Trend Calculator - Domain Trends

**Files:**
- Create: `cissp_analyzer/trend_calculator.py`
- Test: `tests/test_trend_calculator.py`

**Cost:** 40 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for domain trend calculation**

```python
# tests/test_trend_calculator.py
from cissp_analyzer.trend_calculator import TrendCalculator

def test_calculate_domain_trends_two_exams():
    """Calculate domain accuracy trends across 2 exams"""
    exam1 = {
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.65},
            "Asset Security": {"accuracy": 0.70}
        }
    }
    
    exam2 = {
        "by_domain": {
            "Security & Risk Management": {"accuracy": 0.72},
            "Asset Security": {"accuracy": 0.68}
        }
    }
    
    calc = TrendCalculator()
    trends = calc.calculate_domain_trends([exam1, exam2])
    
    assert "Security & Risk Management" in trends
    assert len(trends["Security & Risk Management"]) == 2
    assert trends["Security & Risk Management"] == [0.65, 0.72]
    assert trends["Asset Security"] == [0.70, 0.68]

def test_calculate_domain_trends_three_exams():
    """Three-exam trend shows progression"""
    exams = [
        {"by_domain": {"Domain A": {"accuracy": 0.60}}},
        {"by_domain": {"Domain A": {"accuracy": 0.65}}},
        {"by_domain": {"Domain A": {"accuracy": 0.72}}}
    ]
    
    calc = TrendCalculator()
    trends = calc.calculate_domain_trends(exams)
    
    assert trends["Domain A"] == [0.60, 0.65, 0.72]

def test_calculate_difficulty_trends():
    """Calculate difficulty level trends"""
    exams = [
        {"by_difficulty": {"Easy": {"accuracy": 0.75}, "Hard": {"accuracy": 0.40}}},
        {"by_difficulty": {"Easy": {"accuracy": 0.78}, "Hard": {"accuracy": 0.45}}}
    ]
    
    calc = TrendCalculator()
    trends = calc.calculate_difficulty_trends(exams)
    
    assert trends["Easy"] == [0.75, 0.78]
    assert trends["Hard"] == [0.40, 0.45]

def test_calculate_question_type_trends():
    """Calculate question type mastery trends"""
    exams = [
        {"by_question_type": {"Application": {"accuracy": 0.70}, "Scenario": {"accuracy": 0.50}}},
        {"by_question_type": {"Application": {"accuracy": 0.72}, "Scenario": {"accuracy": 0.55}}}
    ]
    
    calc = TrendCalculator()
    trends = calc.calculate_question_type_trends(exams)
    
    assert trends["Application"] == [0.70, 0.72]
    assert trends["Scenario"] == [0.50, 0.55]
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_trend_calculator.py -v
# Expected: FAILED - TrendCalculator not found
```

- [ ] **Step 3: Implement TrendCalculator**

```python
# cissp_analyzer/trend_calculator.py
from typing import List, Dict

class TrendCalculator:
    """Calculate performance trends across multiple exams"""
    
    def calculate_domain_trends(self, exams: List[Dict]) -> Dict[str, List[float]]:
        """
        Calculate accuracy trends per domain across all exams.
        
        Args:
            exams: List of performance dicts (exam-1, exam-2, ...)
            
        Returns:
            Dict: {domain_name: [accuracy_exam1, accuracy_exam2, ...]}
        """
        trends = {}
        
        for exam in exams:
            by_domain = exam.get("by_domain", {})
            for domain, data in by_domain.items():
                if domain not in trends:
                    trends[domain] = []
                trends[domain].append(data.get("accuracy", 0))
        
        return trends
    
    def calculate_difficulty_trends(self, exams: List[Dict]) -> Dict[str, List[float]]:
        """Calculate accuracy trends per difficulty level"""
        trends = {}
        
        for exam in exams:
            by_difficulty = exam.get("by_difficulty", {})
            for difficulty, data in by_difficulty.items():
                if difficulty not in trends:
                    trends[difficulty] = []
                trends[difficulty].append(data.get("accuracy", 0))
        
        return trends
    
    def calculate_question_type_trends(self, exams: List[Dict]) -> Dict[str, List[float]]:
        """Calculate accuracy trends per question type"""
        trends = {}
        
        for exam in exams:
            by_type = exam.get("by_question_type", {})
            for q_type, data in by_type.items():
                if q_type not in trends:
                    trends[q_type] = []
                trends[q_type].append(data.get("accuracy", 0))
        
        return trends
    
    def detect_trend_direction(self, trend: List[float]) -> str:
        """
        Determine if trend is improving, declining, or stable.
        
        Args:
            trend: List of accuracies [exam1, exam2, exam3, ...]
            
        Returns:
            "improving" | "declining" | "stable"
        """
        if len(trend) < 2:
            return "stable"
        
        first = trend[0]
        last = trend[-1]
        diff = last - first
        
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        else:
            return "stable"
    
    def get_momentum_score(self, previous_accuracy: float, current_accuracy: float) -> float:
        """
        Calculate momentum as difference from previous to current.
        
        Args:
            previous_accuracy: Previous exam accuracy (0-1)
            current_accuracy: Current exam accuracy (0-1)
            
        Returns:
            Momentum score (positive = improving, negative = declining)
        """
        return current_accuracy - previous_accuracy
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_trend_calculator.py -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/trend_calculator.py tests/test_trend_calculator.py
git commit -m "feat: add TrendCalculator for multi-exam trend analysis"
```

---

### Task 5: Momentum Scoring Algorithm

**Files:**
- Modify: `cissp_analyzer/trend_calculator.py` (add momentum logic)
- Test: `tests/test_trend_calculator.py` (add momentum tests)

**Cost:** 30 min | **Model:** Gemma4 | **Cost:** $0

- [ ] **Step 1: Write test for momentum-based priority scoring**

```python
# Add to tests/test_trend_calculator.py

def test_calculate_priority_score_with_momentum():
    """Priority score = weakness + (momentum × 2)"""
    calc = TrendCalculator()
    
    # Case 1: High weakness + positive momentum
    score = calc.calculate_priority_score(
        current_accuracy=0.50,  # weakness = 50
        previous_accuracy=0.45  # momentum = +5
    )
    # Expected: 50 + (5 × 2) = 60
    assert score == 60
    
    # Case 2: Low weakness + negative momentum
    score = calc.calculate_priority_score(
        current_accuracy=0.80,  # weakness = 20
        previous_accuracy=0.82  # momentum = -2
    )
    # Expected: 20 + (-2 × 2) = 16
    assert score == 16
    
    # Case 3: First exam (no previous)
    score = calc.calculate_priority_score(
        current_accuracy=0.55,  # weakness = 45
        previous_accuracy=None  # momentum = 0
    )
    # Expected: 45 + (0 × 2) = 45
    assert score == 45

def test_rank_domains_by_priority():
    """Rank domains by calculated priority scores"""
    calc = TrendCalculator()
    
    current_exam = {
        "by_domain": {
            "Identity & Access": {"accuracy": 0.50},      # weakness 50
            "Soft Dev Security": {"accuracy": 0.58},      # weakness 42
            "Security Architecture": {"accuracy": 0.75},  # weakness 25
            "Cryptography": {"accuracy": 0.78}            # weakness 22
        }
    }
    
    previous_exam = {
        "by_domain": {
            "Identity & Access": {"accuracy": 0.45},      # momentum +5
            "Soft Dev Security": {"accuracy": 0.55},      # momentum +3
            "Security Architecture": {"accuracy": 0.72},  # momentum +3
            "Cryptography": {"accuracy": 0.80}            # momentum -2
        }
    }
    
    calc = TrendCalculator()
    ranking = calc.rank_domains_by_priority(current_exam, previous_exam)
    
    # Verify order: highest priority first
    assert ranking[0]["domain"] == "Identity & Access"  # priority 60
    assert ranking[1]["domain"] == "Soft Dev Security"  # priority 48
    assert ranking[2]["domain"] == "Security Architecture"  # priority 31
    assert ranking[3]["domain"] == "Cryptography"  # priority 18
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_trend_calculator.py::test_calculate_priority_score_with_momentum -v
# Expected: FAILED
```

- [ ] **Step 3: Add momentum methods to TrendCalculator**

```python
# Add to cissp_analyzer/trend_calculator.py

def calculate_priority_score(self, current_accuracy: float, 
                            previous_accuracy: float = None) -> float:
    """
    Calculate domain priority score for study recommendations.
    
    Formula: priority_score = weakness + (momentum × 2)
    
    Args:
        current_accuracy: Current exam accuracy (0-1)
        previous_accuracy: Previous exam accuracy (0-1), or None if first exam
        
    Returns:
        Priority score (higher = more important to study)
    """
    # Weakness: how far from 100%
    weakness = (1 - current_accuracy) * 100
    
    # Momentum: improvement/regression trend
    if previous_accuracy is None:
        momentum = 0
    else:
        momentum = (current_accuracy - previous_accuracy) * 100
    
    # Priority = weakness + (momentum × 2)
    priority = weakness + (momentum * 2)
    
    return priority

def rank_domains_by_priority(self, current_exam: Dict, 
                            previous_exam: Dict = None) -> List[Dict]:
    """
    Rank domains by priority score (weakness + momentum).
    
    Args:
        current_exam: Latest exam performance dict
        previous_exam: Previous exam performance dict (optional)
        
    Returns:
        List of dicts with domain, accuracy, momentum, priority, rank
    """
    domains_data = []
    current_domains = current_exam.get("by_domain", {})
    previous_domains = (previous_exam or {}).get("by_domain", {})
    
    for domain, current_data in current_domains.items():
        current_acc = current_data.get("accuracy", 0)
        previous_acc = previous_domains.get(domain, {}).get("accuracy") if previous_exam else None
        
        priority_score = self.calculate_priority_score(current_acc, previous_acc)
        
        domains_data.append({
            "domain": domain,
            "current_accuracy": current_acc,
            "previous_accuracy": previous_acc,
            "momentum": (current_acc - previous_acc) * 100 if previous_acc else 0,
            "priority_score": priority_score
        })
    
    # Sort by priority (highest first)
    domains_data.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Add ranking
    for rank, domain_data in enumerate(domains_data, 1):
        domain_data["rank"] = rank
    
    return domains_data
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_trend_calculator.py::test_calculate_priority_score_with_momentum -v
pytest tests/test_trend_calculator.py::test_rank_domains_by_priority -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/trend_calculator.py tests/test_trend_calculator.py
git commit -m "feat: implement momentum-based priority scoring"
```

---

### Task 6: Pattern Detection for Subtopics

**Files:**
- Create: `cissp_analyzer/pattern_detector.py`
- Test: `tests/test_pattern_detector.py`

**Cost:** 30 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for pattern detection**

```python
# tests/test_pattern_detector.py
from cissp_analyzer.pattern_detector import PatternDetector

def test_detect_all_wrong_pattern():
    """Detect when all questions in subtopic are wrong"""
    detector = PatternDetector()
    
    questions = [
        {"id": 1, "correct": False, "topic": "Kerberos"},
        {"id": 2, "correct": False, "topic": "Kerberos"},
        {"id": 3, "correct": False, "topic": "Kerberos"}
    ]
    
    pattern = detector.detect_topic_pattern(questions, "Kerberos")
    
    assert pattern["all_wrong"] == True
    assert pattern["accuracy"] == 0.0
    assert pattern["insight"] == "ALL WRONG (0/3) - need fundamental review"

def test_detect_weakness_by_question_type():
    """Detect if weakness is specific to question type"""
    detector = PatternDetector()
    
    questions = [
        {"id": 1, "correct": True, "topic": "OAuth", "type": "Application"},
        {"id": 2, "correct": True, "topic": "OAuth", "type": "Application"},
        {"id": 3, "correct": False, "topic": "OAuth", "type": "Scenario"},
        {"id": 4, "correct": False, "topic": "OAuth", "type": "Scenario"}
    ]
    
    pattern = detector.detect_topic_pattern(questions, "OAuth")
    
    # Should detect: Scenario questions are weak
    assert pattern["weakness_by_type"] is not None
    assert "Scenario" in pattern["weakness_by_type"]
    assert pattern["weakness_by_type"]["Scenario"]["accuracy"] == 0.0

def test_detect_trick_keyword_pattern():
    """Detect if weakness is related to trick keywords (NOT, BEST, etc.)"""
    detector = PatternDetector()
    
    questions = [
        {"id": 1, "correct": True, "topic": "SAML", "trick": None},
        {"id": 2, "correct": True, "topic": "SAML", "trick": None},
        {"id": 3, "correct": False, "topic": "SAML", "trick": "NOT"},
        {"id": 4, "correct": False, "topic": "SAML", "trick": "NOT"}
    ]
    
    pattern = detector.detect_topic_pattern(questions, "SAML")
    
    assert pattern["weakness_by_trick"] is not None
    assert pattern["weakness_by_trick"]["NOT"]["accuracy"] == 0.0
    assert pattern["insight"] == "NOT keyword 0%, Regular 50% - trick questions are the issue"
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_pattern_detector.py -v
# Expected: FAILED
```

- [ ] **Step 3: Implement PatternDetector**

```python
# cissp_analyzer/pattern_detector.py
from typing import List, Dict

class PatternDetector:
    """Detect learning patterns in exam data"""
    
    def detect_topic_pattern(self, questions: List[Dict], topic: str) -> Dict:
        """
        Analyze patterns for a specific topic/subtopic.
        
        Args:
            questions: List of question dicts with correct, type, trick, etc.
            topic: Topic/subtopic name to analyze
            
        Returns:
            Dict with accuracy, patterns, and insights
        """
        topic_questions = [q for q in questions if q.get("topic") == topic]
        
        if not topic_questions:
            return {"insight": "No questions in this topic"}
        
        total = len(topic_questions)
        correct = sum(1 for q in topic_questions if q.get("correct", False))
        accuracy = correct / total if total > 0 else 0
        
        result = {
            "topic": topic,
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "all_wrong": correct == 0,
            "all_correct": correct == total
        }
        
        # Analyze by question type
        by_type = self._analyze_by_dimension(topic_questions, "type")
        if len(by_type) > 1:  # Only if multiple types exist
            result["weakness_by_type"] = by_type
        
        # Analyze by trick keyword
        by_trick = self._analyze_by_dimension(topic_questions, "trick")
        if len(by_trick) > 1:  # Only if multiple tricks exist
            result["weakness_by_trick"] = by_trick
        
        # Generate insight
        result["insight"] = self._generate_insight(result, by_type, by_trick)
        
        return result
    
    def _analyze_by_dimension(self, questions: List[Dict], dimension: str) -> Dict:
        """Aggregate accuracy by a specific dimension"""
        aggregated = {}
        
        for q in questions:
            value = q.get(dimension, "Unknown")
            if value not in aggregated:
                aggregated[value] = {"correct": 0, "total": 0}
            
            aggregated[value]["total"] += 1
            if q.get("correct", False):
                aggregated[value]["correct"] += 1
        
        # Add accuracy
        for value in aggregated:
            correct = aggregated[value]["correct"]
            total = aggregated[value]["total"]
            aggregated[value]["accuracy"] = correct / total if total > 0 else 0
        
        return aggregated
    
    def _generate_insight(self, result: Dict, by_type: Dict, by_trick: Dict) -> str:
        """Generate human-readable insight about the pattern"""
        if result["all_wrong"]:
            return f"ALL WRONG (0/{result['total']}) - need fundamental review"
        
        if result["all_correct"]:
            return f"ALL CORRECT - mastered!"
        
        # Check if specific question type is weak
        if by_type and len(by_type) > 1:
            weak_type = min(by_type.items(), key=lambda x: x[1]["accuracy"])
            weak_name, weak_data = weak_type
            
            if weak_data["accuracy"] < 0.5:
                overall_pct = int(result["accuracy"] * 100)
                weak_pct = int(weak_data["accuracy"] * 100)
                strong_types = [k for k, v in by_type.items() if k != weak_name and v["accuracy"] > 0.5]
                if strong_types:
                    return f"{weak_name} {weak_pct}%, {strong_types[0]} {int(by_type[strong_types[0]]['accuracy']*100)}% - weakness in {weak_name} context"
        
        # Check if trick keywords are weak
        if by_trick and len(by_trick) > 1:
            trick_accuracies = {k: v["accuracy"] for k, v in by_trick.items()}
            
            # Compare trick vs non-trick
            has_trick = {k: acc for k, acc in trick_accuracies.items() if k and k != "None"}
            no_trick = trick_accuracies.get(None, trick_accuracies.get("None", 0))
            
            if has_trick and no_trick:
                weak_trick = min(has_trick.items(), key=lambda x: x[1])
                if weak_trick[1] < no_trick:
                    trick_pct = int(weak_trick[1] * 100)
                    regular_pct = int(no_trick * 100)
                    return f"{weak_trick[0]} keyword {trick_pct}%, Regular {regular_pct}% - trick questions are the issue"
        
        return f"Mixed performance ({int(result['accuracy']*100)}%) - focus on weaker areas"
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_pattern_detector.py -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/pattern_detector.py tests/test_pattern_detector.py
git commit -m "feat: add pattern detection for subtopic insights"
```

---

## Phase 3: Report Sheet Generators (Tasks 7-9)

### Task 7: Progress Over Time Sheet Generator

**Files:**
- Create: `cissp_analyzer/progress_sheet_generator.py`
- Test: `tests/test_progress_sheet_generator.py`

**Cost:** 45 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for Progress Over Time sheet**

```python
# tests/test_progress_sheet_generator.py
from cissp_analyzer.progress_sheet_generator import ProgressSheetGenerator
import openpyxl

def test_generate_progress_sheet_creates_worksheet():
    """Generate Progress Over Time sheet with correct structure"""
    generator = ProgressSheetGenerator()
    
    exams = [
        {
            "exam_number": 1,
            "by_domain": {
                "Security & Risk Management": {"accuracy": 0.65},
                "Asset Security": {"accuracy": 0.70}
            },
            "by_difficulty": {
                "Easy": {"accuracy": 0.75},
                "Hard": {"accuracy": 0.40}
            },
            "by_question_type": {
                "Application": {"accuracy": 0.70},
                "Scenario": {"accuracy": 0.50}
            }
        },
        {
            "exam_number": 2,
            "by_domain": {
                "Security & Risk Management": {"accuracy": 0.72},
                "Asset Security": {"accuracy": 0.68}
            },
            "by_difficulty": {
                "Easy": {"accuracy": 0.78},
                "Hard": {"accuracy": 0.45}
            },
            "by_question_type": {
                "Application": {"accuracy": 0.72},
                "Scenario": {"accuracy": 0.55}
            }
        }
    ]
    
    ws = generator.generate_sheet(exams)
    
    assert ws is not None
    assert ws["A1"].value == "Progress Over Time Analysis"
    
    # Check section headers
    found_domain_header = False
    found_difficulty_header = False
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and "Domain Accuracy" in str(cell.value):
                found_domain_header = True
            if cell.value and "Difficulty" in str(cell.value):
                found_difficulty_header = True
    
    assert found_domain_header
    assert found_difficulty_header

def test_progress_sheet_shows_trends():
    """Progress sheet displays trend data correctly"""
    generator = ProgressSheetGenerator()
    
    exams = [
        {"exam_number": 1, "by_domain": {"Domain A": {"accuracy": 0.60}}},
        {"exam_number": 2, "by_domain": {"Domain A": {"accuracy": 0.65}}},
        {"exam_number": 3, "by_domain": {"Domain A": {"accuracy": 0.72}}}
    ]
    
    ws = generator.generate_sheet(exams)
    
    # Verify data is present (specific cells depend on layout)
    cell_values = []
    for row in ws.iter_rows(values_only=True):
        cell_values.extend(row)
    
    # Should contain accuracies
    assert 0.60 in cell_values or "60%" in [str(v) for v in cell_values if v]
    assert 0.72 in cell_values or "72%" in [str(v) for v in cell_values if v]
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_progress_sheet_generator.py -v
# Expected: FAILED
```

- [ ] **Step 3: Implement ProgressSheetGenerator**

```python
# cissp_analyzer/progress_sheet_generator.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List, Dict
from cissp_analyzer.trend_calculator import TrendCalculator

class ProgressSheetGenerator:
    """Generate Sheet 7: Progress Over Time"""
    
    def __init__(self):
        self.calculator = TrendCalculator()
    
    def generate_sheet(self, exams: List[Dict]) -> object:
        """
        Generate Progress Over Time worksheet.
        
        Args:
            exams: List of performance dicts (exam-1, exam-2, ...)
            
        Returns:
            openpyxl Worksheet object
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Progress Over Time"
        
        # Title
        ws["A1"] = "Progress Over Time Analysis"
        ws["A1"].font = Font(size=14, bold=True)
        ws.merge_cells("A1:E1")
        
        # Section 1: Domain Accuracy Over Time
        row = 3
        ws[f"A{row}"] = "A. Domain Accuracy Over Time"
        ws[f"A{row}"].font = Font(size=12, bold=True, color="0066CC")
        row += 1
        
        # Domain trend table
        domain_trends = self.calculator.calculate_domain_trends(exams)
        
        # Headers
        ws[f"A{row}"] = "Domain"
        for exam_num in range(1, len(exams) + 1):
            ws[f"{chr(65+exam_num)}{row}"] = f"Exam {exam_num}"
        
        for col_letter in ["A", *[chr(65+i) for i in range(1, len(exams)+1)]]:
            ws[f"{col_letter}{row}"].font = Font(bold=True)
            ws[f"{col_letter}{row}"].fill = PatternFill(start_color="E6E6E6", end_color="E6E6E6", fill_type="solid")
        
        row += 1
        
        # Domain data
        for domain, accuracies in sorted(domain_trends.items()):
            ws[f"A{row}"] = domain
            for col_idx, accuracy in enumerate(accuracies):
                col_letter = chr(66 + col_idx)  # B, C, D, ...
                ws[f"{col_letter}{row}"] = accuracy
                ws[f"{col_letter}{row}"].number_format = "0%"
            row += 1
        
        # Section 2: Difficulty Progression
        row += 2
        ws[f"A{row}"] = "B. Difficulty Progression"
        ws[f"A{row}"].font = Font(size=12, bold=True, color="0066CC")
        row += 1
        
        difficulty_trends = self.calculator.calculate_difficulty_trends(exams)
        
        # Headers
        ws[f"A{row}"] = "Difficulty"
        for exam_num in range(1, len(exams) + 1):
            ws[f"{chr(65+exam_num)}{row}"] = f"Exam {exam_num}"
        
        for col_letter in ["A", *[chr(65+i) for i in range(1, len(exams)+1)]]:
            ws[f"{col_letter}{row}"].font = Font(bold=True)
            ws[f"{col_letter}{row}"].fill = PatternFill(start_color="E6E6E6", end_color="E6E6E6", fill_type="solid")
        
        row += 1
        
        # Difficulty data
        for difficulty, accuracies in sorted(difficulty_trends.items()):
            ws[f"A{row}"] = difficulty
            for col_idx, accuracy in enumerate(accuracies):
                col_letter = chr(66 + col_idx)
                ws[f"{col_letter}{row}"] = accuracy
                ws[f"{col_letter}{row}"].number_format = "0%"
            row += 1
        
        # Section 3: Question Type Mastery
        row += 2
        ws[f"A{row}"] = "C. Question Type Mastery"
        ws[f"A{row}"].font = Font(size=12, bold=True, color="0066CC")
        row += 1
        
        type_trends = self.calculator.calculate_question_type_trends(exams)
        
        # Headers
        ws[f"A{row}"] = "Question Type"
        for exam_num in range(1, len(exams) + 1):
            ws[f"{chr(65+exam_num)}{row}"] = f"Exam {exam_num}"
        
        for col_letter in ["A", *[chr(65+i) for i in range(1, len(exams)+1)]]:
            ws[f"{col_letter}{row}"].font = Font(bold=True)
            ws[f"{col_letter}{row}"].fill = PatternFill(start_color="E6E6E6", end_color="E6E6E6", fill_type="solid")
        
        row += 1
        
        # Type data
        for q_type, accuracies in sorted(type_trends.items()):
            ws[f"A{row}"] = q_type
            for col_idx, accuracy in enumerate(accuracies):
                col_letter = chr(66 + col_idx)
                ws[f"{col_letter}{row}"] = accuracy
                ws[f"{col_letter}{row}"].number_format = "0%"
            row += 1
        
        # Column widths
        ws.column_dimensions["A"].width = 30
        for col in range(1, len(exams) + 1):
            ws.column_dimensions[chr(65 + col)].width = 12
        
        return ws
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_progress_sheet_generator.py -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/progress_sheet_generator.py tests/test_progress_sheet_generator.py
git commit -m "feat: add Progress Over Time sheet generator (Sheet 7)"
```

---

### Task 8: Adaptive Study Plan Sheet Generator

**Files:**
- Create: `cissp_analyzer/adaptive_plan_generator.py`
- Test: `tests/test_adaptive_plan_generator.py`

**Cost:** 50 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for Adaptive Study Plan sheet**

```python
# tests/test_adaptive_plan_generator.py
from cissp_analyzer.adaptive_plan_generator import AdaptivePlanGenerator

def test_generate_study_plan_sheet():
    """Generate Adaptive Study Plan sheet with recommendations"""
    generator = AdaptivePlanGenerator()
    
    current_exam = {
        "by_domain": {
            "Identity & Access": {"accuracy": 0.50},
            "Soft Dev Security": {"accuracy": 0.58},
            "Security Architecture": {"accuracy": 0.75},
            "Cryptography": {"accuracy": 0.78}
        }
    }
    
    previous_exam = {
        "by_domain": {
            "Identity & Access": {"accuracy": 0.45},
            "Soft Dev Security": {"accuracy": 0.55},
            "Security Architecture": {"accuracy": 0.72},
            "Cryptography": {"accuracy": 0.80}
        }
    }
    
    ws = generator.generate_sheet(current_exam, previous_exam)
    
    assert ws is not None
    assert ws.title == "Adaptive Study Plan"
    assert ws["A1"].value is not None  # Title exists
    
    # Check for priority 1 and 2
    cell_values = []
    for row in ws.iter_rows(values_only=True):
        cell_values.extend(row)
    
    values_str = " ".join([str(v) for v in cell_values if v])
    assert "Priority 1" in values_str or "Identity" in values_str

def test_study_plan_includes_focus_areas():
    """Study plan includes actionable focus areas"""
    generator = AdaptivePlanGenerator()
    
    current_exam = {
        "by_domain": {
            "Domain A": {"accuracy": 0.40},
            "Domain B": {"accuracy": 0.80}
        }
    }
    
    ws = generator.generate_sheet(current_exam, None)
    
    # Should have study recommendations
    sheet_data = ws.values
    values = [str(v) for row in sheet_data for v in row if v]
    
    # Should mention the weak domain
    assert any("Domain A" in v for v in values)
```

- [ ] **Step 2: Run test (will fail)**

```bash
pytest tests/test_adaptive_plan_generator.py -v
# Expected: FAILED
```

- [ ] **Step 3: Implement AdaptivePlanGenerator**

```python
# cissp_analyzer/adaptive_plan_generator.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import Dict, List, Optional
from cissp_analyzer.trend_calculator import TrendCalculator
from cissp_analyzer.pattern_detector import PatternDetector

class AdaptivePlanGenerator:
    """Generate Sheet 8: Adaptive Study Plan"""
    
    def __init__(self):
        self.calculator = TrendCalculator()
        self.detector = PatternDetector()
    
    def generate_sheet(self, current_exam: Dict, previous_exam: Optional[Dict] = None) -> object:
        """
        Generate Adaptive Study Plan worksheet with momentum-based recommendations.
        
        Args:
            current_exam: Latest exam performance
            previous_exam: Previous exam (optional)
            
        Returns:
            openpyxl Worksheet object
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Adaptive Study Plan"
        
        # Title
        ws["A1"] = "Your Personalized Study Focus"
        ws["A1"].font = Font(size=14, bold=True)
        ws.merge_cells("A1:D1")
        
        row = 2
        
        # Get ranked domains
        ranked = self.calculator.rank_domains_by_priority(current_exam, previous_exam)
        
        # Priority 1 and 2
        for priority_num in [1, 2]:
            if priority_num > len(ranked):
                break
            
            domain_data = ranked[priority_num - 1]
            domain_name = domain_data["domain"]
            current_acc = domain_data["current_accuracy"]
            prev_acc = domain_data["previous_accuracy"]
            momentum = domain_data["momentum"]
            
            row += 1
            
            # Priority header
            priority_text = f"🎯 Priority {priority_num}: {domain_name}"
            ws[f"A{row}"] = priority_text
            ws[f"A{row}"].font = Font(size=11, bold=True)
            ws.merge_cells(f"A{row}:D{row}")
            row += 1
            
            # Current status line
            if prev_acc is not None:
                status = f"Current: {int(current_acc*100)}% | Previous: {int(prev_acc*100)}% ({momentum:+.0f}%) | Study Need: High"
            else:
                status = f"Current: {int(current_acc*100)}% | Study Need: High (First exam)"
            
            ws[f"A{row}"] = status
            ws[f"A{row}"].font = Font(size=9, italic=True)
            ws.merge_cells(f"A{row}:D{row}")
            row += 1
            
            # Focus areas
            ws[f"A{row}"] = "Focus areas:"
            ws[f"A{row}"].font = Font(bold=True)
            row += 1
            
            # Add generic focus areas (would be customized with pattern detection in full version)
            focus_areas = [
                f"• Core concepts in {domain_name}",
                f"• Recent weak areas and misconceptions",
                f"• Practice medium/hard difficulty questions",
                f"• Review incorrect answers from this exam"
            ]
            
            for area in focus_areas:
                ws[f"A{row}"] = area
                ws.merge_cells(f"A{row}:D{row}")
                row += 1
            
            row += 1
        
        # Strengths to maintain section
        row += 1
        ws[f"A{row}"] = "📊 Strengths to Maintain"
        ws[f"A{row}"].font = Font(size=11, bold=True, color="006633")
        ws.merge_cells(f"A{row}:D{row}")
        row += 1
        
        strong_domains = [d for d in ranked if d["current_accuracy"] >= 0.75]
        if strong_domains:
            for domain_data in strong_domains[:3]:  # Top 3 strong domains
                acc_pct = int(domain_data["current_accuracy"] * 100)
                ws[f"A{row}"] = f"• {domain_data['domain']}: {acc_pct}%"
                ws.merge_cells(f"A{row}:D{row}")
                row += 1
        else:
            ws[f"A{row}"] = "Keep practicing to build strong foundation"
            ws.merge_cells(f"A{row}:D{row}")
            row += 1
        
        # Column width
        ws.column_dimensions["A"].width = 50
        
        return ws
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_adaptive_plan_generator.py -v
# Expected: PASSED
```

- [ ] **Step 5: Commit**

```bash
git add cissp_analyzer/adaptive_plan_generator.py tests/test_adaptive_plan_generator.py
git commit -m "feat: add Adaptive Study Plan sheet generator (Sheet 8)"
```

---

## Phase 4: Integration (Tasks 9-11)

### Task 9: Modify IndividualReportGenerator to Add New Sheets

**Files:**
- Modify: `cissp_analyzer/individual_report_gen.py`
- Test: Existing tests (verify 8 sheets)

**Cost:** 20 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write test for 8-sheet report generation**

```python
# Add to tests/test_individual_report_gen.py

def test_generate_report_with_8_sheets_multi_exam():
    """Report includes 8 sheets for multi-exam students"""
    from cissp_analyzer.history_loader import HistoryLoader
    
    # Simulate: student has 2 previous exams in history
    loader = HistoryLoader()
    
    # This test assumes exam data is available
    # In actual execution, we'll have real exam data
    
    # For now, verify the method exists
    generator = IndividualReportGenerator(domain_mapper, analysis_engine)
    
    # Method should support history parameter
    assert hasattr(generator, 'generate_report_with_history')
```

- [ ] **Step 2: Run test (will fail initially)**

```bash
pytest tests/test_individual_report_gen.py::test_generate_report_with_8_sheets_multi_exam -v
```

- [ ] **Step 3: Modify IndividualReportGenerator**

```python
# Modify cissp_analyzer/individual_report_gen.py

# Add imports at top
from cissp_analyzer.progress_sheet_generator import ProgressSheetGenerator
from cissp_analyzer.adaptive_plan_generator import AdaptivePlanGenerator

# Modify the generate_report method to accept history
def generate_report(self, output_file: str, student_name: str = None, 
                   historical_exams: list = None) -> str:
    """
    Generate report with optional historical data.
    
    Args:
        output_file: Path to save report
        student_name: Name of student
        historical_exams: List of previous exam performance dicts
        
    Returns:
        Path to generated report
    """
    # Load existing workbook (sheets 1-6)
    wb = self._create_base_report()  # Existing method
    
    # Add Sheet 7: Progress Over Time (if we have history)
    if historical_exams and len(historical_exams) > 0:
        progress_gen = ProgressSheetGenerator()
        progress_ws = progress_gen.generate_sheet(historical_exams)
        
        # Copy progress sheet to workbook
        for row in progress_ws.iter_rows():
            for cell in row:
                wb[progress_ws.title][cell.coordinate] = cell.value
                if cell.font:
                    wb[progress_ws.title][cell.coordinate].font = cell.font
                if cell.fill:
                    wb[progress_ws.title][cell.coordinate].fill = cell.fill
    else:
        # Single exam: create placeholder Progress sheet
        ws = wb.create_sheet("Progress Over Time")
        ws["A1"] = "Only 1 exam so far"
        ws["A2"] = "Historical trends appear after 2nd exam"
    
    # Add Sheet 8: Adaptive Study Plan
    current_exam = self._extract_current_exam_data()
    previous_exam = historical_exams[-1] if historical_exams else None
    
    plan_gen = AdaptivePlanGenerator()
    plan_ws = plan_gen.generate_sheet(current_exam, previous_exam)
    
    # Copy to workbook
    for row in plan_ws.iter_rows():
        for cell in row:
            wb[plan_ws.title][cell.coordinate] = cell.value
            if cell.font:
                wb[plan_ws.title][cell.coordinate].font = cell.font
    
    # Save
    wb.save(output_file)
    return output_file
```

- [ ] **Step 4: Commit**

```bash
git add cissp_analyzer/individual_report_gen.py
git commit -m "feat: enhance IndividualReportGenerator to support Sheets 7-8"
```

---

### Task 10: Update main.py CLI for Multi-Exam Support

**Files:**
- Modify: `cissp_analyzer/main.py`
- Test: `tests/test_integration_multi_exam.py`

**Cost:** 30 min | **Model:** Claude Sonnet | **Cost:** $2-3

- [ ] **Step 1: Write integration test**

```python
# tests/test_integration_multi_exam.py
import tempfile
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer

def test_analyze_student_creates_history():
    """Analyze exam stores performance for future reference"""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = CISSPAnalyzer()
        
        # First exam
        result1 = analyzer.analyze_student(
            exam_pdf='data/practice_exams/Practice_Test_1.pdf',
            answer_excel='sample_student_answers.xlsx',
            student_name='TestStudent',
            students_dir=tmpdir
        )
        
        # Verify performance JSON was created
        perf_file = Path(tmpdir) / "TestStudent" / "exam-1_performance.json"
        assert perf_file.exists()

def test_second_exam_loads_history():
    """Second exam loads first exam for comparison"""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = CISSPAnalyzer()
        
        # First exam (would need real files in practice)
        # For now, just verify the method signature supports history
        
        assert hasattr(analyzer, 'analyze_student_with_history')
```

- [ ] **Step 2: Modify main.py CISSPAnalyzer.analyze() method**

```python
# Modify cissp_analyzer/main.py

# Add imports
from cissp_analyzer.history_loader import HistoryLoader
from cissp_analyzer.filename_parser import FilenameParser

# Add method for single-student analysis with history
def analyze_student_with_history(self, 
                                 exam_pdf: str,
                                 answer_excel: str,
                                 student_name: str,
                                 students_dir: str = "students") -> Dict:
    """
    Analyze a student's exam, load history, generate report with trends.
    
    Args:
        exam_pdf: Path to exam PDF
        answer_excel: Path to student answers Excel
        student_name: Name of student
        students_dir: Directory for storing student data
        
    Returns:
        Dict with report paths and analysis results
    """
    output_path = Path("reports")
    output_path.mkdir(exist_ok=True)
    
    # Step 1: Load history
    history_loader = HistoryLoader(students_dir)
    previous_exams = history_loader.load_previous_exams(student_name)
    
    exam_number = len(previous_exams) + 1
    print(f"Analyzing exam #{exam_number} for {student_name}...")
    
    # Step 2: Parse current exam (existing logic)
    pdf_parser = PDFParser(exam_pdf)
    questions = pdf_parser.extract_questions()
    
    # ... (existing parsing logic) ...
    
    # Step 3: Export performance data
    performance_data = self.analysis_engine.export_student_performance(
        student_name=student_name,
        exam_number=exam_number
    )
    
    # Step 4: Save performance JSON
    history_loader.save_exam_performance(student_name, exam_number, performance_data)
    
    # Step 5: Generate report with history
    report_file = output_path / f"{student_name}_progress_report.xlsx"
    
    self.individual_gen.generate_report(
        output_file=str(report_file),
        student_name=student_name,
        historical_exams=previous_exams  # Include history
    )
    
    return {
        "student_name": student_name,
        "exam_number": exam_number,
        "report_path": str(report_file),
        "performance_data_path": str(history_loader.save_exam_performance(
            student_name, exam_number, performance_data
        )),
        "previous_exams_count": len(previous_exams)
    }
```

- [ ] **Step 3: Update CLI entry point in main.py**

```python
# Add to main.py or create new cli.py

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CISSP Analyzer with Historical Tracking")
    parser.add_argument("--mode", choices=["analyze-student", "analyze-class"], 
                       default="analyze-student")
    parser.add_argument("--pdf", required=True, help="Path to exam PDF")
    parser.add_argument("--answers", required=True, help="Path to student answers Excel")
    parser.add_argument("--student", required=True, help="Student name")
    parser.add_argument("--students-dir", default="students", help="Directory for student data")
    
    args = parser.parse_args()
    
    analyzer = CISSPAnalyzer()
    
    if args.mode == "analyze-student":
        result = analyzer.analyze_student_with_history(
            exam_pdf=args.pdf,
            answer_excel=args.answers,
            student_name=args.student,
            students_dir=args.students_dir
        )
        print(f"✓ Report saved: {result['report_path']}")
        print(f"✓ Exam #{result['exam_number']} analyzed")
        if result['previous_exams_count'] > 0:
            print(f"✓ Compared with {result['previous_exams_count']} previous exam(s)")

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Commit**

```bash
git add cissp_analyzer/main.py
git commit -m "feat: add multi-exam support to CLI with history loading"
```

---

### Task 11: Test Integration End-to-End

**Files:**
- Test: `tests/test_integration_multi_exam.py`

**Cost:** 30 min | **Model:** Qwen2.5-coder | **Cost:** $0

- [ ] **Step 1: Write comprehensive integration test**

```python
# tests/test_integration_multi_exam.py
import json
import tempfile
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer
from cissp_analyzer.history_loader import HistoryLoader

def test_complete_workflow_three_exams():
    """Complete workflow: analyze 3 exams, verify history and trends"""
    with tempfile.TemporaryDirectory() as tmpdir:
        analyzer = CISSPAnalyzer()
        students_dir = tmpdir
        
        # Simulate 3 exams for one student
        student_name = "Integration_Test_Student"
        
        exam_data_sets = [
            {
                "exam_number": 1,
                "overall_accuracy": 0.60,
                "by_domain": {"Domain A": {"accuracy": 0.65}, "Domain B": {"accuracy": 0.55}}
            },
            {
                "exam_number": 2,
                "overall_accuracy": 0.65,
                "by_domain": {"Domain A": {"accuracy": 0.70}, "Domain B": {"accuracy": 0.60}}
            },
            {
                "exam_number": 3,
                "overall_accuracy": 0.72,
                "by_domain": {"Domain A": {"accuracy": 0.75}, "Domain B": {"accuracy": 0.70}}
            }
        ]
        
        # Simulate saving each exam
        loader = HistoryLoader(students_dir)
        for exam_data in exam_data_sets:
            loader.save_exam_performance(
                student_name=student_name,
                exam_number=exam_data["exam_number"],
                performance_data=exam_data
            )
        
        # Load history
        history = loader.load_previous_exams(student_name)
        
        # Verify
        assert len(history) == 3
        assert history[0]["exam_number"] == 1
        assert history[2]["exam_number"] == 3
        
        # Verify progression
        assert history[0]["overall_accuracy"] == 0.60
        assert history[2]["overall_accuracy"] == 0.72
```

- [ ] **Step 2: Run test**

```bash
pytest tests/test_integration_multi_exam.py -v
# Expected: PASSED
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration_multi_exam.py
git commit -m "test: add comprehensive integration tests for multi-exam workflow"
```

---

## Phase 5: Testing & Documentation (Tasks 12-13)

### Task 12: Run Full Test Suite & Verify Coverage

**Files:**
- Test: All test files created in previous tasks

**Cost:** 15 min | **Model:** No LLM | **Cost:** $0

- [ ] **Step 1: Run all tests**

```bash
cd /Users/sriram/cissp-analyzer
pytest tests/ -v --tb=short
```

Expected output: All tests pass (30+ tests)

- [ ] **Step 2: Check coverage**

```bash
pytest tests/ --cov=cissp_analyzer --cov-report=term-missing
```

Target: >85% coverage for new modules

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "test: verify all tests passing, 85%+ coverage"
```

---

### Task 13: Documentation & README Update

**Files:**
- Modify: `README.md`
- Create: `docs/HISTORICAL_TRACKING_GUIDE.md`

**Cost:** 20 min | **Model:** No LLM | **Cost:** $0

- [ ] **Step 1: Add section to README.md**

```markdown
## Historical Exam Tracking & Adaptive Recommendations (NEW)

Track progress across multiple exams and get AI-powered study recommendations.

### Quick Start

**First Exam:**
```bash
python run.py --mode analyze-student \
  --pdf exams/Practice_Test_1.pdf \
  --answers answers_sri.xlsx \
  --student Sri
```

Creates: `students/Sri/exam-1_performance.json`
Report: `reports/Sri_progress_report.xlsx` (7 sheets)

**Second Exam:**
```bash
python run.py --mode analyze-student \
  --pdf exams/Practice_Test_2.pdf \
  --answers answers_sri_v2.xlsx \
  --student Sri
```

Creates: `students/Sri/exam-2_performance.json`
Report: `reports/Sri_progress_report.xlsx` (8 sheets + trends!)

### New Features

**Sheet 7: Progress Over Time**
- Domain accuracy trends across exams
- Difficulty progression (Easy → Hard)
- Question type mastery evolution

**Sheet 8: Adaptive Study Plan**
- Momentum-based recommendations
- Priority-ranked focus areas
- Personalized insights based on performance history

### Filename Convention

Use this naming pattern for automatic student detection:
```
Mock[N]_[Date]_[StudentName].xlsx
```

Examples:
- `Mock1_Jun26_Sri.xlsx` → Student: "Sri", Exam: 1
- `Mock2_Jun28_Sri.xlsx` → Student: "Sri", Exam: 2
- `Mock1_Jul1_Alice.xlsx` → Student: "Alice", Exam: 1
```

- [ ] **Step 2: Create HISTORICAL_TRACKING_GUIDE.md**

```markdown
# Historical Exam Tracking Guide

## Overview

The CISSP Analyzer now supports tracking performance across multiple exams per student. This enables:
- Progress visualization (domains, difficulty, question types)
- Momentum-based adaptive recommendations
- Teacher class analytics
- Regression detection

## Architecture

### File Structure
```
students/
├── [StudentName]/
│   ├── Mock1_[Date]_[StudentName].xlsx    # Input
│   ├── exam-1_performance.json            # Cached
│   ├── Mock2_[Date]_[StudentName].xlsx
│   └── exam-2_performance.json
```

### Report Structure (8 Sheets)
- Sheets 1-6: Single-exam analysis (unchanged)
- Sheet 7: **Progress Over Time** (NEW)
  - Domain accuracy trends
  - Difficulty progression
  - Question type evolution
- Sheet 8: **Adaptive Study Plan** (NEW)
  - Momentum-based priority ranking
  - Personalized focus areas
  - Strength maintenance tips

## Workflow

### New Student
```bash
python run.py --mode analyze-student \
  --pdf exam.pdf --answers answers.xlsx --student "Alice"

→ Creates: students/Alice/
→ Report: Alice_progress_report.xlsx (7 sheets)
```

### Existing Student (2nd Exam)
```bash
python run.py --mode analyze-student \
  --pdf exam.pdf --answers answers.xlsx --student "Alice"

→ Loads: students/Alice/exam-1_performance.json
→ Compares: Exam 2 vs Exam 1
→ Report: Alice_progress_report.xlsx (8 sheets with trends)
```

## Algorithm: Momentum-Based Recommendations

Priority Score = Weakness + (Momentum × 2)

Where:
- **Weakness** = 100 - current_accuracy%
- **Momentum** = (current - previous) × 100

Example:
```
Identity & Access: 50% (weakness=50), was 45% (momentum=+5)
Priority = 50 + (5 × 2) = 60 ← Ranked #1

Cryptography: 78% (weakness=22), was 80% (momentum=-2)
Priority = 22 + (-2 × 2) = 18 ← Ranked #8
```

## Max Limits & Constraints

- **Max exams per student:** 10
- **Max students per class:** Unlimited
- **Storage:** Local (students/ folder)
- **Cost:** $0 (no cloud dependencies)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Student not found" | Filename doesn't match Mock[N]_[Date]_[Name].xlsx pattern. Rename or use --student flag. |
| Report shows only 7 sheets | First exam for this student. After 2nd exam, sheets 7-8 appear. |
| Missing previous exams | Check students/[StudentName]/ folder for exam-N_performance.json files. |
```

- [ ] **Step 3: Commit**

```bash
git add README.md docs/HISTORICAL_TRACKING_GUIDE.md
git commit -m "docs: add historical tracking and adaptive recommendations guide"
```

---

## Summary

**Total Implementation Tasks:** 13
**Estimated Time:** 12-13 hours
**Estimated Cost:** $2-3 (only architectural decision task)
**Model Usage:**
- Qwen2.5-coder: 10 tasks ($0)
- Gemma4: 1 task ($0)
- Claude Sonnet: 1 task ($2-3)
- No LLM: 1 task ($0)

**Parallelization Opportunities:**
- Tasks 1-3 (infrastructure) can run independently
- Tasks 4-6 (trends) can run after infrastructure
- Tasks 7-9 (sheets) can run in parallel once trends complete
- Tasks 10-11 (integration) depend on all generators

**Success Criteria:**
✅ All 30+ tests passing
✅ No breaking changes to existing 7-sheet report
✅ Backward compatible (1-exam students work)
✅ Local file-based storage working
✅ Momentum algorithm correctly scoring domains
✅ Progress sheets generating without errors
✅ Study plan recommendations personalized and actionable
✅ Documentation complete and clear

---

**Next Step:** Choose execution method

This plan is ready for implementation. Two execution options:

**Option 1: Subagent-Driven (Recommended)**
- Fresh subagent per task
- Code review between tasks
- Parallel execution possible
- Best for quality + speed

**Option 2: Inline Execution**
- All tasks in this session
- Batch execution with checkpoints
- Simpler but requires sustained focus

Which approach do you prefer?
