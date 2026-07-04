# How to Use Example Files

**Version:** 1.0 | **Date:** July 4, 2026 | **Status:** Production Ready

---

## What You Get

Three downloadable example files to start immediately:

### 1. EXAMPLE_answer_key.csv
- Answer key in CSV format (easy to read)
- 30 sample CISSP questions with answers
- Columns: Question | Answer | Explanation

### 2. EXAMPLE_answer_key.json
- Same data as CSV but in JSON format
- Ready to use with the tool
- 30 sample questions

### 3. EXAMPLE_student_answers.xlsx
- Excel spreadsheet with student answer sheet
- 4 sample students: Alice, Bob, Carol, David
- 20 sample questions (expand to 125)
- Includes instruction sheet with formatting guide
- Shows all supported answer formats including multi-part

---

## Quick Start: 5 Minutes to First Analysis

### Step 1: Download Example Files
```bash
# Clone repository
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer

# Files are ready to use:
ls -la EXAMPLE_*
  EXAMPLE_answer_key.csv
  EXAMPLE_answer_key.json
  EXAMPLE_student_answers.xlsx
```

### Step 2: Set Up Directories
```bash
# Create project structure
mkdir -p exams answers/batch_example students outputs/batch_example

# Copy example answer key
cp EXAMPLE_answer_key.json exams/example_answer_key.json
```

### Step 3: Create Sample PDF (Optional)
```bash
# For testing, use any PDF as exam
# The tool will extract answers from answer key file
cp ~/Downloads/any_document.pdf exams/example_exam.pdf
```

### Step 4: Copy Student Answers
```bash
# Copy the Excel file to answers folder
cp EXAMPLE_student_answers.xlsx answers/batch_example/
```

### Step 5: Run Analysis
```bash
python3 analyze.py

# Follow prompts:
# Select: 1 (Batch Analysis)
# Select: batch_example
# Exam file: exams/example_exam.pdf
# Answer key: exams/example_answer_key.json
# Answer sheet: answers/batch_example/EXAMPLE_student_answers.xlsx
# Output dir: outputs/batch_example
```

### Step 6: View Results
```bash
ls outputs/batch_example/
# Will show:
# - CISSP_Class_Report_Example.xlsx
# - CISSP_Individual_Report_Alice.xlsx
# - CISSP_Individual_Report_Bob.xlsx
# - CISSP_Individual_Report_Carol.xlsx
# - CISSP_Individual_Report_David.xlsx
```

---

## Understanding the Files

### EXAMPLE_answer_key.csv

Open in any text editor or Excel:

```
Question,Answer,Explanation
1,A,AES uses 128, 192, or 256-bit encryption with block size of 128 bits
2,B,Public key infrastructure enables digital certificates and signatures
3,C,Defense in depth uses multiple layers of security controls
4,D,Authentication, Authorization, Accounting are AAA framework components
...
30,B,Sample explanation for question 30
```

**How to Use:**
1. Open in Excel
2. Add more rows (Q31, Q32, ... Q125)
3. Fill in actual answers and explanations
4. Save as CSV or convert to JSON
5. Place in `exams/` folder

**To Convert to JSON:**
```bash
python3 << 'EOF'
import csv
import json

# Read CSV
with open('EXAMPLE_answer_key.csv', 'r') as f:
    reader = csv.DictReader(f)
    answer_key = {}
    for row in reader:
        answer_key[row['Question']] = {
            "letter": row['Answer'],
            "text": row['Explanation']
        }

# Write JSON
with open('answer_key.json', 'w') as f:
    json.dump(answer_key, f, indent=2)
EOF
```

---

### EXAMPLE_student_answers.xlsx

Open in Excel, Google Sheets, or LibreOffice:

**Sheet 1: "Student Answers"**
```
Question | Alice | Bob   | Carol | David
---------|-------|-------|-------|-------
Q1       | A     | B     | A     | C
Q2       | B     | C     | B     | D
Q3       | C     | A     | D     | A
Q4       | 1-D,2-A,3-B,4-C | A,B,C,D | 1D2C3B4A | 1-D,2-A,3-C,4-B
...
Q20      | ...   | ...   | ...   | ...
```

**Sheet 2: "Instructions"**
- Detailed formatting guide
- Answer format variations
- Naming conventions
- Step-by-step to expand

**How to Use:**

#### Option 1: Expand for Your First Real Analysis
1. Open EXAMPLE_student_answers.xlsx
2. Add rows for Q21 through Q125
3. Replace Alice/Bob/Carol/David with real student names
4. Fill in actual student answers
5. Save as: `exam_1_batch_[yourname].xlsx`
6. Place in `answers/batch_[yourname]/` folder

#### Option 2: Use as Template
```bash
# Copy to create new analysis
cp EXAMPLE_student_answers.xlsx answers/batch_dec25/exam_1_batch_dec25.xlsx

# Edit in Excel:
# 1. Replace student names (keep Column A as "Question")
# 2. Expand rows to Q125
# 3. Fill in real answers
# 4. Save
```

---

## Understanding Answer Formats

### Single Answers
**Q1-Q3, Q5-Q20: Single Answer Format**

These show the basic format (single letter answer):
```
Alice's Q1: A
Bob's Q2:   C
Carol's Q3: D
```

### Multi-Part Answers
**Q4, Q16: Multi-Part Answer Format**

These show ordering/matching questions with multiple correct answers:

**Q4 Example - Four Part Answer:**
```
Alice: 1-D,2-A,3-B,4-C   ← Proper format: number-letter,number-letter,...
Bob:   A,B,C,D           ← Positional format (auto-converted to 1-A,2-B,3-C,4-D)
Carol: 1D2C3B4A          ← No separators (auto-converted to 1-D,2-C,3-B,4-A)
David: 1-D,2-A,3-C,4-B   ← With dash format
```

All of these are automatically converted to: `1-D,2-A,3-B,4-C` format

**Q16 Example - Three Part Answer:**
```
Alice: 1-A,2-B,3-C       ← Three correct answers in order
Bob:   A,B,C             ← Auto-converted
Carol: 1A2B3C            ← Auto-converted
David: 1-A,2-B,3-C       ← Proper format
```

---

## Expanding to 125 Questions

### In Excel:

**Manual Way (Quick):**
1. Open EXAMPLE_student_answers.xlsx
2. Rows 2-21 have Q1-Q20
3. Select rows 2-21 (all data)
4. Copy
5. Click on row 22
6. Paste 5 times to reach row 126 (20×5=100 more rows)
7. Edit column A to have Q21, Q22, ... Q125
8. Fill in answers for each student

**Formula Way (Better):**
1. In row 22, put: =IF(ROW()<=126,"Q"&(ROW()-1),"")
2. Drag down to row 126
3. Add sample answers or leave blank for editing
4. Fill in real answers

### In Python:

```python
import openpyxl

# Load existing file
wb = openpyxl.load_workbook('EXAMPLE_student_answers.xlsx')
ws = wb['Student Answers']

# Current data goes from row 2 to 21 (Q1-Q20)
# Add Q21 to Q125

for q_num in range(21, 126):
    row_num = q_num + 1  # Row numbers start at 1
    ws[f'A{row_num}'] = f'Q{q_num}'
    # Leave columns B-E empty for manual entry
    # Or fill with random answers for testing

# Save
wb.save('expanded_answers.xlsx')
```

---

## Troubleshooting: Using Example Files

### Problem 1: "File not found"
```
Error: Cannot find EXAMPLE files

Solution:
1. Make sure you cloned the repository
2. Check files exist:
   ls -la EXAMPLE_*
3. Copy to correct location:
   cp EXAMPLE_*.* exams/ or answers/
```

### Problem 2: "CSV won't open in Excel"
```
Error: CSV looks wrong in Excel

Solution:
1. Right-click file → Open With → Excel
2. Let Excel auto-detect format
3. Or manually specify CSV format in Excel import wizard
4. Or use: EXAMPLE_answer_key.json instead
```

### Problem 3: "Excel file is corrupted"
```
Error: Cannot open EXAMPLE_student_answers.xlsx

Solution:
1. Try opening with Google Sheets (more forgiving)
2. Copy data manually to new Excel file
3. Or regenerate:
   rm EXAMPLE_student_answers.xlsx
   python3 generate_examples.py  (if available)
4. Or use CSV version instead
```

### Problem 4: "Multi-part answers not working"
```
Error: Q4 showing as 0% correct

Solution:
1. Check format matches answer key exactly:
   Answer Key: 1-D,2-A,3-B,4-C
   Student:    1-D,2-A,3-B,4-C ✓ Correct
   
2. Make sure no spaces:
   1-D,2-A,3-B,4-C  ✓ Correct
   1-D, 2-A, 3-B, 4-C  ✗ Wrong (spaces after comma)
   
3. Test with simpler format:
   A,B,C,D → Auto-converts to 1-A,2-B,3-C,4-D
```

### Problem 5: "Column mismatch error"
```
Error: "Student name not found"

Solution:
1. Open Excel and check column headers
2. Verify student names exactly match CLI input
3. No spaces: "Alice" not " Alice " or "alice"
4. Consistent spelling throughout
5. First row must have "Question" in A1 and student names in B1, C1, D1, etc.
```

---

## From Example to Production

### Phase 1: Understand (Today)
- Download and review example files
- Run test analysis with examples
- See output reports
- Understand format requirements

### Phase 2: Adapt (Hour 1)
- Copy EXAMPLE files
- Customize with your data
- Replace student names
- Add actual exam PDF
- Expand to 125 questions

### Phase 3: Validate (Hour 2)
- Check validation before running:
  - 125 questions? ✓
  - Student names match? ✓
  - All answers A/B/C/D? ✓
  - Answer key valid JSON? ✓
  - File paths correct? ✓

### Phase 4: Run (Hour 2)
- Execute analysis
- Review reports
- Verify results make sense
- Share reports with students

### Phase 5: Scale (Ongoing)
- Create batch folders for each cohort
- Use same templates for multiple batches
- Automate report distribution
- Track student progress over time

---

## Complete File Reference

### Location in Repository
```
cissp-analyzer/
├── EXAMPLE_answer_key.csv          (30 sample questions)
├── EXAMPLE_answer_key.json         (Same data, JSON format)
├── EXAMPLE_student_answers.xlsx    (4 students, 20 questions)
├── TEMPLATE_answer_key.json        (Blank template)
├── TEMPLATE_student_answers.md     (Format documentation)
├── FORMATS_AND_TEMPLATES_GUIDE.md  (Complete guide)
└── exams/                          (Put your files here)
    ├── your_exam.pdf
    └── your_exam_answer_key.json
```

### What Each File Contains

| File | Type | Contents | Use For |
|------|------|----------|---------|
| EXAMPLE_answer_key.csv | CSV | 30 sample Q&A | Reference, editing |
| EXAMPLE_answer_key.json | JSON | 30 sample Q&A | Tool input, testing |
| EXAMPLE_student_answers.xlsx | Excel | 4 students, 20 Q | Template, testing |
| TEMPLATE_answer_key.json | JSON | Blank structure | Start new answer key |
| TEMPLATE_student_answers.md | Markdown | Format guide | Learn formatting |
| FORMATS_AND_TEMPLATES_GUIDE.md | Markdown | Complete guide | Reference, validation |

---

## Quick Copy-Paste Workflow

```bash
# 1. Clone repo
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer

# 2. Set up directories
mkdir -p exams answers/batch_1 students outputs/batch_1

# 3. Copy and customize answer key
cp EXAMPLE_answer_key.json exams/my_exam_answer_key.json
# Edit with your actual answers

# 4. Copy and customize student answers
cp EXAMPLE_student_answers.xlsx answers/batch_1/my_exam_batch_1.xlsx
# Open in Excel, replace names, expand to 125 questions, fill answers

# 5. Get exam PDF
cp ~/Downloads/cissp_exam.pdf exams/my_exam.pdf

# 6. Run analysis
python3 analyze.py
# Follow prompts...

# 7. View results
ls outputs/batch_1/
# See all reports generated!
```

---

## Video/Screenshot Guide

For visual learners, here's what each example shows:

### EXAMPLE_answer_key.csv
```
When you open it, you see a table:
┌──────────┬────────┬──────────────────────────────┐
│ Question │ Answer │ Explanation                  │
├──────────┼────────┼──────────────────────────────┤
│ 1        │ A      │ AES uses 128, 192, or 256-..│
│ 2        │ B      │ Public key infrastructure..  │
│ 3        │ C      │ Defense in depth uses...     │
│ ...      │ ...    │ ...                          │
└──────────┴────────┴──────────────────────────────┘

This is what the answer key should look like!
```

### EXAMPLE_student_answers.xlsx
```
When you open it, you see:

Sheet 1: Student Answers
┌──────────┬────────┬─────┬───────┬────────┐
│ Question │ Alice  │ Bob │ Carol │ David  │
├──────────┼────────┼─────┼───────┼────────┤
│ Q1       │ A      │ B   │ A     │ C      │
│ Q2       │ B      │ C   │ B     │ D      │
│ Q3       │ C      │ A   │ D     │ A      │
│ Q4       │ 1-D... │ A.. │ 1D... │ 1-D... │ (multi-part)
│ ...      │ ...    │ ... │ ...   │ ...    │
└──────────┴────────┴─────┴───────┴────────┘

Sheet 2: Instructions (with formatting guide)

This is what your student answer sheet should look like!
```

---

## Support & Help

### Where to Find Help
| Question | Answer |
|----------|--------|
| How do I format answers? | See TEMPLATE_student_answers.md |
| What's the JSON format? | See EXAMPLE_answer_key.json |
| What answer formats work? | See FORMATS_AND_TEMPLATES_GUIDE.md |
| How do I use examples? | See THIS FILE |
| Where do files go? | See TEMPLATE_directory_structure.md |

### Quick Validation
```bash
# Check JSON is valid
python3 -c "import json; json.load(open('answer_key.json')); print('✓ Valid')"

# Check Excel file exists
ls -la answers/batch_1/*.xlsx

# Check answer count (should be ~126 for 125 questions + header)
python3 << 'EOF'
import openpyxl
wb = openpyxl.load_workbook('answers/batch_1/my_exam_batch_1.xlsx')
ws = wb.active
print(f"Rows: {ws.max_row}, Columns: {ws.max_column}")
print(f"Questions: Q1 to Q{ws.max_row-1}")
EOF
```

---

## Next Steps

1. **Download:** Clone repo and get example files
2. **Review:** Open EXAMPLE files in Excel/text editor
3. **Test:** Run with example data first
4. **Customize:** Replace with your data
5. **Expand:** Add Q21-Q125
6. **Validate:** Use checklist before running
7. **Run:** Execute analysis.py
8. **Share:** Review reports with students

---

**All example files are production-tested and ready to use! 🚀**

For more details, see: FORMATS_AND_TEMPLATES_GUIDE.md
