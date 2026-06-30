# START HERE - 3 Commands to Analyze CISSP Exams

## Do This Once

### 1. Install
Copy and paste this:
```
pip install -r requirements.txt
```

Done! All dependencies installed automatically.

---

## Analyze Each Exam

### 2. Run Analysis
Copy and paste this:
```
python3 analyze.py
```

### 3. Answer Questions
The tool asks you simple questions:

```
Exam number: 1
Path to exam PDF file: /path/to/exam.pdf
Path to answer key (optional): [press Enter if you don't have one]
Student name: Sri
Excel file for Sri: /path/to/sri_answers.xlsx
Student name: [press Enter when done]
Where to save reports: outputs
Run analysis now? [Y/n]: y
```

**Done!** Reports are created automatically.

---

## That's It!

- **3 questions** to answer
- **No config files** to create
- **No commands** to remember
- **Automatic reports** generated

---

## What You Get

After running, you'll have:
- 📊 **Student Performance Reports** (one per student)
- 📈 **Class Analysis Report** (overall summary)
- 📝 **All saved as Excel files** (easy to view/share)

---

## File Locations (Examples)

**On Mac/Linux:**
```
Exam PDF:     /Users/name/exams/mock1.pdf
Student file: /Users/name/answers/student1.xlsx
Answer key:   /Users/name/keys/answers.json
```

**On Windows:**
```
Exam PDF:     C:\Users\name\exams\mock1.pdf
Student file: C:\Users\name\answers\student1.xlsx
Answer key:   C:\Users\name\keys\answers.json
```

---

## Common Questions

**Q: What if I don't have an answer key?**
A: Just press Enter - it will auto-extract from the PDF

**Q: Can I analyze multiple students?**
A: Yes! The tool asks for each student one by one

**Q: How many times can I run this?**
A: As many times as you want! Run for exam 1, then exam 2, etc.

**Q: Where are the reports?**
A: They're saved in the directory you specified (default: "outputs")

---

## Two Commands Total

1. **First time only:**
   ```
   pip install -r requirements.txt
   ```

2. **Every time you analyze:**
   ```
   python3 analyze.py
   ```

Then just answer the questions!

---

## Questions?

- See `USAGE.md` for detailed examples
- See `INSTALLATION.md` if setup issues
- See `README.md` for full documentation

---

**Ready? Run: `python3 analyze.py`**
