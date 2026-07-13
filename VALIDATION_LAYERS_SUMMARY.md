# Answer Sheet Validation Layers

Complete validation pipeline to ensure 5-6 submitted answer sheets are correct, grouped, and ready for analysis.

---

## The 3 Validation Layers

```
Layer 1: File & Format Validation
    ↓
Layer 2: Sheet Variation Detection
    ↓
Layer 3: Exam Consistency Grouping
    ↓
✅ Ready for Analysis
```

---

## Layer 1: File & Format Validation

**What it checks:**
- ✓ Files exist in correct location
- ✓ File format is valid (JSON or Excel)
- ✓ Directory structure is proper
- ✓ Student roster is present

**Tool:** `setup_wizard.py` (integrated in `analyze.py`)

**How to use:**
```bash
python3 analyze.py
# Choose batch
# Wizard validates files
# Shows clear guidance if anything missing
```

**Example output:**
```
Step 1: Student Roster
✓ Found: student_roster.json

Step 2: Directory Structure
  ✓ exams/ (Exam PDFs)
  ✓ answers/july12/ (Student answer files)
  ✓ reports/ (Analysis reports)

Step 3: Batch Files
✓ Found exam PDFs for 'july12': july12_exam.pdf
✓ Found 6 answer files in answers/july12/
```

**What it validates:**
- [ ] student_roster.json exists
- [ ] exams/ directory exists
- [ ] answers/{batch}/ directory exists
- [ ] Exam PDF files found
- [ ] Answer files found (JSON or Excel)

---

## Layer 2: Sheet Variation Detection

**What it checks:**
- ✓ Excel sheet naming consistency
- ✓ Column header variations
- ✓ Format normalization (Q1 vs 1 vs Q.1)
- ✓ Different sheets per student

**Tool:** `handle_sheet_variations.py`

**Why it matters:**
3 students, 3 different sheet names:
```
Student 1: Sheet named "John Doe"
Student 2: Sheet named "Answers"
Student 3: Sheet named "Sheet1"
```

**How to use:**
```bash
# Check single file
python3 handle_sheet_variations.py --file john_doe.xlsx --student "John Doe"

# Check batch consistency
python3 handle_sheet_variations.py --batch july12 --check

# Extract all sheets from one file
python3 handle_sheet_variations.py --file combined.xlsx --extract-all
```

**Example output:**
```
Sheet Consistency for batch: july12

Files: 6 students
Sheet patterns found:
  'john doe': student1.xlsx
  'answers': student2.xlsx
  'sheet1': student3.xlsx
  (3 different patterns)

Result: ✓ Auto-detected (no action needed)
        Analyzer handles automatically
```

**What it validates:**
- [ ] All Excel files have valid sheets
- [ ] Sheet names are detectable (student name or common pattern)
- [ ] Column headers are standard (Question, Answer, etc.)
- [ ] Format is consistent across files

---

## Layer 3: Exam Consistency Grouping

**What it checks:**
- ✓ Question count matches (Q1-Q125 vs Q1-Q50?)
- ✓ Question pattern is consistent
- ✓ Column structure is the same
- ✓ All sheets from same exam version

**Tool:** `detect_exam_consistency.py`

**Why it matters:**
If 6 sheets are submitted, are they ALL from:
- Same full exam (125 questions)?
- Mix of full exam + practice test?
- Different exam versions?

**How to use:**
```bash
# Quick consistency check
python3 detect_exam_consistency.py --batch july12

# Detailed per-file analysis
python3 detect_exam_consistency.py --batch july12 --detailed

# Create organization manifests
python3 detect_exam_consistency.py --batch july12 --fix-groups
```

**Example output - Single Exam:**
```
FILES CHECKED: 6
GROUPS FOUND: 1

Group 1: 6 files, 125 questions each
  • john_doe.json
  • jane_smith.json
  • alice_brown.json
  • bob_wilson.json
  • charlie_davis.json
  • diana_evans.json

✓ All 6 files are from SAME exam
```

**Example output - Multiple Exams:**
```
FILES CHECKED: 6
GROUPS FOUND: 2

Group 1: 3 files, 125 questions
  • john_doe.json
  • jane_smith.json
  • alice_brown.json

Group 2: 3 files, 50 questions
  • bob_wilson.json
  • charlie_davis.json
  • diana_evans.json

⚠️  Multiple exam versions detected!
  Option 1: Move Group 2 to separate batch
  Option 2: Add exam_version metadata
```

**What it validates:**
- [ ] All sheets have same question count
- [ ] All sheets use same question pattern
- [ ] All sheets have same column structure
- [ ] No mixed exam versions in same batch

---

## Complete Workflow: 5-6 Sheets Submitted

### Step 1: Receive Submissions

```
5-6 answer sheets from students:
  • Student 1: john_doe.xlsx (sheet: "John Doe")
  • Student 2: jane_smith.json (questions: Q1-Q125)
  • Student 3: alice_brown.xlsx (sheet: "Answers")
  • Student 4: bob_wilson.json (questions: Q1-Q125)
  • Student 5: charlie_davis.json (questions: Q1-Q125)
  • Student 6: diana_evans.xlsx (sheet: "Sheet1")
```

### Step 2: Place in Batch Directory

```bash
mkdir -p answers/july12
# Copy all files
cp *.xlsx *.json answers/july12/
```

### Step 3: Run Setup Wizard (Layer 1)

```bash
python3 analyze.py
# Choose [1] Batch Analysis
# Enter: july12

Setup wizard checks:
  ✓ Directory structure
  ✓ Files exist
  ✓ Formats valid
```

If Layer 1 passes → Continue to Layer 2

### Step 4: Check Sheet Variations (Layer 2)

```bash
python3 handle_sheet_variations.py --batch july12 --check

Output:
  john_doe.xlsx → "John Doe" sheet detected ✓
  jane_smith.json → JSON format ✓
  alice_brown.xlsx → "Answers" sheet detected ✓
  bob_wilson.json → JSON format ✓
  charlie_davis.json → JSON format ✓
  diana_evans.xlsx → "Sheet1" sheet detected ✓

Result: Different sheet names, but all auto-detected ✓
```

If Layer 2 passes → Continue to Layer 3

### Step 5: Verify Exam Consistency (Layer 3)

```bash
python3 detect_exam_consistency.py --batch july12

Output:
  Files checked: 6
  Groups found: 1
  
  Group 1: 6 files, 125 questions
    ✓ john_doe.xlsx
    ✓ jane_smith.json
    ✓ alice_brown.xlsx
    ✓ bob_wilson.json
    ✓ charlie_davis.json
    ✓ diana_evans.xlsx

Result: ✓ All 6 files are from SAME exam
```

If Layer 3 passes → All validations complete ✓

### Step 6: Run Analysis

```bash
python3 analyze.py
# Choose [3] Full Batch Workflow
# Enter: july12
# Setup wizard confirms all validations passed
# Analysis runs automatically ✓
```

---

## Validation Checklist

Use this before running analysis on 5-6 sheets:

### Layer 1: Format Validation
- [ ] Files placed in: `answers/{batch_name}/`
- [ ] At least one exam PDF in: `exams/{batch_name}*.pdf`
- [ ] Directory structure exists
- [ ] `student_roster.json` present

### Layer 2: Sheet Variation Validation
- [ ] Run: `python3 handle_sheet_variations.py --batch {name} --check`
- [ ] All sheets have valid names or patterns detected
- [ ] Column headers are recognizable
- [ ] No obvious format errors

### Layer 3: Exam Consistency Validation
- [ ] Run: `python3 detect_exam_consistency.py --batch {name}`
- [ ] All sheets have same question count
- [ ] All sheets use same question pattern
- [ ] Output shows: `✓ All N files are from SAME exam`

### Ready to Analyze
- [ ] All three layers passed
- [ ] No warnings from setup wizard
- [ ] Can proceed to `python3 analyze.py`

---

## Error Handling

### Layer 1 Failure: Missing Files

**Error:** `✗ No exam PDFs found`

**Fix:**
```bash
ls exams/
# If empty, place exam PDF:
cp exam.pdf exams/july12_exam.pdf
```

### Layer 2 Failure: Unrecognizable Sheets

**Error:** `⚠ Excel files use 3 different sheet names`

**Fix:**
```bash
# Most common patterns auto-detected, but if not:
python3 handle_sheet_variations.py --file problem.xlsx --student "StudentName"
# Edit the sheet name in Excel manually if needed
```

### Layer 3 Failure: Multiple Exams Detected

**Error:** `⚠ Multiple exam versions detected! Found 2 different question sets.`

**Fix - Option A:** Split into separate batches
```bash
mkdir answers/july12_full answers/july12_practice
# Move files accordingly
```

**Fix - Option B:** Add exam version metadata
```bash
# Edit student_roster.json:
# Add "exam_version": "july12_full.pdf" per student
```

---

## Summary: What Each Layer Does

| Layer | Tool | Detects | Action |
|-------|------|---------|--------|
| 1 | setup_wizard.py | Missing files, directories | Create, show guidance |
| 2 | handle_sheet_variations.py | Different sheet names | Auto-detect, normalize |
| 3 | detect_exam_consistency.py | Different question papers | Group, warn, organize |

---

## Real Example: 6 Student Submissions

### Before Validation
```
answers/july12/ (messy!)
├── john_doe.xlsx (sheet: "John Doe", 125 Q)
├── jane_smith.json (1-125, 125 Q)
├── alice_brown.xlsx (sheet: "Answers", 125 Q)
├── bob_wilson.json (Q1-Q125, 125 Q)
├── charlie_davis.json (Q1-Q125, 125 Q)
└── diana_evans.xlsx (sheet: "Sheet1", 125 Q)

Questions:
  ✓ Are files in right place?
  ✓ Do sheets have consistent names?
  ✓ Are all from same exam?
```

### After Validation
```
✅ Layer 1 PASSED
   All files in correct locations
   Directory structure valid

✅ Layer 2 PASSED
   Sheet names detected:
     "John Doe" → Student 1
     JSON format → Students 2, 4, 5
     "Answers" → Student 3
     "Sheet1" → Student 6
   Auto-normalized for analysis

✅ Layer 3 PASSED
   All 6 files have:
     - 125 questions
     - Q-prefixed pattern
     - Same column structure
   ✓ All from SAME exam
   
✅ READY TO ANALYZE
   Run: python3 analyze.py
```

---

## Integration Points

Each layer is integrated at key points:

**Setup Wizard (`analyze.py`):**
- Automatically runs Layer 1 & 3
- Blocks analysis if either fails
- Shows clear error messages

**Manual Tools:**
- Layer 2: `handle_sheet_variations.py`
- Layer 3: `detect_exam_consistency.py`

**Batch Workflow (`run_batch_workflow.py`):**
- Calls all three layers
- Validates before processing
- Reports issues with solutions

---

## Next Steps

1. **Place 5-6 answer sheets** in `answers/{batch}/`
2. **Run:** `python3 analyze.py`
3. **Follow wizard guidance** - it validates all layers
4. **If issues:** Use manual tools for detailed analysis
5. **Organize as needed** (split batches, add metadata)
6. **Re-run analysis** - now with validated data ✓

All three layers ensure you know exactly what you're analyzing!
