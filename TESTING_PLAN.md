# Pre-GitHub Testing Plan - Using Local Ollama Models

## Goal
Verify CISSP Analyzer runs smoothly on a typical user machine with local Ollama models before GitHub push.

---

## Phase 1: Environment Setup (15 min)

### Prerequisites Check
- [ ] Python 3.9+ installed: `python3 --version`
- [ ] pip available: `pip3 --version`
- [ ] Ollama running: Check if `ollama serve` is active
- [ ] Available Ollama models: `ollama list`

### Recommended Models for Testing
```
- qwen2.5-coder:7b    (primary - coding/analysis)
- gemma4:latest       (reasoning/logic)
- deepseek-coder:6.7b (fallback - coding)
```

### Fresh Environment Setup
```bash
# Create fresh virtual environment
python3 -m venv test_venv
source test_venv/bin/activate

# Verify clean state
pip list
```

---

## Phase 2: Installation Testing (20 min)

### Test 1: Automated Installer
```bash
chmod +x install.sh
./install.sh
# Choose: Create virtual environment (Y/n)
# Verify all dependencies install correctly
```

**Expected Results:**
- [ ] Python version verified (3.9+)
- [ ] pip upgraded
- [ ] Virtual environment created
- [ ] All packages installed (openpyxl, pandas, pypdf)
- [ ] Installation verified with no errors

### Test 2: Manual Installation
```bash
pip install -r requirements.txt
pip install -e .
```

**Expected Results:**
- [ ] All dependencies installed
- [ ] Package installed in dev mode
- [ ] No import errors

### Test 3: Verify Installation
```bash
python3 -c "from cissp_analyzer import CISSPAnalyzer; print('✓ Ready')"
python3 -m cissp_analyzer.dependency_checker
```

**Expected Results:**
- [ ] Package imports successfully
- [ ] All required dependencies shown as ✓
- [ ] Status report displays correctly

---

## Phase 3: Interactive CLI Testing (30 min)

### Test 1: Single Student Analysis
```bash
python3 analyze.py
```

**Simulate User Input:**
```
Exam number: 1
Path to exam PDF: data/sample_exam.pdf
Answer key (optional): [press Enter]
Student name: TestStudent
Excel file: data/sample_answers.xlsx
Student name: [press Enter]
Output directory: test_output
Run analysis: y
```

**Expected Results:**
- [ ] Interactive prompts appear
- [ ] File validation works
- [ ] Colored output displays correctly
- [ ] Analysis runs without errors
- [ ] Reports generated in test_output/

### Test 2: Multiple Students
```bash
python3 analyze.py
```

**Simulate User Input:**
```
Exam: 1
PDF: data/sample_exam.pdf
Answer key: [Enter]
Student: Student1
File: data/student1.xlsx
Student: Student2
File: data/student2.xlsx
Student: Student3
File: data/student3.xlsx
Student: [Enter]
Output: test_multi_output
Run: y
```

**Expected Results:**
- [ ] Multiple students added successfully
- [ ] All files validated
- [ ] All reports generated
- [ ] No cross-contamination between students

### Test 3: Error Handling
```bash
python3 analyze.py
```

**Test Missing File:**
```
Path to exam PDF: /nonexistent/file.pdf
```

**Expected Results:**
- [ ] Clear error message
- [ ] Helpful suggestion (use full path)
- [ ] Can retry without restarting

**Test Invalid Excel Column:**
```
Student name: Test
Excel file: /path/to/bad_format.xlsx
```

**Expected Results:**
- [ ] Clear error about missing "Question" column
- [ ] Program doesn't crash
- [ ] Can continue or exit gracefully

---

## Phase 4: Performance Testing (15 min)

### Test with Real Exam Data
```bash
time python3 analyze.py < test_inputs.txt
```

**Measure:**
- [ ] Time to completion
- [ ] Memory usage
- [ ] CPU load
- [ ] Report file sizes

**Expected Performance:**
- [ ] Single exam: < 5 minutes
- [ ] Multiple students: < 10 minutes
- [ ] Memory usage: < 500MB

---

## Phase 5: Output Quality Testing (20 min)

### Generated Files Check
```bash
# Verify files exist
ls -lh test_output/
```

**Check Each Report:**
- [ ] File exists with correct name
- [ ] File is valid .xlsx format
- [ ] Can open in Excel/Sheets
- [ ] Contains expected data
- [ ] No corruption or errors

### Report Content Validation
Open Excel files and verify:
- [ ] Student Performance Summary sheet exists
- [ ] Q&A Breakdown sheet exists
- [ ] By Question Type sheet exists
- [ ] By Domain sheet exists
- [ ] Study Plan sheet exists
- [ ] All data populated correctly
- [ ] No missing values
- [ ] Formatting looks good

### Class Report Validation
- [ ] CISSP_Class_Analysis.xlsx created
- [ ] Contains class statistics
- [ ] Shows performance by domain
- [ ] Averages calculated correctly

---

## Phase 6: Documentation Testing (15 min)

### Test START_HERE.md Instructions
- [ ] Read START_HERE.md (2 min)
- [ ] Follow instructions exactly
- [ ] Everything works as described
- [ ] No confusing parts

### Test USAGE.md Examples
- [ ] Try Example 1 from USAGE.md
- [ ] Try Example 2 from USAGE.md
- [ ] Both work as documented

### Test QUICK_REFERENCE.txt
- [ ] Print it out
- [ ] Can understand without other docs
- [ ] All information is accurate

---

## Phase 7: Edge Cases & Stress Testing (20 min)

### Test 1: Large Exam (150+ questions)
```bash
python3 analyze.py
# Use larger exam PDF
# Measure performance
```

**Check:**
- [ ] No timeout errors
- [ ] Memory stays reasonable
- [ ] Reports still accurate

### Test 2: Many Students (10+ students)
```bash
python3 analyze.py
# Add 10+ students
```

**Check:**
- [ ] All students processed
- [ ] No data loss
- [ ] Reports accurate for all students

### Test 3: Special Characters in Names
```
Student name: José García-López
Student name: 李明 (Chinese)
Student name: O'Brien
```

**Check:**
- [ ] Names handled correctly
- [ ] No encoding errors
- [ ] Reports display properly

### Test 4: Long File Paths
```bash
/very/long/path/to/deeply/nested/directory/exam.pdf
```

**Check:**
- [ ] Paths handled correctly
- [ ] No truncation
- [ ] Files found properly

---

## Phase 8: Dependency Scenarios (15 min)

### Test 1: Missing Dependency
```bash
pip uninstall openpyxl -y
python3 analyze.py
```

**Expected:**
- [ ] Clear error message
- [ ] Instructions to install
- [ ] No cryptic errors

**Fix:**
```bash
pip install openpyxl
```

### Test 2: Old Dependency Version
```bash
pip install openpyxl==3.9.0  # Old version
python3 analyze.py
```

**Expected:**
- [ ] Works or shows version warning
- [ ] Graceful handling

### Test 3: Fresh Install Simulation
```bash
# Create new venv
python3 -m venv fresh_test
source fresh_test/bin/activate
pip install -r requirements.txt
python3 analyze.py
# Run full test
```

**Expected:**
- [ ] Everything works fresh
- [ ] No hidden dependencies

---

## Phase 9: Cross-Platform Testing

### macOS
- [ ] Test on macOS (current system)
- [ ] File paths work correctly
- [ ] Colors display properly in terminal

### Linux (if available)
```bash
# Same tests as above
```

### Windows (document for users)
- [ ] Document Windows-specific paths
- [ ] Note any cmd.exe vs PowerShell differences

---

## Phase 10: Documentation & Final Check (10 min)

### README Check
- [ ] All features documented
- [ ] Installation steps clear
- [ ] Usage examples work

### Commit Log Check
```bash
git log --oneline -10
```

- [ ] All commits have clear messages
- [ ] No "WIP" or "temp" commits
- [ ] Ready for public view

### Final Checklist
- [ ] All tests passing
- [ ] No lingering test files
- [ ] No debug print statements
- [ ] No hardcoded paths
- [ ] Code follows project style
- [ ] Documentation is complete
- [ ] Performance is acceptable

---

## Ollama Model Integration Notes

### Using Ollama (Optional Future Enhancement)
If integrating Ollama for analysis enhancement:

```python
from ollama import Ollama

# Analyze weak areas with reasoning
client = Ollama(model='gemma4:latest')
response = client.generate("Analyze these weak domains: ...")
```

### Local Testing Advantage
- [ ] No API calls needed
- [ ] No rate limiting
- [ ] No internet dependency
- [ ] Fast feedback loop
- [ ] Free testing

---

## Success Criteria

✓ All tests pass  
✓ No errors or warnings  
✓ Documentation is clear  
✓ Performance is acceptable  
✓ Edge cases handled  
✓ Ready for GitHub upload  

---

## Test Data Locations

Sample files for testing:
```
data/sample_exam.pdf           - Test exam PDF
data/sample_answers.xlsx       - Sample student answers
data/answer_key.json          - Answer key
tests/fixtures/               - Test fixtures
```

---

## Timeline

| Phase | Time | Status |
|-------|------|--------|
| 1. Setup | 15 min | Tomorrow AM |
| 2. Installation | 20 min | Tomorrow AM |
| 3. CLI | 30 min | Tomorrow AM |
| 4. Performance | 15 min | Tomorrow PM |
| 5. Output | 20 min | Tomorrow PM |
| 6. Docs | 15 min | Tomorrow PM |
| 7. Edge Cases | 20 min | Tomorrow PM |
| 8. Dependencies | 15 min | Tomorrow PM |
| 9. Cross-Platform | 10 min | Tomorrow PM |
| 10. Final | 10 min | Tomorrow PM |
| **TOTAL** | **~3 hours** | **Ready to push** |

---

## Ready to Push Checklist

After all testing:

- [ ] All tests pass
- [ ] No regressions
- [ ] Documentation complete
- [ ] Performance acceptable
- [ ] Edge cases handled
- [ ] Can run on fresh Python install
- [ ] Works with local Ollama
- [ ] Error messages are helpful
- [ ] No debug code left
- [ ] Git history is clean

**THEN: Safe to push to GitHub!**

---

## Notes

- Keep a log of any issues found
- Document solutions for similar problems
- Collect timing data for performance baseline
- Screenshot successful test runs
- Note any platform-specific behaviors
- Create bug report template for issues found

---

**Ready for comprehensive pre-GitHub testing tomorrow!** 🚀
