# CISSP Analyzer - Production Ready

A fully automated system for analyzing CISSP exam results with intelligent question categorization and personalized student reports.

## Quick Start (30 seconds)

```bash
cd /Users/sriram/cissp-analyzer
source venv/bin/activate
python3 setup.py
```

That's it! The interactive wizard handles everything.

## Features

✅ **Automated Analysis**
- Extract questions from PDF
- Extract answer key from PDF
- Auto-categorize questions (domain, topic, difficulty, exam tricks)
- Score all student answers
- Generate detailed reports

✅ **Multi-Format Support**
- Single answers: `A`, `B`, `C`, `D`
- Multi-part answers: `1-B,2-A,3-C` or `1B2A3C` or `B,A,C`
- Auto-normalization of answer formats

✅ **Comprehensive Reports**
- Individual reports (7 sheets per student)
- Class analysis (consolidated results)
- Personalized recommendations
- Domain/topic/difficulty breakdowns

✅ **Production Ready**
- No manual configuration needed
- Interactive setup wizard
- Handles unlimited students
- Reusable for any exam

## Installation (One-time Setup)

### Prerequisites
- Python 3.12+
- macOS/Linux/Windows

### Setup Steps

1. **Clone repository:**
   ```bash
   cd /Users/sriram
   git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
   cd cissp-analyzer
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

4. **Run setup wizard:**
   ```bash
   python3 setup.py
   ```

## Usage

### For New Exam (Recommended)

```bash
python3 setup.py
```

The wizard will guide you through:
1. Exam PDF path
2. Answer key location (or auto-extract)
3. Output directory
4. Each student's name + Excel file

Then it automatically:
- Extracts answer key from PDF
- Regenerates question mappings
- Runs batch analysis
- Generates all reports

### Manual Workflow (Advanced)

```bash
# Step 1: Create config
cat > batch_config.json << 'EOF'
{
  "exam_pdf": "/path/to/exam.pdf",
  "answer_key": "/path/to/answer_key.json",
  "output_dir": "outputs",
  "students": [
    {"name": "Student1", "excel": "/path/to/student1.xlsx"},
    {"name": "Student2", "excel": "/path/to/student2.xlsx"}
  ]
}
EOF

# Step 2: Extract answer key
python3 extract_answer_key.py "exam.pdf" "answer_key.json"

# Step 3: Regenerate mappings
python3 regenerate_mapping.py

# Step 4: Run analysis
python3 run_batch.py batch_config.json
```

## File Formats

### Exam PDF
- Questions and answers embedded
- Must have "Correct Answer" section
- Format: `121. B. [explanation]`

### Student Excel
- **Column A:** `Question` (1-125)
- **Column B:** Student name, values A-D

Example:
```
| Question | Kapil |
|----------|-------|
| 1        | B     |
| 2        | C     |
| 3        | B     |
```

## Output Reports

### Individual Reports (7 sheets each)
1. **Performance Summary** - Score, status, message
2. **Q&A Breakdown** - Question-by-question analysis
3. **By Question Type** - Application/Exception/Scenario/Sequence
4. **By Exam Tricks** - NOT/BEST/MOST/FIRST/ONLY
5. **By Domain** - 8 CISSP domains
6. **By Difficulty** - Easy/Medium/Hard
7. **Study Plan** - Personalized recommendations

### Class Report (4 sheets)
1. **Class Overview** - Metrics, averages, pass rates
2. **Student Rankings** - All students sorted by score
3. **Weakness Analysis** - Topics needing improvement
4. **Topic Analysis** - Performance by topic

## System Architecture

```
setup.py
  ↓
user input → batch_config.json
  ↓
regenerate_mapping.py → question_domain_mapping.json
  ↓
extract_answer_key.py → answer_key.json
  ↓
run_batch.py
  ├→ pdf_parser.py (extract questions)
  ├→ excel_parser.py (parse student answers)
  ├→ question_analyzer.py (categorize questions)
  ├→ analysis_engine.py (score answers)
  ├→ individual_report_gen.py (create reports)
  └→ class_report_gen.py (create class report)
  ↓
outputs/
  ├→ CISSP_Individual_Report_Student1.xlsx
  ├→ CISSP_Individual_Report_Student2.xlsx
  └→ CISSP_Class_Analysis.xlsx
```

## Key Files

| File | Purpose |
|------|---------|
| `setup.py` | Interactive wizard for new exams |
| `run_batch.py` | Batch runner for multiple students |
| `regenerate_mapping.py` | Extract questions + mappings from PDF |
| `extract_answer_key.py` | Extract answer key from PDF |
| `batch_config.json` | Configuration template |
| `requirements.txt` | Python dependencies |
| `QUICKSTART_SETUP.md` | Usage guide |
| `TROUBLESHOOTING.md` | Common issues + solutions |

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

Quick fixes:
- Missing dependencies: `pip install -r requirements.txt`
- File not found: Use absolute paths with quotes
- Wrong answers: Check answer_key.json format
- Questions wrong domain: Edit data/question_domain_mapping.json

## What Gets Automated

| Task | Automated? |
|------|-----------|
| Extract 125 questions from PDF | ✅ Yes |
| Extract answer key from PDF | ✅ Yes |
| Categorize questions (domain/topic/difficulty/tricks) | ✅ Yes |
| Parse student answers | ✅ Yes |
| Score all answers | ✅ Yes |
| Generate 7-sheet individual reports | ✅ Yes |
| Generate class analysis | ✅ Yes |
| Create personalized study plans | ✅ Yes |

## Performance

- **Per student:** 2-5 seconds
- **Class of 4:** 10-30 seconds total
- **Report generation:** 5-10 seconds

## Technology Stack

- **Language:** Python 3.12
- **PDF Parsing:** pypdf
- **Excel:** openpyxl, pandas
- **Analysis:** Custom keyword-based engine
- **Question Categorization:** ISC2 official domains + keyword matching

## Version

**2.1** - Production Ready ✅

**Changes:**
- Interactive setup wizard
- Batch runner for multiple students
- Multi-format answer support
- All dependencies documented
- Comprehensive troubleshooting guide

## Support

For issues:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verify dependencies: `pip list`
3. Check file formats (Excel columns, PDF structure)
4. Recreate venv if needed

## License

Educational use only

## Author

Sriram (with AI assistance)

---

**Last Updated:** June 29, 2026  
**Status:** Production Ready ✅  
**Next Steps:** Run `python3 setup.py` for new exam
