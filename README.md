# CISSP Analyzer

**Professional CISSP Exam Analysis Tool**

Analyzes exam results and generates beautiful 7-sheet Excel reports showing exactly where students are weak.

**Status:** ✅ Production Ready | **Tests:** 26/26 Passing | **Installation:** 2 minutes

---

## What Does It Do?

You provide:
- 📄 Exam PDF (questions and answers)
- 📊 Student answer Excel file
- 👤 Student name(s)

You get:
- 📈 Professional 7-sheet Excel reports
- 📍 Shows weak domains, topics, question types
- 📅 Personalized study plan for each student
- 🎯 Color-coded results (easy to understand)

**Example Output:**
```
Input:
  - June_21st_Test.pdf
  - student_answers.xlsx (John Doe's answers)

Output:
  - CISSP_Individual_Report_John_Doe.xlsx (7 professional sheets)
  - Shows John got 68.8%, weak in Kerberos, strong in Access Control, etc.
```

---

## Quick Start (5 Minutes)

### 1. Install (2 minutes)

**On Mac:**
```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v  # Should show 26 passed
```

**On Windows (Command Prompt):**
```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

**On Linux (Ubuntu/Debian):**
```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v
```

### 2. Run (1 minute)

```bash
python3 run.py "exam.pdf" "answers.xlsx" "Student Name" "outputs/"
```

**Example:**
```bash
python3 run.py "downloads/June_21st_Test.pdf" "downloads/answers.xlsx" "John Doe" "outputs/"
```

**Output:**
```
outputs/CISSP_Individual_Report_John_Doe.xlsx  ← Open this file!
```

### 3. View Results (1 minute)

Open the Excel file in:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc

---

## What's In The Report? (7 Sheets)

| # | Sheet Name | What It Shows |
|---|---|---|
| 1 | **Performance Summary** | Score, pass/fail status, how much more needed to pass, personalized message |
| 2 | **Q&A Breakdown** | Every question - was it right or wrong, color-coded (green=correct, red=wrong) |
| 3 | **By Question Type** | Performance on Definition vs Scenario vs Application questions |
| 4 | **By Exam Tricks** | Performance on trick questions (MOST, BEST, FIRST, NOT, EXCEPT keywords) |
| 5 | **By Domain** | Performance across 8 CISSP domains (which domain is weakest?) |
| 6 | **By Difficulty** | Performance on Easy vs Medium vs Hard questions |
| 7 | **Study Plan** | Personalized weekly study plan based on weak areas |

**Example:** If student got 68.8%, the report shows:
- ✅ Strengths: Domain 2 (88.9%), Domain 6 (100%)
- ❌ Weaknesses: Domain 3 (47%), Domain 5 Kerberos (0%)
- 📅 Study Plan: "Focus on Kerberos - 3 hours/week"

---

## Historical Exam Tracking (NEW)

Track student progress across multiple exams and get adaptive study recommendations.

### First Exam (Baseline)
```bash
python3 run.py "exam.pdf" "answers.xlsx" "Student Name" "outputs/"
```

Output:
```
outputs/Mock1_2026-06-28_StudentName.xlsx  ← Named with date & student
```

### Second Exam (Progress Tracking)
```bash
python3 run.py "exam.pdf" "answers2.xlsx" "Student Name" "outputs/"
```

The tool automatically detects prior exams and adds:
- **Sheet 7:** Progress Over Time (trends in domains, difficulty levels, question types)
- **Sheet 8:** Adaptive Study Plan (momentum-based recommendations)

Output:
```
outputs/Mock2_2026-06-28_StudentName.xlsx  ← Shows progress vs Mock1
```

### Filename Convention
All reports follow this pattern:
```
Mock[N]_[YYYY-MM-DD]_[StudentName].xlsx
```

Where:
- `N` = exam sequence (Mock1, Mock2, Mock3, etc.)
- `YYYY-MM-DD` = analysis date
- `StudentName` = student name (spaces converted to underscores)

### New Report Sheets (Exams 2+)

| Sheet | Content |
|---|---|
| **Sheet 7:** Progress Over Time | Trend charts showing performance across exams: domains improving/declining, difficulty level progression, question type mastery |
| **Sheet 8:** Adaptive Study Plan | Momentum-based recommendations: focus areas with highest ROI based on trend analysis, not just raw weaknesses |

### How It Works

The adaptive recommendation engine:
1. Compares exam-to-exam performance
2. Calculates momentum (improving vs declining topics)
3. Identifies "quick wins" (topics improving but still weak)
4. Recommends 3-week focused study plan with daily time allocation

---

## Multiple Students

Analyze 3 students at once:

```bash
python3 run.py "exam.pdf" "answers.xlsx" "John,Jane,Bob" "outputs/"
```

Output:
```
outputs/CISSP_Individual_Report_John.xlsx
outputs/CISSP_Individual_Report_Jane.xlsx
outputs/CISSP_Individual_Report_Bob.xlsx
outputs/CISSP_Class_Analysis.xlsx  ← Compare all students
```

---

## Requirements

- **Python:** 3.11 or higher
- **Packages:** pandas, openpyxl, pypdf (auto-installed via `pip install -r requirements.txt`)
- **Time:** Installation = 2 min, Analysis = 5 sec per student
- **AI:** None needed - pure data analysis

---

## Files You Need

### 1. Exam PDF
- Questions and answers
- Standard format
- Example: `downloads/exam.pdf`

### 2. Student Answers Excel
- Column headers = student names
- Rows = answers (A, B, C, or D)
- Example:

| John Doe | Jane Smith |
|----------|-----------|
| A | B |
| B | A |
| C | C |
| D | D |

### 3. (Optional) Domain Mapping
- Already provided for CISSP
- JSON file with question metadata
- Can customize for other exams

---

## Detailed Setup

**Full instructions for each platform:**
- 👉 **Windows setup:** See [INSTALLATION.md](INSTALLATION.md)
- 👉 **Mac setup:** See [INSTALLATION.md](INSTALLATION.md)
- 👉 **Linux setup:** See [INSTALLATION.md](INSTALLATION.md)

**Quick reference:**
- 👉 See [QUICKSTART.md](QUICKSTART.md)

**Step-by-step GitHub push:**
- 👉 See [GITHUB_PUSH_STEPS.txt](GITHUB_PUSH_STEPS.txt)

---

## How It Works (Technical)

**Step 1:** Parse PDF → Extract 125 questions
**Step 2:** Parse Excel → Get student answers
**Step 3:** Match answers to questions → Calculate correct/wrong
**Step 4:** Analyze 5 dimensions:
  - Domain (8 CISSP domains)
  - Topic (20+ topics within domains)
  - Difficulty (Easy/Medium/Hard)
  - Question Type (Definition, Application, Scenario, Exception, Sequence)
  - Exam Tricks (MOST, BEST, FIRST, NOT, EXCEPT keywords)
**Step 5:** Generate 7-sheet Excel report with color coding

**No AI involved** - pure data processing and analysis.

---

## Test Coverage

All components are tested:
```bash
pytest -v
# Result: 26 passed, 3 skipped (skipped = need full Excel data)
```

Tests cover:
- ✅ PDF extraction
- ✅ Excel parsing
- ✅ Question mapping
- ✅ Performance analysis
- ✅ Report generation
- ✅ Real exam data

---

## Common Questions

**Q: Does this use AI?**
A: No. Pure Python data analysis and Excel generation.

**Q: Can I use it with a different exam?**
A: Yes! Provide a mapping file with question → domain/topic data.

**Q: What if my Excel format is different?**
A: The parser is flexible. It handles most formats. Minor adjustments may be needed.

**Q: Can it handle 200 questions instead of 125?**
A: Yes! Works with any number of questions.

**Q: Can teachers use this?**
A: Yes! Teachers provide exam PDF + student answer file, get reports for each student.

**Q: Is it free?**
A: Yes! Open source, MIT licensed.

---

## Project Structure

```
cissp-analyzer/
├── README.md                          ← You are here
├── INSTALLATION.md                    ← Setup instructions
├── QUICKSTART.md                      ← Quick reference
├── GITHUB_PUSH_STEPS.txt             ← GitHub upload guide
├── requirements.txt                   ← Dependencies (pandas, openpyxl, pypdf)
├── run.py                            ← Main program (run this!)
│
├── cissp_analyzer/                   ← Source code
│   ├── pdf_parser.py                 ← Reads exam PDF
│   ├── excel_parser.py               ← Reads student answers
│   ├── domain_mapper.py              ← Question metadata
│   ├── analysis_engine.py            ← Performance analysis
│   ├── individual_report_gen.py      ← Creates 7-sheet report
│   ├── class_report_gen.py           ← Compares students
│   └── main.py                       ← Orchestrator
│
├── data/                             ← Question mappings
│   ├── question_domain_mapping.json  ← 125 CISSP questions
│   └── practice_test_1_mapping.json  ← 107 practice questions
│
└── tests/                            ← Test suite (26 tests)
    └── test_*.py                     ← All components tested
```

---

## Example

**Real example from Arjun (Practice Test 1):**

Input:
- Practice_Test_1.pdf (107 questions)
- arjun_answers.xlsx (Arjun's 124 answers)

Output:
- CISSP_Individual_Report_Arjun.xlsx

**Arjun's Results:**
- ✅ Score: 40/117 = 34.2% (needs 35.8% improvement)
- ✅ Weakest Domain: Domain 5 (IAM) = 12.5%
- ✅ Weakest Topic: Kerberos = 0%
- ✅ Weakest Trick Type: Multiple keyword tricks = 0%
- 📅 Study Plan: Focus on Domain 4 (Network) and Domain 5 (IAM)

---

## Installation Issues?

If you get stuck:
1. Make sure Python 3.11+ is installed: `python3 --version`
2. Make sure pip is installed: `python3 -m pip --version`
3. Reinstall packages: `pip install -r requirements.txt --force-reinstall`
4. See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting

---

## License

MIT License - Free to use for any purpose

---

## Questions?

- 📖 Read [INSTALLATION.md](INSTALLATION.md) for setup
- 📖 Read [QUICKSTART.md](QUICKSTART.md) for examples
- 📖 Check test files (`tests/`) for code examples
- 🐛 Open an issue if something doesn't work

---

**Ready to analyze exams? Run:** `python3 run.py exam.pdf answers.xlsx "Name" outputs/`

---

**Version:** 1.0 | **Last Updated:** June 25, 2026 | **Built with Python**
