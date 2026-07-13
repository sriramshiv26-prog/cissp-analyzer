# Handling Different Excel Sheet Names

**Problem:** Students submit answer files with different sheet naming conventions.

**Solution:** Automatic sheet detection and conversion tools.

---

## Quick Answer

**YES, it will work!** The analyzer automatically detects and handles different sheet naming conventions from different students. If sheets are inconsistent, there's a tool to fix them.

---

## Three Student Scenarios

### Scenario: Students Name Sheets Differently

**Student 1:** Submits `answers_student1.xlsx` with sheet named `"Student 1 Answers"`

**Student 2:** Submits `answers_student2.xlsx` with sheet named `"Response Sheet"`

**Student 3:** Submits `answers_student3.xlsx` with sheet named `"Sheet1"`

✅ **No problem!** The analyzer handles all three automatically.

---

## How It Works

### Automatic Sheet Detection

When processing each file, the analyzer uses this strategy:

**Step 1:** Look for sheet matching student name
```
File: john_doe.xlsx
Sheets in file: ["John Doe", "Responses", "Other"]
✓ Matches! Uses: "John Doe"
```

**Step 2:** Look for common patterns
```
File: student2.xlsx
Sheets in file: ["Answers", "Data", "Notes"]
✓ Matches pattern! Uses: "Answers"
```

**Step 3:** Use first sheet (default)
```
File: student3.xlsx
Sheets in file: ["Sheet1", "Sheet2"]
⚠ No match. Uses: "Sheet1" (default)
```

---

## Common Sheet Name Patterns (Auto-Detected)

The analyzer recognizes these sheet name patterns automatically:

```
✓ "Answers"
✓ "Response"  
✓ "Exam"
✓ "CISSP"
✓ "Quiz"
✓ "Test"
✓ "Questions"
✓ "Q1-Q50"
✓ Or student's name: "John Doe", "Jane Smith"
```

Any of these work — no configuration needed!

---

## What If Sheets Are Inconsistent?

Run the consistency checker:

```bash
python3 handle_sheet_variations.py --batch july12 --check
```

Output shows exactly which students use which sheet names:

```
🔍 Checking sheet consistency for batch: july12
────────────────────────────────────────────────

Files checked: 3
Patterns found: 3

Patterns:
  'answers':
    • student1.xlsx: 'Answers'
  'response sheet':
    • student2.xlsx: 'Response Sheet'
  'sheet1':
    • student3.xlsx: 'Sheet1'

Recommendations:
  ⚠ 3 different sheet patterns found:
    • 'answers': used in 1 file(s)
    • 'response sheet': used in 1 file(s)
    • 'sheet1': used in 1 file(s)
```

---

## Fixing Inconsistent Sheets

### Option 1: Auto-Detect (Recommended)

The analyzer auto-detects and handles different sheets, **no action needed**.

### Option 2: Standardize Sheet Names

If you want all files to use the same sheet name:

```bash
# This guides you through each file
python3 handle_sheet_variations.py --file answers/july12/student1.xlsx --student "John Doe"
```

Shows what sheet will be used:

```
📄 Sheet Information: student1.xlsx
────────────────────────────────────

  📄 Found 3 sheet(s): ['Answers', 'Data', 'Notes']
  ✓ Matched pattern 'answers': 'Answers'

✓ Would use sheet: 'Answers'
```

### Option 3: Extract All Sheets from One File

If a file has multiple students in separate sheets:

```bash
python3 handle_sheet_variations.py --file combined_answers.xlsx --extract-all
```

Creates separate files for each sheet:

```
📂 Extracting all sheets from: combined_answers.xlsx
────────────────────────────────────────────────────

Extracted 3 sheet(s) from combined_answers.xlsx
  • Student 1: 50 rows → combined_answers_extracted/Student 1.json
  • Student 2: 50 rows → combined_answers_extracted/Student 2.json
  • Student 3: 50 rows → combined_answers_extracted/Student 3.json
```

---

## Real-World Example

### Setup: 3 Students, 3 Different Sheet Names

**Directory structure:**
```
answers/july12/
├── john_doe.xlsx          (sheet: "John Doe")
├── jane_smith.xlsx        (sheet: "Answers")
└── bob_wilson.xlsx        (sheet: "Sheet1")
```

**Run analysis:**
```bash
python3 analyze.py
# Choose [3] Full Batch Workflow
# Enter: july12
# Setup wizard validates everything
# Finds all 3 files with different sheet names
# Analysis proceeds normally ✓
```

**What happens internally:**
```
Processing john_doe.xlsx
  → Found sheets: ["John Doe", "Data"]
  → Matches student name "John Doe"
  → Uses: "John Doe" ✓

Processing jane_smith.xlsx
  → Found sheets: ["Answers", "Notes"]
  → Matches pattern "answers"
  → Uses: "Answers" ✓

Processing bob_wilson.xlsx
  → Found sheets: ["Sheet1", "Backup"]
  → No pattern match
  → Uses: "Sheet1" (default) ✓
```

**Result:** All 3 students analyzed successfully despite different sheet names!

---

## Tools Available

### 1. Setup Wizard (Built-in)
```bash
python3 analyze.py
# Automatically detects sheet variations during setup
```

### 2. Sheet Checker
```bash
python3 handle_sheet_variations.py --file <path> --student <name>
# Shows what sheet will be used for each file
```

### 3. Batch Consistency Checker
```bash
python3 handle_sheet_variations.py --batch july12 --check
# Shows all sheet patterns used in batch
```

### 4. Sheet Extractor
```bash
python3 handle_sheet_variations.py --file combined.xlsx --extract-all
# Extracts each sheet to separate JSON file
```

---

## Expected Column Names

Regardless of sheet name, the analyzer expects **two columns**:

| Format 1 | Format 2 | Format 3 |
|----------|----------|----------|
| Question | Q | Q.NO |
| Answer | John Doe | Response |

The auto-fixer normalizes these automatically to:
```
| Question | [Student Name] |
```

---

## Troubleshooting

### ❓ "Different students use different sheet names - will this break?"

**Answer:** ✅ No! It handles it automatically.

The analyzer:
1. Reads sheet names from each file
2. Matches them using smart detection
3. Processes each with the correct sheet
4. Warns you if inconsistency found

### ❓ "What if a student's sheet name is completely unusual?"

**Answer:** The tool uses the first sheet as fallback.

If a student names their sheet something random like "XYZ123", it will:
1. Try to match by student name ❌
2. Try to match common patterns ❌
3. Use first sheet (default) ✓

Then warn you: `⚠ Using first sheet (no pattern match): 'XYZ123'`

### ❓ "Can I manually specify which sheet to use per student?"

**Answer:** Yes! Three ways:

**Method 1:** Rename sheet before submitting (ask students)
```
Standard: "Answers" for all students
```

**Method 2:** Use student name as sheet name
```
Sheet named: "John Doe" for john_doe.xlsx
```

**Method 3:** Edit student roster
```json
{
  "students": [
    {
      "name": "John Doe",
      "excel_sheet": "John Doe",
      "file": "john_doe.xlsx"
    }
  ]
}
```

---

## Workflow: Different Sheet Names Per Student

### Step 1: Students Submit Files

```
john_doe.xlsx     → Sheet: "John Doe"
jane_smith.xlsx   → Sheet: "Answers"  
bob_wilson.xlsx   → Sheet: "Sheet1"
```

### Step 2: Place in Batch Directory

```bash
mkdir -p answers/july12
# Copy all files to answers/july12/
cp john_doe.xlsx answers/july12/
cp jane_smith.xlsx answers/july12/
cp bob_wilson.xlsx answers/july12/
```

### Step 3: (Optional) Check Consistency

```bash
python3 handle_sheet_variations.py --batch july12 --check
# Shows what sheets will be used
```

Output:
```
Patterns:
  'john doe': john_doe.xlsx
  'answers': jane_smith.xlsx
  'sheet1': bob_wilson.xlsx
```

### Step 4: Run Analysis

```bash
python3 analyze.py
# Choose [3] Full Batch Workflow
# Enter: july12
# Setup validates files
# Analysis starts automatically
```

✅ All 3 students analyzed correctly despite different sheet names!

---

## Column Name Variations (Also Auto-Handled)

If students use different column headers:

| Student 1 | Student 2 | Student 3 |
|-----------|-----------|-----------|
| Question | Q | Q.NO |
| John Doe | Answers | Response |

The auto-fixer normalizes to:
```
| Question | [Student Name] |
```

**Automatically fixed during:** `python3 auto_fix_answers.py --batch july12`

---

## Summary

| Scenario | Solution | Effort |
|----------|----------|--------|
| Different sheet names | Auto-detected | ✓ Automatic |
| Different column names | Auto-fixed | ✓ Automatic |
| Multiple sheets per file | Sheet extractor tool | ⚠ Manual (simple) |
| Completely non-standard | Use first sheet + warning | ⚠ May need edit |

**Bottom Line:** 3 students with different sheet names? **No problem!** It just works. ✅
