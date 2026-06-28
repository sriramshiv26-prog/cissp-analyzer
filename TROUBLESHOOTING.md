# CISSP Analyzer - Troubleshooting Guide

## Installation Issues

### Issue: `ModuleNotFoundError: No module named 'pandas'`

**Cause:** Dependencies not installed in virtual environment

**Solution:**
```bash
cd /Users/sriram/cissp-analyzer
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

### Issue: `pip install pandas` fails with build error

**Cause:** Missing build tools or setuptools in venv

**Solution:**
```bash
# Install build tools first
pip install --upgrade setuptools wheel pip

# Then install dependencies
pip install -r requirements.txt
```

If still failing:
```bash
# Use binary wheels (no compilation needed)
pip install --only-binary :all: pandas openpyxl pypdf
```

---

## Excel File Issues

### Issue: `Excel must have column for student 'StudentName'`

**Cause:** Column names have leading/trailing spaces or wrong name

**Solution:**
- Column A must be: `Question`
- Column B must be: Exact student name (e.g., `Kapil`, not `kapil`)
- Check for extra spaces: `Question ` or ` Kapil`

**Fix:** Rename columns in Excel before uploading

---

### Issue: `'<' not supported between instances of 'NoneType' and 'str'`

**Cause:** Some questions have `None` exam_trick values that can't be sorted

**Solution:** Already fixed in latest version. Update:
```bash
git pull origin main
```

---

## PDF Processing Issues

### Issue: Only 5 answers extracted instead of 125

**Cause:** PDF format not recognized by extraction script

**Solution:**
1. Verify PDF has "Correct Answer" section with format: `121. B. [explanation]`
2. For multi-part answers (Q43, Q64), provide manually:
   ```bash
   python3 setup.py
   # When prompted, enter paths for both PDF and answer key
   ```

---

### Issue: Answer key JSON missing answers for some questions

**Cause:** PDF extraction incomplete

**Solution:**
```bash
# Manually check PDF and add missing answers to answer_key.json:
{
  "1": "B",
  "2": "C",
  ...
  "43": "1-B,2-A,3-C",
  "64": "1-D,2-C,3-B"
}
```

---

## Batch Analysis Issues

### Issue: Only one student in class report instead of all 4

**Cause:** Students analyzed separately instead of together

**Solution:**
```bash
# Use batch runner, not individual runs
python3 run_batch.py batch_config.json

# Or use setup wizard
python3 setup.py
```

---

### Issue: `FileNotFoundError` for Excel files

**Cause:** File paths have spaces but not quoted properly

**Solution:**
- Always use double quotes for paths with spaces
- Use absolute paths (starting with `/`)

**Wrong:**
```bash
python3 setup.py /path/file name.xlsx
```

**Correct:**
```bash
python3 setup.py "/path/file name.xlsx"
```

---

## Data Format Issues

### Issue: Student answers not recognized (all marked wrong)

**Cause:** Answer format doesn't match key

**Solution:** Supported formats for single answers:
- `A` (single letter)
- `B` (single letter)

Supported formats for multi-part:
- `1-B,2-A,3-C` (standard)
- `1B2A3C` (no separators)
- `B,A,C` (positional, no numbers)
- `1-B, 2-A, 3-C` (with spaces)

System auto-normalizes all formats.

---

## Question Mapping Issues

### Issue: Questions mapped to wrong domain/topic

**Cause:** Keyword-based analysis incomplete

**Solution:**

**Option 1:** Edit manually
```bash
nano data/question_domain_mapping.json
# Update domain, topic, difficulty, question_type, exam_trick
```

**Option 2:** Update keywords
```bash
nano cissp_analyzer/question_analyzer.py
# Update DOMAIN_KEYWORDS and TOPIC_KEYWORDS
python3 regenerate_mapping.py
```

---

## Performance Issues

### Issue: Analysis takes too long

**Cause:** Large PDFs or slow disk

**Solution:**
- Normal time: 10-30 seconds per student
- Ensure sufficient disk space
- Close other applications

---

## Git/GitHub Issues

### Issue: `git push` fails with authentication error

**Cause:** SSH keys not set up or GitHub credentials expired

**Solution:**
```bash
# Use HTTPS instead (one-time setup)
git remote set-url origin https://github.com/sriramshiv26-prog/cissp-analyzer.git

# Then push
git push origin main
```

---

## Common Workflows

### Setup New Exam

```bash
python3 setup.py
```

Interactive wizard handles all steps.

### Analyze Specific Students Only

Edit `batch_config.json`:
```json
{
  "students": [
    {"name": "Kapil", "excel": "/path/to/kapil.xlsx"},
    {"name": "Senthilraj", "excel": "/path/to/senthilraj.xlsx"}
  ]
}
```

Then run:
```bash
python3 run_batch.py batch_config.json
```

### Re-run Analysis with Same Data

```bash
python3 run_batch.py batch_config.json
```

(Previous reports in `outputs/` will be overwritten)

### Keep Multiple Exam Results

```bash
# Rename outputs before new analysis
mv outputs outputs_exam1
python3 setup.py  # Creates new outputs/
```

---

## Dependencies Checklist

Required packages:
- ✅ `pandas` - Excel parsing
- ✅ `openpyxl` - Excel file generation
- ✅ `pypdf` - PDF text extraction
- ✅ `python-docx` - DOCX file support (optional)

Verify all installed:
```bash
pip list | grep -E "pandas|openpyxl|pypdf|python-docx"
```

---

## Getting Help

If issue not listed:

1. **Check logs:** Run with verbose output
   ```bash
   python3 -u setup.py 2>&1 | tee debug.log
   ```

2. **Verify files:** Check all input files exist
   ```bash
   ls -la /path/to/pdf.pdf
   ls -la /path/to/student.xlsx
   ```

3. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.12+
   ```

4. **Recreate venv:**
   ```bash
   deactivate
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

**Version:** 2.1  
**Last Updated:** June 29, 2026
