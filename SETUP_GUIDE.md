# CISSP Analyzer - Setup Guide

A step-by-step guide for getting the CISSP Analyzer ready to run batch or standalone analysis.

---

## Quick Start (3 Steps)

```bash
# 1. Run the analyzer
python3 analyze.py

# 2. Choose batch or standalone analysis
# (The setup wizard will guide you through file creation)

# 3. Provide exam files and student data when prompted
```

---

## What You Need

### For Batch Analysis
To analyze multiple students from a single exam batch, you need:

1. **Exam PDF** — The test questions (scanned exam or exported PDF)
2. **Student Roster** — List of students (auto-created as `student_roster.json`)
3. **Answer Files** — Student answers in JSON format (one per student)

### For Standalone Analysis
To analyze a single student's exam:

1. **Exam PDF** — The test questions
2. **Student Answers** — JSON or Excel with answers
3. **Answer Key** — (Optional) Expected correct answers

---

## Setup Workflow

### Step 1: Run the Setup Wizard

When you run `python3 analyze.py` and select Batch or Full Batch Workflow, the setup wizard automatically:

✓ Checks if `student_roster.json` exists  
✓ Creates it if missing (with sample data)  
✓ Verifies directory structure (`exams/`, `answers/`, `reports/`)  
✓ Validates all required files are present  
✓ Guides you to place files in the correct locations  

### Step 2: Prepare Your Files

#### Directory Structure
```
cissp-analyzer/
├── exams/                    # Place exam PDFs here
│   ├── july12_exam.pdf      # Format: {batch_name}_exam.pdf
│   └── july26_exam.pdf
│
├── answers/
│   ├── july12/              # Place student answers here
│   │   ├── student1.json
│   │   └── student2.json
│   └── july26/
│       ├── student1.json
│       └── student2.json
│
├── reports/                 # Auto-generated analysis reports
│
├── student_roster.json      # Auto-created template
└── analyze.py              # Main entry point
```

#### Student Roster Format (`student_roster.json`)

```json
{
  "batches": {
    "july12": {
      "name": "July 12, 2026 Batch",
      "students": [
        {
          "id": "S001",
          "name": "John Doe",
          "email": "john@example.com"
        },
        {
          "id": "S002",
          "name": "Jane Smith",
          "email": "jane@example.com"
        }
      ],
      "exam_file": "exams/july12_exam.pdf",
      "answer_dir": "answers/july12"
    }
  }
}
```

**Edit this file to:**
- Add your student names, IDs, and emails
- Update the exam file paths
- Add new batches (copy-paste a batch section and rename)

#### Answer File Format

Each student gets their own JSON file with their answers:

**File:** `answers/july12/john_doe.json`

```json
{
  "student_name": "John Doe",
  "student_id": "S001",
  "answers": {
    "Q1": "A",
    "Q2": "C",
    "Q3": "B",
    "Q4": "D",
    "Q5": "A"
  }
}
```

**Or if you have them in Excel:**
- Place the Excel file in `answers/july12/`
- Run: `python3 auto_fix_answers.py --batch july12`
- This auto-converts Excel → JSON files

---

## Common Workflows

### Scenario 1: Starting Fresh with a New Batch

```bash
# 1. Run the analyzer
python3 analyze.py

# 2. Choose [3] Full Batch Workflow
# 3. Enter batch name: july12

# 4. Setup wizard will:
#    ✓ Create student_roster.json template
#    ✓ Create answers/july12/ directory
#    ✓ Ask you to place exam PDF and answer files

# 5. Once files are placed, re-run:
python3 analyze.py

# 6. Choose [3] Full Batch Workflow again
# 7. Setup wizard validates all files
# 8. Analysis starts automatically
```

### Scenario 2: Quick Standalone Analysis (One Student)

```bash
# 1. Run the analyzer
python3 analyze.py

# 2. Choose [2] Standalone Analysis
# 3. Answer the prompts (no files needed!)
# 4. Enter student name, answers, etc. interactively
```

### Scenario 3: Analyzing Existing Batch

```bash
# If you already have student_roster.json with batches defined:
python3 analyze.py

# Choose [1] Batch Analysis
# Enter batch name (e.g., july12)
# Setup wizard validates files
# Analysis runs
```

---

## Troubleshooting

### ❌ "student_roster.json not found"

**Solution:** Run `python3 analyze.py` → The setup wizard will create it automatically.

### ❌ "No exam PDFs found matching: july12*.pdf"

**Solution:** 
1. Place your exam PDF in the `exams/` folder
2. Name it with the batch name: `exams/july12_exam.pdf`
3. Re-run the analysis

### ❌ "No answer files in: answers/july12/"

**Solution:**
1. Create the directory: `mkdir -p answers/july12`
2. Place student answer files (.json) inside
3. Re-run the analysis

### ❌ "student_roster.json is corrupted"

**Solution:** Delete it and re-run `python3 analyze.py` to create a fresh template.

### ✅ Answer Files in Excel Format?

```bash
# Convert Excel to JSON automatically:
python3 auto_fix_answers.py --batch july12

# This creates JSON files from your Excel
# Then re-run the batch analysis
```

---

## File Placement Checklist

Before running analysis, verify:

- [ ] `student_roster.json` exists in project root
- [ ] Exam PDF exists: `exams/{batch_name}_exam.pdf`
- [ ] Answer directory exists: `answers/{batch_name}/`
- [ ] Student answer files exist: `answers/{batch_name}/*.json`
- [ ] Each answer file has: `student_name` and `answers` fields
- [ ] Student roster has batch defined with correct paths

---

## Next Steps

Once setup is complete:

1. **Run Batch Analysis:**
   ```bash
   python3 analyze.py
   Choose [1] or [3]
   ```

2. **Check Results:**
   - Reports saved to: `reports/{batch_name}_results/`
   - Open the Excel files to see scores and analytics

3. **Review Insights:**
   - Student performance by domain
   - Weak areas and recommended study topics
   - Class-wide statistics

---

## Getting Help

**Setup Wizard Not Clear?**
- Run: `python3 analyze.py --help`
- Read the prompts carefully—they tell you exactly what's needed

**Files in Wrong Format?**
- Use the auto-fix tool: `python3 auto_fix_answers.py --batch july12`
- It validates and corrects common format issues

**Still Stuck?**
- Check the examples in `examples/` folder (if available)
- The setup wizard will create sample files when needed
