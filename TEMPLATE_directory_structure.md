# CISSP Analyzer - Directory Structure Template

## Recommended Project Layout

```
your_cissp_project/
│
├── README.md (your project documentation)
├── requirements.txt (if customizing)
│
├── exams/                          # Exam PDFs and answer keys
│   ├── exam_1_week1.pdf
│   ├── exam_1_week1_answer_key.json
│   ├── exam_2_week2.pdf
│   ├── exam_2_week2_answer_key.json
│   ├── exam_3_practice.pdf
│   └── exam_3_practice_answer_key.json
│
├── answers/                        # Student answer sheets
│   ├── batch_dec25/
│   │   ├── exam_1_batch_dec25.xlsx
│   │   ├── exam_2_batch_dec25.xlsx
│   │   └── exam_3_batch_dec25.xlsx
│   │
│   ├── batch_july26/
│   │   ├── exam_1_batch_july26.xlsx
│   │   ├── exam_2_batch_july26.xlsx
│   │   └── exam_3_batch_july26.xlsx
│   │
│   └── standalone/                # Individual/ad-hoc tests
│       ├── practice_exam_alice.xlsx
│       ├── practice_exam_bob.xlsx
│       └── retake_exam_carol.xlsx
│
├── students/                       # (Auto-generated) Student history
│   ├── Alice/
│   │   ├── exam_1_performance.json
│   │   ├── exam_2_performance.json
│   │   └── exam_3_performance.json
│   │
│   ├── Bob/
│   │   ├── exam_1_performance.json
│   │   └── exam_2_performance.json
│   │
│   └── Carol/
│       ├── exam_1_performance.json
│       ├── exam_2_performance.json
│       └── exam_3_performance.json
│
└── outputs/                        # Generated reports
    ├── batch_dec25/
    │   ├── CISSP_Class_Report_Dec25.xlsx
    │   ├── CISSP_Individual_Report_Alice.xlsx
    │   ├── CISSP_Individual_Report_Bob.xlsx
    │   └── CISSP_Individual_Report_Carol.xlsx
    │
    ├── batch_july26/
    │   ├── CISSP_Class_Report_July26.xlsx
    │   ├── CISSP_Individual_Report_Alice.xlsx
    │   └── ...
    │
    └── standalone/
        ├── Alice/
        │   ├── CISSP_Individual_Report_Alice_Exam1.xlsx
        │   ├── CISSP_Individual_Report_Alice_Exam2.xlsx
        │   └── CISSP_Individual_Report_Alice_Exam3.xlsx
        │
        └── Bob/
            └── CISSP_Individual_Report_Bob_Exam1.xlsx
```

---

## Folder Descriptions

### `/exams/` - Exam Materials
**Purpose:** Store exam PDFs and answer keys  
**Organization:** One PDF + one JSON file per exam

**File Naming Convention:**
```
exam_[NUMBER]_[DESCRIPTION].pdf
exam_[NUMBER]_[DESCRIPTION]_answer_key.json

Examples:
exam_1_week1.pdf
exam_1_week1_answer_key.json

exam_2_week2_midterm.pdf
exam_2_week2_midterm_answer_key.json

exam_3_practice_test.pdf
exam_3_practice_test_answer_key.json
```

**Naming Rules:**
- Use underscores, not spaces
- All lowercase
- Question number at start (exam_1, exam_2, exam_3, etc.)
- Optional description after underscore (week1, midterm, practice, etc.)
- Answer key file must match PDF name with "_answer_key.json" suffix

---

### `/answers/` - Student Answer Sheets
**Purpose:** Store student responses for each exam and batch

**Sub-folders:**
```
batch_[BATCH_NAME]/     → Cohort-based exams (entire class)
  exam_1_batch_dec25.xlsx
  exam_2_batch_dec25.xlsx

standalone/             → Individual/ad-hoc exams
  practice_exam_alice.xlsx
  retake_exam_bob.xlsx
```

**File Naming Convention:**
```
exam_[NUMBER]_batch_[BATCH_NAME].xlsx
OR
[DESCRIPTION]_exam_[STUDENT_NAME].xlsx

Examples:
exam_1_batch_dec25.xlsx
exam_2_batch_july26.xlsx
practice_exam_alice.xlsx
retake_exam_bob.xlsx
```

**Important:**
- Each Excel file can contain multiple student columns
- File must be .xlsx format (not .xls or .csv)
- Keep exams separated by batch or purpose
- Use descriptive names for standalone exams

---

### `/students/` - Auto-Generated Student History
**Purpose:** Store student performance history for comparative analysis

**Auto-Created By:** CISSP Analyzer tool  
**Do Not Manually Edit:** These files are auto-generated

**Structure:**
```
students/
├── [Student Name]/
│   ├── exam_1_performance.json
│   ├── exam_2_performance.json
│   └── exam_3_performance.json
```

**File Format (Auto-Generated):**
```json
{
  "exam_number": 1,
  "student_name": "Alice",
  "date_analyzed": "2026-07-04T15:30:00",
  "score_percentage": 78.5,
  "correct_count": 98,
  "wrong_count": 27,
  "by_domain": {
    "Security Architecture & Design": 0.82,
    "Security Operations": 0.76,
    ...
  },
  "by_difficulty": {
    "easy": 0.85,
    "medium": 0.78,
    "hard": 0.72
  },
  "by_question_type": {
    "multiple_choice": 0.78,
    "complex": 0.79
  },
  "wrong_question_ids": [5, 12, 23, 45, ...]
}
```

**When Used:**
- Automatically loaded for comparative analysis
- Compared with current exam results
- Shows progress/improvement trends
- Feeds adaptive recommendations

---

### `/outputs/` - Generated Reports
**Purpose:** Store all analysis results

**Sub-folders by Analysis Type:**

#### Batch Analysis Reports
```
outputs/batch_[BATCH_NAME]/
├── CISSP_Class_Report_[BATCH_NAME].xlsx (overall class stats)
├── CISSP_Individual_Report_[STUDENT_NAME].xlsx (per-student)
├── CISSP_Individual_Report_[STUDENT_NAME].xlsx
└── ...
```

#### Standalone Analysis Reports
```
outputs/standalone/
├── [Student Name]/
│   ├── CISSP_Individual_Report_[Name]_Exam1.xlsx
│   ├── CISSP_Individual_Report_[Name]_Exam2.xlsx
│   └── CISSP_Individual_Report_[Name]_Exam3.xlsx
└── ...
```

**Report File Structure:**
Each Excel report has 9 sheets:
1. **Performance Summary** - Overall score, pass/fail status
2. **Domain Breakdown** - Performance by security domain
3. **Topic Analysis** - Performance by topic within domain
4. **Difficulty Progression** - Easy/Medium/Hard questions
5. **Question Type Analysis** - Multiple choice vs complex
6. **Question Analysis** - Wrong questions with context
7. **Exam Trick Analysis** - Tricky vs normal questions
8. **Progress Over Time** (comparative mode only) - Trend analysis
9. **Recommendations** - Adaptive study plan

---

## Setup Instructions

### Step 1: Create Directory Structure
```bash
cd /path/to/your/project

# Create main folders
mkdir -p exams answers students outputs

# Create batch subfolders
mkdir -p answers/batch_dec25 answers/batch_july26 answers/standalone
mkdir -p outputs/batch_dec25 outputs/batch_july26 outputs/standalone
```

### Step 2: Add Exam Materials
```bash
# Copy exam PDFs to exams/
cp exam_1.pdf exams/exam_1_week1.pdf
cp exam_2.pdf exams/exam_2_week2.pdf

# Create or add answer keys
# See TEMPLATE_answer_key.json for format
cp answer_key_1.json exams/exam_1_week1_answer_key.json
cp answer_key_2.json exams/exam_2_week2_answer_key.json
```

### Step 3: Add Student Answer Sheets
```bash
# Copy Excel files to appropriate folder
cp class_responses_dec.xlsx answers/batch_dec25/exam_1_batch_dec25.xlsx
cp class_responses_july.xlsx answers/batch_july26/exam_1_batch_july26.xlsx
```

### Step 4: Run Analysis
```bash
cd /path/to/your/project
python3 /path/to/cissp-analyzer/analyze.py

# Or use standalone mode
python3 /path/to/cissp-analyzer/analyze_standalone.py
```

---

## Naming Convention Rules

### Do ✅
```
exam_1_week1.pdf                      ✓ Clear
exam_2_midterm.pdf                    ✓ Descriptive
batch_dec25_answers.xlsx              ✓ Organized
alice_exam1_responses.xlsx            ✓ Specific
```

### Don't ❌
```
Exam 1.pdf                            ✗ Spaces & capital
EXAM_1_WEEK_1_CISSP.pdf               ✗ Too long & all caps
answers 1 (final).xlsx                ✗ Spaces & parens
exam(1).pdf                           ✗ Special chars
```

### Rules
1. Use lowercase letters
2. Use underscores for spacing (not hyphens in middle)
3. No spaces in filenames
4. No special characters except underscore
5. Include exam number and batch name
6. Keep under 50 characters

---

## Batch vs Standalone Organization

### Batch Analysis (Cohort-Based)
```
answers/batch_dec25/
├── exam_1_batch_dec25.xlsx (50 students, columns: Name | Student1 | Student2 | ...)
├── exam_2_batch_dec25.xlsx
└── exam_3_batch_dec25.xlsx

outputs/batch_dec25/
├── CISSP_Class_Report_Dec25.xlsx (aggregate stats)
├── CISSP_Individual_Report_Alice.xlsx
├── CISSP_Individual_Report_Bob.xlsx
└── ...
```

**Use When:**
- Entire class/cohort taking same exam
- 20+ students per exam
- Want class-level analytics
- Need aggregate statistics

### Standalone Analysis (Individual)
```
answers/standalone/
├── alice_exam1_practice.xlsx
├── bob_exam1_practice.xlsx
├── alice_exam2_retake.xlsx
└── ...

outputs/standalone/
├── Alice/
│   ├── CISSP_Individual_Report_Alice_Exam1.xlsx
│   └── CISSP_Individual_Report_Alice_Exam2.xlsx
├── Bob/
│   └── CISSP_Individual_Report_Bob_Exam1.xlsx
└── ...
```

**Use When:**
- Individual practice tests
- Students taking exams at different times
- Retake examinations
- 1-10 students per exam
- Ad-hoc testing

---

## Example: Setting Up for Your First Run

### Create Structure
```bash
mkdir -p exams answers/batch_dec25 students outputs/batch_dec25
```

### Add Files
```bash
# Exam materials
exams/
├── exam_1_week1.pdf
└── exam_1_week1_answer_key.json

# Student answers
answers/batch_dec25/
└── exam_1_batch_dec25.xlsx

# Run analysis
python3 analyze.py
  → Choose [1] Batch Analysis
  → Select batch_dec25
  → Choose exam_1_week1
  → Specify answer file: answers/batch_dec25/exam_1_batch_dec25.xlsx
  → Output: outputs/batch_dec25/

# Results
outputs/batch_dec25/
├── CISSP_Class_Report_Dec25.xlsx
├── CISSP_Individual_Report_Student1.xlsx
├── CISSP_Individual_Report_Student2.xlsx
└── ...

students/
├── Student1/
│   └── exam_1_performance.json
├── Student2/
│   └── exam_1_performance.json
└── ...
```

---

## Quick Reference

| Scenario | Folder | Filename | Mode |
|----------|--------|----------|------|
| Class exam | answers/batch_dec25/ | exam_1_batch_dec25.xlsx | Batch |
| Individual retake | answers/standalone/ | alice_retake_exam1.xlsx | Standalone |
| Second exam (same class) | answers/batch_dec25/ | exam_2_batch_dec25.xlsx | Batch |
| Practice test | answers/standalone/ | bob_practice_exam3.xlsx | Standalone |
| New batch cohort | answers/batch_july26/ | exam_1_batch_july26.xlsx | Batch |

---

## Troubleshooting

### Problem: "Cannot find exam file"
**Solution:**
1. Check file is in `/exams/` folder
2. Verify filename exactly matches (case-sensitive)
3. Use relative path: `exams/exam_1_week1.pdf`

### Problem: "Cannot find answer key"
**Solution:**
1. Ensure answer key JSON in same folder as PDF
2. Filename must be: `exam_[NUMBER]_[DESC]_answer_key.json`
3. Check JSON is valid: use online JSON validator

### Problem: "Student not found in results"
**Solution:**
1. Check student name in Excel exactly matches CLI input
2. Verify Excel column has student name in header
3. No extra spaces: "Alice" not " Alice " or "alice"

### Problem: "Scores showing as 0%"
**Solution:**
1. Verify answer key has all 125 answers
2. Check student answer count = 125 rows
3. Ensure answers are only A, B, C, D

---

## Best Practices

1. **Keep exams and answers organized** - Use batch folders
2. **Use descriptive names** - "exam_2_midterm_week8" is better than "exam2"
3. **Don't edit student history** - Let tool manage /students/ folder
4. **Backup before batch runs** - Keep copies of Excel files
5. **Use same folder structure** - Makes analysis consistent
6. **Document your batches** - Add README in each batch folder
7. **Archive old runs** - Move old outputs to archive/ periodically

---

**Version:** 1.0  
**Last Updated:** July 4, 2026  
**Status:** Production Ready
