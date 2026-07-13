# CISSP Exam Analysis - Quick Start Guide

## 🚀 How to Run a Complete Analysis

### **Option 1: Interactive Mode (Recommended)**

```bash
python3 run_exam_analysis.py
```

This will guide you through:
1. ✅ Create exam folder (with name)
2. ✅ Upload PDF question file
3. ✅ **Answer key extraction** with confidence checking
   - If confidence is high (>75%): Automatically uses extracted answers
   - If confidence is low: **Shows 5 options:**
     - Option 1: Use extracted anyway (risky)
     - Option 2: Upload answer_key.json file
     - Option 3: Enter answers manually (Q by Q)
     - Option 4: Review & correct extracted answers
     - Option 5: Skip this exam
4. ✅ Upload student answer Excel files
5. ✅ Automatic analysis
6. ✅ Generate reports

---

## 📋 Answer Key Formats Supported

### **Option A: JSON Upload**
Create a file `answer_key.json`:
```json
{
  "1": "D",
  "2": "B",
  "3": "A",
  "4": "C",
  ...
}
```

Or with Q prefix:
```json
{
  "Q1": "D",
  "Q2": "B",
  ...
}
```

### **Option B: Manual Entry**
System will prompt you to enter answers one by one.

### **Option C: Review & Correct**
System extracts automatically, you review and fix any errors.

---

## 📂 Exam Folder Structure

After running analysis, your exam will be organized as:

```
exams/CISSP_July_2026/
├── questions/
│   └── CISSP_Practice_Assessment_-_With_Answers_S6QnQf1.pdf
├── answer_keys/
│   ├── answer_key.json
│   └── answer_key_metadata.json
├── student_answers/
│   ├── kapil-july-12.xlsx
│   ├── 12 July 2026-Mock test 7 - Senthilraj.xlsx
│   └── Mock Test Aman 11 july.xlsx
├── reports/
│   ├── Kapil_Report.xlsx
│   ├── Senthilraj_Report.xlsx
│   └── Aman_Report.xlsx
├── logs/
└── metadata.json
```

---

## 🎯 Features

### ✅ Smart Answer Key Detection

**Automatic Extraction:**
- Scans PDF for "The correct answer is [A/B/C/D]" pattern
- Calculates confidence score
- Shows warnings if pattern looks unusual

**Confidence Scoring:**
- 95%+ = Use automatically
- 75-95% = Ask user
- <75% = Show all fallback options

### ✅ Flexible Excel Parsing

Automatically detects column names:
- "Question" / "Questions" / "Q"
- "Answer" / "Answers" / "A"

Works with different Excel formats without configuration.

### ✅ Validated Answer Extraction

- Blank answer detection
- Lowercase auto-correction (a → A)
- Typo detection with suggestions
- Invalid input handling
- Whitespace trimming

### ✅ Complete Report Generation

- Individual student reports (Excel)
- Class summary reports
- All metrics calculated:
  - Overall score
  - Domain breakdown
  - Topic analysis
  - Difficulty levels
  - Question types
  - Validation statistics

---

## 💾 Metadata Tracking

Each analysis saves:

**answer_key_metadata.json:**
```json
{
  "method": "automatic",
  "total_answers": 162,
  "confidence": 0.95,
  "timestamp": "2026-07-13T16:30:00"
}
```

This tracks:
- How answers were obtained (auto / manual / json)
- When analysis was run
- Confidence of extraction

---

## ⚠️ What Happens If...

### PDF can't be read?
→ System asks you to upload answer_key.json manually

### Excel columns are different format?
→ System detects & asks for confirmation

### Student has blanks/typos?
→ System flags them separately in validation stats

### Answer key extraction has low confidence?
→ System offers 5 options (automatic, json, manual, review, skip)

---

## 🔍 Example Workflow

```
$ python3 run_exam_analysis.py

================================================================================
CISSP EXAM ANALYSIS SYSTEM
================================================================================

Enter exam name (e.g., CISSP_July_2026):
> CISSP_Aug_2026

Enter path to PDF question file (or press ENTER to skip):
> /path/to/exam.pdf
✓ Copied PDF

================================================================================
ANSWER KEY MANAGER - Extract & Validate
================================================================================

Extracted: 125 answers
Confidence: 92%

✓ Confidence sufficient. Using extracted answers.

Enter paths to student answer files (one per line, empty line to finish):
File 1: /path/to/student1.xlsx
  Student name (suggested: 'student1'): John
✓ Copied

File 2: /path/to/student2.xlsx
  Student name (suggested: 'student2'): Jane
✓ Copied

File 3: 
(empty line to finish)

================================================================================
ANALYZING PERFORMANCE
================================================================================

✓ John: 82.4% (103/125)
✓ Jane: 91.2% (114/125)

================================================================================
GENERATING REPORTS
================================================================================

✓ John_Report.xlsx (17.5 KB)
✓ Jane_Report.xlsx (17.5 KB)

================================================================================
ANALYSIS COMPLETE
================================================================================

Exam Folder: /Users/sriram/cissp-analyzer/exams/CISSP_Aug_2026

Results:
  Jane    : 91.2% (114/125)
  John    : 82.4% (103/125)

All files saved in:
  /Users/sriram/cissp-analyzer/exams/CISSP_Aug_2026
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| PDF extraction returns 0 answers | Ensure PDF has "The correct answer is" text |
| Excel parsing fails | Check column names (Question/Q, Answer/A) |
| Low confidence on extraction | Upload answer_key.json manually or enter answers |
| Student file not found | Double-check file path |

---

## 📞 Support

- Answers extracted with **95% confidence** → Auto-accepted
- Answers extracted with **75-95% confidence** → Show options
- Answers extracted with **<75% confidence** → Require manual entry or JSON upload

**Always verify first exam analysis before processing multiple students.**

---

## 🚀 Next Steps

1. Run: `python3 run_exam_analysis.py`
2. Choose your exam name
3. Provide PDF path
4. Let system extract answers (or upload JSON)
5. Add student Excel files
6. Check reports in exam folder

All files stay organized by exam!
