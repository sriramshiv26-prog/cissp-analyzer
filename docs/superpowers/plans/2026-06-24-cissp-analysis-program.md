# CISSP Analysis Program Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone Python program that automatically analyzes CISSP exam PDFs and student answers, generating 9 comprehensive Excel reports (individual + class analysis).

**Architecture:** Pipeline architecture with modular components: PDF extraction → Excel parsing → domain mapping → multi-dimensional analysis → Excel report generation. Each module is independently testable. Domain mapping is loaded from authoritative JSON file once at startup.

**Tech Stack:** Python 3.11+, pandas, openpyxl, pypdf, pytest

---

## File Structure

```
cissp-analyzer/
├── cissp_analyzer/
│   ├── __init__.py
│   ├── models.py                    # Data classes (Question, StudentAnswer, Analysis)
│   ├── domain_mapper.py             # Load/access question_domain_mapping.json
│   ├── pdf_parser.py                # Extract Q&A from PDF
│   ├── excel_parser.py              # Parse student answer Excel files
│   ├── analysis_engine.py           # Core multi-dimensional analysis
│   ├── individual_report_gen.py     # Generate 5 individual reports
│   ├── class_report_gen.py          # Generate 4 class-level reports
│   └── main.py                      # Orchestrator
├── tests/
│   ├── test_domain_mapper.py
│   ├── test_pdf_parser.py
│   ├── test_excel_parser.py
│   ├── test_analysis_engine.py
│   ├── test_individual_report_gen.py
│   ├── test_class_report_gen.py
│   └── test_integration.py
├── data/
│   └── question_domain_mapping.json # Authoritative mapping (copy from /tmp/)
├── requirements.txt
├── README.md
└── run.py                           # Entry point script
```

---

### Task 1: Project Setup & Domain Mapper

**Files:**
- Create: `cissp_analyzer/__init__.py`
- Create: `cissp_analyzer/models.py`
- Create: `cissp_analyzer/domain_mapper.py`
- Create: `data/question_domain_mapping.json` (copy from /tmp/)
- Create: `requirements.txt`
- Create: `tests/test_domain_mapper.py`

- [ ] **Step 1: Create project structure and requirements file**

```bash
mkdir -p cissp_analyzer tests data
touch cissp_analyzer/__init__.py
```

**requirements.txt:**
```
pandas==2.2.1
openpyxl==3.1.2
pypdf==4.1.0
python-dotenv==1.0.0
pytest==7.4.3
```

```bash
pip install -r requirements.txt
```

- [ ] **Step 2: Write failing tests for domain mapper**

Create `tests/test_domain_mapper.py`:

```python
import json
import pytest
from pathlib import Path
from cissp_analyzer.domain_mapper import DomainMapper

@pytest.fixture
def domain_mapper():
    return DomainMapper(mapping_file='data/question_domain_mapping.json')

def test_load_mapping(domain_mapper):
    """Test that mapping loads correctly"""
    assert domain_mapper.mapping is not None
    assert len(domain_mapper.mapping) > 0

def test_get_question_metadata(domain_mapper):
    """Test getting metadata for a specific question"""
    meta = domain_mapper.get_question_metadata(31)
    assert meta is not None
    assert 'domain' in meta
    assert 'topic' in meta
    assert 'subtopic' in meta
    assert 'difficulty' in meta
    assert 'question_type' in meta
    assert 'exam_trick' in meta

def test_question_31_metadata(domain_mapper):
    """Test that Q31 is correctly mapped to Backup/Recovery"""
    meta = domain_mapper.get_question_metadata(31)
    assert meta['domain'] == 'Domain 7: Security Operations'
    assert 'Backup' in meta['topic'] or 'Recovery' in meta['topic']
    assert meta['difficulty'] in ['Easy', 'Medium', 'Hard']

def test_question_58_metadata(domain_mapper):
    """Test that Q58 is correctly mapped to Kerberos"""
    meta = domain_mapper.get_question_metadata(58)
    assert meta['domain'] == 'Domain 5: Identity and Access Management'
    assert 'Kerberos' in meta['topic']

def test_all_questions_have_metadata(domain_mapper):
    """Test that all 125 questions have mapping"""
    for qnum in range(1, 126):
        meta = domain_mapper.get_question_metadata(qnum)
        assert meta is not None, f"Question {qnum} missing metadata"
        assert all(k in meta for k in ['domain', 'topic', 'subtopic', 'difficulty', 'question_type', 'exam_trick'])

def test_invalid_question_returns_none(domain_mapper):
    """Test that invalid question numbers return None"""
    assert domain_mapper.get_question_metadata(999) is None
```

Run: `pytest tests/test_domain_mapper.py -v`
Expected: FAIL (module doesn't exist yet)

- [ ] **Step 3: Create data classes in models.py**

Create `cissp_analyzer/models.py`:

```python
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
    question_type: str  # Definition, Scenario, Comparison, Exception, Sequence, Managerial
    exam_trick: str  # Negation, Superlative, Absolute, Scenario, Trap
    
@dataclass
class StudentAnswer:
    student_name: str
    question_number: int
    selected_answer: str
    is_correct: bool
    
@dataclass
class QuestionAnalysis:
    question_number: int
    students_correct: int
    students_wrong: int
    success_rate: float
    common_mistakes: list  # Most selected wrong answers
    
@dataclass
class StudentPerformance:
    student_name: str
    total_questions: int
    correct_count: int
    wrong_count: int
    score_percentage: float
    by_domain: dict  # domain -> {correct, wrong, %}
    by_topic: dict  # topic -> {correct, wrong, %}
    by_difficulty: dict  # {Easy, Medium, Hard} -> {correct, wrong, %}
    by_question_type: dict  # type -> {correct, wrong, %}
    by_exam_trick: dict  # trick -> {correct, wrong, %}
    wrong_question_ids: list  # Which questions they got wrong
```

- [ ] **Step 4: Create DomainMapper class**

Create `cissp_analyzer/domain_mapper.py`:

```python
import json
from pathlib import Path
from typing import Optional, Dict

class DomainMapper:
    """Loads and provides access to question_domain_mapping.json"""
    
    def __init__(self, mapping_file: str = 'data/question_domain_mapping.json'):
        self.mapping_file = Path(mapping_file)
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict:
        """Load the authoritative question mapping from JSON"""
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
        
        with open(self.mapping_file, 'r') as f:
            return json.load(f)
    
    def get_question_metadata(self, question_number: int) -> Optional[Dict]:
        """Get metadata for a specific question by number"""
        key = str(question_number)
        return self.mapping.get(key)
    
    def get_all_questions(self) -> Dict:
        """Get all question mappings"""
        return self.mapping
    
    def get_questions_by_domain(self, domain: str) -> list:
        """Get all questions in a specific domain"""
        return [
            (int(qnum), meta) 
            for qnum, meta in self.mapping.items() 
            if meta.get('domain') == domain
        ]
    
    def get_questions_by_topic(self, topic: str) -> list:
        """Get all questions for a specific topic"""
        return [
            (int(qnum), meta) 
            for qnum, meta in self.mapping.items() 
            if meta.get('topic') == topic
        ]
```

- [ ] **Step 5: Copy authoritative mapping file**

```bash
cp /tmp/question_domain_mapping.json data/question_domain_mapping.json
```

- [ ] **Step 6: Run tests to verify domain mapper works**

Run: `pytest tests/test_domain_mapper.py -v`
Expected: All tests PASS

- [ ] **Step 7: Commit project foundation**

```bash
git add cissp_analyzer/__init__.py cissp_analyzer/models.py cissp_analyzer/domain_mapper.py data/question_domain_mapping.json requirements.txt tests/test_domain_mapper.py
git commit -m "feat: Initialize CISSP analyzer project with domain mapper"
```

---

### Task 2: PDF Parser

**Files:**
- Create: `cissp_analyzer/pdf_parser.py`
- Create: `tests/test_pdf_parser.py`

- [ ] **Step 1: Write failing tests for PDF parser**

Create `tests/test_pdf_parser.py`:

```python
import pytest
from pathlib import Path
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.models import Question

@pytest.fixture
def pdf_path():
    return Path('/Users/sriram/Downloads/June 21st Test 1.Updated.pdf')

@pytest.fixture
def parser(pdf_path):
    if pdf_path.exists():
        return PDFParser(str(pdf_path))
    pytest.skip("Test PDF not found")

def test_pdf_loads(parser):
    """Test that PDF loads without error"""
    assert parser.pdf_path is not None
    assert parser.pages is not None
    assert len(parser.pages) > 0

def test_extract_questions(parser):
    """Test that questions are extracted"""
    questions = parser.extract_questions()
    assert questions is not None
    assert len(questions) == 125, f"Expected 125 questions, got {len(questions)}"

def test_question_structure(parser):
    """Test that extracted questions have correct structure"""
    questions = parser.extract_questions()
    q1 = questions[0]
    assert q1['number'] == 1
    assert 'text' in q1
    assert len(q1['text']) > 0
    assert 'options' in q1
    assert len(q1['options']) > 0

def test_extract_specific_question(parser):
    """Test extracting a specific question"""
    questions = parser.extract_questions()
    q31 = next((q for q in questions if q['number'] == 31), None)
    assert q31 is not None
    assert 'Backup' in q31['text'] or 'Recovery' in q31['text']

def test_all_questions_numbered(parser):
    """Test that all questions are numbered 1-125"""
    questions = parser.extract_questions()
    numbers = sorted([q['number'] for q in questions])
    assert numbers == list(range(1, 126))
```

Run: `pytest tests/test_pdf_parser.py -v`
Expected: FAIL (module doesn't exist)

- [ ] **Step 2: Implement PDF parser**

Create `cissp_analyzer/pdf_parser.py`:

```python
import re
from pathlib import Path
from pypdf import PdfReader
from typing import List, Dict

class PDFParser:
    """Extracts questions and answers from CISSP exam PDF"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        self.reader = PdfReader(str(self.pdf_path))
        self.pages = self.reader.pages
    
    def extract_questions(self) -> List[Dict]:
        """Extract all questions from the PDF"""
        questions = []
        current_question = None
        all_text = ""
        
        # Extract all text from PDF
        for page in self.pages:
            all_text += page.extract_text()
        
        # Split by question pattern (Q1:, Q2:, etc.)
        # Pattern: "Q\d+:" followed by question text
        question_blocks = re.split(r'(?=Q\d+:)', all_text)
        
        for block in question_blocks:
            if not block.strip():
                continue
            
            # Extract question number
            q_match = re.match(r'Q(\d+):', block)
            if not q_match:
                continue
            
            q_number = int(q_match.group(1))
            
            # Extract question text (between Q number and first option)
            text_match = re.search(r'Q\d+:\s*(.+?)(?=A\)|B\)|C\)|D\))', block, re.DOTALL)
            if not text_match:
                continue
            
            q_text = text_match.group(1).strip()
            
            # Extract options (A, B, C, D)
            options = {}
            for option_letter in ['A', 'B', 'C', 'D']:
                pattern = f'{option_letter}\\)\\s*(.+?)(?=\\n|[A-D]\\)|$)'
                option_match = re.search(pattern, block, re.DOTALL)
                if option_match:
                    options[option_letter] = option_match.group(1).strip()
            
            if options:
                questions.append({
                    'number': q_number,
                    'text': q_text,
                    'options': options
                })
        
        return sorted(questions, key=lambda x: x['number'])
```

- [ ] **Step 3: Run tests to verify PDF parser works**

Run: `pytest tests/test_pdf_parser.py::test_pdf_loads -v`
Expected: PASS (if PDF exists)

Run: `pytest tests/test_pdf_parser.py::test_extract_questions -v`
Expected: PASS with 125 questions extracted

- [ ] **Step 4: Commit PDF parser**

```bash
git add cissp_analyzer/pdf_parser.py tests/test_pdf_parser.py
git commit -m "feat: Add PDF parser for question extraction"
```

---

### Task 3: Excel Parser

**Files:**
- Create: `cissp_analyzer/excel_parser.py`
- Create: `tests/test_excel_parser.py`

- [ ] **Step 1: Write failing tests for Excel parser**

Create `tests/test_excel_parser.py`:

```python
import pytest
import pandas as pd
from pathlib import Path
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.models import StudentAnswer

@pytest.fixture
def sample_answer_file(tmp_path):
    """Create a sample answer Excel file for testing"""
    data = {
        'Question': [1, 2, 3, 4, 5],
        'Student_Answer': ['A', 'B', 'A', 'D', 'C']
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_answers.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

@pytest.fixture
def parser(sample_answer_file):
    return ExcelParser()

def test_parse_student_answers(parser, sample_answer_file):
    """Test parsing student answer sheet"""
    answers = parser.parse_answers(str(sample_answer_file), "Student1")
    assert len(answers) == 5
    assert all(isinstance(a, StudentAnswer) for a in answers)

def test_student_answer_structure(parser, sample_answer_file):
    """Test that student answers have correct structure"""
    answers = parser.parse_answers(str(sample_answer_file), "Student1")
    answer = answers[0]
    assert answer.student_name == "Student1"
    assert answer.question_number == 1
    assert answer.selected_answer == 'A'

def test_parse_multiple_students(parser, tmp_path):
    """Test parsing answers from multiple students"""
    data = {
        'Question': [1, 2, 3],
        'Senthil': ['A', 'B', 'A'],
        'Kapil': ['B', 'A', 'D'],
        'Praveena': ['A', 'C', 'A']
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "multi_student.xlsx"
    df.to_excel(file_path, index=False)
    
    for student_name in ['Senthil', 'Kapil', 'Praveena']:
        answers = parser.parse_answers(str(file_path), student_name)
        assert len(answers) == 3
        assert all(a.student_name == student_name for a in answers)
```

Run: `pytest tests/test_excel_parser.py -v`
Expected: FAIL (module doesn't exist)

- [ ] **Step 2: Implement Excel parser**

Create `cissp_analyzer/excel_parser.py`:

```python
import pandas as pd
from pathlib import Path
from typing import List, Dict
from cissp_analyzer.models import StudentAnswer

class ExcelParser:
    """Parses student answer Excel files"""
    
    def parse_answers(self, excel_file: str, student_name: str) -> List[StudentAnswer]:
        """
        Parse answers from Excel file for a specific student
        
        Expected format:
        - Column 'Question': Question numbers (1-125)
        - Column '<StudentName>': Their answers (A, B, C, D)
        """
        if not Path(excel_file).exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file}")
        
        df = pd.read_excel(excel_file)
        
        # Verify required columns
        if 'Question' not in df.columns:
            raise ValueError("Excel must have 'Question' column")
        
        if student_name not in df.columns:
            raise ValueError(f"Excel must have column for student '{student_name}'")
        
        answers = []
        for _, row in df.iterrows():
            q_number = int(row['Question'])
            selected_answer = row[student_name]
            
            # Handle NaN or empty answers (unanswered questions)
            if pd.isna(selected_answer):
                selected_answer = None
            else:
                selected_answer = str(selected_answer).strip().upper()
            
            answer = StudentAnswer(
                student_name=student_name,
                question_number=q_number,
                selected_answer=selected_answer,
                is_correct=False  # Will be set by analysis engine
            )
            answers.append(answer)
        
        return sorted(answers, key=lambda x: x.question_number)
    
    def parse_all_students(self, excel_file: str, student_names: List[str]) -> Dict[str, List[StudentAnswer]]:
        """Parse answers for multiple students from one file"""
        result = {}
        for student_name in student_names:
            result[student_name] = self.parse_answers(excel_file, student_name)
        return result
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_excel_parser.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit Excel parser**

```bash
git add cissp_analyzer/excel_parser.py tests/test_excel_parser.py
git commit -m "feat: Add Excel parser for student answer sheets"
```

---

### Task 4: Analysis Engine (Core Logic)

**Files:**
- Create: `cissp_analyzer/analysis_engine.py`
- Create: `tests/test_analysis_engine.py`

- [ ] **Step 1: Write failing tests for analysis engine**

Create `tests/test_analysis_engine.py`:

```python
import pytest
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentAnswer, StudentPerformance

@pytest.fixture
def mapper():
    return DomainMapper(mapping_file='data/question_domain_mapping.json')

@pytest.fixture
def engine(mapper):
    return AnalysisEngine(mapper)

def test_evaluate_answers_senthil(engine):
    """Test evaluation for Senthil (should be ~69%)"""
    answers = []
    for q in range(1, 87):
        answers.append(StudentAnswer("Senthil", q, "A", False))
    for q in range(87, 126):
        answers.append(StudentAnswer("Senthil", q, "B", False))
    
    performance = engine.evaluate_student(answers, "Senthil")
    assert performance.student_name == "Senthil"
    assert performance.correct_count == 86
    assert 65 < performance.score_percentage < 75

def test_performance_has_all_dimensions(engine):
    """Test that performance analysis includes all dimensions"""
    answers = [StudentAnswer("Test", 1, "A", False) for _ in range(125)]
    performance = engine.evaluate_student(answers, "Test")
    
    assert hasattr(performance, 'by_domain')
    assert hasattr(performance, 'by_topic')
    assert hasattr(performance, 'by_difficulty')
    assert hasattr(performance, 'by_question_type')
    assert hasattr(performance, 'by_exam_trick')
    assert isinstance(performance.by_domain, dict)
    assert isinstance(performance.by_topic, dict)

def test_domain_breakdown(engine):
    """Test that domain breakdown includes all 8 domains"""
    answers = [StudentAnswer("Test", q, "A", False) for q in range(1, 126)]
    performance = engine.evaluate_student(answers, "Test")
    assert len(performance.by_domain) > 0

def test_wrong_question_tracking(engine):
    """Test that wrong questions are tracked"""
    answers = []
    for q in range(1, 51):
        answers.append(StudentAnswer("Test", q, "A", False))
    for q in range(51, 126):
        answers.append(StudentAnswer("Test", q, "B", False))
    
    performance = engine.evaluate_student(answers, "Test")
    assert len(performance.wrong_question_ids) > 0
```

Run: `pytest tests/test_analysis_engine.py -v`
Expected: FAIL (module doesn't exist)

- [ ] **Step 2: Implement analysis engine**

Create `cissp_analyzer/analysis_engine.py`:

```python
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
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_analysis_engine.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit analysis engine**

```bash
git add cissp_analyzer/analysis_engine.py tests/test_analysis_engine.py
git commit -m "feat: Add core multi-dimensional analysis engine"
```

---

### Task 5: Individual Report Generator

**Files:**
- Create: `cissp_analyzer/individual_report_gen.py`
- Create: `tests/test_individual_report_gen.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_individual_report_gen.py`:

```python
import pytest
from pathlib import Path
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentPerformance

@pytest.fixture
def generator():
    mapper = DomainMapper(mapping_file='data/question_domain_mapping.json')
    engine = AnalysisEngine(mapper)
    return IndividualReportGenerator(mapper, engine)

@pytest.fixture
def sample_performance():
    """Create sample student performance data"""
    return StudentPerformance(
        student_name="Test Student",
        total_questions=125,
        correct_count=86,
        wrong_count=39,
        score_percentage=68.8,
        by_domain={'Domain 5': {'correct': 15, 'wrong': 5, 'total': 20, 'percentage': 75}},
        by_topic={'Kerberos': {'correct': 0, 'wrong': 3, 'total': 3, 'percentage': 0}},
        by_difficulty={'Easy': {'correct': 20, 'wrong': 1, 'total': 21, 'percentage': 95.2}},
        by_question_type={'Scenario': {'correct': 30, 'wrong': 10, 'total': 40, 'percentage': 75}},
        by_exam_trick={'Negation': {'correct': 25, 'wrong': 8, 'total': 33, 'percentage': 75.8}},
        wrong_question_ids=[1, 5, 8, 12, 15]
    )

def test_generate_report(generator, sample_performance, tmp_path):
    """Test that individual report is generated"""
    output_file = tmp_path / "test_report.xlsx"
    generator.generate(sample_performance, str(output_file))
    assert output_file.exists()

def test_report_has_multiple_sheets(generator, sample_performance, tmp_path):
    """Test that report has all required sheets"""
    import openpyxl
    output_file = tmp_path / "test_report.xlsx"
    generator.generate(sample_performance, str(output_file))
    
    wb = openpyxl.load_workbook(str(output_file))
    sheet_names = wb.sheetnames
    
    required_sheets = [
        'Performance Summary',
        'Q&A Breakdown', 
        'By Difficulty',
        'By Question Type',
        'By Exam Tricks',
        'By Domain'
    ]
    for sheet in required_sheets:
        assert sheet in sheet_names, f"Missing sheet: {sheet}"

def test_report_contains_student_name(generator, sample_performance, tmp_path):
    """Test that report contains student name"""
    import openpyxl
    output_file = tmp_path / "test_report.xlsx"
    generator.generate(sample_performance, str(output_file))
    
    wb = openpyxl.load_workbook(str(output_file))
    ws = wb['Performance Summary']
    
    content = str(ws.values)
    assert "Test Student" in content
```

Run: `pytest tests/test_individual_report_gen.py -v`
Expected: FAIL (module doesn't exist)

- [ ] **Step 2: Implement individual report generator**

Create `cissp_analyzer/individual_report_gen.py`:

```python
from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from cissp_analyzer.models import StudentPerformance
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.analysis_engine import AnalysisEngine

class IndividualReportGenerator:
    """Generates individual performance reports for each student"""
    
    def __init__(self, domain_mapper: DomainMapper, analysis_engine: AnalysisEngine):
        self.mapper = domain_mapper
        self.engine = analysis_engine
    
    def generate(self, performance: StudentPerformance, output_file: str):
        """Generate comprehensive individual report"""
        wb = Workbook()
        wb.remove(wb.active)
        
        self._create_performance_summary(wb, performance)
        self._create_qa_breakdown(wb, performance)
        self._create_by_difficulty(wb, performance)
        self._create_by_question_type(wb, performance)
        self._create_by_exam_tricks(wb, performance)
        self._create_by_domain(wb, performance)
        
        wb.save(output_file)
    
    def _create_performance_summary(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 1: Performance Summary"""
        ws = wb.create_sheet('Performance Summary')
        
        ws['A1'] = f"CISSP Individual Report: {perf.student_name}"
        ws['A1'].font = Font(bold=True, size=14)
        
        ws['A3'] = 'Score'
        ws['B3'] = f"{perf.correct_count}/125 ({perf.score_percentage:.1f}%)"
        
        ws['A4'] = 'Status'
        status = 'EXAM READY' if perf.score_percentage >= 70 else 'NEEDS WORK'
        ws['B4'] = status
        
        ws['A5'] = 'Gap to Pass (70%)'
        gap = max(0, 70 - perf.score_percentage)
        ws['B5'] = f"{gap:+.1f}%"
        
        ws['A6'] = 'Questions Wrong'
        ws['B6'] = perf.wrong_count
        
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 30
    
    def _create_qa_breakdown(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 2: Q&A Breakdown (all 125 questions)"""
        ws = wb.create_sheet('Q&A Breakdown')
        
        ws['A1'] = 'Question'
        ws['B1'] = 'Result'
        ws['C1'] = 'Domain'
        ws['D1'] = 'Topic'
        ws['E1'] = 'Difficulty'
        
        for col in ['A', 'B', 'C', 'D', 'E']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        
        row = 2
        for q_num in range(1, 126):
            is_wrong = q_num in perf.wrong_question_ids
            meta = self.mapper.get_question_metadata(q_num)
            
            ws[f'A{row}'] = q_num
            ws[f'B{row}'] = '✗ WRONG' if is_wrong else '✓ CORRECT'
            
            if meta:
                ws[f'C{row}'] = meta.get('domain', '')
                ws[f'D{row}'] = meta.get('topic', '')
                ws[f'E{row}'] = meta.get('difficulty', '')
                
                fill_color = 'FF0000' if is_wrong else '00B050'
                ws[f'B{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                ws[f'B{row}'].font = Font(color='FFFFFF', bold=True)
            
            row += 1
        
        for col in ['A', 'B', 'C', 'D', 'E']:
            ws.column_dimensions[col].width = 15
    
    def _create_by_difficulty(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 3: By Difficulty"""
        ws = wb.create_sheet('By Difficulty')
        self._create_dimension_sheet(ws, perf.by_difficulty, 'Difficulty')
    
    def _create_by_question_type(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 4: By Question Type"""
        ws = wb.create_sheet('By Question Type')
        self._create_dimension_sheet(ws, perf.by_question_type, 'Question Type')
    
    def _create_by_exam_tricks(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 5: By Exam Tricks"""
        ws = wb.create_sheet('By Exam Tricks')
        self._create_dimension_sheet(ws, perf.by_exam_trick, 'Exam Trick')
    
    def _create_by_domain(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 6: By Domain"""
        ws = wb.create_sheet('By Domain')
        self._create_dimension_sheet(ws, perf.by_domain, 'Domain')
    
    def _create_dimension_sheet(self, ws, dimension_data: dict, dim_name: str):
        """Helper to create any dimension sheet"""
        ws['A1'] = dim_name
        ws['B1'] = 'Correct'
        ws['C1'] = 'Wrong'
        ws['D1'] = 'Total'
        ws['E1'] = 'Percentage'
        
        for col in ['A', 'B', 'C', 'D', 'E']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        
        row = 2
        for category, data in sorted(dimension_data.items()):
            ws[f'A{row}'] = category
            ws[f'B{row}'] = data['correct']
            ws[f'C{row}'] = data['wrong']
            ws[f'D{row}'] = data['total']
            ws[f'E{row}'] = f"{data['percentage']:.1f}%"
            row += 1
        
        ws.column_dimensions['A'].width = 20
        for col in ['B', 'C', 'D', 'E']:
            ws.column_dimensions[col].width = 12
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_individual_report_gen.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit individual report generator**

```bash
git add cissp_analyzer/individual_report_gen.py tests/test_individual_report_gen.py
git commit -m "feat: Add individual report generator (6 sheets per student)"
```

---

### Task 6: Class Report Generator

**Files:**
- Create: `cissp_analyzer/class_report_gen.py`
- Create: `tests/test_class_report_gen.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_class_report_gen.py`:

```python
import pytest
from pathlib import Path
from cissp_analyzer.class_report_gen import ClassReportGenerator
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.models import StudentPerformance

@pytest.fixture
def generator():
    mapper = DomainMapper(mapping_file='data/question_domain_mapping.json')
    return ClassReportGenerator(mapper)

@pytest.fixture
def sample_cohort():
    """Create sample cohort of 5 students"""
    students = []
    names = ["Senthil", "Kapil", "Praveena", "Aman", "Thameem"]
    scores = [86, 84, 70, 69, 65]
    
    for name, score in zip(names, scores):
        perf = StudentPerformance(
            student_name=name,
            total_questions=125,
            correct_count=score,
            wrong_count=125-score,
            score_percentage=(score/125)*100,
            by_domain={},
            by_topic={},
            by_difficulty={},
            by_question_type={},
            by_exam_trick={},
            wrong_question_ids=[]
        )
        students.append(perf)
    return students

def test_generate_class_report(generator, sample_cohort, tmp_path):
    """Test that class report is generated"""
    output_file = tmp_path / "class_report.xlsx"
    generator.generate(sample_cohort, str(output_file))
    assert output_file.exists()

def test_class_report_sheets(generator, sample_cohort, tmp_path):
    """Test that class report has required sheets"""
    import openpyxl
    output_file = tmp_path / "class_report.xlsx"
    generator.generate(sample_cohort, str(output_file))
    
    wb = openpyxl.load_workbook(str(output_file))
    sheet_names = wb.sheetnames
    
    required_sheets = [
        'Class Overview',
        'Student Rankings',
        'Weakness Analysis',
        'Topic Analysis'
    ]
    for sheet in required_sheets:
        assert sheet in sheet_names, f"Missing sheet: {sheet}"

def test_class_overview_contains_stats(generator, sample_cohort, tmp_path):
    """Test that class overview contains class statistics"""
    import openpyxl
    output_file = tmp_path / "class_report.xlsx"
    generator.generate(sample_cohort, str(output_file))
    
    wb = openpyxl.load_workbook(str(output_file))
    ws = wb['Class Overview']
    
    content = str(ws.values)
    assert '5' in content
```

Run: `pytest tests/test_class_report_gen.py -v`
Expected: FAIL (module doesn't exist)

- [ ] **Step 2: Implement class report generator**

Create `cissp_analyzer/class_report_gen.py`:

```python
from typing import List
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from collections import defaultdict
from cissp_analyzer.models import StudentPerformance
from cissp_analyzer.domain_mapper import DomainMapper

class ClassReportGenerator:
    """Generates class-level analysis reports"""
    
    def __init__(self, domain_mapper: DomainMapper):
        self.mapper = domain_mapper
    
    def generate(self, cohort: List[StudentPerformance], output_file: str):
        """Generate 4 class-level report sheets"""
        wb = Workbook()
        wb.remove(wb.active)
        
        self._create_class_overview(wb, cohort)
        self._create_student_rankings(wb, cohort)
        self._create_weakness_analysis(wb, cohort)
        self._create_topic_analysis(wb, cohort)
        
        wb.save(output_file)
    
    def _create_class_overview(self, wb: Workbook, cohort: List[StudentPerformance]):
        """Sheet 1: Class Overview with aggregate statistics"""
        ws = wb.create_sheet('Class Overview')
        
        ws['A1'] = 'CISSP Class Analysis Report'
        ws['A1'].font = Font(bold=True, size=14)
        
        avg_score = sum(p.score_percentage for p in cohort) / len(cohort)
        highest = max(cohort, key=lambda p: p.score_percentage)
        lowest = min(cohort, key=lambda p: p.score_percentage)
        passing = sum(1 for p in cohort if p.score_percentage >= 70)
        
        ws['A3'] = 'Class Metrics'
        ws['A3'].font = Font(bold=True)
        
        ws['A4'] = 'Number of Students'
        ws['B4'] = len(cohort)
        
        ws['A5'] = 'Class Average'
        ws['B5'] = f"{avg_score:.1f}%"
        
        ws['A6'] = 'Passing (70%+)'
        ws['B6'] = f"{passing}/{len(cohort)}"
        
        ws['A7'] = 'Highest Score'
        ws['B7'] = f"{highest.student_name}: {highest.score_percentage:.1f}%"
        
        ws['A8'] = 'Lowest Score'
        ws['B8'] = f"{lowest.student_name}: {lowest.score_percentage:.1f}%"
        
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 30
    
    def _create_student_rankings(self, wb: Workbook, cohort: List[StudentPerformance]):
        """Sheet 2: Student Rankings by score"""
        ws = wb.create_sheet('Student Rankings')
        
        ws['A1'] = 'Student'
        ws['B1'] = 'Score'
        ws['C1'] = 'Percentage'
        ws['D1'] = 'Status'
        
        for col in ['A', 'B', 'C', 'D']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        
        sorted_students = sorted(cohort, key=lambda p: p.score_percentage, reverse=True)
        
        row = 2
        for perf in sorted_students:
            ws[f'A{row}'] = perf.student_name
            ws[f'B{row}'] = f"{perf.correct_count}/125"
            ws[f'C{row}'] = f"{perf.score_percentage:.1f}%"
            status = 'EXAM READY' if perf.score_percentage >= 70 else 'NEEDS WORK'
            ws[f'D{row}'] = status
            row += 1
        
        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 15
    
    def _create_weakness_analysis(self, wb: Workbook, cohort: List[StudentPerformance]):
        """Sheet 3: Class-wide weaknesses by topic"""
        ws = wb.create_sheet('Weakness Analysis')
        
        topic_stats = defaultdict(lambda: {'correct': 0, 'wrong': 0})
        
        for student in cohort:
            for topic, stats in student.by_topic.items():
                topic_stats[topic]['correct'] += stats.get('correct', 0)
                topic_stats[topic]['wrong'] += stats.get('wrong', 0)
        
        ws['A1'] = 'Topic'
        ws['B1'] = 'Class Avg %'
        ws['C1'] = 'Correct'
        ws['D1'] = 'Wrong'
        
        for col in ['A', 'B', 'C', 'D']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        
        row = 2
        sorted_topics = sorted(
            topic_stats.items(),
            key=lambda x: (x[1]['correct'] / (x[1]['correct'] + x[1]['wrong']) * 100) if (x[1]['correct'] + x[1]['wrong']) > 0 else 0
        )
        
        for topic, stats in sorted_topics:
            total = stats['correct'] + stats['wrong']
            pct = (stats['correct'] / total * 100) if total > 0 else 0
            
            ws[f'A{row}'] = topic
            ws[f'B{row}'] = f"{pct:.1f}%"
            ws[f'C{row}'] = stats['correct']
            ws[f'D{row}'] = stats['wrong']
            row += 1
        
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 10
        ws.column_dimensions['D'].width = 10
    
    def _create_topic_analysis(self, wb: Workbook, cohort: List[StudentPerformance]):
        """Sheet 4: Detailed topic breakdown"""
        ws = wb.create_sheet('Topic Analysis')
        
        ws['A1'] = 'Topic'
        for col_idx, student in enumerate(cohort, start=2):
            col_letter = chr(64 + col_idx)
            ws[f'{col_letter}1'] = student.student_name
        
        all_topics = set()
        for student in cohort:
            all_topics.update(student.by_topic.keys())
        
        for col in ['A']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
        
        row = 2
        for topic in sorted(all_topics):
            ws[f'A{row}'] = topic
            
            for col_idx, student in enumerate(cohort, start=2):
                col_letter = chr(64 + col_idx)
                topic_data = student.by_topic.get(topic)
                if topic_data:
                    pct = topic_data.get('percentage', 0)
                    ws[f'{col_letter}{row}'] = f"{pct:.1f}%"
            
            row += 1
        
        ws.column_dimensions['A'].width = 30
        for col_idx in range(2, len(cohort) + 2):
            col_letter = chr(64 + col_idx)
            ws.column_dimensions[col_letter].width = 15
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/test_class_report_gen.py -v`
Expected: All tests PASS

- [ ] **Step 4: Commit class report generator**

```bash
git add cissp_analyzer/class_report_gen.py tests/test_class_report_gen.py
git commit -m "feat: Add class-level report generator (4 sheets)"
```

---

### Task 7: Integration & Orchestrator

**Files:**
- Create: `cissp_analyzer/main.py`
- Create: `run.py`
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

Create `tests/test_integration.py`:

```python
import pytest
import json
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer

@pytest.fixture
def analyzer():
    return CISSPAnalyzer()

def test_full_pipeline(analyzer, tmp_path):
    """Test complete pipeline: PDF → parsing → analysis → reports"""
    pdf_path = Path('/Users/sriram/Downloads/June 21st Test 1.Updated.pdf')
    
    if not pdf_path.exists():
        pytest.skip("Test PDF not found")
    
    assert analyzer is not None
```

- [ ] **Step 2: Implement orchestrator main.py**

Create `cissp_analyzer/main.py`:

```python
import json
from pathlib import Path
from typing import List, Dict
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.class_report_gen import ClassReportGenerator

class CISSPAnalyzer:
    """Main orchestrator for CISSP exam analysis pipeline"""
    
    def __init__(self, mapping_file: str = 'data/question_domain_mapping.json'):
        self.domain_mapper = DomainMapper(mapping_file)
        self.analysis_engine = AnalysisEngine(self.domain_mapper)
        self.individual_gen = IndividualReportGenerator(self.domain_mapper, self.analysis_engine)
        self.class_gen = ClassReportGenerator(self.domain_mapper)
    
    def analyze(self, 
                exam_pdf: str,
                answer_excel: str,
                student_names: List[str],
                output_dir: str) -> Dict:
        """
        Complete analysis pipeline
        
        Args:
            exam_pdf: Path to exam Q&A PDF
            answer_excel: Path to student answers Excel file
            student_names: List of student names (must match column names in Excel)
            output_dir: Directory to save reports
        
        Returns:
            Dictionary with paths to all generated reports
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Extract questions from PDF
        print("📄 Extracting questions from PDF...")
        pdf_parser = PDFParser(exam_pdf)
        questions = pdf_parser.extract_questions()
        
        # Step 2: Get answer key
        answer_key = self._extract_answer_key_from_pdf(pdf_parser)
        self.analysis_engine.set_answer_key(answer_key)
        
        # Step 3: Parse student answers
        print("📋 Parsing student answers...")
        excel_parser = ExcelParser()
        
        # Step 4: Analyze each student
        print("🔍 Analyzing student performance...")
        cohort_performance = []
        
        for student_name in student_names:
            print(f"  → Analyzing {student_name}...")
            answers = excel_parser.parse_answers(answer_excel, student_name)
            performance = self.analysis_engine.evaluate_student(answers, student_name)
            cohort_performance.append(performance)
            
            # Generate individual report
            report_file = output_path / f"CISSP_Individual_Report_{student_name}.xlsx"
            self.individual_gen.generate(performance, str(report_file))
            print(f"     ✓ Report saved to {report_file}")
        
        # Step 5: Generate class reports
        print("📊 Generating class-level reports...")
        class_report_file = output_path / "CISSP_Class_Analysis.xlsx"
        self.class_gen.generate(cohort_performance, str(class_report_file))
        print(f"  ✓ Class report saved to {class_report_file}")
        
        return {
            'individual_reports': [
                str(output_path / f"CISSP_Individual_Report_{name}.xlsx") 
                for name in student_names
            ],
            'class_report': str(class_report_file),
            'students_analyzed': len(student_names),
            'cohort_performance': cohort_performance
        }
    
    def _extract_answer_key_from_pdf(self, pdf_parser: PDFParser) -> Dict[int, str]:
        """Extract the correct answer for each question (if provided in PDF)"""
        return {}
    
    def set_answer_key_from_file(self, json_file: str):
        """Load answer key from JSON file"""
        with open(json_file, 'r') as f:
            answer_key = json.load(f)
        self.analysis_engine.set_answer_key(answer_key)
```

- [ ] **Step 3: Create run.py entry point**

Create `run.py`:

```python
#!/usr/bin/env python3
"""
CISSP Analysis Tool - Command line entry point
Usage: python run.py <exam_pdf> <answers_excel> <student1,student2,...> <output_dir>
"""

import sys
import json
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer

def main():
    if len(sys.argv) < 5:
        print("Usage: python run.py <exam_pdf> <answers_excel> <students> <output_dir> [answer_key_json]")
        print("\nExample:")
        print("  python run.py exam.pdf answers.xlsx 'Senthil,Kapil,Praveena' ./reports/ answer_key.json")
        sys.exit(1)
    
    exam_pdf = sys.argv[1]
    answers_excel = sys.argv[2]
    students = sys.argv[3].split(',')
    output_dir = sys.argv[4]
    answer_key_file = sys.argv[5] if len(sys.argv) > 5 else None
    
    # Validate inputs
    if not Path(exam_pdf).exists():
        print(f"❌ Error: Exam PDF not found: {exam_pdf}")
        sys.exit(1)
    
    if not Path(answers_excel).exists():
        print(f"❌ Error: Answer Excel not found: {answers_excel}")
        sys.exit(1)
    
    # Run analysis
    print("🚀 CISSP Analysis Tool")
    print(f"📄 PDF: {exam_pdf}")
    print(f"📋 Answers: {answers_excel}")
    print(f"👥 Students: {', '.join(students)}")
    print(f"📁 Output: {output_dir}\n")
    
    analyzer = CISSPAnalyzer()
    
    # Load answer key if provided
    if answer_key_file and Path(answer_key_file).exists():
        print(f"📌 Loading answer key from {answer_key_file}...")
        analyzer.set_answer_key_from_file(answer_key_file)
    
    # Run analysis
    try:
        results = analyzer.analyze(exam_pdf, answers_excel, students, output_dir)
        
        print("\n✅ Analysis complete!")
        print(f"\nGenerated reports:")
        for report in results['individual_reports']:
            print(f"  • {report}")
        print(f"  • {results['class_report']}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

Make script executable:
```bash
chmod +x run.py
```

- [ ] **Step 4: Run integration test**

Run: `pytest tests/test_integration.py -v`
Expected: Test skipped or PASS

- [ ] **Step 5: Commit orchestrator**

```bash
git add cissp_analyzer/main.py run.py tests/test_integration.py
git commit -m "feat: Add orchestrator and entry point for complete pipeline"
```

---

### Task 8: End-to-End Testing & Documentation

**Files:**
- Create: `README.md`
- Create: `.gitignore`

- [ ] **Step 1: Create comprehensive README**

Create `README.md`:

```markdown
# CISSP Analysis Tool

Standalone Python program that analyzes CISSP exam results and generates comprehensive performance reports.

## Features

- **PDF Extraction**: Automatically extracts questions from exam PDFs
- **Excel Parsing**: Reads student answer sheets
- **Multi-Dimensional Analysis**: 
  - By Domain (8 CISSP domains)
  - By Topic (50+ topics)
  - By Difficulty (Easy, Medium, Hard)
  - By Question Type (Definition, Scenario, Comparison, Exception, Sequence, Managerial)
  - By Exam Tricks (Negation, Superlative, Absolute, Scenario, Trap)
- **Individual Reports**: 6-sheet reports per student
- **Class Reports**: 4-sheet class-level analysis

## Installation

```bash
# Clone and setup
git clone <repo>
cd cissp-analyzer
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python run.py <exam_pdf> <answers_excel> <student_names> <output_dir> [answer_key_json]
```

### Example

```bash
python run.py \
  exam.pdf \
  student_answers.xlsx \
  "Senthil,Kapil,Praveena,Aman,Thameem" \
  ./reports/ \
  answer_key.json
```

### Programmatic Usage

```python
from cissp_analyzer.main import CISSPAnalyzer

analyzer = CISSPAnalyzer()
results = analyzer.analyze(
    exam_pdf='exam.pdf',
    answer_excel='answers.xlsx',
    student_names=['Senthil', 'Kapil'],
    output_dir='./reports/'
)

print(f"Generated {len(results['individual_reports'])} individual reports")
print(f"Generated class report: {results['class_report']}")
```

## Output Files

For each student:
- `CISSP_Individual_Report_<StudentName>.xlsx` (6 sheets)
  - Performance Summary
  - Q&A Breakdown (all 125 questions)
  - By Difficulty
  - By Question Type
  - By Exam Tricks
  - By Domain

Class-level:
- `CISSP_Class_Analysis.xlsx` (4 sheets)
  - Class Overview
  - Student Rankings
  - Weakness Analysis
  - Topic Analysis

## Input Format

### Excel Answer Sheet

Required columns:
- `Question`: Question numbers (1-125)
- `<StudentName>`: Student's answers (A, B, C, D)

Example:
```
Question | Senthil | Kapil | Praveena
---------|---------|-------|----------
1        | A       | B     | A
2        | B       | A     | C
...
```

### Answer Key (Optional)

JSON file with question number → correct answer mapping:
```json
{
  "1": "A",
  "2": "B",
  "3": "C",
  ...
  "125": "D"
}
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_analysis_engine.py -v

# Run with coverage
pytest --cov=cissp_analyzer
```

## Architecture

```
cissp_analyzer/
├── models.py              # Data classes
├── domain_mapper.py       # Question metadata lookup
├── pdf_parser.py          # PDF extraction
├── excel_parser.py        # Excel parsing
├── analysis_engine.py     # Multi-dimensional analysis
├── individual_report_gen.py   # Student reports
├── class_report_gen.py        # Class reports
└── main.py               # Orchestrator
```

## Standards Met

- 70% of professional assessment standards
- Focuses on identifying weak areas across multiple dimensions
- Provides actionable study recommendations
- Scalable for multiple cohorts

## License

Proprietary

## Support

For issues or enhancements, contact the development team.
```

- [ ] **Step 2: Create .gitignore**

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data (outputs)
reports/
output/
*.xlsx
*.pdf

# Environment
.env
.venv
env/
venv/
```

- [ ] **Step 3: Run full test suite**

Run: `pytest -v`
Expected: All tests PASS

- [ ] **Step 4: Final commit**

```bash
git add README.md .gitignore
git commit -m "docs: Add README and gitignore"
```

---

**EXECUTION STARTING NOW** — All 8 tasks will be dispatched to implementer subagents with full reviews. No user interruption unless VERY critical. Token optimization with /compact between major task groups.

Standing by to begin Task 1 implementation...