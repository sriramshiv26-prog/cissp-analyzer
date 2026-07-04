# Naming Conventions & Formats Guide

**Version:** 1.0 | **Date:** July 4, 2026 | **Status:** Production Ready

---

## Overview: Data Flow

```
CISSP Exam (PDF) 
    ↓ Extract Answers
Answer Key (JSON or CSV)
    +
Student Responses (Excel or CSV)
    ↓ Analyze
Reports (Excel with 9 sheets)
```

---

## Format Guide: What Goes Where

### Format 1: Exam Questions
**File Format:** PDF  
**Source:** Your CISSP exam document  
**Contains:** Questions (tool reads PDF text for reference)

**File Naming:**
```
exam_[NUMBER]_[DESCRIPTION].pdf

✓ Good:
  exam_1_week1.pdf
  exam_2_midterm.pdf
  exam_3_practice.pdf
  exam_1_cissp_domain1.pdf

✗ Bad:
  Exam 1.pdf
  CISSP EXAM 1 (FINAL).pdf
  exam (1).pdf
  questions_1.pdf
```

**Where It Goes:**
```
your_project/exams/exam_1_week1.pdf
```

**Example:**
```bash
your_project/
└── exams/
    ├── exam_1_week1.pdf          ← Your PDF exam document
    ├── exam_2_week2.pdf
    └── exam_3_practice.pdf
```

---

### Format 2: Answer Key
**File Format:** JSON or CSV  
**Source:** Either extracted from PDF or created manually  
**Contains:** 125 correct answers + explanations

#### Option A: Answer Key as JSON
**File Naming:**
```
exam_[NUMBER]_[DESCRIPTION]_answer_key.json

✓ Good:
  exam_1_week1_answer_key.json
  exam_2_midterm_answer_key.json
  exam_3_practice_answer_key.json

✗ Bad:
  answer_key_1.json
  answers_exam_1.json
  key_exam_1.json
  exam_1_key.json
```

**MUST Match:** Answer key must match exam PDF filename
```
exam_1_week1.pdf              → exam_1_week1_answer_key.json        ✓ Match
exam_2_midterm.pdf            → exam_2_midterm_answer_key.json      ✓ Match
exam_1_week1.pdf              → exam_1_answer_key.json              ✗ No match
```

**File Format (JSON):**
```json
{
  "1": {
    "letter": "A",
    "text": "Full explanation of why A is correct"
  },
  "2": {
    "letter": "B",
    "text": "Full explanation of why B is correct"
  },
  ...
  "125": {
    "letter": "D",
    "text": "Explanation for question 125"
  }
}
```

**File Size:** ~50-100 KB (for 125 questions with explanations)

**Where It Goes:**
```
your_project/exams/exam_1_week1_answer_key.json
                       ↑
                       Must be same folder as PDF
```

#### Option B: Answer Key as CSV
**File Naming:**
```
exam_[NUMBER]_[DESCRIPTION]_answer_key.csv

✓ Good:
  exam_1_week1_answer_key.csv
  exam_2_midterm_answer_key.csv

✗ Bad:
  answers_1.csv
  answer_key_exam1.csv
```

**File Format (CSV):**
```
Question,Answer,Explanation
1,A,AES uses 128-bit, 192-bit, or 256-bit encryption
2,B,Public key infrastructure enables digital certificates
3,C,Defense in depth uses multiple layers of controls
...
125,D,Final question explanation
```

**When to Use CSV:**
- Easier to edit in Excel
- Better for team collaboration
- Before converting to JSON
- For documentation/reference

**Convert CSV to JSON:**
```bash
python3 << 'EOF'
import csv, json

# Read CSV
with open('exam_1_week1_answer_key.csv', 'r') as f:
    reader = csv.DictReader(f)
    answer_key = {}
    for row in reader:
        answer_key[row['Question']] = {
            "letter": row['Answer'],
            "text": row['Explanation']
        }

# Write JSON
with open('exam_1_week1_answer_key.json', 'w') as f:
    json.dump(answer_key, f, indent=2)
EOF
```

**Where It Goes (if using):**
```
your_project/exams/exam_1_week1_answer_key.csv
```

---

### Format 3: Student Responses
**File Format:** Excel (.xlsx) or CSV  
**Source:** Students' test responses  
**Contains:** 125 answers per student

#### Option A: Student Answers as Excel (.xlsx)
**File Naming:**
```
exam_[NUMBER]_batch_[BATCH_NAME].xlsx    (for cohorts)
[DESCRIPTION]_exam_[STUDENT].xlsx        (for individuals)

✓ Good:
  exam_1_batch_dec25.xlsx
  exam_2_batch_july26.xlsx
  alice_practice_exam1.xlsx
  bob_retake_exam2.xlsx

✗ Bad:
  Exam 1 Batch Dec25.xlsx
  answers 1 (final).xlsx
  exam_1_responses_(1).xlsx
  batch_responses.xlsx
```

**File Format (Excel - Wide Layout Recommended):**
```
Column A: Question
Column B: Alice (Student 1)
Column C: Bob (Student 2)
Column D: Carol (Student 3)
Column E: David (Student 4)
...

Row 1:  Question | Alice | Bob | Carol | David
Row 2:  Q1       | A     | B   | A     | C
Row 3:  Q2       | B     | C   | B     | D
Row 4:  Q3       | C     | A   | D     | A
Row 5:  Q4       | 1-D,2-A,3-B,4-C | A,B,C,D | 1D2C3B4A | 1-D,2-A,3-C,4-B
...
Row 126: Q125    | A     | B   | C     | D
```

**Total Rows:** 126 (1 header + 125 questions)  
**Total Columns:** N+1 (question column + one per student)  
**File Size:** ~50-200 KB (depends on answer complexity)

**Requirements:**
- ✓ Must be .xlsx (Excel 2007+), not .xls or .csv
- ✓ Exactly 125 rows (Q1-Q125)
- ✓ Student names in header (no blanks)
- ✓ Answers are A/B/C/D (uppercase)
- ✓ Multi-part: 1-A,2-B,3-C,4-D format

**Where It Goes:**
```
For batch (multiple students):
your_project/answers/batch_dec25/exam_1_batch_dec25.xlsx

For individual/standalone:
your_project/answers/standalone/alice_practice_exam1.xlsx
```

#### Option B: Student Answers as CSV
**File Naming:**
```
Same as Excel above, but .csv extension

exam_1_batch_dec25.csv
alice_practice_exam1.csv
```

**File Format (CSV):**
```
Question,Alice,Bob,Carol,David
Q1,A,B,A,C
Q2,B,C,B,D
Q3,C,A,D,A
Q4,1-D,2-A,3-B,4-C,A,B,C,D,1D2C3B4A,1-D,2-A,3-C,4-B
...
Q125,A,B,C,D
```

**When to Use CSV:**
- Direct import from online forms
- Quick manual entry
- Smaller file size
- For single student at a time

**Note:** Excel .xlsx is recommended because:
- Better handles complex multi-part answers
- Preserves formatting
- More reliable parsing
- Standard for batch analysis

---

## Complete Directory Structure with Naming

```
your_cissp_project/
│
├── README.md
├── SETUP.md
│
├── exams/                              # PDFs + Answer Keys
│   ├── exam_1_week1.pdf                ← Exam PDF
│   ├── exam_1_week1_answer_key.json    ← MUST MATCH filename
│   │
│   ├── exam_2_week2.pdf
│   ├── exam_2_week2_answer_key.json
│   │
│   ├── exam_3_practice.pdf
│   ├── exam_3_practice_answer_key.json
│   │
│   ├── exam_4_midterm.pdf
│   └── exam_4_midterm_answer_key.csv   (alternative: CSV format)
│
├── answers/                            # Student Response Files
│   │
│   ├── batch_dec25/                    # Cohort 1 (multiple students)
│   │   ├── exam_1_batch_dec25.xlsx     ← 50+ students per file
│   │   ├── exam_2_batch_dec25.xlsx
│   │   └── exam_3_batch_dec25.xlsx
│   │
│   ├── batch_july26/                   # Cohort 2 (multiple students)
│   │   ├── exam_1_batch_july26.xlsx
│   │   ├── exam_2_batch_july26.xlsx
│   │   └── exam_3_batch_july26.xlsx
│   │
│   └── standalone/                     # Individual/Ad-hoc Students
│       ├── alice_practice_exam1.xlsx   ← Single student files
│       ├── bob_practice_exam1.xlsx
│       ├── alice_retake_exam2.xlsx
│       ├── carol_diagnostic_exam3.xlsx
│       └── ...
│
├── students/                           # Auto-Generated History
│   ├── Alice/
│   │   ├── exam_1_performance.json     ← Auto-created by tool
│   │   ├── exam_2_performance.json
│   │   └── exam_3_performance.json
│   │
│   ├── Bob/
│   │   ├── exam_1_performance.json
│   │   └── exam_2_performance.json
│   │
│   └── Carol/
│       └── exam_1_performance.json
│
└── outputs/                            # Generated Reports
    │
    ├── batch_dec25/                    # Class reports + individual reports
    │   ├── CISSP_Class_Report_Dec25.xlsx
    │   ├── CISSP_Individual_Report_Alice.xlsx
    │   ├── CISSP_Individual_Report_Bob.xlsx
    │   └── ... (one per student)
    │
    ├── batch_july26/
    │   ├── CISSP_Class_Report_July26.xlsx
    │   ├── CISSP_Individual_Report_Alice.xlsx
    │   └── ...
    │
    └── standalone/                     # Individual reports organized by student
        ├── Alice/
        │   ├── CISSP_Individual_Report_Alice_Exam1.xlsx
        │   ├── CISSP_Individual_Report_Alice_Exam2.xlsx
        │   └── CISSP_Individual_Report_Alice_Exam3.xlsx
        │
        ├── Bob/
        │   └── CISSP_Individual_Report_Bob_Exam1.xlsx
        │
        └── Carol/
            └── CISSP_Individual_Report_Carol_Exam3.xlsx
```

---

## Naming Convention Rules (Summary)

### Rule 1: Exam PDF Files
```
Format: exam_[NUMBER]_[DESCRIPTION].pdf
```
- `[NUMBER]` = exam sequence (1, 2, 3, etc.)
- `[DESCRIPTION]` = descriptive label (week1, midterm, practice, etc.)
- All lowercase
- Underscores only (no spaces)

**Examples:**
```
exam_1_week1.pdf ✓
exam_2_midterm.pdf ✓
exam_3_final_assessment.pdf ✓
exam_1_domain_1_security_architecture.pdf ✓
```

### Rule 2: Answer Key Files
```
Format: exam_[NUMBER]_[DESCRIPTION]_answer_key.[json|csv]
```
- MUST match corresponding PDF filename
- Append `_answer_key` before extension
- Use either `.json` or `.csv`

**Examples:**
```
exam_1_week1_answer_key.json ✓
exam_2_midterm_answer_key.csv ✓
exam_3_practice_answer_key.json ✓
```

**MUST Match (Important!):**
```
PDF: exam_1_week1.pdf
KEY: exam_1_week1_answer_key.json  ✓ CORRECT

PDF: exam_1_week1.pdf
KEY: exam_1_answer_key.json        ✗ WRONG - Won't find it
```

### Rule 3: Student Answer Files (Batch)
```
Format: exam_[NUMBER]_batch_[BATCH_NAME].xlsx
```
- Include exam number
- Include batch name
- For multiple students in one file
- Must be `.xlsx` format

**Examples:**
```
exam_1_batch_dec25.xlsx ✓
exam_2_batch_july26.xlsx ✓
exam_3_batch_batch_august.xlsx ✓
exam_1_batch_cohort_2024.xlsx ✓
```

**Batch Name Ideas:**
```
batch_dec25      (Month + Year)
batch_july26     (Month + Year)
batch_cohort1    (Cohort identifier)
batch_group_a    (Group letter)
batch_sep2024    (Full date)
```

### Rule 4: Student Answer Files (Individual)
```
Format: [DESCRIPTION]_exam_[STUDENT].xlsx
OR
Format: [STUDENT]_exam_[DESCRIPTION].xlsx
```
- For single student per file
- Include exam descriptor
- Include student name
- Must be `.xlsx` format

**Examples:**
```
alice_practice_exam1.xlsx ✓
bob_retake_exam2.xlsx ✓
carol_diagnostic_exam3.xlsx ✓
practice_exam_alice.xlsx ✓
retake_exam_bob.xlsx ✓
```

### Rule 5: Folder Names
```
Format: [type]_[descriptor]
```
- All lowercase
- Underscores for spacing
- No special characters

**Batch Folders:**
```
batch_dec25 ✓
batch_july26 ✓
batch_sep2024 ✓
batch_cohort1 ✓
```

**Folder Hierarchy:**
```
answers/
├── batch_dec25/      ← For multiple cohorts, use subfolder
├── batch_july26/
└── standalone/       ← For individual students
```

---

## Validation Checklist

Before running analysis, verify all naming:

### PDF File Naming
- [ ] Format: `exam_[N]_[DESC].pdf`
- [ ] All lowercase (except optional student names)
- [ ] Underscores only
- [ ] File exists in `exams/` folder
- [ ] Number starts at 1 (exam_1, exam_2, etc.)

### Answer Key Naming
- [ ] Format: `exam_[N]_[DESC]_answer_key.[json|csv]`
- [ ] **MATCHES PDF filename exactly** (except extension)
- [ ] PDF: `exam_1_week1.pdf` → KEY: `exam_1_week1_answer_key.json` ✓
- [ ] Both in `exams/` folder
- [ ] JSON is valid (check with `python3 -m json.tool`)
- [ ] 125 questions present

### Student Answer Naming
- [ ] Format: `exam_[N]_batch_[NAME].xlsx` (batch) OR `[DESC]_exam_[STUDENT].xlsx` (individual)
- [ ] File extension is `.xlsx` (not `.xls` or `.csv`)
- [ ] Batch files in `answers/batch_[name]/`
- [ ] Individual files in `answers/standalone/`
- [ ] 125 rows (Q1-Q125) + header row = 126 total

### Directory Naming
- [ ] `exams/` contains PDFs + answer keys
- [ ] `answers/` organized into subfolders
- [ ] `students/` exists (auto-populated by tool)
- [ ] `outputs/` exists (holds results)
- [ ] All folders lowercase with underscores

---

## Common Naming Mistakes & Fixes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `Exam 1 Week 1.pdf` | Spaces, capitals | `exam_1_week1.pdf` |
| `exam_1.json` | Doesn't match PDF | `exam_1_week1_answer_key.json` |
| `answers_1.xlsx` | Wrong pattern | `exam_1_batch_dec25.xlsx` |
| `exam (1).pdf` | Special chars | `exam_1.pdf` |
| `EXAM_1_WEEK_1.pdf` | All caps | `exam_1_week1.pdf` |
| `exam_1 week1.pdf` | Space in middle | `exam_1_week1.pdf` |
| `answers.xlsx` | No exam reference | `exam_1_batch_dec25.xlsx` |

---

## Quick Reference Table

| File Type | Format | Naming Pattern | Extension | Location | Example |
|-----------|--------|----------------|-----------|----------|---------|
| Exam | PDF | exam_[N]_[DESC] | .pdf | exams/ | exam_1_week1.pdf |
| Answer Key | JSON | exam_[N]_[DESC]_answer_key | .json | exams/ | exam_1_week1_answer_key.json |
| Answer Key | CSV | exam_[N]_[DESC]_answer_key | .csv | exams/ | exam_1_week1_answer_key.csv |
| Batch Answers | Excel | exam_[N]_batch_[NAME] | .xlsx | answers/batch_[N]/ | exam_1_batch_dec25.xlsx |
| Individual Answers | Excel | [DESC]_exam_[STUDENT] | .xlsx | answers/standalone/ | alice_practice_exam1.xlsx |
| Student History | JSON | [STUDENT]/exam_[N]_performance | .json | students/ | Alice/exam_1_performance.json |

---

## Step-by-Step Naming Example

### Scenario: Dec-25 Cohort, Week 1 Exam

**Step 1: Name Your Exam PDF**
```
exam_1_week1.pdf
↑ Your source document (actual exam questions)
Location: exams/exam_1_week1.pdf
```

**Step 2: Create/Name Answer Key**
```
exam_1_week1_answer_key.json
↑ MUST match PDF name (same format)
Contains: {"1": {"letter": "A", "text": "..."}, ...}
Location: exams/exam_1_week1_answer_key.json
```

**Step 3: Prepare Student Responses**
```
exam_1_batch_dec25.xlsx
↑ Batch identifier = cohort name
Contains: Alice, Bob, Carol, ... (multiple students)
Location: answers/batch_dec25/exam_1_batch_dec25.xlsx
```

**Step 4: Run Analysis**
```bash
python3 analyze.py
# Tool automatically:
# 1. Finds exam_1_week1.pdf in exams/
# 2. Looks for exam_1_week1_answer_key.json in exams/ (MUST MATCH!)
# 3. Reads student answers from exam_1_batch_dec25.xlsx
# 4. Generates reports in outputs/batch_dec25/
```

**Step 5: View Results**
```
outputs/batch_dec25/
├── CISSP_Class_Report_Dec25.xlsx
├── CISSP_Individual_Report_Alice.xlsx
├── CISSP_Individual_Report_Bob.xlsx
├── CISSP_Individual_Report_Carol.xlsx
└── ...

students/
├── Alice/exam_1_performance.json     ← Auto-created
├── Bob/exam_1_performance.json
└── Carol/exam_1_performance.json
```

---

## File Format Details

### JSON Answer Key Format
```json
{
  "1": {
    "letter": "A",
    "text": "AES is symmetric encryption using 128, 192, or 256-bit keys"
  },
  "2": {
    "letter": "B",
    "text": "RSA is asymmetric, used for key exchange and signatures"
  },
  ...
  "125": {
    "letter": "D",
    "text": "Business continuity ensures critical operations continue post-disaster"
  }
}
```

**Requirements:**
- Valid JSON syntax
- All numbers quoted ("1", not 1)
- All 125 questions
- "letter" field: A/B/C/D
- "text" field: non-empty string

### CSV Answer Key Format
```
Question,Answer,Explanation
1,A,AES is symmetric encryption using 128, 192, or 256-bit keys
2,B,RSA is asymmetric, used for key exchange and signatures
...
125,D,Business continuity ensures critical operations continue post-disaster
```

**Requirements:**
- Comma-separated values
- Header row: Question,Answer,Explanation
- All 125 rows
- Answer: A/B/C/D only
- Explanation: non-empty string

### Excel Student Answers Format
```
Column A (Questions):  Question, Q1, Q2, Q3, ..., Q125
Column B (Student 1):  Alice, A, B, C, ..., A
Column C (Student 2):  Bob, B, C, D, ..., B
Column D (Student 3):  Carol, A, B, A, ..., C
...
```

**Requirements:**
- .xlsx format only
- Header row with Question + Student names
- 125 data rows (Q1-Q125)
- Student names unique and non-blank
- Answers: A/B/C/D (case-insensitive, auto-normalized)
- Multi-part: 1-A,2-B,3-C,4-D format

---

## Support & Validation

### Quick Validation
```bash
# 1. Check PDF exists
ls exams/exam_1_week1.pdf

# 2. Check answer key exists with matching name
ls exams/exam_1_week1_answer_key.json

# 3. Validate JSON syntax
python3 -c "import json; json.load(open('exams/exam_1_week1_answer_key.json')); print('✓ Valid')"

# 4. Check answer count
python3 << 'EOF'
import json
with open('exams/exam_1_week1_answer_key.json') as f:
    answers = json.load(f)
    print(f"Questions: {len(answers)} (should be 125)")
EOF

# 5. Check Excel file
ls answers/batch_dec25/exam_1_batch_dec25.xlsx

# 6. Count rows in Excel
python3 << 'EOF'
import openpyxl
wb = openpyxl.load_workbook('answers/batch_dec25/exam_1_batch_dec25.xlsx')
ws = wb.active
print(f"Rows: {ws.max_row} (should be ~126 for 125 questions)")
print(f"Questions: {ws.max_row - 1} (header + data)")
EOF
```

---

**This naming convention ensures consistency, prevents errors, and makes file management seamless! 🎯**

For more details:
- See: TEMPLATE_directory_structure.md (folder layout)
- See: FORMATS_AND_TEMPLATES_GUIDE.md (complete guide)
- See: EXAMPLE_FILES_HOW_TO_USE.md (working examples)
