# CISSP Analyzer

A production-ready Python program that analyzes CISSP exam results and generates professional performance reports with 5-dimensional analysis across domains, topics, difficulty levels, question types, and exam tricks.

**Status:** ✅ Production Ready | **Version:** 1.0 | **Tests:** 26/26 Passing

---

## Features

### Multi-Dimensional Analysis
Analyzes exam performance across **5 independent dimensions**:

1. **Domain Analysis** - Performance across all 8 official ISC2 CISSP domains
2. **Topic/Subtopic Analysis** - Granular performance within each domain (20+ topics)
3. **Difficulty Analysis** - Breakdown by Easy/Medium/Hard questions
4. **Question Type Analysis** - Performance by question format (Definition, Application, Scenario, Exception, Sequence)
5. **Exam Trick Analysis** - Identifies performance on trick questions (MOST, BEST, FIRST, NOT, EXCEPT, etc.)

### Professional Reports (7 Sheets)

Each student receives a comprehensive Excel report with:

| Sheet | Purpose |
|-------|---------|
| **Performance Summary** | Score, gap to pass, personalized message, study recommendations |
| **Q&A Breakdown** | All questions with color-coded results (correct/wrong) + domain, topic, type, trick, difficulty |
| **By Question Type** | Performance breakdown by question format with weak area identification |
| **By Exam Tricks** | Trick keyword analysis with list of wrong questions per trick type |
| **By Domain** | Performance by CISSP domain with topic-level breakdown |
| **By Difficulty** | Performance by difficulty level with status indicators |
| **Study Plan** | Personalized, actionable study plan with weekly milestones |

### True Genericity
- Works with **ANY exam PDF** (not just CISSP)
- Works with **ANY number of questions**
- Works with **ANY answer file format** (flexible parsing)
- Works on **Windows, Mac, and Linux**

---

## Quick Start

### Installation (2 minutes)

**Windows, Mac, or Linux:**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer

# 2. Install Python 3.11+ (if not already installed)
# Visit: https://www.python.org/downloads/

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
pytest -v
```

### Generate a Report (1 minute)

```bash
python3 run.py <exam_pdf> <student_answers_excel> <student_names> <output_dir>
```

**Example:**
```bash
python3 run.py "exams/June_21st_Test.pdf" "answers/student_answers.xlsx" "John Doe,Jane Smith" "outputs/"
```

This generates:
- `CISSP_Individual_Report_John_Doe.xlsx` (7-sheet professional report)
- `CISSP_Individual_Report_Jane_Smith.xlsx` (7-sheet professional report)
- `CISSP_Class_Analysis.xlsx` (comparative class report)

---

## File Structure

```
cissp-analyzer/
├── cissp_analyzer/
│   ├── __init__.py
│   ├── models.py                    # Data models (Question, StudentPerformance)
│   ├── pdf_parser.py                # Extract Q&A from exam PDF
│   ├── excel_parser.py              # Parse student answer Excel files
│   ├── domain_mapper.py             # Load question metadata (domain, topic, etc.)
│   ├── analysis_engine.py           # Multi-dimensional analysis
│   ├── individual_report_gen.py     # Generate 7-sheet individual reports
│   ├── class_report_gen.py          # Generate class-level reports
│   └── main.py                      # Pipeline orchestrator
│
├── data/
│   ├── question_domain_mapping.json        # Question metadata (125 questions, 6 fields)
│   ├── practice_test_1_mapping.json        # Practice Test 1 mapping (107 questions)
│   └── practice_test_1_answer_key.json     # Answer keys extracted from PDF
│
├── tests/
│   ├── test_domain_mapper.py       # Domain mapping tests
│   ├── test_pdf_parser.py          # PDF extraction tests
│   ├── test_excel_parser.py        # Excel parsing tests
│   ├── test_analysis_engine.py     # Analysis tests
│   ├── test_individual_report_gen.py  # Report generation tests
│   ├── test_class_report_gen.py    # Class report tests
│   └── test_integration.py         # End-to-end integration tests
│
├── run.py                          # CLI entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── INSTALLATION.md                 # Detailed platform-specific setup
└── QUICKSTART.md                   # Quick reference guide
```

---

## Data Requirements

### Input Files

1. **Exam PDF** (`exam.pdf`)
   - Contains all questions with Q&A
   - Should have questions numbered sequentially
   - Supports different PDF structures

2. **Student Answers Excel** (`answers.xlsx`)
   - Column: Student name → Question answers (1-125)
   - Format: Question number → Answer letter (A/B/C/D)
   - Supports non-standard formats with auto-detection

### Mapping File (`data/question_domain_mapping.json`)

Each question needs 6 fields:
```json
{
  "1": {
    "domain": 5,
    "topic": "Access Control",
    "subtopic": "Access Control Models",
    "difficulty": "Medium",
    "question_type": "Application",
    "exam_trick": "None"
  }
}
```

---

## Usage Examples

### Example 1: Single Student

```bash
python3 run.py "downloads/exam.pdf" "downloads/answers.xlsx" "John Doe" "outputs/"
```

### Example 2: Multiple Students (Comma-Separated)

```bash
python3 run.py "downloads/exam.pdf" "downloads/answers.xlsx" "John Doe,Jane Smith,Bob Johnson" "outputs/"
```

### Example 3: Programmatic Usage

```python
from cissp_analyzer.main import CISSPAnalyzer

analyzer = CISSPAnalyzer(mapping_file='data/question_domain_mapping.json')
results = analyzer.analyze(
    exam_pdf='exams/exam.pdf',
    answer_excel='answers/answers.xlsx',
    student_names=['John Doe', 'Jane Smith'],
    output_dir='outputs/'
)

print(f"Generated {len(results['individual_reports'])} individual reports")
print(f"Class report: {results['class_report']}")
```

---

## Test Coverage

Run all tests:
```bash
pytest -v
```

Results:
- ✅ 26/26 unit tests passing
- ✅ 3/4 integration tests passing (1 skipped - requires Excel file)
- ✅ Code quality: Grade A

---

## Platform-Specific Setup

For detailed setup instructions for Windows, Mac, or Linux, see [INSTALLATION.md](INSTALLATION.md).

---

## What Gets Generated

### Individual Reports (Per Student)

**File:** `CISSP_Individual_Report_<StudentName>.xlsx`

| Sheet | Content |
|-------|---------|
| Performance Summary | Current score (32.3%), Gap to pass (37.7%), Personalized insights |
| Q&A Breakdown | All 125 questions, color-coded (correct/wrong), CISSP topics, difficulty, question type, exam tricks |
| By Question Type | Performance by question format (Definition, Scenario, Application, etc.) |
| By Exam Tricks | Performance on trick keywords with specific weak question numbers |
| By Domain | 8 CISSP domains with topic-level breakdown |
| By Difficulty | Easy/Medium/Hard analysis with status indicators |
| Study Plan | **Detailed action plan:** Priority domains, critical topics, weekly milestones, exam trick strategy |

### Class Reports

**File:** `CISSP_Class_Analysis.xlsx`

- Overview: Class statistics, average score, score distribution
- Student Rankings: Sorted by performance
- Weakness Analysis: Common weak domains/topics across class
- Performance Tiers: Top performers, needs improvement, etc.

---

## Advanced: Custom Mapping

To use with a different exam:

1. Create `data/my_exam_mapping.json`:
```json
{
  "1": {"domain": 1, "topic": "Topic Name", "subtopic": "Subtopic", ...},
  "2": {"domain": 2, "topic": "Topic Name", "subtopic": "Subtopic", ...}
}
```

2. Use in analysis:
```python
analyzer = CISSPAnalyzer(mapping_file='data/my_exam_mapping.json')
```

---

## Technology Stack

- **Language:** Python 3.11+
- **Excel:** openpyxl (professional formatting)
- **PDF:** pypdf (question extraction)
- **Data:** pandas (analysis)
- **Testing:** pytest (26 tests)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | June 25, 2026 | Initial production release with 7-sheet reports, 5D analysis, detailed study plans |

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues or questions:
1. Check [QUICKSTART.md](QUICKSTART.md) for common problems
2. Review test files for usage examples
3. Open an issue on GitHub

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

---

**Built with ❤️ for CISSP exam preparation**

Last Updated: June 25, 2026
