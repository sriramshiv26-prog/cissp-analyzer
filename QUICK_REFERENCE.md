# CISSP Analyzer - Quick Reference Card

## One Command = Complete Analysis

```bash
python3 setup.py
```

**That's it!** The wizard handles everything.

---

## Setup (First Time Only)

```bash
cd /Users/sriram/cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## For Each New Exam

```bash
source venv/bin/activate
python3 setup.py
```

The wizard will ask for:
1. Exam PDF path
2. Answer key path (or auto-extract)
3. Output directory
4. Each student's name + Excel file

---

## What You Need

| Item | Format |
|------|--------|
| **Exam PDF** | Questions + answers embedded |
| **Student Excel** | Column A: "Question" (1-125)<br>Column B: Student name (A/B/C/D answers) |

---

## What You Get

✅ **Individual Reports** (7 sheets each)
- Performance Summary
- Q&A Breakdown
- By Question Type
- By Exam Tricks
- By Domain
- By Difficulty
- Study Plan

✅ **Class Report** (4 sheets)
- Class Overview
- Student Rankings
- Weakness Analysis
- Topic Analysis

---

## Manual Workflow (Advanced)

```bash
# Step 1: Create config
nano batch_config.json

# Step 2: Regenerate mappings
python3 regenerate_mapping.py

# Step 3: Run analysis
python3 run_batch.py batch_config.json
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| File not found | Use absolute paths with quotes |
| Wrong answers | Check `answer_key.json` format |
| Only 1 student in class report | Use `run_batch.py`, not individual runs |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

---

## Key Commands

```bash
# New exam (recommended)
python3 setup.py

# Manual batch run
python3 run_batch.py batch_config.json

# Regenerate question mappings
python3 regenerate_mapping.py

# Extract answer key only
python3 extract_answer_key.py "exam.pdf" "answer_key.json"

# Check if everything installed
pip list | grep -E "pandas|openpyxl|pypdf"
```

---

## File Structure

```
/Users/sriram/cissp-analyzer/
├── setup.py                    ← Run this
├── run_batch.py
├── regenerate_mapping.py
├── extract_answer_key.py
├── requirements.txt
├── batch_config.json          ← Config template
├── data/
│   └── question_domain_mapping.json
├── outputs/                   ← Reports go here
│   ├── CISSP_Individual_Report_*.xlsx
│   └── CISSP_Class_Analysis.xlsx
└── docs/
    ├── QUICKSTART_SETUP.md
    ├── TROUBLESHOOTING.md
    └── README_PRODUCTION.md
```

---

## Excel Column Format

**Right ✅**
```
| Question | StudentName |
|----------|-------------|
| 1        | B           |
| 2        | C           |
```

**Wrong ❌**
```
| Q        | Answer |      (wrong column names)
| 1        | B      |      (missing student name)
```

---

## Multi-Part Answer Formats

All these work (auto-normalized):
- `1-B,2-A,3-C` (standard)
- `1B2A3C` (no separators)
- `B,A,C` (positional)
- `1-B, 2-A, 3-C` (with spaces)

---

## Performance

- Per student: 2-5 seconds
- Class of 4: 10-30 seconds
- Generating reports: 5-10 seconds

---

## System Requirements

- Python 3.12+
- ~100MB disk space
- 2GB RAM

---

## GitHub Repo

📍 https://github.com/sriramshiv26-prog/cissp-analyzer

**Latest commit:** Push after each test  
**Branch:** main  
**Status:** Production Ready ✅

---

## Support

1. **Quick issues:** Check this card
2. **Common problems:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **Setup help:** [QUICKSTART_SETUP.md](QUICKSTART_SETUP.md)
4. **Full details:** [README_PRODUCTION.md](README_PRODUCTION.md)

---

## Workflow Diagram

```
┌─────────────────┐
│  python3 setup.py
└────────┬────────┘
         │
    ┌────▼────────────────────┐
    │ Interactive Wizard       │
    │ - Ask for PDF            │
    │ - Ask for students       │
    │ - Ask for output dir     │
    └────┬────────────────────┘
         │
    ┌────▼──────────────────┐
    │ Automatic Processing  │
    │ - Extract questions   │
    │ - Extract answer key  │
    │ - Analyze questions   │
    │ - Score answers       │
    │ - Generate reports    │
    └────┬──────────────────┘
         │
    ┌────▼────────────────────┐
    │ outputs/                 │
    │ - Individual reports     │
    │ - Class analysis         │
    └─────────────────────────┘
```

---

**Version:** 2.1  
**Last Updated:** June 29, 2026  
**Print this card for easy reference!** 🎓
