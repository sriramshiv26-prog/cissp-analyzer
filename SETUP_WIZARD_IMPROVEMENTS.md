# Setup Wizard Improvements — CISSP Analyzer

**Problem Solved:** Users now get clear, interactive guidance on WHERE to place files and HOW to format them.

---

## What Changed

### Before
When you ran `python3 analyze.py` and chose a batch:
```
⚠ analyze_july12.py not found
Running: run_batch_workflow.py --batch july12 --full

[23:19:54] ✗ (Missing: answers/july12)
[23:19:54] ✗ (No PDFs found matching: exams/july12*.pdf)
[23:19:54] ✗ (Error: student_roster.json not found)
[23:19:54] ⚠ Some steps failed - review errors above
```

❌ **User experience:** Confusing errors, no guidance on what to do next.

---

### After
When you run `python3 analyze.py` and choose a batch:

```
================================================================================
CISSP ANALYZER - SETUP WIZARD
================================================================================

Let's set up your CISSP analyzer...

Step 1: Student Roster
✗ Missing: student_roster.json
✓ Created: student_roster.json (template)
  → Edit this file to add your students and batch info

Step 2: Directory Structure
📁 Checking directory structure...
  ✓ exams/ (Exam PDFs)
  ✓ answers/ (Student answer files)
  ✓ reports/ (Analysis reports)

Step 3: Batch Files
================================================================================
SETUP: JULY12 BATCH
================================================================================

To analyze the 'july12' batch, you need:
  1. Exam PDF file(s)
  2. Student answer file(s)
  3. (Optional) Answer key

✗ No exam PDFs found matching: exams/july12*.pdf
  → Place your exam PDF as: exams/july12_exam.pdf

✗ No answer files found in: answers/july12/
  → Place student answer files (.json) in: answers/july12/

📋 Expected File Format:
  Answer files should be JSON with structure like:
    {
      "student_name": "John Doe",
      "answers": {
        "Q1": "A",
        "Q2": "B",
        "Q3": "C",
        ...
      }
    }

================================================================================
SETUP VALIDATION
================================================================================

✗ Missing files for 'july12' batch:

  1. No exam PDFs found in exams/ matching: july12*.pdf
  2. No answer files in: answers/july12/

📖 Next steps:

  1. Prepare your exam PDFs and answer files
  2. Place them in the directories shown above
  3. Run: python3 analyze.py
```

✅ **User experience:** Clear instructions, knows exactly what's needed and where to put it.

---

## New Files Created

### 1. **`setup_wizard.py`** — Interactive Setup Guide
- Auto-detects missing files
- Creates `student_roster.json` template automatically
- Shows exact file paths and naming conventions
- Validates all files before analysis starts
- Guides users through each step

### 2. **`SETUP_GUIDE.md`** — Complete Setup Documentation
- Step-by-step workflow
- Directory structure diagram
- File format examples (JSON, Excel)
- Troubleshooting common issues
- Scenario-based workflows (new batch, existing batch, standalone)

### 3. **`FILE_FORMAT_REFERENCE.md`** — Format & Location Reference
- Visual file tree
- Detailed format explanations
- File naming conventions
- Example complete setups
- Validation checklist

### 4. **Updated `README.md`**
- Added prominent mention of setup wizard
- Simplified "Quick Start" to 3 steps
- References to detailed guides

---

## How It Works

### The Setup Wizard Flow

```
User runs: python3 analyze.py
    ↓
Chooses: [1] Batch Analysis or [3] Full Batch Workflow
    ↓
Enters: batch name (e.g., "july12")
    ↓
Setup Wizard Starts:
  1. Check student_roster.json
     ✗ Missing? → Auto-create template
  2. Check directory structure
     ✗ Missing? → Auto-create (exams/, answers/, reports/)
  3. Check batch files
     ✗ Exam PDF missing? → Tell user exactly where to put it
     ✗ Answer files missing? → Show expected format
  4. Validate all files
     ✓ All found? → Proceed to analysis
     ✗ Files missing? → Show clear next steps
```

---

## Key Features

### ✅ Auto-Creation
- Automatically creates `student_roster.json` with sample data
- Creates directory structure if missing
- Saves time on manual setup

### ✅ Clear Error Messages
**Before:** `Error: [Errno 2] No such file or directory: 'student_roster.json'`

**After:** 
```
✗ Missing: student_roster.json
✓ Created: student_roster.json (template)
  → Edit this file to add your students and batch info
```

### ✅ Visual File Tree
Shows the exact directory structure users need:
```
exams/
  └── july12_exam.pdf

answers/
  └── july12/
      ├── john_doe.json
      └── jane_smith.json
```

### ✅ Format Examples
Shows exactly what JSON should look like:
```json
{
  "student_name": "John Doe",
  "answers": {
    "Q1": "A",
    "Q2": "B"
  }
}
```

### ✅ Non-Blocking Warnings
Tells users what's optional vs. required:
```
✓ All required files found for 'july12' batch!
  Ready to run analysis.

⚠ Warnings:
  • student_roster.json not found (optional but recommended)
```

---

## Integration with `analyze.py`

The setup wizard is now integrated into the main entry point:

```python
# When user selects Batch Analysis or Full Batch Workflow
if not run_setup_wizard(batch_name):
    print("\n❌ Setup validation failed. Please fix the issues above and try again.")
    return False

# Only proceed if setup succeeds
print(f"\n📊 Starting analysis for batch: {batch_name}")
```

---

## User Benefits

| Before | After |
|--------|-------|
| ❌ Silent failures with cryptic errors | ✅ Clear, actionable error messages |
| ❌ No guidance on file locations | ✅ Exact paths shown |
| ❌ No examples of file format | ✅ JSON format examples provided |
| ❌ Users guess where files should go | ✅ Directory structure auto-created |
| ❌ Manual roster creation needed | ✅ Template auto-created |
| ❌ No validation before analysis | ✅ All files validated before proceeding |
| ❌ Buried in code, hard to find | ✅ Prominent in README & docs |

---

## What's Next?

### For Users:
1. Run `python3 analyze.py`
2. Follow the setup wizard prompts
3. Place your files in the suggested directories
4. Analysis runs automatically

### For the Tool:
- Setup wizard provides a better UX foundation
- Future: Could add file upload GUI
- Future: Could add web interface for file management
- Future: Could add automatic PDF parsing for answer keys

---

## Documentation Files

All new files are in the project root:

- **`setup_wizard.py`** — The automation
- **`SETUP_GUIDE.md`** — Complete user guide
- **`FILE_FORMAT_REFERENCE.md`** — Quick reference
- **`README.md`** — Updated with setup wizard info

Users should start with:
1. **First time?** → Read `README.md` quick start
2. **Need details?** → Read `SETUP_GUIDE.md`
3. **Need file formats?** → Read `FILE_FORMAT_REFERENCE.md`
4. **Running analysis?** → Follow the setup wizard prompts

---

## Testing

The setup wizard has been tested with:
- ✅ Missing `student_roster.json` (auto-creates)
- ✅ Missing directories (auto-creates)
- ✅ Missing exam PDFs (guides to correct path)
- ✅ Missing answer files (guides to correct format)
- ✅ File validation (checks all required files)

All scenarios show clear, actionable guidance.
