# CISSP Analyzer Phase 2 - User Guide

**Version:** 2.0 | **Status:** Production Ready | **Release Date:** July 2026

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [New Workflow Overview](#new-workflow-overview)
4. [Step-by-Step Tutorials](#step-by-step-tutorials)
5. [FAQ](#faq)
6. [Troubleshooting](#troubleshooting)
7. [File Organization](#file-organization)

---

## Quick Start

### Single Command Entry Point

```bash
python3 run.py
```

That's it! The entire exam analysis system is now accessed through an interactive menu.

**What it does:**
- Shows available questionnaires
- Allows uploading new PDF exams
- Processes student answer sheets
- Generates individual and class reports
- Tracks processed files automatically

---

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd cissp-analyzer

# Install dependencies
pip install -r requirements.txt

# Verify installation
python3 run.py
```

If you see the main menu, installation is successful!

---

## New Workflow Overview

### The Complete Process

```
START
  ↓
[Main Menu]
  ├─→ Upload New Questionnaire
  │     ├─→ Provide PDF file path
  │     ├─→ Enter exam name
  │     └─→ Exam folder created
  │
  ├─→ Select Exam
  │     ├─→ [Exam Submenu]
  │     │     ├─→ Process Answer Sheets
  │     │     │     ├─→ Auto-detects new files
  │     │     │     ├─→ Validates format
  │     │     │     ├─→ Generates reports
  │     │     │     └─→ Tracks processed files
  │     │     │
  │     │     └─→ Generate Class Report
  │     │           ├─→ Loads all student reports
  │     │           ├─→ Calculates metrics
  │     │           └─→ Generates aggregated report
  │     │
  │     └─→ Back to Main Menu
  │
  └─→ Exit
```

### Key Features

✓ **Menu-Driven Interface** - No command-line arguments needed  
✓ **Auto-Detection** - New files detected automatically  
✓ **State Tracking** - Never re-processes the same file  
✓ **Validation** - Comprehensive error checking  
✓ **Feedback** - Clear success/error messages  
✓ **Multi-Exam Support** - Handle multiple questionnaires  
✓ **Class Aggregation** - Automatic metrics calculation  

---

## Step-by-Step Tutorials

### Tutorial 1: First Time Setup (Upload Your First Questionnaire)

**Scenario:** You have a CISSP exam PDF and want to set it up for student analysis.

**Steps:**

1. Run the analyzer:
   ```bash
   python3 run.py
   ```

2. You'll see the main menu:
   ```
   ======================================================================
   CISSP ANALYZER - Main Menu
   ======================================================================
   
   No questionnaires found.
   
   [1] Upload NEW questionnaire
   [2] Exit
   
   ======================================================================
   ```

3. Press `1` to upload a questionnaire

4. When prompted, enter the PDF file path:
   ```
   Enter PDF file path (or drag/drop): /path/to/exam.pdf
   ```
   - You can type the path or drag/drop the file

5. Provide the exam name:
   ```
   Exam name (e.g., CISSP_June_2026): CISSP_Practice_Set_1
   ```

6. Add an optional description:
   ```
   Description (optional, press Enter to skip): June 2026 practice exam
   ```

7. Confirm:
   ```
   Exam Name: CISSP_Practice_Set_1
   Description: June 2026 practice exam
   
   Confirm? (y/n): y
   ```

8. Success! You'll see:
   ```
   ✓ Questionnaire 'CISSP_Practice_Set_1' created with 100 questions.
   Folder: exams/CISSP_Practice_Set_1_20260716_095423
   ```

**Result:** The exam is now in the system and ready for student submissions.

---

### Tutorial 2: Adding Student Answer Sheets

**Scenario:** Students have submitted their answer sheets as Excel files. You want to process them.

**Prerequisites:**
- You've already uploaded a questionnaire (see Tutorial 1)
- Student answer sheets as `.xlsx` files

**Steps:**

1. Run the analyzer:
   ```bash
   python3 run.py
   ```

2. Main menu shows your exam:
   ```
   Available Questionnaires:
   
   [1] CISSP_Practice_Set_1
       Created: 20260716_095423
   
   [2] Upload NEW questionnaire
   [3] Exit
   ```

3. Select your exam by pressing `1`

4. You'll see the exam submenu:
   ```
   ======================================================================
   Exam: CISSP_Practice_Set_1
   ======================================================================
   
   [1] Process new answer sheets
   [2] Generate class report
   [3] Back to main menu
   ```

5. Place student answer Excel files in the exam folder or press `1` to process existing files

6. The system auto-detects new files:
   ```
   Processing Summary - CISSP_Practice_Set_1
   ======================================================================
   
   Total files in exam: 3
   New files to process: 3
   
   Files:
   • Alice.xlsx
   • Bob.xlsx
   • Charlie.xlsx
   
   Estimated time: ~15 seconds
   
   Continue processing? (y/n): y
   ```

7. Processing starts and you'll see:
   ```
   ✓ Processing complete! Processed: 3, Failed: 0, Skipped: 0
   ```

8. Individual reports are generated and saved

**Result:** Each student has an individual report with their scores and analysis.

---

### Tutorial 3: Generating Class Reports

**Scenario:** All students have submitted answers. You want to see class-level analytics.

**Prerequisites:**
- At least one exam with processed student files
- See Tutorials 1 & 2

**Steps:**

1. Run the analyzer and select your exam (see Tutorial 2, steps 1-4)

2. Press `2` to generate class report

3. You'll see a preview:
   ```
   ======================================================================
   Class Report Preview - CISSP_Practice_Set_1
   ======================================================================
   
   Students Analyzed: 3
   Average Score: 76.7%
   Median Score: 75.0%
   Score Range: 60.0% - 95.0%
   Std Dev: 14.2%
   
   Pass Rate (>75%): 66.7% (2/3 students)
   
   Student Scores:
   ──────────────────────────────────────────────────────
     Alice                            95/100 ( 95.0%) ✓ PASS
     Bob                              75/100 ( 75.0%) ✓ PASS
     Charlie                          60/100 ( 60.0%) ✗ FAIL
   ======================================================================
   ```

4. Confirm to generate:
   ```
   Generate class report? (y/n): y
   ```

5. Report is generated:
   ```
   ✓ Class report generated: exams/CISSP_Practice_Set_1_xxx/reports/Class_Report.json
   ```

**Result:** You have detailed class analytics showing averages, pass rates, and individual performance.

---

### Tutorial 4: Managing Multiple Questionnaires

**Scenario:** You teach multiple CISSP exam prep courses. You want to manage them separately.

**Steps:**

1. Each questionnaire is completely independent
   - When you upload a new PDF, a new folder is created
   - Each folder has its own students, reports, and state tracking

2. From the main menu:
   ```
   Available Questionnaires:
   
   [1] CISSP_Practice_Set_1
       Created: 20260716_095423
   
   [2] CISSP_Practice_Set_2
       Created: 20260716_100234
   
   [3] CISSP_June_2026_Exam
       Created: 20260716_110045
   
   [4] Upload NEW questionnaire
   [5] Exit
   ```

3. Select any exam to process its students and reports independently

4. Student answer sheets for each exam go in that exam's folder

5. Reports are organized by exam automatically

**Result:** Clean separation - each exam maintains its own data and analysis.

---

## FAQ

### Q: Where do I place student answer sheets?

**A:** Answer sheets are automatically placed in the exam's folder. The system detects them when you:
1. Run `python3 run.py`
2. Select the exam
3. Choose "Process new answer sheets"

You can place `.xlsx` files in the `exams/EXAM_NAME_TIMESTAMP/` folder before running, or select them when prompted.

---

### Q: How does the system detect new files?

**A:** The system uses a `.processed.json` file to track which files have been analyzed:

```json
[
  {
    "filename": "Alice.xlsx",
    "report_path": "reports/Alice.json",
    "processed_date": "2026-07-16T10:30:00"
  }
]
```

When processing starts, it compares all files in the folder against this list. Only new files are processed.

---

### Q: Can I process the same exam twice?

**A:** Yes! The system won't re-process files it's already seen, but:
- If you add NEW answer sheets, they'll be processed automatically
- If you REPLACE an answer sheet, the old one is skipped (state-tracked)
- To reprocess everything, manually delete `.processed.json` and individual reports

---

### Q: What happens if I change an answer sheet?

**A:** The system won't reprocess it because the filename is already marked as processed. To reprocess:

1. Rename the file (e.g., `Alice.xlsx` → `Alice_v2.xlsx`)
2. Delete the entry from `.processed.json` (in the exam folder)
3. Run processing again

---

### Q: What file formats are supported for answer sheets?

**A:** Currently supported:
- Excel files (`.xlsx`) - **Recommended**
- Required columns: `Question` and `Answer`
- Answer formats:
  - Single letter: `A`, `B`, `C`, `D`
  - Multi-part: `1-A,2-B,3-C`

Example structure:
```
Question | Answer
---------|--------
1        | A
2        | B
3        | A
```

---

### Q: How are scores calculated?

**A:** For each student:
- **Individual Score** = (Correct Answers / Total Questions) × 100
- **Pass Status** = Score ≥ 75% → PASS, < 75% → FAIL

For class:
- **Average** = Sum of all scores / Number of students
- **Median** = Middle value when scores sorted
- **Pass Rate** = (Number passing / Total students) × 100
- **Std Dev** = Statistical standard deviation of scores

---

### Q: Can I export reports in different formats?

**A:** Currently reports are saved as JSON files. This can be extended to:
- Excel format (`.xlsx`)
- PDF reports
- CSV exports

Check back for updates!

---

### Q: What happens if a student submits a blank or invalid answer?

**A:** The system:
1. Detects empty cells and logs them as warnings
2. Validates answer format (must be A-D or multi-part)
3. Reports issues during processing
4. Includes validation warnings in the report

---

## Troubleshooting

### Issue: "File not found: exam.pdf"

**Cause:** The PDF path is incorrect or the file doesn't exist

**Solution:**
```bash
# Check the file exists
ls -la /path/to/exam.pdf

# Drag/drop in terminal instead of typing
python3 run.py
# At prompt, drag the PDF file instead of typing path
```

---

### Issue: "Invalid PDF file: Stream has ended unexpectedly"

**Cause:** The PDF is corrupted or not a valid PDF

**Solution:**
1. Open the PDF in a PDF reader (Adobe, Preview, etc.)
2. If it won't open there, the file is corrupted
3. Get a fresh copy of the PDF and try again

---

### Issue: "No new answer sheets found"

**Cause:** All files have already been processed, or files are in wrong location

**Solution:**
```bash
# 1. Check files are in the exam folder
cd exams/EXAM_NAME_TIMESTAMP/
ls -la *.xlsx

# 2. Check .processed.json to see what's already processed
cat .processed.json

# 3. If you want to reprocess, remove the entry or rename the file
mv Alice.xlsx Alice_v2.xlsx
```

---

### Issue: "Duplicate student names found"

**Cause:** Two or more files have identical student names (case-insensitive)

**Solution:**
1. Rename files to have unique names: `Alice.xlsx`, `Alice_2.xlsx`
2. Or include more identifying info: `Alice_Section_A.xlsx`, `Alice_Section_B.xlsx`

---

### Issue: "Answer validation failed"

**Cause:** Answers don't match question format or have invalid letters

**Solution:**
1. Check answer format (only A, B, C, D allowed)
2. Check column names match ("Question", "Answer")
3. No empty cells in answer column

---

### Issue: Menu won't load / "Cannot read exams"

**Cause:** Permissions issue or corrupted metadata

**Solution:**
```bash
# 1. Check folder permissions
ls -la exams/

# 2. Check metadata is valid JSON
cat exams/EXAM_NAME/.exam_metadata.json | python3 -m json.tool

# 3. If JSON is corrupted, recreate the exam
```

---

### Issue: "Cannot generate class report: No student reports found"

**Cause:** No individual reports have been generated yet

**Solution:**
1. First, process answer sheets (Tutorial 2)
2. Wait for processing to complete
3. Then generate class report

---

## File Organization

### Folder Structure

```
cissp-analyzer/
├── run.py                          # Main entry point ← RUN THIS!
├── requirements.txt                # Python dependencies
├── README.md                       # Project overview
│
├── cissp_analyzer/                 # Main package
│   ├── exam_folder_manager.py     # Manages exam folders
│   ├── state_tracker.py            # Tracks processed files
│   ├── menu_controller.py          # Interactive menus
│   ├── pdf_upload_handler.py       # PDF upload & validation
│   ├── exam_processor.py           # Processes answer sheets
│   ├── class_report_aggregator.py  # Generates class reports
│   ├── processing_validator.py     # Data validation
│   └── ...other modules
│
├── exams/                          # Your exam data
│   ├── CISSP_Practice_Set_1_20260716_095423/
│   │   ├── exam.pdf               # Original PDF
│   │   ├── .exam_metadata.json    # Exam info
│   │   ├── .processed.json        # Processed file tracking
│   │   ├── Alice.xlsx             # Student answer sheet
│   │   ├── Bob.xlsx
│   │   └── reports/               # Generated reports
│   │       ├── Individual_Report_Alice.json
│   │       ├── Individual_Report_Bob.json
│   │       └── Class_Report.json
│   │
│   └── CISSP_June_2026_Exam_20260716_100200/
│       ├── exam.pdf
│       ├── .exam_metadata.json
│       └── ...
│
└── tests/                          # Test suite
    └── test_phase2_integration.py  # Integration tests
```

### What's in Each File

**`.exam_metadata.json`** - Exam information:
```json
{
  "exam_name": "CISSP Practice Set 1",
  "pdf_path": "/full/path/to/exam.pdf",
  "created_date": "20260716_095423",
  "total_questions": 100,
  "folder_id": "CISSP_Practice_Set_1_20260716_095423"
}
```

**`.processed.json`** - Tracking of processed files:
```json
[
  {
    "filename": "Alice.xlsx",
    "report_path": "reports/Individual_Report_Alice.json",
    "processed_date": "2026-07-16T10:30:00.123456"
  }
]
```

**`Individual_Report_*.json`** - Student analysis:
```json
{
  "student_name": "Alice",
  "exam": "CISSP Practice Set 1",
  "total_questions": 100,
  "answers_provided": 100,
  "answers": {1: "A", 2: "B", 3: "A", ...}
}
```

**`Class_Report.json`** - Class aggregation:
```json
{
  "total_students": 3,
  "average_score": 76.7,
  "median_score": 75.0,
  "min_score": 60.0,
  "max_score": 95.0,
  "std_dev": 14.2,
  "passing_count": 2,
  "pass_rate": 66.7,
  "exam_name": "CISSP Practice Set 1",
  "student_metrics": [...]
}
```

---

## Support & Feedback

For issues or feedback:
1. Check Troubleshooting section above
2. Review FAQ for common questions
3. Run with verbose logging: `python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)" && python3 run.py`

---

**End of User Guide**

Version 2.0 | July 2026 | CISSP Analyzer Project
