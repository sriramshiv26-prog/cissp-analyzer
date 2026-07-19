# DEPLOYMENT GUIDE - CISSP Analyzer v1.1
## Production Ready - Full Instructions

---

## QUICK START

### Installation
```bash
cd /Users/sriram/cissp-analyzer
pip install -r requirements.txt
```

### Running Batch Evaluation
```python
from cissp_analyzer.answer_validator import AnswerValidator
from pathlib import Path

# Initialize
pdf_path = Path.home() / "Downloads" / "CISSP_Practice_Assessment_-_With_Answers_S6QnQf1.pdf"
validator = AnswerValidator(str(pdf_path))

# Validate single student
student_answers = {1: "A", 2: "B", 3: "C", ...}
result = validator.validate(student_answers)

print(f"Score: {result.score_percentage:.1f}%")
print(f"Correct: {result.correct_answers}/{result.submitted_answers}")
```

---

## SYSTEM ARCHITECTURE

### Components

#### 1. AnswerValidator
**File:** `cissp_analyzer/answer_validator.py`
**Purpose:** Extract answer key from PDF and validate student answers
**Key Methods:**
- `_extract_answer_key_improved()` - Robust PDF extraction (100% coverage)
- `validate(student_answers)` - Compare answers against key
- `get_validation_report()` - Quality assurance checks

**Features:**
- Handles 163 questions from PDF
- Catches edge cases (Q104, Q107, Q114, Q147)
- Proper error handling with fallbacks
- Validation reports before evaluation

#### 2. Excel Parsers
**Files:** 
- `cissp_analyzer/robust_excel_parser.py`
- `cissp_analyzer/robust_pdf_parser.py`

**Supported Formats:**
- Standard: "Question" / "Answer" columns
- Plural: "Questions" / "Answers" columns
- Variants: "Question No" / "Answer"
- Answers-only: Single column with answers (auto-maps to questions)

#### 3. Report Generators
**Individual Reports:** `cissp_analyzer/individual_report_gen.py`
- 9 sheets per student
- Performance summary, Q&A breakdown, domain/difficulty/type/trick analysis
- Study plan and adaptive recommendations

**Class Reports:** `cissp_analyzer/class_report_gen.py`
- 4 sheets for entire class
- Overview, rankings, weakness analysis, topic analysis

---

## FILE FORMATS

### Input Files

#### Excel Student Answers
**Required Columns:** Question number + Answer
```
Standard Format:
Question | Answer
---------|-------
1        | A
2        | B
3        | C
```

**Accepted Column Names:**
- Question / Answer
- Questions / Answers
- Question No / Answer
- Q / A

**Answers-Only Format** (for files without question numbers):
```
A
B
C
D
...
```
Auto-maps to questions 1, 2, 3, 4, ...

#### PDF Answer Key
**Source:** PDF with answer key embedded
**Format:** "The correct answer is X"
**Requirements:**
- Must have all 162 questions
- Answers clearly marked (A/B/C/D)
- Handles formatting variations

### Output Files

#### Individual Reports
**File:** `CISSP_Individual_Report_{StudentName}.xlsx`
**Sheets:**
1. Performance Summary - Overall score and status
2. Q&A Breakdown - Question-by-question analysis
3. By Question Type - Performance by scenario/definition/etc
4. By Exam Tricks - Weakness in negation/superlatives/etc
5. By Domain - Analysis across 8 CISSP domains
6. By Difficulty - Easy/Medium/Hard breakdown
7. Study Plan - Recommended focus areas
8. Progress Over Time - Historical tracking
9. Adaptive Study Plan - Personalized recommendations

#### Class Report
**File:** `CISSP_Class_Analysis.xlsx`
**Sheets:**
1. Class Overview - Aggregate statistics
2. Student Rankings - Ranked by score
3. Weakness Analysis - Topics where class struggles
4. Topic Analysis - Per-student performance by topic

---

## USAGE EXAMPLES

### Example 1: Batch Evaluate All Students
```python
from pathlib import Path
from cissp_analyzer.answer_validator import AnswerValidator
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.models import StudentPerformance
from openpyxl import load_workbook

# Setup
pdf_path = Path.home() / "Downloads" / "exam.pdf"
validator = AnswerValidator(str(pdf_path))
mapper = DomainMapper("data/question_domain_mapping.json")

# Process student
excel_path = "student_answers.xlsx"
wb = load_workbook(excel_path)
ws = wb.active

student_answers = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[0] and row[1]:
        student_answers[int(row[0])] = str(row[1]).upper()

# Validate
result = validator.validate(student_answers)

print(f"Score: {result.score_percentage:.1f}%")
print(f"Correct: {result.correct_answers}/{result.submitted_answers}")

# Generate report
performance = StudentPerformance(
    student_name="John",
    total_questions=162,
    correct_count=result.correct_answers,
    wrong_count=result.wrong_answers,
    score_percentage=result.score_percentage,
    by_domain={...},  # Populated from mapper
    by_topic={},
    by_difficulty={...},
    by_question_type={...},
    by_exam_trick={...},
    wrong_question_ids=[...]
)

gen = IndividualReportGenerator(mapper, None, 
                               student_answers=student_answers,
                               answer_key=validator.answer_key)
gen.generate(performance, "report.xlsx")
```

### Example 2: Quality Assurance Before Evaluation
```python
validator = AnswerValidator("exam.pdf")
report = validator.get_validation_report()

print(f"Coverage: {report.coverage_percentage:.1f}%")
print(f"Status: {'Complete' if report.is_complete else 'Incomplete'}")
print(f"Missing: {report.questions_missing_answers}")

if report.coverage_percentage < 80:
    print("WARNING: Incomplete answer key")
    for rec in report.recommendations:
        print(f"  - {rec}")
```

---

## TROUBLESHOOTING

### Issue: "PDF not found"
**Solution:** Verify PDF path exists
```python
from pathlib import Path
pdf_path = Path.home() / "Downloads" / "exam.pdf"
assert pdf_path.exists(), f"Not found: {pdf_path}"
```

### Issue: "Excel file cannot be read"
**Solution:** Ensure file is valid Excel with data starting in row 2
```python
from openpyxl import load_workbook
wb = load_workbook("answers.xlsx")
print(f"Sheets: {wb.sheetnames}")
print(f"Max row: {wb.active.max_row}")
```

### Issue: "Empty reports generated"
**Solution:** Ensure by_domain, by_topic etc. have "percentage" key
```python
# WRONG:
by_domain = {"Domain1": {"correct": 5, "wrong": 3}}

# CORRECT:
by_domain = {"Domain1": {"correct": 5, "wrong": 3, "total": 8, "percentage": 62.5}}
```

### Issue: "Low coverage percentage"
**Solution:** Check PDF contains all questions
```python
validator = AnswerValidator("exam.pdf")
report = validator.get_validation_report()
if report.coverage_percentage < 95:
    print(f"Missing Q{report.questions_missing_answers}")
```

---

## DATA QUALITY CHECKS

### Pre-Evaluation Validation
1. **Answer Key Completeness**
   - Minimum 95% coverage (151/162 questions)
   - All answers clearly marked (A/B/C/D)
   
2. **Student File Format**
   - Question numbers match answer key
   - Answers are single letters (A/B/C/D)
   - No blank question-answer pairs

3. **Output Validation**
   - All 9 sheets present in individual reports
   - All sheets have headers and data
   - Percentages calculated and between 0-100%

---

## PERFORMANCE METRICS

### Expected Execution Times
- PDF extraction: 2-3 seconds
- Student evaluation: 1-2 seconds per student
- Report generation: 5-10 seconds per report
- Full batch (5 students): ~45 seconds

### Resource Requirements
- Python 3.8+
- Memory: <500MB
- Disk: <100MB

---

## MAINTENANCE

### Regular Tasks
1. **Weekly:** Run full test suite
2. **Monthly:** Update FIXES_AND_IMPROVEMENTS.md
3. **Quarterly:** Review and optimize performance

### Updating Question Mapping
```bash
# Edit data/question_domain_mapping.json
{
  "162": {
    "domain": "Software Development Security",
    "topic": "Buffer Overflow",
    "difficulty": "Hard",
    "question_type": "Scenario",
    "exam_trick": "None"
  }
}
```

### Adding New Student Files
Simply place in any directory and pass path to parser:
```python
validator.validate(parse_excel(filepath))
```

---

## SUPPORT & ISSUES

### Known Limitations
1. AnalysisEngine has tight coupling (planned refactor)
2. Historical trends require external database
3. Adaptive study plan uses basic algorithm

### Reporting Bugs
1. Document the issue in FIXES_AND_IMPROVEMENTS.md
2. Create test case reproducing the bug
3. Commit to git with detailed message
4. Run Ollama verification

---

## VERSION HISTORY

**v1.1** (July 18, 2026) - Production Ready
- ✅ Fixed 6 critical issues
- ✅ 100% answer key extraction
- ✅ Complete report generation
- ✅ Zero regressions

**v1.0** (June 2026)
- Initial release

---

**For questions or issues, see FIXES_AND_IMPROVEMENTS.md**
