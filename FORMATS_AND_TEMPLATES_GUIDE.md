# CISSP Analyzer - Complete Formats & Templates Guide

**Purpose:** Ensure consistent data formats to avoid errors and maximize tool accuracy

**Status:** Production Ready | Version 1.0 | July 4, 2026

---

## Quick Start: 3 Files You Need

1. **Exam PDF** (`exam_1_week1.pdf`)
   - Your CISSP exam questions (any PDF format)

2. **Answer Key JSON** (`exam_1_week1_answer_key.json`)
   - Correct answers → See: TEMPLATE_answer_key.json

3. **Student Answers Excel** (`exam_1_batch_dec25.xlsx`)
   - Student responses → See: TEMPLATE_student_answers.md

---

## Format 1: Answer Key JSON

### What It Is
A JSON file containing all 125 correct answers with explanations.

### Where It Goes
```
exams/exam_1_week1_answer_key.json
```

### Required Structure
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
    "text": "Final question explanation"
  }
}
```

### Validation Rules
✅ Must have exactly 125 questions (1-125)
✅ Each question must have "letter" (A/B/C/D)
✅ Each question must have "text" (explanation)
✅ Valid JSON format (no trailing commas)
✅ Letter must be uppercase (A not a)

### Quick Validation
```bash
# Linux/Mac: Validate JSON syntax
python3 -c "import json; json.load(open('answer_key.json')); print('✓ Valid')"
```

### Example: Complete Answer Key
```json
{
  "1": {
    "letter": "A",
    "text": "AES uses 128, 192, or 256-bit encryption with block size of 128 bits"
  },
  "2": {
    "letter": "B",
    "text": "Public key infrastructure enables digital certificates and signatures"
  },
  "3": {
    "letter": "C",
    "text": "Defense in depth uses multiple layers of security controls"
  },
  "4": {
    "letter": "D",
    "text": "Authentication, Authorization, Accounting are AAA framework components"
  },
  "5": {
    "letter": "A",
    "text": "Least privilege restricts access to minimum required permissions"
  }
}
```

---

## Format 2: Student Answer Sheet (Excel)

### What It Is
An Excel file with one column per student, containing their answers to all 125 questions.

### Where It Goes
```
answers/batch_dec25/exam_1_batch_dec25.xlsx         (for cohorts)
answers/standalone/alice_practice_exam1.xlsx        (for individuals)
```

### File Format: Two Options

#### Option A: Wide Format (Recommended)
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Student Name │ Alice        │ Bob          │ Carol        │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ Question 1   │ A            │ B            │ A            │
│ Question 2   │ B            │ C            │ B            │
│ Question 3   │ C            │ A            │ D            │
│ ...          │ ...          │ ...          │ ...          │
│ Question 125 │ A            │ B            │ C            │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

**Pros:** Easy to read, multiple students at once  
**Cons:** Requires exact header naming

#### Option B: Tall Format
```
┌──────────────┬──────────────┐
│ Student      │ Answer       │
├──────────────┼──────────────┤
│ Alice        │ (below)      │
├──────────────┼──────────────┤
│ Q1           │ A            │
│ Q2           │ B            │
│ Q3           │ C            │
│ ...          │ ...          │
│ Q125         │ A            │
└──────────────┴──────────────┘
```

**Pros:** Works for single student  
**Cons:** Can't do multiple students in one file

### Supported Answer Formats

| Format | Example | Auto-Converted? |
|--------|---------|-----------------|
| Single letter | `A` | ✓ Yes |
| Letter with dash | `1-A` | ✓ Yes |
| Multi-part with dash | `1-A,2-B,3-C,4-D` | ✓ Yes |
| Multi-part no spaces | `1A2B3C4D` | ✓ Yes |
| Multi-part positional | `A,B,C,D` | ✓ Yes (to 1-A,2-B,3-C,4-D) |
| Lowercase | `a` | ✓ Yes (to A) |
| Extra spaces | `1 - A , 2 - B` | ✓ Yes (normalized) |

### Validation Rules
✅ Exactly 125 rows of answers (one per question)
✅ Answers are only A, B, C, or D (case-insensitive)
✅ Student name in header (no blanks)
✅ Multi-part answers properly formatted
✅ File is .xlsx format (Excel 2007+)

### Common Multi-Part Formats

**Ordering/Matching Questions:**
```
Answer Key:  1-A,2-B,3-C,4-D
Student 1:   1-A,2-B,3-C,4-D    ✓ Correct
Student 2:   A,B,C,D            ✓ Correct (auto-converted)
Student 3:   ABCD               ✓ Correct (auto-converted)
Student 4:   1A2B3C4D           ✓ Correct (auto-converted)
Student 5:   1 - A, 2 - B, 3 - C, 4 - D   ✓ Correct (auto-cleaned)
```

### Excel Sheet Requirements
- Sheet name doesn't matter (auto-detected)
- First row can be header with "Student Name" or just student names
- Subsequent rows are Q1, Q2, ... Q125
- No empty columns in middle (but trailing empty OK)
- No merged cells

### Example: Complete Excel Layout

```
Column A: Row Labels
Column B: Alice
Column C: Bob
Column D: Carol
Column E: David

Row 1:  Student Name | Alice | Bob | Carol | David
Row 2:  Q1           | A     | B   | A     | C
Row 3:  Q2           | B     | C   | B     | D
Row 4:  Q3           | C     | A   | D     | A
Row 5:  Q4           | 1-D,2-A,3-B,4-C | A,B,C,D | 1D2C3B4A | 1-D,2-A,3-C,4-B
...
Row 126: Q125        | A     | B   | C     | D
```

---

## Format 3: Directory Structure

### What It Is
Organized folder layout for exams, answers, history, and reports.

### Full Structure
```
your_project/
├── exams/                          # PDFs + answer keys
│   ├── exam_1_week1.pdf
│   ├── exam_1_week1_answer_key.json
│   ├── exam_2_week2.pdf
│   └── exam_2_week2_answer_key.json
│
├── answers/                        # Student response files
│   ├── batch_dec25/
│   │   ├── exam_1_batch_dec25.xlsx
│   │   └── exam_2_batch_dec25.xlsx
│   ├── batch_july26/
│   │   └── exam_1_batch_july26.xlsx
│   └── standalone/
│       ├── alice_practice_exam1.xlsx
│       └── bob_retake_exam2.xlsx
│
├── students/                       # Auto-generated history
│   ├── Alice/
│   │   ├── exam_1_performance.json
│   │   └── exam_2_performance.json
│   └── Bob/
│       └── exam_1_performance.json
│
└── outputs/                        # Generated reports
    ├── batch_dec25/
    │   ├── CISSP_Class_Report_Dec25.xlsx
    │   ├── CISSP_Individual_Report_Alice.xlsx
    │   └── CISSP_Individual_Report_Bob.xlsx
    └── standalone/
        ├── Alice/
        │   └── CISSP_Individual_Report_Alice_Exam1.xlsx
        └── Bob/
            └── CISSP_Individual_Report_Bob_Exam1.xlsx
```

### Folder Rules
✅ Use lowercase for folder names
✅ Use underscores for spacing (not spaces)
✅ Separate exams by batch or type
✅ Don't manually edit /students/ folder
✅ Check outputs folder after each run

### See Also
→ Full details: `TEMPLATE_directory_structure.md`

---

## File Naming Conventions

### Answer Key Files
```
exam_[NUMBER]_[DESCRIPTION]_answer_key.json

✓ Good:
  exam_1_week1_answer_key.json
  exam_2_midterm_answer_key.json
  exam_3_practice_answer_key.json

✗ Bad:
  answer_key_1.json
  Exam 1 Answer Key.json
  answers (1).json
```

### Exam PDF Files
```
exam_[NUMBER]_[DESCRIPTION].pdf

✓ Good:
  exam_1_week1.pdf
  exam_2_midterm.pdf
  exam_3_practice.pdf

✗ Bad:
  Exam 1.pdf
  CISSP_EXAM_1.pdf
  exam (1).pdf
```

### Student Answer Files
```
exam_[NUMBER]_batch_[BATCH_NAME].xlsx    (cohort)
[DESCRIPTION]_exam_[STUDENT].xlsx        (individual)

✓ Good:
  exam_1_batch_dec25.xlsx
  exam_2_batch_july26.xlsx
  alice_practice_exam1.xlsx
  bob_retake_exam2.xlsx

✗ Bad:
  Exam 1 - Class Responses.xlsx
  ANSWERS_1_(FINAL).xlsx
  exam 1 batch dec25.xlsx
```

### Rules
- All lowercase (except student names can be capitalized in individual files)
- Underscores not spaces or hyphens
- Include exam number and batch name
- Keep under 50 characters
- Use descriptive words (week1, midterm, practice, retake)

---

## Validation Checklist

Before running analysis, verify all formats:

### Answer Key JSON ✓
- [ ] Valid JSON syntax (no trailing commas)
- [ ] Contains keys 1-125 (all questions)
- [ ] Each question has "letter" and "text"
- [ ] Letters are A, B, C, or D
- [ ] All answers present (no null values)

### Student Answers Excel ✓
- [ ] File is .xlsx format (not .xls or .csv)
- [ ] Exactly 125 rows (one per question)
- [ ] Student names in header (no blanks)
- [ ] Answers are A, B, C, D (or multi-part format)
- [ ] No merged cells or special formatting
- [ ] File not open in Excel during analysis

### Directory Structure ✓
- [ ] /exams/ contains PDF and matching JSON
- [ ] /answers/ organized by batch or standalone
- [ ] /students/ exists (auto-populated by tool)
- [ ] /outputs/ exists (can be empty initially)
- [ ] All file paths use forward slashes (/)
- [ ] No spaces in folder or file names

### Naming Conventions ✓
- [ ] Answer key: exam_[N]_[DESC]_answer_key.json
- [ ] PDF file: exam_[N]_[DESC].pdf
- [ ] Excel file: exam_[N]_batch_[NAME].xlsx
- [ ] All lowercase (except student names)
- [ ] Underscores for spacing only
- [ ] No special characters

---

## Common Issues & Fixes

### Issue 1: JSON Parse Error
```
Error: "Invalid JSON in answer key"

Cause: Syntax error in JSON file

Fix:
1. Open answer_key.json in text editor
2. Check for:
   - Trailing commas: {"1": {...},}  ← Remove this comma
   - Missing quotes: {1: ...}  ← Should be "1": ...
   - Missing colons: {"1" "letter": "A"}  ← Add :
3. Use JSON validator: jsonlint.com
4. Ensure last item has no comma after it
```

### Issue 2: Excel File Won't Read
```
Error: "Cannot parse Excel file"

Cause: Wrong format or file is locked

Fix:
1. Save as .xlsx (not .xls, .csv, or .xlsm)
2. Close Excel if file is open
3. Ensure no special formatting (no colors, fonts, etc.)
4. No merged cells - each cell unique
5. Check file path has no spaces
```

### Issue 3: Student Scores 0%
```
Error: "All students showing 0% score"

Cause: Answers not matching format

Fix:
1. Verify answer count = 125 (not 124 or 126)
2. Check answers are A/B/C/D only (not 1/2/3/4)
3. Ensure student name in Excel matches CLI entry
4. Verify answer key has all 125 answers
5. Check for empty rows or columns in Excel
```

### Issue 4: Multi-Part Answers Wrong
```
Error: "4-part answers showing as incorrect"

Cause: Format mismatch

Fix:
Use format: 1-A,2-B,3-C,4-D
Not:        A,B,C,D (positional only)
Not:        1A2B3C4D (no dashes)
Not:        1-A 2-B 3-C 4-D (spaces not commas)
Not:        1-A, 2-B, 3-C, 4-D (spaces after comma)
```

### Issue 5: Student Name Not Found
```
Error: "Cannot find student results"

Cause: Name mismatch between files

Fix:
1. Check Excel column header: "Alice"
2. Check CLI input matches: "Alice" (exact case)
3. Remove extra spaces: " Alice " → "Alice"
4. Replace special chars: "José" → "Jose"
5. No accents or unicode characters
```

---

## Template Files in Repository

Three templates provided to help you get started:

### 1. TEMPLATE_answer_key.json
```bash
# View example
cat TEMPLATE_answer_key.json

# Use as starting point
cp TEMPLATE_answer_key.json exams/exam_1_answer_key.json
# Then edit with real answers
```

### 2. TEMPLATE_student_answers.md
```bash
# View complete guide
cat TEMPLATE_student_answers.md

# Contains:
# - Excel file format
# - Answer format variations
# - Multi-part answer examples
# - Common issues & fixes
```

### 3. TEMPLATE_directory_structure.md
```bash
# View directory setup guide
cat TEMPLATE_directory_structure.md

# Contains:
# - Full folder layout
# - Naming conventions
# - Setup instructions
# - Best practices
```

---

## Quick Setup: Step-by-Step

### Step 1: Create Directories
```bash
mkdir -p exams answers/batch_dec25 students outputs/batch_dec25
```

### Step 2: Copy Templates
```bash
# Answer key template
cp TEMPLATE_answer_key.json exams/exam_1_answer_key.json

# Edit with real answers
nano exams/exam_1_answer_key.json
```

### Step 3: Prepare Excel
```bash
# Create Excel file with:
# Column A: Student Name | Q1 | Q2 | Q3 | ... | Q125
# Column B: Alice        | A  | B  | C  | ... | A
# Column C: Bob          | B  | C  | D  | ... | B
# Save as: answers/batch_dec25/exam_1_batch_dec25.xlsx
```

### Step 4: Get Exam PDF
```bash
# Place exam PDF
cp your_exam.pdf exams/exam_1_week1.pdf
```

### Step 5: Run Analysis
```bash
python3 analyze.py
# Select: 1 (Batch Analysis)
# Select: batch_dec25
# Enter exam: exam_1_week1
# Specify answer file: answers/batch_dec25/exam_1_batch_dec25.xlsx
# Enter output dir: outputs/batch_dec25
```

### Step 6: Check Results
```bash
ls outputs/batch_dec25/
# Should see:
# - CISSP_Class_Report_Dec25.xlsx
# - CISSP_Individual_Report_Alice.xlsx
# - CISSP_Individual_Report_Bob.xlsx
# - ...
```

---

## Examples: Real-World Scenarios

### Scenario 1: Class Exam (Batch)
```
Input:
├── exams/exam_1_week1.pdf
├── exams/exam_1_week1_answer_key.json
└── answers/batch_dec25/exam_1_batch_dec25.xlsx
   (Contains: Alice, Bob, Carol, David, ...)

Command: python3 analyze.py → Choose [1] Batch

Output:
├── outputs/batch_dec25/CISSP_Class_Report_Dec25.xlsx
├── outputs/batch_dec25/CISSP_Individual_Report_Alice.xlsx
├── outputs/batch_dec25/CISSP_Individual_Report_Bob.xlsx
└── students/[Alice,Bob,...]/exam_1_performance.json
```

### Scenario 2: Student Retake (Standalone)
```
Input:
├── exams/exam_2_week2.pdf
├── exams/exam_2_week2_answer_key.json
└── answers/standalone/alice_retake_exam2.xlsx
   (Contains: Alice only)

Command: python3 analyze.py → Choose [2] Standalone → [B] Comparative

Detection:
✓ Found 1 previous exam(s) for Alice (exam_1)
✓ Shows progress from Exam 1 → Exam 2

Output:
├── outputs/standalone/Alice/CISSP_Individual_Report_Alice_Exam2.xlsx
   (Includes Progress Over Time sheet)
└── students/Alice/exam_2_performance.json
```

### Scenario 3: Practice Test (Standalone Ad-Hoc)
```
Input:
├── exams/exam_3_practice.pdf
├── exams/exam_3_practice_answer_key.json
└── answers/standalone/bob_practice_exam3.xlsx
   (Contains: Bob only)

Command: python3 analyze.py → Choose [2] Standalone → [A] Single Exam

Output:
├── outputs/standalone/Bob/CISSP_Individual_Report_Bob_Exam3.xlsx
   (9 sheets, no progress tracking)
└── students/Bob/exam_3_performance.json
```

---

## Troubleshooting by Error Message

| Error | Cause | Fix |
|-------|-------|-----|
| "JSON decode error" | Invalid JSON syntax | Check for trailing commas, missing quotes |
| "File not found" | Wrong path or filename | Verify exact path and filename |
| "Cannot parse Excel" | Wrong format or locked | Save as .xlsx, close Excel, remove formatting |
| "No answers found" | Wrong answer key format | Ensure "letter" and "text" fields present |
| "Question count mismatch" | Wrong number of questions | Must have exactly 125 answers |
| "Invalid answer letter" | Answer not A/B/C/D | Check for numbers (1/2/3/4) instead of letters |
| "Student not found" | Name doesn't match | Check spelling and capitalization exactly |
| "Zero percent score" | Answers not matching key | Verify 125 rows, correct format |

---

## Best Practices

1. **Use Templates** - Copy TEMPLATE files and customize
2. **Consistent Naming** - Always use: exam_[N]_[DESC] pattern
3. **Keep Organized** - Use batch folders for cohorts
4. **Validate Before Running** - Check all files before analysis
5. **Don't Edit History** - Let tool manage /students/ folder
6. **Backup Excel Files** - Keep originals before batch runs
7. **Document Your Setup** - Add README to each batch folder
8. **Test with Small Sample** - Run with 1-2 students first

---

## Need Help?

### Check These Files
1. `TEMPLATE_answer_key.json` - Answer key format example
2. `TEMPLATE_student_answers.md` - Excel format guide
3. `TEMPLATE_directory_structure.md` - Folder setup guide
4. `README.md` - General project documentation
5. `TESTING_GUIDE_STANDALONE.md` - Testing procedures

### Validation Tools
```bash
# Validate JSON
python3 -c "import json; json.load(open('answer_key.json')); print('✓ Valid')"

# Check file exists
ls -la exams/exam_1_week1.pdf

# List Excel files
find answers/ -name "*.xlsx"
```

---

**Version:** 1.0  
**Last Updated:** July 4, 2026  
**Status:** Production Ready
