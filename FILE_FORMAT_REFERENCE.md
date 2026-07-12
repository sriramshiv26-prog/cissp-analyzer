# File Format Reference

Quick visual guide to file formats and locations for the CISSP Analyzer.

---

## Directory Tree

```
cissp-analyzer/
│
├── analyze.py                    ← RUN THIS: python3 analyze.py
│
├── student_roster.json           ← AUTO-CREATED: Lists students & batches
│
├── exams/                        ← PLACE YOUR EXAM PDFs HERE
│   ├── july12_exam.pdf          ← Format: {batch_name}_exam.pdf
│   ├── july26_exam.pdf
│   └── dec25_exam.pdf
│
├── answers/                      ← PLACE ANSWER FILES HERE
│   ├── july12/                  ← One folder per batch
│   │   ├── john_doe.json        ← One JSON file per student
│   │   ├── jane_smith.json
│   │   └── student3.json
│   ├── july26/
│   │   ├── student1.json
│   │   └── student2.json
│   └── dec25/
│       └── ... more students
│
├── reports/                      ← AUTO-GENERATED: Analysis results
│   ├── july12_results/
│   │   ├── CISSP_Individual_Report_john_doe.xlsx
│   │   ├── CISSP_Individual_Report_jane_smith.xlsx
│   │   └── CISSP_Class_Report_July12.xlsx
│   └── july26_results/
│       └── ... more reports
│
└── [other config files]
```

---

## File Formats in Detail

### 1. Student Roster (`student_roster.json`)

**Location:** Project root  
**Auto-created:** Yes  
**Edit:** Yes (add your students)

```json
{
  "batches": {
    "july12": {
      "name": "July 12, 2026 Batch",
      "students": [
        {
          "id": "S001",
          "name": "John Doe",
          "email": "john.doe@company.com"
        },
        {
          "id": "S002",
          "name": "Jane Smith",
          "email": "jane.smith@company.com"
        }
      ],
      "exam_file": "exams/july12_exam.pdf",
      "answer_dir": "answers/july12"
    },
    "july26": {
      "name": "July 26, 2026 Batch",
      "students": [
        {
          "id": "S003",
          "name": "Alice Johnson",
          "email": "alice@company.com"
        }
      ],
      "exam_file": "exams/july26_exam.pdf",
      "answer_dir": "answers/july26"
    }
  }
}
```

**Key Points:**
- One entry per batch
- Student names should match answer files
- Email is optional but recommended
- Exam file path: relative to project root

---

### 2. Student Answers (JSON Format)

**Location:** `answers/{batch_name}/` directory  
**One file per student**  
**Naming:** `firstname_lastname.json` or any `.json` name  

**Format:**

```json
{
  "student_name": "John Doe",
  "student_id": "S001",
  "exam_date": "2024-07-12",
  "answers": {
    "Q1": "A",
    "Q2": "B",
    "Q3": "C",
    "Q4": "D",
    "Q5": "A",
    "Q6": "B",
    "Q7": "C"
  }
}
```

**Required Fields:**
- `student_name` — Must match name in student_roster.json
- `answers` — Object with Question → Answer pairs
  - Keys: "Q1", "Q2", "Q3" (or "1", "2", "3")
  - Values: "A", "B", "C", "D" (or 1, 2, 3, 4)

**Optional Fields:**
- `student_id` — For reference
- `exam_date` — When they took the exam

**Alternative Formats Supported:**

If you have answers in Excel instead:

```excel
Student Name  | Q1  | Q2  | Q3  | Q4
-----------   | --- | --- | --- | ---
John Doe      | A   | B   | C   | D
Jane Smith    | B   | A   | D   | C
```

Run: `python3 auto_fix_answers.py --batch july12`  
This automatically converts to JSON format ✓

---

### 3. Exam PDF

**Location:** `exams/` directory  
**Naming:** `{batch_name}_exam.pdf`  
**Format:** PDF with questions and answer key  

**Example names:**
- `july12_exam.pdf` ✓
- `july26_exam.pdf` ✓
- `dec25_exam.pdf` ✓
- `exam_july12.pdf` ✗ (wrong order)

**Content Requirements:**
- Must have CISSP questions (with question numbers)
- Must have answer key (correct answers marked)
- Common sources: Scanned PDFs, exported test files, practice tests

---

### 4. Generated Reports

**Location:** `reports/{batch_name}_results/`  
**Format:** Excel (.xlsx)  
**Auto-created:** Yes  

**Report Types:**

#### Individual Reports
```
CISSP_Individual_Report_John_Doe.xlsx
├── Summary (Score, % correct, weak domains)
├── Detailed Analysis (Each question with category, your answer, correct answer)
├── Domain Breakdown (Performance by domain)
├── Study Plan (Adaptive recommendations)
└── Performance Chart (Visual breakdown)
```

#### Class Report
```
CISSP_Class_Report_July12.xlsx
├── Summary (Class average, high/low scores)
├── Individual Scores (All students' performance)
├── Domain Analysis (Which topics the class struggled with)
├── Question Analysis (Which questions most students missed)
└── Class Statistics (Distribution, trends)
```

---

## Step-by-Step File Setup

### For a New Batch (july12)

**1. Prepare Exam PDF**
```bash
# Copy your exam to exams/
# Rename it: july12_exam.pdf
cp ~/Downloads/Test_July.pdf exams/july12_exam.pdf
```

**2. Prepare Student Answers**
```bash
# Create folder for this batch
mkdir -p answers/july12

# Option A: JSON files (recommended)
# Create one file per student
cat > answers/july12/john_doe.json << 'EOF'
{
  "student_name": "John Doe",
  "answers": {
    "Q1": "A",
    "Q2": "B"
  }
}
EOF

# Option B: Excel file (will be auto-converted)
# Place Excel in answers/july12/student_answers.xlsx
# Run: python3 auto_fix_answers.py --batch july12
```

**3. Update Roster**
```bash
# Edit student_roster.json
# Add your students to the "july12" section
```

**4. Run Analysis**
```bash
python3 analyze.py
# Choose [1] or [3]
# Enter batch: july12
# Setup wizard validates everything
# Analysis starts automatically
```

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| "No exam PDFs found" | Exam not in `exams/` or wrong name | Rename to `{batch_name}_exam.pdf` |
| "No answer files found" | Answers not in `answers/{batch}/` | Create folder and add JSON files |
| "Student name mismatch" | Name in JSON doesn't match roster | Update either roster or JSON file |
| "Invalid JSON" | Typo in answer file | Check brackets, quotes, colons |
| "Can't read PDF" | Wrong file type | Ensure it's a PDF (not image) |

---

## Validation Checklist

Before running analysis:

```
[ ] Exam PDF exists: exams/{batch_name}_exam.pdf
[ ] Answer folder exists: answers/{batch_name}/
[ ] At least one answer file in answers/{batch_name}/*.json
[ ] Each answer file has: student_name, answers
[ ] Answer file is valid JSON (no syntax errors)
[ ] Student names match between roster and answer files
[ ] student_roster.json exists in project root
```

---

## Example: Complete Setup for "july12"

**Final structure:**
```
cissp-analyzer/
├── student_roster.json
│   └── Contains: july12 batch with S001, S002, S003
├── exams/
│   └── july12_exam.pdf
├── answers/
│   └── july12/
│       ├── john_doe.json (S001)
│       ├── jane_smith.json (S002)
│       └── alice_brown.json (S003)
└── analyze.py
```

**Run:**
```bash
python3 analyze.py
# Choose [3] Full Batch Workflow
# Enter: july12
# → Analysis starts automatically!
```

**Get:**
```
reports/july12_results/
├── CISSP_Individual_Report_John_Doe.xlsx
├── CISSP_Individual_Report_Jane_Smith.xlsx
├── CISSP_Individual_Report_Alice_Brown.xlsx
└── CISSP_Class_Report_July12.xlsx
```

---

## Need Help?

- **Setup Guide:** Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Quick Reference:** Run `python3 analyze.py --help`
- **Auto-Fix Issues:** Run `python3 auto_fix_answers.py --batch july12`
