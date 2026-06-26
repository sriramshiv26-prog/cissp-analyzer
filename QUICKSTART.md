# Quick Start Guide

Get started in **5 minutes**.

---

## Installation (2 minutes)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer

# 2. Install Python 3.11+ from https://www.python.org/downloads/

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify (should see 26 passed)
pytest -v
```

---

## Running the Program (3 minutes)

### Prepare Your Files

1. **Exam PDF** - Questions and answers
   - Example: `downloads/June_21st_Test.pdf`

2. **Student Answers Excel** - Student names as columns, answers below
   - Example: `downloads/student_answers.xlsx`
   - Format: Each column is a student, rows contain answers (A/B/C/D)

3. **Output Folder** - Where reports will be saved
   - Example: `outputs/`

### Run Analysis

```bash
python3 run.py <exam_pdf> <answers_excel> <student_names> <output_dir>
```

#### Example 1: Single Student

```bash
python3 run.py \
  "downloads/June_21st_Test.pdf" \
  "downloads/student_answers.xlsx" \
  "John Doe" \
  "outputs/"
```

**Output:**
- `outputs/CISSP_Individual_Report_John_Doe.xlsx` (7-sheet professional report)

#### Example 2: Multiple Students

```bash
python3 run.py \
  "downloads/June_21st_Test.pdf" \
  "downloads/student_answers.xlsx" \
  "John Doe,Jane Smith,Bob Johnson" \
  "outputs/"
```

**Output:**
- `outputs/CISSP_Individual_Report_John_Doe.xlsx`
- `outputs/CISSP_Individual_Report_Jane_Smith.xlsx`
- `outputs/CISSP_Individual_Report_Bob_Johnson.xlsx`
- `outputs/CISSP_Class_Analysis.xlsx` (class-level report)

---

## What You Get

### Individual Reports (7 Sheets Each)

| # | Sheet | Shows |
|---|-------|-------|
| 1 | **Performance Summary** | Score, status, gap to pass, personalized insights |
| 2 | **Q&A Breakdown** | All questions with correct/wrong (color-coded) + domain + topic + type + trick |
| 3 | **By Question Type** | Performance by question format (Application, Scenario, etc.) |
| 4 | **By Exam Tricks** | Performance on trick questions (NOT, BEST, MOST, etc.) |
| 5 | **By Domain** | Performance across 8 CISSP domains with topic breakdown |
| 6 | **By Difficulty** | Easy/Medium/Hard analysis |
| 7 | **Study Plan** | Personalized weekly study plan with priorities and milestones |

### Class Report (1 File)

- Student rankings
- Class statistics
- Common weak areas
- Performance distribution

---

## Common Tasks

### Task 1: Analyze June 21st Test (5 students)

```bash
python3 run.py \
  "downloads/June 21st Test.pdf" \
  "downloads/student_answers.xlsx" \
  "Senthil Raj,Kapil,Praveena,Aman,Thameem" \
  "outputs/"
```

### Task 2: Analyze Practice Test (1 student)

```bash
python3 run.py \
  "downloads/Practice Test 1.pdf" \
  "downloads/arjun_answers.xlsx" \
  "Arjun" \
  "outputs/"
```

### Task 3: Analyze Custom Exam (2 students)

```bash
python3 run.py \
  "my_exams/custom_exam.pdf" \
  "my_exams/answers.xlsx" \
  "Student A,Student B" \
  "my_outputs/"
```

---

## View Results

Open the generated Excel files in:
- **Windows:** Microsoft Excel, Google Sheets
- **Mac:** Microsoft Excel, Numbers, Google Sheets
- **Linux:** LibreOffice Calc, Google Sheets

---

## Data Format Reference

### Excel Answer File Format

| Student 1 | Student 2 | Student 3 |
|-----------|-----------|-----------|
| A | B | C |
| B | A | A |
| C | C | B |
| D | D | D |
| ... | ... | ... |

- **First Row:** Student names (column headers)
- **Subsequent Rows:** Answer letters (A, B, C, D)
- **One answer per row** (for question 1, 2, 3, ...)

### Mapping File Format

If you want to analyze a custom exam, create `data/my_exam_mapping.json`:

```json
{
  "1": {
    "domain": 1,
    "topic": "Topic Name",
    "subtopic": "Specific Subtopic",
    "difficulty": "Easy|Medium|Hard",
    "question_type": "Definition|Application|Scenario|Exception|Sequence",
    "exam_trick": "MOST|BEST|FIRST|NOT|EXCEPT|None"
  },
  "2": {
    "domain": 2,
    ...
  }
}
```

Then run:
```bash
python3 run.py exam.pdf answers.xlsx "Student Name" outputs/ --mapping data/my_exam_mapping.json
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.11+ from https://www.python.org/downloads/ |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| pytest not found | Run `pip install pytest` |
| File not found | Check file paths are correct (use absolute paths if needed) |
| Excel won't open | Ensure .xlsx format, try opening in Google Sheets |

---

## Next Steps

1. ✅ **Install** → Follow Installation Guide
2. ✅ **Prepare files** → Gather exam PDF + answer Excel
3. ✅ **Run analysis** → Execute command above
4. ✅ **Review results** → Open Excel reports
5. ✅ **Share insights** → Use Study Plan for student guidance

---

## Support

- **README.md** - Full documentation and features
- **INSTALLATION.md** - Detailed platform-specific setup
- **Test files** - `tests/` folder has usage examples

---

**Ready to analyze?** Run your first report now! 🚀
