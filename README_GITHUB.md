# CISSP Analyzer

**Automated CISSP exam analysis system with intelligent scoring, performance tracking, and adaptive recommendations.**

Perfect for:
- ✓ Managing CISSP exam cohorts (Dec-25, July-26, etc.)
- ✓ Individual student analysis (make-up exams, new students)
- ✓ Automatic data quality detection and fixing
- ✓ Performance trends across multiple exams
- ✓ Class-level analytics and insights

---

## Quick Start (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data
```
exams/
├── july26_week1.pdf          # Exam PDF with questions + answers
├── july26_week2.pdf
└── ...

answers/july26_batch/
├── student1_week1.xlsx       # Student answer files
├── student2_week1.xlsx
├── student1_week2.xlsx
└── ...
```

### 3. Run Analysis
```bash
python3 analyze.py
```

Then choose:
- **[1]** Batch Analysis (multiple students)
- **[2]** Standalone Analysis (single student)
- **[3]** Full Batch Workflow (automated everything)

---

## How It Works

### Smart Routing
You don't need to know batch names or complex config. Just run `analyze.py` and choose what you want to do.

```
┌─────────────────────────────┐
│   python3 analyze.py        │
└────────────┬────────────────┘
             │
      ┌──────┴──────┐
      │             │
   Batch       Standalone
   │              │
   │              └─→ Single student analysis
   │
   └─→ Multiple students
       ├─ Auto-validates
       ├─ Auto-fixes data issues
       ├─ Consolidates answers
       ├─ Scores all students
       └─ Generates reports
```

### Automatic Data Quality Fixes

The system automatically handles common issues:

| Issue | Example | Auto-Fixed? |
|-------|---------|-----------|
| Column name variations | `Q.NO` → `Question` | ✓ Yes |
| Answer format | `1b, 2a, 3c` → `1-B,2-A,3-C` | ✓ Yes |
| Lowercase answers | `a, b, c` → `A, B, C` | ✓ Yes |
| Extra whitespace | `1b , 2a , 3c` → `1-B,2-A,3-C` | ✓ Yes |

**You don't need to fix data manually** — the system handles it automatically.

---

## Usage Modes

### Mode 1: Batch Analysis (Multiple Students)

**Best for:** Analyzing a cohort (Dec-25, July-26, etc.)

```bash
python3 analyze.py
# Choose [1] Batch Analysis
# Enter batch name: july26
```

**What it does:**
1. Validates exam PDFs
2. Auto-fixes student answer files
3. Consolidates all answers
4. Scores each student
5. Generates individual + class reports

**Output:**
```
reports/july26_results/
├── week1/
│   ├── CISSP_Individual_Report_Student1.xlsx
│   ├── CISSP_Individual_Report_Student2.xlsx
│   └── CISSP_Class_Analysis.xlsx
├── week2/
│   ├── CISSP_Individual_Report_Student1.xlsx
│   ├── CISSP_Individual_Report_Student2.xlsx
│   └── CISSP_Class_Analysis.xlsx
└── ...
```

### Mode 2: Standalone Analysis (Single Student)

**Best for:** One-time exams, make-ups, new students

```bash
python3 analyze.py
# Choose [2] Standalone Analysis
# Follow interactive prompts
```

**What it asks:**
- Student name
- Exam PDF location
- Student answer file location

**Output:**
```
output/<StudentName>/
└── CISSP_Individual_Report_<StudentName>.xlsx
```

### Mode 3: Full Batch Workflow

**Best for:** Complete automated pipeline with validation

```bash
python3 analyze.py
# Choose [3] Full Batch Workflow
# Enter batch name: july26
```

**What it includes:**
1. **Validate** exam PDFs
2. **Auto-Fix** data quality issues
3. **Consolidate** student answers
4. **Analyze** each student
5. **Verify** output reports

**Handles everything automatically** — no manual steps.

---

## Manual Entry Points (Advanced)

If you prefer, you can run specific scripts directly:

```bash
# Batch-specific analysis (if script exists)
python3 analyze_july26.py

# Automated workflow
python3 run_batch_workflow.py --batch july26 --full

# Individual tools (if needed)
python3 auto_fix_answers.py --batch july26
python3 consolidate_answers.py --batch july26
python3 analyze_standalone.py
```

---

## Report Formats

### Individual Report (9 Sheets)
Each student gets:
- **Performance Summary** - Overall score, accuracy, status
- **Q&A Breakdown** - Question-by-question analysis
- **By Question Type** - Multiple choice vs complex questions
- **By Exam Tricks** - Tricky questions performance
- **By Domain** - Security+Trust+Risk, etc.
- **By Difficulty** - Easy/Medium/Hard breakdown
- **Study Plan** - Personalized recommendations
- **Progress Over Time** - Trends across exams
- **Adaptive Study Plan** - AI-suggested focus areas

### Class Report (4 Sheets)
For the entire cohort:
- **Class Overview** - Class metrics and averages
- **Student Rankings** - Individual scores ranked
- **Weakness Analysis** - Common problem areas
- **Topic Analysis** - Performance by domain

---

## Data Formats

### Expected Answer Key (JSON)
```json
{
  "1": "A",
  "2": "B",
  "11": "1-C,2-D,3-B,4-A",
  "43": "1-B,2-A,3-C",
  "109": "A,C,B,D",
  "125": "D"
}
```

**Formats supported:**
- Single answers: `"A"`, `"B"`, `"C"`, `"D"`
- Matching questions: `"1-C,2-D,3-B,4-A"` (4 or 5 items)
- Ordering questions: `"A,C,B,D"` (any order)

### Student Answer File (Excel)
```
Question | StudentName
---------|------------
1        | A
2        | B
3        | D
...      | ...
125      | C
```

**Column names:**
- First column: `Question`, `Q.NO`, `Q`, `Questions`
- Second column: Student name (or `Answer`, `Answers`, `Answer options`)

The system auto-normalizes these.

---

## Setup for New Batch

### Step 1: Create Batch Folder
```bash
mkdir -p answers/august26_batch
```

### Step 2: Add Exam PDFs
```bash
cp exam_week1.pdf exams/august26_week1.pdf
cp exam_week2.pdf exams/august26_week2.pdf
```

### Step 3: Add Student Files
```bash
cp student_responses/*.xlsx answers/august26_batch/
```

### Step 4: Update Roster (Optional)
Edit `student_roster.json` to add batch metadata:
```json
{
  "batches": {
    "august26_batch": {
      "id": "AUG26",
      "name": "August-26 Batch",
      "status": "active",
      "start_date": "2026-08-01",
      "exams": ["week1", "week2"],
      "students": [
        {
          "id": "STU001",
          "name": "StudentName",
          "email": "student@example.com",
          "enrollment_date": "2026-08-01",
          "files": {
            "week1": "answers/august26_batch/student_week1.xlsx",
            "week2": "answers/august26_batch/student_week2.xlsx"
          }
        }
      ]
    }
  }
}
```

### Step 5: Run Analysis
```bash
python3 analyze.py
# Choose [1] Batch Analysis
# Enter batch name: august26
```

---

## Troubleshooting

### "File not found" errors
**Check:**
- Exam PDFs are in `exams/` folder
- Student files are in `answers/<batch>/` folder
- File paths in `student_roster.json` are correct

### "No answer key found" warning
**This is normal!** The system will:
1. Try to load `exams/<exam>_answer_key.json`
2. If not found, extract from PDF (if available)
3. If neither, use auto-extracted standard answers

**To fix:**
```bash
# Create answer key interactively
python3 quick_answer_key.py create --exam july26_week1
```

### Scores showing 0% or incorrect
**Check:**
- Answer key JSON has all 125 questions
- Student answer files match expected format
- Run auto-fix tool: `python3 auto_fix_answers.py --batch july26`

### Data quality warnings
**Normal!** The system detects and reports issues but continues. To auto-fix:
```bash
python3 auto_fix_answers.py --batch july26
```

---

## Features

✅ **Automatic** - One command, handles everything  
✅ **Smart** - Auto-detects and fixes data issues  
✅ **Flexible** - Works with any batch name or cohort  
✅ **Comprehensive** - 9-sheet individual + 4-sheet class reports  
✅ **Adaptive** - Personalized recommendations per student  
✅ **Scalable** - Handles 5 to 500+ students  
✅ **Production-Ready** - Thoroughly tested and documented  

---

## Requirements

- Python 3.8+
- pandas
- openpyxl
- pypdf

All specified in `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
cissp-analyzer/
├── analyze.py                 # ⭐ Master entry point (start here!)
├── analyze_standalone.py      # Single student analysis
├── analyze_dec25.py          # Dec-25 batch (template)
├── analyze_july26.py         # July-26 batch (template)
├── run_batch_workflow.py     # Full automated workflow
├── auto_fix_answers.py       # Data quality auto-fix
├── consolidate_answers.py    # Answer file consolidation
│
├── cissp_analyzer/
│   ├── main.py              # Core analyzer engine
│   ├── pdf_parser.py        # PDF extraction
│   ├── excel_parser.py      # Excel reading
│   ├── data_quality_validator.py  # Data validation + auto-fix
│   ├── analysis_engine.py   # Scoring logic
│   ├── individual_report_gen.py   # Student reports
│   ├── class_report_gen.py  # Class reports
│   └── ...
│
├── exams/                   # Exam PDFs + answer keys
├── answers/                 # Student answer files
├── reports/                 # Generated Excel reports
├── data/                    # Domain mappings, question data
└── requirements.txt         # Python dependencies
```

---

## How to Start

### First Time?
```bash
python3 analyze.py --help
```

### Ready to analyze?
```bash
python3 analyze.py
```

### Got a specific batch?
```bash
python3 run_batch_workflow.py --batch july26 --full
```

---

## Questions or Issues?

1. **Check the logs** - Detailed error messages guide you
2. **Read the data quality report** - Shows what was fixed
3. **Check `reports/` folder** - Verify Excel files were created
4. **Review `student_roster.json`** - Ensure batch is configured

---

## License

This project is designed for CISSP exam analysis and educational use.

---

**Ready to analyze? Run:**
```bash
python3 analyze.py
```

**That's it! The system handles the rest.** 🚀
