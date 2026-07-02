# Data Quality Guide - Answer Sheet Validation

## Overview

The CISSP Analyzer validates student answer sheets before processing to catch data quality issues early. This guide explains what issues can occur and how to fix them.

## Quick Start

Before running analysis, validate all answer files:

```bash
python3 validate_answers.py                    # Check Dec-25 batch
python3 validate_answers.py --batch july26     # Check July-26 batch
python3 validate_answers.py --file <path> <name>  # Check single file
```

## Issue Types & Fixes

### 1. **MISSING ANSWERS** ❌ (ERROR)

**What it means:** One or more questions don't have answers

**Example:**
```
Aman - MISSING_ANSWERS: 2 missing answers at questions: [57, 80]
```

**How to fix:**
1. Open the Excel file in a spreadsheet app
2. Go to the flagged question number
3. Check the Answer column for that row
4. If empty, enter the correct answer (A, B, C, or D)
5. Save the file

**Prevention:** Make sure every question (1-125) has an answer entered.

---

### 2. **MISSING QUESTION COLUMN** ❌ (ERROR)

**What it means:** The file doesn't have a "Question" column

**Example:**
```
Thameem - MISSING_QUESTION_COLUMN: No 'Question' column found. Columns: c
```

**How to fix:**
1. The file structure is wrong - it may have been saved in wrong format
2. Ask the student to provide the original file with proper structure
3. Or manually fix it:
   - Insert a new column at the beginning
   - Add header "Question" in cell A1
   - Add numbers 1-125 in cells A2-A126
   - Move the answers to column B with header "Answer"

**Prevention:** When students fill out answers, provide template with "Question" and "Answer" columns.

---

### 3. **MISSING ANSWER COLUMN** ❌ (ERROR)

**What it means:** The file doesn't have an "Answer" column (or proper data structure)

**Example:**
```
Thameem - MISSING_ANSWER_COLUMN: No 'Answer' column found. Columns: c
```

**How to fix:**
Same as MISSING_QUESTION_COLUMN above.

---

### 4. **INCOMPLETE DATA** ❌ (ERROR)

**What it means:** File has fewer than 125 questions

**Example:**
```
Thameem - INCOMPLETE_DATA: Only 124 answers found, expected 125
```

**How to fix:**
1. Open the file in Excel
2. Count the number of rows (should be 125 data rows + 1 header = 126 total)
3. If missing rows:
   - Find where the gap is
   - Add missing question(s)
   - Enter the correct answer
4. Save the file

**Prevention:** After filling out exam, verify all 125 questions were completed.

---

### 5. **EXTRA COLUMNS** ⚠️ (WARNING)

**What it means:** File has more than 2 columns (Question + Answer)

**Example:**
```
Aman - EXTRA_COLUMNS: File has 3 columns instead of 2. Columns: Question, Answer, Unnamed: 2
```

**Impact:** Won't prevent analysis, but indicates possible data entry error.

**How to fix:**
1. Open the file in Excel
2. Look for the extra column(s) - usually contains blank data or formatting
3. Delete the extra column
4. Save the file

**Prevention:** Use clean template with only two columns.

---

### 6. **INVALID ANSWERS** ⚠️ (WARNING)

**What it means:** Some answer values don't start with A, B, C, or D

**Example:**
```
Senthil - INVALID_ANSWERS: 2 invalid answer values: Q11:'1C2D3B4A', Q118:'1D2A3E4C5B'
```

**Impact:** The analyzer will attempt to extract the first letter, but data quality is questionable.

**What's likely happening:**
- Student entered multiple values in one cell (combined exam keys, notes, etc.)
- Formatting issue where values got concatenated

**How to fix:**
1. Open the file
2. Go to the flagged question
3. Check the answer cell
4. If it contains multiple values (like "1C2D3B4A"), extract just ONE answer (usually the last one is correct)
5. Delete the extra content, keep only the single letter (A, B, C, or D)
6. Save the file

**Example:**
```
Before: Q11 = "1C2D3B4A"    →    After: Q11 = "A"
```

---

### 7. **ANOMALIES** ⚠️ (WARNING)

**What it means:** Cells contain multiple values (comma-separated, multi-letter, etc.)

**Example:**
```
Praveena - ANOMALIES: 2 anomalous values: Q11:'1C, 2D, 3B, 4A,'(comma-separated)
```

**What's likely happening:**
- Student copied explanations/notes into the answer cell
- Multiple answer keys got merged
- Exam explanation or answer breakdown instead of just the answer

**How to fix:**
Same as INVALID ANSWERS - extract the single correct answer and delete the rest.

---

## Common Scenarios & Solutions

### Scenario 1: Student Excel has "Exam Key" Format

**File looks like:**
```
Question | Answer
1        | 1-A
2        | 2-B
3        | 3-C
```

**Fix:**
Remove the question number prefix - keep only A, B, C, or D:
```
Question | Answer
1        | A
2        | B
3        | C
```

### Scenario 2: Student Excel has Explanations

**File looks like:**
```
Question | Answer
1        | A - Based on ISO standards...
2        | B - Related to authentication...
```

**Fix:**
Keep only the letter:
```
Question | Answer
1        | A
2        | B
```

### Scenario 3: Wrong Column Names

**File has:**
```
Q.NO | Answer options
```

**Should have:**
```
Question | Answer
```

**Fix:**
- Rename "Q.NO" to "Question"
- Rename "Answer options" to "Answer"

### Scenario 4: Column Names Have Spaces or Special Characters

**File has:**
```
Question | Senthil's Answers | Extra Info
```

**Fix:**
- Rename "Senthil's Answers" to "Answer"
- Delete "Extra Info" column
- Result: Question | Answer

---

## Validation Before Consolidation

When multiple students' files are being consolidated for batch analysis:

1. **Each file is validated individually**
   - Checked for completeness (125 questions)
   - Checked for proper structure (Question + Answer columns)
   - Checked for data quality (no NaN, valid formats)

2. **Issues are reported by student and file**
   - Errors must be fixed before analysis
   - Warnings can proceed but may affect accuracy

3. **Consolidation handles minor variations**
   - Different column names (Answer, Answers, answer, etc.)
   - Different case (A vs a, B vs b)
   - Multi-option cells (extracts first valid letter)

---

## Error Reference

| Issue | Severity | Blocks Analysis | Solution |
|-------|----------|-----------------|----------|
| MISSING_ANSWERS | ERROR | Partially | Add missing answers in Excel |
| MISSING_QUESTION_COLUMN | ERROR | Yes | Fix file structure, add Question column |
| MISSING_ANSWER_COLUMN | ERROR | Yes | Fix file structure, add Answer column |
| INCOMPLETE_DATA | ERROR | Yes | Add missing questions to reach 125 total |
| EXTRA_COLUMNS | WARNING | No | Delete extra columns |
| INVALID_ANSWERS | WARNING | No | Fix answer format, keep only A/B/C/D |
| ANOMALIES | WARNING | No | Remove multi-value cells, keep single answer |

---

## Prevention Best Practices

### For Students Filling Out Answers:

1. **Use the provided template** - Don't modify column structure
2. **Enter single answers only** - No notes, explanations, or multiple values
3. **Valid answers: A, B, C, or D** - No numbers, no combinations
4. **Complete all 125 questions** - Don't skip or leave blanks
5. **Save as Excel (.xlsx format)** - Not CSV, not PDF, not Google Sheets

### For Batch Coordinators:

1. **Validate files before analysis** - Run `python3 validate_answers.py`
2. **Fix errors, not workarounds** - Don't ignore errors, fix the source
3. **Document templates** - Show students exactly what format you expect
4. **Spot-check files** - Manually review a few files for quality
5. **Create clean consolidation** - Validate before consolidating

---

## Automated Checks During Analysis

When you run analysis:

```bash
python3 analyze_dec25.py
```

The system will:

1. ✓ Automatically validate all individual files
2. ⚠️ Report any data quality issues found
3. ⚠️ Suggest running `python3 validate_answers.py` for details
4. ▶️ Continue with analysis if issues aren't blocking

---

## Getting Help

### To check a specific file:
```bash
python3 validate_answers.py --file answers/dec25_batch/senthil_week1.xlsx Senthil
```

### To check all files in a batch:
```bash
python3 validate_answers.py --batch dec25
```

### To understand a specific error:
Check the **Error Reference** table above or read the detailed issue descriptions.

---

## Quality Assurance Checklist

Before submitting answer files:

- [ ] File is in Excel format (.xlsx)
- [ ] File has exactly 2 columns: "Question" and "Answer"
- [ ] First column has numbers 1-125
- [ ] Second column has single letter answers (A, B, C, or D)
- [ ] No empty cells in answer column
- [ ] No extra columns or formatting
- [ ] No notes or explanations in answer cells
- [ ] Total of 125 rows of data (plus 1 header row)

If all boxes checked ✓, your file is ready for analysis!
