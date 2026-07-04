# CISSP Analyzer - Student Answer Sheet Template

## Excel File Format

### File Name Convention
```
exam_[exam_number]_batch_[batch_name].xlsx
OR
answers_[exam_number]_[batch_date].xlsx

Examples:
- exam_1_batch_dec25.xlsx
- answers_1_batch_july26.xlsx
- exam_2_batch_standalone.xlsx
```

---

## Excel Sheet Structure

### Column Headers (MUST be exactly as shown)
```
Question Number | Student Name 1 | Student Name 2 | Student Name 3 | ...
Question | Answer |  Answer | Answer | ...
```

OR simpler format:

```
Student Name
Answer 1
Answer 2
Answer 3
...
Answer 125
```

---

## Answer Format Variations (All Supported)

### Format 1: Single Letter Answer
```
Column: "Question 1"
Value: "A"
Value: "B"
Value: "C"
```

### Format 2: Letter with Dash
```
Column: "Question 1"
Value: "A"
Value: "1-A"
```

### Format 3: Multi-Part Answers (Ordering/Matching)
```
Column: "Question 45"
Value: "1-A,2-B,3-C,4-D"
OR
Value: "1-A, 2-B, 3-C, 4-D"  (spaces OK)
OR
Value: "1A2B3C4D"  (no separators)
```

### Format 4: Positional Format (Auto-Numbered)
```
Column: "Question 45"
Value: "A,B,C,D"  (will be converted to 1-A,2-B,3-C,4-D)
OR
Value: "ABCD"  (will be converted to 1-A,2-B,3-C,4-D)
```

### Format 5: Mixed Case (Auto-Normalized)
```
Value: "a"  →  converts to "A"
Value: "a,b,c,d"  →  converts to "A,B,C,D" or "1-A,2-B,3-C,4-D"
```

### Format 6: Spaces & Separators (Auto-Cleaned)
```
Value: "1 - A, 2 - B, 3 - C"  →  converts to "1-A,2-B,3-C"
Value: "  A  "  →  converts to "A"
```

---

## Complete Excel Example

### Column Layout
```
┌─────────────────┬──────────────┬──────────────┬──────────────┐
│ Student Name    │ Student Name │ Student Name │ Student Name │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ Alice           │ Bob          │ Carol        │ David        │
├─────────────────┼──────────────┼──────────────┼──────────────┤
│ A               │ B            │ A            │ C            │
│ B               │ C            │ B            │ D            │
│ C               │ A            │ D            │ A            │
│ 1-D,2-A,3-B,4-C │ A,B,C,D      │ 1D2C3B4A     │ 1-D,2-A,3-C, │
│ ...             │ ...          │ ...          │ ...          │
└─────────────────┴──────────────┴──────────────┴──────────────┘
```

### Row-by-Row Example
```
Row 1: Student Name | Alice | Bob | Carol | David
Row 2: Q1           | A     | B   | A     | C
Row 3: Q2           | B     | C   | B     | D
Row 4: Q3           | C     | A   | D     | A
Row 5: Q4 (Multi)   | 1-D,2-A,3-B,4-C | A,B,C,D | 1D2C3B4A | 1-D,2-A,3-C,4-B
...
Row 126: Q125       | A     | B   | C     | D
```

---

## Supported Multi-Part Answer Types

### Type 1: Ordering/Sequencing (Questions with Multiple Correct Answers in Order)
```
Question: "What is the correct order of incident response steps?"
Answer Key: "1-A,2-D,3-B,4-C" (A is first, D is second, B is third, C is fourth)
Student: "1-A,2-D,3-B,4-C" ✓ Correct
Student: "A,D,B,C" ✓ Correct (auto-converted)
Student: "1A2D3B4C" ✓ Correct (auto-converted)
```

### Type 2: Matching (Questions with Multiple Correct Selections)
```
Question: "Match security domains to their primary focus"
Answer Key: "1-A,2-B,3-C,4-D"
Student: "1-A,2-B,3-C,4-D" ✓ Correct
Student: "1A2B3C4D" ✓ Correct
```

---

## Directory Structure

```
your_project/
├── exams/
│   ├── exam_1.pdf (or similar)
│   ├── exam_1_answer_key.json (or auto-extracted)
│   ├── exam_2.pdf
│   └── exam_2_answer_key.json
│
├── answers/
│   ├── batch_dec25/
│   │   ├── exam_1_batch_dec25.xlsx
│   │   └── exam_2_batch_dec25.xlsx
│   │
│   ├── batch_july26/
│   │   ├── exam_1_batch_july26.xlsx
│   │   └── exam_2_batch_july26.xlsx
│   │
│   └── standalone/
│       └── exam_3_standalone.xlsx
│
└── outputs/
    ├── batch_dec25/
    ├── batch_july26/
    └── standalone/
```

---

## Validation Rules

### Required Elements
- ✅ Student names in header (unique)
- ✅ Answer letters are A, B, C, or D (case-insensitive)
- ✅ Multi-part answers have numbers (1-4 or 1-5)
- ✅ Total answers = total questions (125)

### Will Auto-Fix
- ✅ Extra spaces in answers → stripped
- ✅ Lowercase letters → converted to uppercase
- ✅ Missing dashes → added (A,B,C,D → 1-A,2-B,3-C,4-D)
- ✅ Inconsistent separators → normalized to dashes

### Will Fail With Error
- ❌ Student name is blank
- ❌ Answer contains invalid letters (E, F, X, etc.)
- ❌ Wrong number of questions (not 125)
- ❌ Multi-part answer has wrong count (4 answers instead of 3)

---

## Common Issues & Fixes

### Issue 1: File Won't Load
```
Error: "Cannot read Excel file"

Fix:
1. Save as .xlsx (not .xls or .csv)
2. Make sure file is not open in Excel
3. Check file path has no spaces in middle of name
4. Ensure student names don't have special characters (use _ or - instead)
```

### Issue 2: Scores Show as 0%
```
Error: "Student scores are all 0%"

Fix:
1. Check answer key file is in same directory as PDF
2. Verify answers in Excel match question numbers (Q1=Row 1, Q2=Row 2, etc.)
3. Ensure answer key has all 125 answers
4. Verify student name in Excel exactly matches name entered in CLI
```

### Issue 3: Multi-Part Answers Don't Match
```
Error: "Multi-part answers showing as wrong"

Fix:
1. Use format: "1-A,2-B,3-C,4-D" (with dashes and commas)
2. No spaces after commas: "1-A,2-B" not "1-A, 2-B"
3. All parts must have both number and letter: "1-A" not "A1"
4. Maximum 4 parts per answer (1-4)
```

### Issue 4: Special Characters in Student Name
```
Error: "Cannot find student results"

Fix:
Bad:  "José García"  →  Good: "Jose_Garcia" or "Jose-Garcia"
Bad:  "O'Brien"      →  Good: "OBrien" or "O_Brien"
Bad:  "李明"          →  Good: "Li_Ming" or "LiMing"
```

---

## Minimal Working Example

### Excel File (exam_1_batch_test.xlsx)

```
Student Name | Alice | Bob
Question 1   | A     | B
Question 2   | B     | C
Question 3   | C     | A
Question 4   | 1-A,2-B,3-C,4-D | A,B,C,D
...
Question 125 | A     | B
```

### Answer Key File (exam_1_answer_key.json)

```json
{
  "1": {"letter": "A", "text": "First answer explanation"},
  "2": {"letter": "B", "text": "Second answer explanation"},
  "3": {"letter": "C", "text": "Third answer explanation"},
  "4": {"letter": "D", "text": "Fourth answer explanation"},
  ...
  "125": {"letter": "A", "text": "Last answer explanation"}
}
```

---

## Quick Validation Checklist

Before running analysis:

- [ ] Excel file is .xlsx format
- [ ] Answer key is valid JSON
- [ ] Student names match between Excel and CLI input
- [ ] 125 rows of answers (one per question)
- [ ] No blank student names
- [ ] No invalid answer letters (only A, B, C, D)
- [ ] Answer key has all 125 questions
- [ ] All file paths are correct

---

## Auto-Validation Help

The tool will automatically:
✅ Clean up whitespace and capitalization
✅ Convert multi-format answers to standard form
✅ Validate answer key JSON structure
✅ Check for missing answers
✅ Verify answer letters are valid
✅ Report specific errors with solutions

If validation fails, check the error message for the exact issue!

---

**Version:** 1.0  
**Last Updated:** July 4, 2026  
**Status:** Production Ready
