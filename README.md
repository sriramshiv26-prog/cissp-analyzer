# CISSP Analyzer

**Professional CISSP Exam Analysis Tool**

Analyzes exam results and generates beautiful 7-sheet Excel reports showing exactly where students are weak.

**Status:** ✅ Production Ready | **Tests:** 279/279 Passing | **Version:** 1.0.1 | **Python:** 3.9-3.12 | **Platforms:** macOS, Windows, Linux

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

## Quick Start (10 Minutes)

### Step 1: Install (2 minutes)

**On Mac:**
```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v  # Should show 279 passed
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

### Step 2: Verify Setup (1 minute)

```bash
python3 check_setup.py
```

This checks that all dependencies, directories, and files are ready. You should see all checks passed.

### Step 3: Run the Analyzer with Setup Wizard (7 minutes)

```bash
python3 analyze.py
```

**That's it!** The setup wizard will:
- ✅ Check if all files exist
- ✅ Create `student_roster.json` template if missing
- ✅ Guide you to place exam PDFs and answer files
- ✅ Tell you exactly what's needed and where to put it
- ✅ Start analysis automatically once files are ready

**Detailed Setup Help:** See [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

### Step 4: Choose Your Analysis Path

**FIRST TIME?** Try with included example files:
```bash
python3 analyze.py
# Select: [2] Standalone Analysis
# When asked for exam PDF: exams/practice_test_1_mapping.json
# When asked for student answers: EXAMPLE_student_answers.xlsx
# Check the generated report in outputs/
```

**HAVE YOUR OWN FILES?** Prepare these first:
1. **Exam PDF** - Your test file with questions and answers
2. **Student Answers Excel** - See EXAMPLE_student_answers.xlsx for format
3. Then run:
```bash
python3 analyze.py
# Select: [2] Standalone Analysis (for single student)
# OR      [1] Batch Analysis (for multiple students)
# Provide file paths when prompted
```

**RUNNING A FULL CLASS?**
1. Prepare student roster (see FORMATS_AND_TEMPLATES_GUIDE.md)
2. Set up folder structure (see TEMPLATE_directory_structure.md)
3. Run:
```bash
python3 analyze.py
# Select: [1] Batch Analysis
# OR      [3] Full Batch Workflow (includes validation + auto-fix)
```

### Step 4: View Results (1 minute)

Open the generated Excel file in:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc

---

## ✨ What's New in v1.0.1 (July 2026)

**Multi-Week Question Bank Management & Flexible Answer Sheet Matching**

Solve the problem: "If I upload a question bank today and answer sheets next week, will the system remember it without re-uploading?"

**Answer: YES!** We've added a complete multi-question-bank system:

### New Features (6-Layer Validation Pipeline)

| Layer | Feature | Benefit |
|-------|---------|---------|
| **0.25** | 📚 **Question Bank Registry** | Remember PDFs forever - no re-uploading across months/years |
| **0** | 🔍 **Fuzzy File Matching** | Find sheets matching PDFs despite typos (Jul12 = july12 = JULY12) |
| **0.5** | 🎯 **Interactive Question Bank Mapper** | Explicitly confirm which answer sheets belong to which PDF |
| **1** | ✅ **Format Validation** | Verify files are valid before processing |
| **2** | 🔄 **Sheet Variation Detection** | Handle different Excel sheet naming patterns automatically |
| **3** | 🎓 **Exam Consistency Check** | Verify answer sheets match question bank before analysis |

### Key New Tools

```bash
# Remember question banks across time
python3 question_bank_registry.py --register july12
python3 question_bank_registry.py --find-matches july26
python3 question_bank_registry.py --list

# Interactive PDF → Answer sheet mapping
python3 map_questions_to_answers.py --batch july26

# Detect exam consistency & groupings
python3 detect_exam_consistency.py --batch july26

# Fuzzy filename matching debug
python3 fuzzy_file_matcher.py --batch july26
```

### Real Scenario (Why This Matters)

```
Month 1, Week 1: Upload 5 question banks (CISSP, CompTIA, AWS, GCP, Azure)
                 python3 question_bank_registry.py --register qbanks_july

Month 1, Week 2: Program A submits 100 answer sheets for CISSP exam
                 python3 question_bank_registry.py --find-matches program_a
                 → System auto-suggests CISSP_Exam.pdf from 1 week ago ✓

Month 1, Week 3: Program B submits 80 answer sheets for CompTIA exam
                 python3 question_bank_registry.py --find-matches program_b
                 → System auto-suggests CompTIA_Security+.pdf from 2 weeks ago ✓

Month 2, Week 1: Program A retakes CISSP (new 100 students)
                 python3 question_bank_registry.py --find-matches program_a_round2
                 → System recognizes CISSP_Exam.pdf (now used in 2 batches) ✓
                 → NO re-uploading needed!
```

### Comprehensive Documentation (New)

Start here for complete workflows:
- 📖 **[START_HERE.md](START_HERE.md)** ← Begin here! Day 1 to ongoing use
- 📖 **[QUICK_WORKFLOW_GUIDE.md](QUICK_WORKFLOW_GUIDE.md)** - First-time setup vs recurring
- 📖 **[PERSISTENT_QUESTION_BANK_REGISTRY.md](PERSISTENT_QUESTION_BANK_REGISTRY.md)** - Registry deep dive
- 📖 **[MULTI_QUESTION_BANK_SCENARIO.md](MULTI_QUESTION_BANK_SCENARIO.md)** - 3+ to 10+ different banks
- 📖 **[COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)** - All 6 layers working together
- 📖 **[INTERACTIVE_MAPPING_GUIDE.md](INTERACTIVE_MAPPING_GUIDE.md)** - PDF ↔ Answer sheet mapping

---

## Main Menu Options Explained

When you run `python3 analyze.py`, you see 3 choices:

| Option | Use Case | Input |
|--------|----------|-------|
| **[1] Batch Analysis** | Multiple students in one exam | Exam PDF + Excel with multiple students |
| **[2] Standalone Analysis** | Single student, one-time exam | Exam PDF + Single student answers |
| **[3] Full Batch Workflow** | Complete pipeline with validation | Same as [1] + auto-fix + consolidation |

Choose based on your needs. See section above for examples.

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
python3 analyze.py
# Select: Standalone Analysis → Single Student Mode
```

Output:
```
outputs/CISSP_Individual_Report_StudentName.xlsx
```

### Second Exam (Progress Tracking)
```bash
python3 analyze.py
# Select: Standalone Analysis → Comparative Mode (with history)
# Tool auto-detects previous exam and tracks progress
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

## Multiple Students / Batch Analysis

Analyze multiple students at once:

```bash
python3 analyze.py
# Select: Batch Analysis (Multiple students in cohort)
# Provide exam PDF and student answers Excel file
```

Output (one report per student):
```
outputs/CISSP_Individual_Report_John.xlsx
outputs/CISSP_Individual_Report_Jane.xlsx
outputs/CISSP_Individual_Report_Bob.xlsx
outputs/CISSP_Class_Report.xlsx  ← Compare all students
```

---

## Requirements

- **Python:** 3.9, 3.10, 3.11, or 3.12
- **Packages:** pandas, openpyxl, pypdf (auto-installed via `pip install -r requirements.txt`)
- **Time:** Installation = 2 min, Analysis = 10-15 sec per exam
- **AI:** None needed - pure data analysis

---

## Files You Need

### MINIMUM (To Run Any Analysis)
1. **Exam PDF** - Your test file with questions (example: `exam.pdf`)
2. **Student Answers Excel** - Student responses in Excel format (see EXAMPLE_student_answers.xlsx)

### OPTIONAL (For Advanced Features)
3. **Domain Mapping JSON** - Already included for CISSP exams
4. **student_roster.json** - Only needed for [1] Batch Analysis option

### Correct Excel Format

**Column headers = Student names, Rows = Answers (A/B/C/D)**

Example:
| Question | John Doe | Jane Smith |
|----------|----------|-----------|
| Q1 | A | B |
| Q2 | B | A |
| Q3 | C | C |
| Q4 | D | D |

**See EXAMPLE_student_answers.xlsx for real example**
**See FORMATS_AND_TEMPLATES_GUIDE.md for all accepted formats**

---

## Detailed Setup

**Platform-specific installation commands:**
- 👉 See [INSTALLATION_COMMANDS.md](INSTALLATION_COMMANDS.md) for macOS, Windows (CMD), and Windows (PowerShell)

**Quick reference card (printable):**
- 👉 See [QUICK_SETUP_CARD.txt](QUICK_SETUP_CARD.txt)

**Complete documentation index:**
- 👉 See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for all guides and learning paths

**Download templates and examples:**
- 👉 See [WHERE_TO_DOWNLOAD_TEMPLATES.md](WHERE_TO_DOWNLOAD_TEMPLATES.md)

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

All components are thoroughly tested:
```bash
pytest -v
# Result: 279 passed, 2 skipped (comprehensive coverage across all modules)
```

Tests cover:
- ✅ Environment validation (12 tests)
- ✅ Question bank registry (persistence & fingerprinting)
- ✅ Fuzzy filename matching (flexible file grouping)
- ✅ Sheet variation detection (Excel naming patterns)
- ✅ Exam consistency detection (grouping & validation)
- ✅ Interactive mapping (PDF → Answer sheet confirmation)
- ✅ PDF extraction & parsing
- ✅ Excel parsing (multiple formats)
- ✅ Question mapping & metadata
- ✅ Performance analysis (5 dimensions)
- ✅ Report generation (7-sheet format)
- ✅ Error handling & edge cases (15+ scenarios)
- ✅ Input format variations (40+ formats)
- ✅ Integration across all modules
- ✅ Performance benchmarks

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
├── README.md                                  ← You are here
├── check_setup.py                            ← RUN THIS FIRST! (verify setup)
├── INSTALLATION_COMMANDS.md                   ← Platform-specific setup
├── QUICK_SETUP_CARD.txt                      ← 7-step quick start
├── DOCUMENTATION_INDEX.md                    ← Master documentation index
├── WORKFLOW_OVERVIEW.md                      ← 5-step process explanation
├── FORMATS_AND_TEMPLATES_GUIDE.md            ← All input formats
├── NAMING_CONVENTIONS_AND_FORMATS.md         ← Naming rules
├── WHERE_TO_DOWNLOAD_TEMPLATES.md            ← Download guide
├── requirements.txt                          ← Dependencies
├── analyze.py                                ← Main entry point (run this!)
├── analyze_standalone.py                     ← Standalone analysis mode
├── analyze_dec25.py                          ← Dec-25 batch analysis (pre-configured)
├── analyze_july26.py                         ← July-26 batch analysis (pre-configured)
│
├── cissp_analyzer/                           ← Source code modules
│   ├── pdf_parser.py                         ← Reads exam PDF
│   ├── excel_parser.py                       ← Reads student answers
│   ├── domain_mapper.py                      ← Question metadata
│   ├── analysis_engine.py                    ← Performance analysis
│   ├── adaptive_plan_generator.py            ← Study recommendations
│   ├── individual_report_gen.py              ← Creates 7-sheet report
│   ├── class_report_gen.py                   ← Compares students
│   ├── interactive_cli.py                    ← CLI interface
│   ├── main.py                               ← Orchestrator
│   └── dependency_checker.py                 ← Environment validation
│
├── data/                                     ← Question mappings
│   └── question_domain_mapping.json          ← 125 CISSP questions
│
├── EXAMPLE_answer_key.json                   ← 30 sample questions (JSON)
├── EXAMPLE_answer_key.csv                    ← 30 sample questions (CSV)
├── EXAMPLE_student_answers.xlsx              ← 4 students, 20 questions (USE THIS!)
├── EXAMPLE_FILES_HOW_TO_USE.md               ← How to expand examples
├── TEMPLATE_answer_key.json                  ← Blank JSON template
├── TEMPLATE_student_answers.md               ← Excel format guide
├── TEMPLATE_directory_structure.md           ← Project setup guide
├── TEMPLATE_REFERENCE.txt                    ← Template overview
│
└── tests/                                    ← Test suite (277 tests)
    ├── test_environment_validation.py
    ├── test_analysis_engine.py
    ├── test_adaptive_plan_generator.py
    ├── test_input_formats.py
    ├── test_error_handling.py
    ├── test_integration.py
    └── ... (additional test modules)
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

## Troubleshooting

### Problem: "FileNotFoundError: student_roster.json"
**Cause:** You selected [1] Batch Analysis but don't have the batch setup files.
**Solution:** 
1. For first-time use, select [2] Standalone Analysis instead
2. For batch analysis, read [TEMPLATE_directory_structure.md](TEMPLATE_directory_structure.md)

### Problem: "FileNotFoundError: No such file or directory: 'exam.pdf'"
**Cause:** The exam PDF doesn't exist at the path you provided.
**Solution:**
1. Check the file path is correct
2. Make sure the file exists: `ls -la path/to/file.pdf`
3. Try using the full path: `/Users/yourname/Downloads/exam.pdf`

### Problem: "FileNotFoundError: (Errno 2) No such file or directory: '.../answers.xlsx'"
**Cause:** The student answers Excel file doesn't exist.
**Solution:**
1. Check the file path is correct
2. Try using EXAMPLE_student_answers.xlsx first to verify the format
3. Make sure your Excel file matches the format in [FORMATS_AND_TEMPLATES_GUIDE.md](FORMATS_AND_TEMPLATES_GUIDE.md)

### Problem: "KeyError: column 'StudentName' not found"
**Cause:** Column names in Excel don't match student names in the mapping.
**Solution:**
1. Open EXAMPLE_student_answers.xlsx and check the format
2. Make sure your Excel column headers are student names
3. See [FORMATS_AND_TEMPLATES_GUIDE.md](FORMATS_AND_TEMPLATES_GUIDE.md) for details

### Problem: "pytest shows fewer than 277 passed"
**Cause:** Some tests are being skipped (usually 4 skipped is normal).
**Solution:**
1. Run: `pytest -v` to see details
2. 277 passed + 4 skipped = healthy test suite
3. If you see failures, check your Python version: `python3 --version` (need 3.9+)

### Before Asking for Help

Run these checks:
```bash
# 1. Verify setup
python3 check_setup.py

# 2. Verify tests pass
pytest -v

# 3. Check Python version
python3 --version

# 4. Check required packages
pip list | grep -E "pandas|openpyxl|pypdf"

# 5. Verify file exists
ls -la your_exam_file.pdf
ls -la your_student_answers.xlsx
```

If all pass and you still have issues:
1. Read [FORMATS_AND_TEMPLATES_GUIDE.md](FORMATS_AND_TEMPLATES_GUIDE.md) for file format help
2. Check [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for more resources
3. Open an issue on GitHub with the error message

---

## Installation Issues?

If you get stuck during installation:
1. Make sure Python 3.9+ is installed: `python3 --version`
2. Make sure pip is installed: `python3 -m pip --version`
3. Reinstall packages: `pip install -r requirements.txt --force-reinstall`
4. See [INSTALLATION_COMMANDS.md](INSTALLATION_COMMANDS.md) for detailed platform-specific troubleshooting

---

## License

MIT License - Free to use for any purpose

---

## Questions?

**NEW: Complete Onboarding Guides (v1.0.1)**
- 🚀 Start with **[START_HERE.md](START_HERE.md)** - Day 1 setup through ongoing use
- 📋 Then **[QUICK_WORKFLOW_GUIDE.md](QUICK_WORKFLOW_GUIDE.md)** - First-time vs recurring
- 📚 Then **[COMPLETE_SOLUTION_SUMMARY.md](COMPLETE_SOLUTION_SUMMARY.md)** - All features overview

**Setup & Format Help**
- 📖 Read [INSTALLATION_COMMANDS.md](INSTALLATION_COMMANDS.md) for platform-specific setup
- 📖 Read [QUICK_SETUP_CARD.txt](QUICK_SETUP_CARD.txt) for quick start (printable)
- 📖 Read [FORMATS_AND_TEMPLATES_GUIDE.md](FORMATS_AND_TEMPLATES_GUIDE.md) for data format help
- 📖 Read [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete guide index
- 📖 Check test files (`tests/`) for code examples
- 🐛 Open an issue if something doesn't work

---

**Ready to analyze exams? Run:** `python3 analyze.py`

---

**Version:** 1.0.1 | **Last Updated:** July 13, 2026 | **Tests:** 279/279 Passing | **Status:** Production Ready | **New Features:** Question Bank Registry, Fuzzy Matching, Interactive Mapping
