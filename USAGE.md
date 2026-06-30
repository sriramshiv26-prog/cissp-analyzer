# CISSP Analyzer - Simple Usage Guide

## Quickest Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Interactive Setup
```bash
python3 analyze.py
```

### Step 3: Follow the Questions
The tool will ask you:
- Which exam? (1, 2, 3, etc.)
- Where is the exam PDF?
- Do you have an answer key?
- Student name?
- Student answer file?
- More students? (yes/no)
- Where to save reports?

**That's it!** Reports are generated automatically.

---

## What Happens Step-by-Step

### Question 1: Which Exam?
```
Exam number: 1
✓ Analyzing Mock Exam 1
```

### Question 2: Exam PDF Location
```
Path to exam PDF file: /Users/name/exams/mock1.pdf
✓ PDF found
```

### Question 3: Answer Key (Optional)
```
Path to answer key (optional): /Users/name/exams/answers.json
✓ Answer key found

OR

Path to answer key (optional): 
ℹ Will auto-extract from PDF
```

### Question 4: Add Students
```
Student 1:
Student name: Sri
Excel file for Sri: /Users/name/answers/sri_answers.xlsx
✓ Added: Sri

Student name: 
```
(Press Enter when done)

### Question 5: Output Directory
```
Where to save reports: outputs
✓ Output directory created
```

### Step 6: Run Analysis
```
Configuration Summary:
- Exam: Mock 1
- PDF: /Users/name/exams/mock1.pdf
- Students: 2
  • Sri: /Users/name/answers/sri_answers.xlsx
  • Sam: /Users/name/answers/sam_answers.xlsx
- Output: outputs

Run analysis now? [Y/n]: y

Running Analysis...
✓ Analysis Complete!
✓ Reports saved to: outputs
```

---

## Reports Generated

After running analysis, you'll get:

1. **Individual Reports** (one per student)
   - Student's performance summary
   - Breakdown by domain
   - Breakdown by difficulty
   - Breakdown by question type
   - Personalized study plan
   - Progress tracking (if multiple exams)
   - Adaptive recommendations

2. **Class Report**
   - Overall class performance
   - Class averages
   - Performance by domain
   - Top performers / areas for improvement

All saved as `.xlsx` files (Excel format) in your output directory.

---

## Examples

### Example 1: Single Student
```bash
$ python3 analyze.py

Exam number: 1
Path to exam PDF file: exam.pdf
Path to answer key (optional): 
Student name: John
Excel file for John: john_answers.xlsx
Student name: 
Where to save reports: reports
Run analysis now? [Y/n]: y

✓ Report saved: reports/CISSP_Individual_Report_John.xlsx
✓ Class report: reports/CISSP_Class_Analysis.xlsx
```

### Example 2: Multiple Students
```bash
$ python3 analyze.py

Exam number: 2
Path to exam PDF file: mock2.pdf
Path to answer key (optional): answer_key.json
Student name: Alice
Excel file for Alice: alice.xlsx
✓ Added: Alice

Student name: Bob
Excel file for Bob: bob.xlsx
✓ Added: Bob

Student name: Carol
Excel file for Carol: carol.xlsx
✓ Added: Carol

Student name: 
Where to save reports: mock2_results
Run analysis now? [Y/n]: y

✓ Reports saved for: Alice, Bob, Carol
✓ Class analysis complete
```

### Example 3: With Answer Key
```bash
$ python3 analyze.py

Exam number: 1
Path to exam PDF file: exam.pdf
Path to answer key (optional): keys/mock1_answers.json
✓ Answer key found

Student name: Student1
Excel file for Student1: responses.xlsx
✓ Added: Student1

Student name: 
Where to save reports: output
Run analysis now? [Y/n]: y

✓ Analysis complete - reports in: output
```

---

## Common File Paths

### macOS/Linux
```
Exam PDF:      /Users/yourname/exams/mock1.pdf
Answers:       /Users/yourname/answers/student1.xlsx
Answer Key:    /Users/yourname/keys/answers.json
Output:        output/  or  /Users/yourname/reports/
```

### Windows
```
Exam PDF:      C:\Users\YourName\exams\mock1.pdf
Answers:       C:\Users\YourName\answers\student1.xlsx
Answer Key:    C:\Users\YourName\keys\answers.json
Output:        output\  or  C:\Users\YourName\reports\
```

---

## Troubleshooting

### Error: "File not found"
- Check the file path is correct
- Make sure file exists in that location
- Try copying the full path from file explorer
- On macOS: Can drag file to terminal to get path

### Error: "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`
- Then try again: `python3 analyze.py`

### Error: "Invalid Excel file"
- Make sure Excel file has "Question" column
- Column names must match (Student names as column headers)
- File must be in .xlsx format

### Excel file has wrong format?
Expected structure:
```
Question | Student1 | Student2 | Student3
---------|----------|----------|----------
1        | A        | B        | A
2        | C        | A        | B
3        | A        | C        | C
...
```

---

## Tips

1. **Organize files first** - Keep exam PDFs, answer keys, and student files in separate folders
2. **Use consistent naming** - e.g., mock1.pdf, mock2.pdf, etc.
3. **Run multiple exams** - Run analyze.py again for exam 2, 3, etc.
4. **Track progress** - Compare reports across exams to see student improvement
5. **Save reports** - Excel files are easy to share and present

---

## Next Steps After Analysis

1. Open the .xlsx files in Excel or Google Sheets
2. Review individual student performance
3. Check class-level trends
4. Identify weak domains for extra study
5. Track progress across multiple exams

---

## Need Help?

- Run: `python3 analyze.py` - Interactive guide
- Check: `INSTALLATION.md` - Setup issues
- See: `README.md` - Full documentation

**That's it! Enjoy analyzing! 📊**
