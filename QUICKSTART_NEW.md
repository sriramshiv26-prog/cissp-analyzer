# CISSP Analyzer - Quick Start Guide

## Prerequisites
- Python 3.12+
- Virtual environment (venv)

## Setup (First Time Only)
```bash
cd /Users/sriram/cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Workflow: Analyzing Student Exam Results

### Step 1: Prepare Files
- **Exam PDF:** Questions + answer key (e.g., `exam.pdf`)
- **Student Excel:** One file per student with columns "Question" | "StudentName"

### Step 2: Extract Answer Key & Regenerate Mappings
```bash
python3 regenerate_mapping.py
```

### Step 3: Run Analysis
**Single student:**
```bash
python3 run.py "exam.pdf" "student.xlsx" "StudentName" "outputs/" "answer_key.json"
```

**Multiple students:**
```bash
rm -rf outputs/*
python3 run.py "exam.pdf" "kapil.xlsx" "Kapil" "outputs/" "answer_key.json"
python3 run.py "exam.pdf" "aman.xlsx" "Aman" "outputs/" "answer_key.json"
python3 run.py "exam.pdf" "senthilraj.xlsx" "Senthilraj" "outputs/" "answer_key.json"
python3 run.py "exam.pdf" "praveena.xlsx" "Praveena" "outputs/" "answer_key.json"
```

### Step 4: Check Reports
- `outputs/CISSP_Individual_Report_[Name].xlsx` - Individual reports (7 sheets)
- `outputs/CISSP_Class_Analysis.xlsx` - Class analysis

## Report Sheets (7 per student)
1. Performance Summary - Overall score & status
2. Q&A Breakdown - Question-by-question analysis
3. By Question Type - Application/Exception/Scenario/Sequence
4. By Exam Tricks - NOT/BEST/MOST/FIRST/ONLY analysis
5. By Domain - 8 CISSP domains
6. By Difficulty - Easy/Medium/Hard
7. Study Plan - Personalized recommendations

## Excel Format
```
| Question | StudentName |
|----------|-------------|
| 1        | B           |
| 2        | C           |
| 3        | B           |
```

## System Components
- **pdf_parser.py** - Extract questions from PDF
- **excel_parser.py** - Parse student answers
- **question_analyzer.py** - Auto-analyze domain/topic/difficulty using keywords
- **analysis_engine.py** - Score comparison
- **report generators** - Create Excel reports

## What's Automated
✅ Extract questions from PDF
✅ Extract answer key from PDF
✅ Analyze question metadata (domain, topic, difficulty, exam tricks)
✅ Parse student answers from Excel
✅ Score answers
✅ Generate individual + class reports

## Troubleshooting
- Missing deps: `pip install -r requirements.txt`
- File paths: Use double quotes for paths with spaces
- Wrong mappings: Edit `data/question_domain_mapping.json` or update keywords in `question_analyzer.py`

---
Version 2.0 | Production Ready ✅
