# Comprehensive Pre-Deployment Testing Design

**Date:** July 3, 2026  
**Project:** CISSP Analyzer  
**Purpose:** Validate all code, integration, dependencies, and input handling before GitHub deployment  
**Scope:** macOS + Windows, Python 3.9-3.12, 8 functional modes, 15 error scenarios, 10 input format variations  
**Estimated Effort:** 8-10 hours  
**Success Criteria:** All tests pass, zero crashes, both platforms working identically, no missing dependencies  

---

## Section 1: Testing Architecture & Scope

### Overall Structure

A 3-tier testing pyramid with progressively thorough validation:

**Tier 1: Environment & Dependencies** (Foundation)
- Dependency validation (all 46 packages load correctly)
- Python version compatibility (3.9, 3.10, 3.11, 3.12)
- Fresh install on both macOS and Windows
- No conflicts or missing transitive dependencies

**Tier 2: Code Quality Gates** (Quality Assurance)
- Static type checking (mypy)
- Code style validation (black, flake8)
- Import correctness across all modules
- No deprecated library usage

**Tier 3: Functional Testing** (Correctness)
- All 8 standalone analysis modes (single exam, comparative with/without history, etc.)
- Integration across all modules (interactive_cli → main → report generators)
- Error handling for 15+ edge cases (missing files, invalid formats, corrupted data)
- File I/O validation (Excel generation, JSON loading, PDF parsing)

### Test Environments

**macOS:**
- Virtualenv 1: Python 3.9
- Virtualenv 2: Python 3.10
- Virtualenv 3: Python 3.11
- Virtualenv 4: Python 3.12 (current)
- Fresh install test directory

**Windows:**
- Virtualenv 1: Python 3.9
- Virtualenv 2: Python 3.10
- Virtualenv 3: Python 3.11
- Virtualenv 4: Python 3.12
- Fresh install test directory

### Test Data

- Week 1 & Week 2 exam PDFs (existing)
- Answer key JSON files (existing)
- 5 student records with various answer formats
- Synthetic test data for error scenarios

### Success Criteria

- All tests pass on both macOS and Windows
- All Python versions (3.9-3.12) supported
- Zero import errors or missing dependencies
- All 8 standalone modes work without user intervention
- All error scenarios handled gracefully
- No performance regressions
- Input formats validated or auto-detected

---

## Section 2: Environment Setup & Validation

### Fresh Installation Process

For **macOS** and **Windows**, repeat for each Python version (3.9, 3.10, 3.11, 3.12):

```bash
# 1. Create clean virtualenv
python3 -m venv test_env_py39

# 2. Activate
source test_env_py39/bin/activate  # macOS
# OR
test_env_py39\Scripts\activate  # Windows

# 3. Clone repo fresh (simulating student download)
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git test_fresh_install

# 4. Install dependencies
cd test_fresh_install
pip install -r requirements.txt

# 5. Verify imports
python3 -c "import cissp_analyzer; print('✓ Import successful')"
python3 -c "from cissp_analyzer.interactive_cli import main; print('✓ CLI import successful')"

# 6. Test entry points
python3 analyze.py --help
python3 analyze_standalone.py --help

# 7. Run existing test suite
pytest tests/ -v
```

### Validation Checklist Per Environment

- [ ] Create clean virtualenv successfully
- [ ] Activate virtualenv without errors
- [ ] Clone repo without issues
- [ ] `pip install -r requirements.txt` completes without errors
- [ ] All 6 core dependencies installed:
  - openpyxl >= 3.10.0
  - pandas >= 2.0.0
  - pypdf >= 3.16.0
  - pytest >= 7.4.0
  - pytest-cov >= 4.1.0
  - mypy >= 1.5.0
- [ ] Test: `python3 -c "import cissp_analyzer"` → ✓ success
- [ ] Test: `python3 analyze.py --help` → Shows menu, no errors
- [ ] Test: `pytest tests/ -v` → All tests pass

**Expected Outcome:** Zero errors, dependencies resolve cleanly on all Python versions and both platforms.

---

## Section 3: Dependency Validation Testing

### Test Scenarios

1. **Clean Install** — Fresh virtualenv, requirements.txt installs without conflicts
2. **Transitive Dependencies** — All indirect dependencies resolve correctly (pandas → numpy, etc.)
3. **Version Pinning** — No version conflicts between packages
4. **Platform-Specific Builds** — Windows .exe vs macOS .dylib dependencies resolve correctly
5. **Optional Dependencies** — pytest/mypy are optional; project still runs without them
6. **Import Chain Validation** — Every `import` statement in code resolves successfully

### Automated Checks

```bash
# Check for dependency conflicts
pip check

# Validate each core module imports
python3 -c "import openpyxl; print('✓ openpyxl')"
python3 -c "import pandas; print('✓ pandas')"
python3 -c "import pypdf; print('✓ pypdf')"
python3 -c "import pytest; print('✓ pytest')"
python3 -c "import mypy; print('✓ mypy')"

# Validate module chain
python3 -c "import cissp_analyzer"
python3 -c "import cissp_analyzer.interactive_cli"
python3 -c "import cissp_analyzer.main"
python3 -c "import cissp_analyzer.history_loader"

# Ensure pytest can discover tests
pytest --collect-only
```

**Expected Outcome:** No warnings, no conflicts, all imports resolve cleanly.

---

## Section 4: Code Quality Gates

### Static Analysis

#### Type Checking (mypy)
```bash
mypy cissp_analyzer/interactive_cli.py --strict
mypy cissp_analyzer/main.py --strict
mypy analyze.py --strict
mypy analyze_standalone.py --strict
```
**Expected:** Zero type errors in dual-mode implementation code

#### Style Validation (black & flake8)
```bash
black --check cissp_analyzer/ analyze.py analyze_standalone.py
flake8 cissp_analyzer/ analyze.py analyze_standalone.py --max-line-length=100
```
**Expected:** No formatting violations

#### Import Validation
```bash
# Check for circular imports
python3 -c "import cissp_analyzer; cissp_analyzer.interactive_cli"

# Check for unused imports in new code
pylint cissp_analyzer/interactive_cli.py --disable=all --enable=unused-import
```
**Expected:** Clean import graph, no cycles

#### Deprecated Usage Check
```bash
# Search for deprecated pandas API
grep -r "\.append(" cissp_analyzer/ # Deprecated in newer pandas
grep -r "\.ix\[" cissp_analyzer/   # Deprecated indexing
grep -r "inplace=True" cissp_analyzer/ | wc -l  # Count usage

# Check Python version compatibility
python3 -m py_compile cissp_analyzer/*.py analyze.py
```
**Expected:** All code compatible with Python 3.9+

### Quality Checklist

- [ ] mypy passes (zero type errors)
- [ ] black passes (all formatting correct)
- [ ] flake8 passes (no linting violations)
- [ ] No circular imports
- [ ] No deprecated API usage
- [ ] Python 3.9+ compatible syntax only

**Expected Outcome:** Clean code, high quality standards met.

---

## Section 5: Functional Testing Suite (8 Standalone Modes)

### Test Case 1: Single Exam Mode (Ad-hoc)

**Input:**
- Week 1 exam PDF + answer key
- 1 student (TestStudent1)
- No previous exam history

**Steps:**
```
1. python3 analyze.py
2. Choose [2] Standalone Analysis
3. Choose [A] Single Exam
4. Enter exam number: 1
5. Enter PDF path: exams/dec25_week1.pdf
6. Enter answer key: exams/dec25_week1_answer_key.json
7. Add student: TestStudent1
8. Enter answer file: answers/test_batch/teststu1_week1.xlsx
9. Output directory: outputs/test1
10. Run analysis: Yes
```

**Expected Results:**
- [ ] Report file created: `outputs/test1/CISSP_Individual_Report_TestStudent1.xlsx`
- [ ] All 9 sheets present
- [ ] No "Progress Over Time" sheet (single mode)
- [ ] Scores NOT 0% (actual calculations shown)
- [ ] Domain breakdown populated
- [ ] Performance Summary sheet shows data

**Validation:** Open Excel file and verify all sheets contain data

---

### Test Case 2: Comparative Mode (No History)

**Input:**
- Week 1 exam PDF + answer key
- 1 student with NO previous history (TestStudent1)
- Choose comparative mode

**Steps:**
```
1. python3 analyze_standalone.py
2. Choose [B] Compare with Previous Exams
3. Enter exam number: 1
4. Enter PDF path: exams/dec25_week1.pdf
5. Enter answer key: exams/dec25_week1_answer_key.json
6. Add student: TestStudent1
   → System detects: "No previous exam history found"
   → Asks: "Proceed as single exam analysis?"
7. User chooses: Yes
8. Enter answer file: answers/test_batch/teststu1_week1.xlsx
9. Output directory: outputs/test2
10. Run analysis: Yes
```

**Expected Results:**
- [ ] Warning message shown: "No previous exam history found for TestStudent1"
- [ ] Fallback prompt appears: "Proceed as single exam?"
- [ ] Report generated with fallback logic
- [ ] Analysis completes successfully
- [ ] Report file: `outputs/test2/CISSP_Individual_Report_TestStudent1.xlsx`
- [ ] 9 sheets present (no progress sheet)

---

### Test Case 3: Comparative Mode (With History)

**Setup (run once):**
```bash
mkdir -p students/TestStudent2
cat > students/TestStudent2/exam-1_performance.json << 'EOF'
{
  "exam_number": 1,
  "student_name": "TestStudent2",
  "score_percentage": 65.5,
  "correct_count": 82,
  "wrong_count": 43,
  "by_domain": {"Domain1": 0.7, "Domain2": 0.6},
  "by_difficulty": {"easy": 0.8, "medium": 0.65, "hard": 0.5},
  "by_question_type": {"mc": 0.65, "complex": 0.65},
  "by_topic": {"Topic1": 0.7, "Topic2": 0.6},
  "by_exam_trick": {"tricky": 0.6, "normal": 0.67},
  "wrong_question_ids": [1, 2, 3, 5, 8]
}
EOF
```

**Test Steps:**
```
1. python3 analyze_standalone.py
2. Choose [B] Compare with Previous Exams
3. Enter exam number: 2
4. Enter PDF path: exams/dec25_week2.pdf
5. Enter answer key: exams/dec25_week2_answer_key.json
6. Add student: TestStudent2
   → System detects: "Found 1 previous exam(s)"
7. Enter answer file: answers/test_batch/teststu2_week2.xlsx
8. Output directory: outputs/test3
9. Run analysis: Yes
```

**Expected Results:**
- [ ] Success message: "Found 1 previous exam(s)"
- [ ] Comparative analysis executes
- [ ] Report generated with history: `output/TestStudent2/CISSP_Individual_Report_TestStudent2_Exam2.xlsx`
- [ ] 9 sheets present including "Progress Over Time"
- [ ] Progress sheet shows comparison between Exam 1 and Exam 2
- [ ] Trends displayed (improvement/regression)
- [ ] Adaptive recommendations generated

---

### Test Case 4: Multiple History (5+ Exams)

**Setup:** Create mock exam files for TestStudent3 with 4 previous exams

**Test:** Run analysis for 5th exam, verify all 5 exams loaded and trended

**Expected Results:**
- [ ] All 5 exams detected and loaded
- [ ] Trend analysis spans all 5 exams
- [ ] Performance momentum shown
- [ ] Regression detection working
- [ ] Execution completes in < 30 seconds
- [ ] No performance degradation with history

---

### Test Case 5: Master Entry Point (analyze.py)

**Input:** Run via analyze.py (not analyze_standalone.py)

**Steps:**
```
1. python3 analyze.py
   → Shows welcome
2. Choose [2] Standalone Analysis
   → Shows explanation of modes [A] and [B]
3. Proceeds to analyze_standalone.py flow
```

**Expected Results:**
- [ ] analyze.py displays welcome correctly
- [ ] Menu shows 3 options: [1] Batch, [2] Standalone, [3] Full Workflow
- [ ] Choosing [2] shows mode explanation
- [ ] Routes to analyze_standalone.py
- [ ] All standalone functions work correctly

---

### Test Case 6: Answer Key Loading (JSON Priority)

**Input:** Week 1 PDF + answer_key.json

**Test Steps:**
```
1. Verify both files exist:
   - exams/dec25_week1.pdf
   - exams/dec25_week1_answer_key.json
2. Run: python3 analyze.py → [2] → [A]
3. Follow prompts through analysis
```

**Expected Results:**
- [ ] Answer key JSON loads successfully (not PDF extraction)
- [ ] All 125 questions matched
- [ ] Scores calculated correctly (NOT 0%)
- [ ] No PDF extraction attempted (verification via logging/timing)

---

### Test Case 7: Multi-Student Batch

**Input:** 5 students from test data (TestStudent1-5)

**Test Steps:**
```
1. python3 analyze.py → [2] Standalone → [A] Single Exam
2. Add all 5 students:
   - When prompted "Add another student?", choose Yes
   - Repeat for all 5 students
3. Run analysis
```

**Expected Results:**
- [ ] 5 reports generated (one per student)
- [ ] Each report has correct student name
- [ ] No data cross-contamination
- [ ] All scores calculated correctly
- [ ] Batch completes in < 2 minutes

---

### Test Case 8: Mixed Modes (Single + Comparative Sequence)

**Input:** Run analysis twice for same student

**Test Steps:**
```
1. FIRST RUN - Single Mode:
   python3 analyze.py → [2] → [A] Single Exam
   Student: TestStudent4, Week 1
   
2. SECOND RUN - Comparative Mode:
   python3 analyze_standalone.py → [B] Compare with Previous Exams
   Student: TestStudent4, Week 2
   → Should detect: "Found 1 previous exam(s)"
```

**Expected Results:**
- [ ] First run: Single mode, no history detection
- [ ] Second run: Comparative mode, history detected
- [ ] Both reports generated correctly
- [ ] History from first exam used in second report
- [ ] Trends calculated accurately

---

## Section 6: Error Handling & Edge Cases

### 15 Error Scenarios

| Scenario | Input | Expected Behavior | Test |
|----------|-------|-------------------|------|
| 1. Missing PDF file | Path: `exams/nonexistent.pdf` | Error message + re-prompt for path | ✓ |
| 2. Invalid PDF | Binary file with .pdf extension | Error: "Invalid PDF" + fallback option | ✓ |
| 3. Missing answer key JSON | Exam PDF with no .json answer key | Error message + option to continue | ✓ |
| 4. Corrupted answer key | JSON with invalid format | Error: "Corrupted answer key" | ✓ |
| 5. Missing student folder | Student with no history folder | Graceful fallback: "No history found" | ✓ |
| 6. Empty Excel answer file | Excel sheet with no data | Error: "No answers found" + re-prompt | ✓ |
| 7. Wrong column headers | Excel with unexpected column names | Error: "Invalid format" + expected columns | ✓ |
| 8. Duplicate student names | Two students with same name | Warning: "Duplicate detected" + prompt | ✓ |
| 9. Invalid mode choice | User enters "Z" instead of A/B | Error: "Please enter A or B" + re-prompt | ✓ |
| 10. Memory pressure | 50+ exams for one student | Completes without crashing, memory < 1GB | ✓ |
| 11. Concurrent file access | Two analyses running simultaneously | File locking handled gracefully | ✓ |
| 12. Partial upload | Student interrupted mid-analysis | Cleanup old temp files gracefully | ✓ |
| 13. Special characters in name | Student: "José García" | Handles UTF-8 correctly in filenames | ✓ |
| 14. Very long paths | Deeply nested directories | Paths handled correctly on Windows | ✓ |
| 15. Read-only output folder | Output directory with no write permission | Clear error: "Cannot write to output folder" | ✓ |

**Validation Approach:** Test each scenario, verify error message is clear and user can recover.

---

## Section 7: Integration Testing

### Module Interaction Tests

**Integration 1: interactive_cli ↔ main.py**
- User input from interactive_cli flows correctly to analyzer
- Test: Single exam mode input → analyze() method
- Expected: No parameter loss, correct analysis mode executed

**Integration 2: History Loader Integration**
- check_student_history() correctly calls HistoryLoader
- Test: Comparative mode → HistoryLoader.load_previous_exams()
- Expected: History loaded, passed to analyzer, used in report

**Integration 3: Report Generation Pipeline**
- All report generators work with dual-mode system
- Test Single: 9-sheet report generated
- Test Comparative: 9-sheet report + progress sheet
- Expected: All sheets generated, no missing data

**Integration 4: Answer Key Auto-Loading**
- main.py._get_answer_key_file_path() integration
- Test: PDF path "exams/week1.pdf" → "exams/week1_answer_key.json"
- Expected: JSON loaded first, PDF as fallback only

**Integration 5: Cross-Module Data Flow**
- Data consistency across all modules
- Test: Input → interactive_cli → main → analyzers → generators → Excel
- Expected: No data loss, all calculations preserved

**Validation Checklist:**
- [ ] All modules integrate seamlessly
- [ ] Data flows correctly through pipeline
- [ ] No breaking changes to existing functionality
- [ ] History detection works end-to-end
- [ ] Reports generated with correct data

---

## Section 8: Performance Testing

### Benchmarks

| Scenario | Expected Time | Expected Memory | Test |
|----------|---------------|-----------------|------|
| Single exam (1 student, 1 exam) | < 10 seconds | < 200 MB | ✓ |
| Comparative (1 student, 5 exams) | < 20 seconds | < 400 MB | ✓ |
| Batch (5 students, 1 exam each) | < 30 seconds | < 500 MB | ✓ |
| Full workflow (validation + fix + analyze) | < 2 minutes | < 800 MB | ✓ |
| Master entry point startup | < 2 seconds | < 50 MB | ✓ |

### Performance Validation

```bash
# Measure execution time
time python3 analyze.py

# Monitor memory on macOS
top -l 1 | grep Memory

# Monitor memory on Windows
tasklist /v | grep python
```

**Expected Outcome:** All benchmarks met, no performance regressions, consistent timing.

---

## Section 9: Deployment Readiness Checklist

### Pre-GitHub Deployment Validation

```
ENVIRONMENT & DEPENDENCIES (Tier 1)
☐ Fresh install works on macOS (Python 3.9, 3.10, 3.11, 3.12)
☐ Fresh install works on Windows (Python 3.9, 3.10, 3.11, 3.12)
☐ pip install -r requirements.txt completes without errors
☐ pip check shows no conflicts
☐ All imports resolve successfully
☐ No missing dependencies

CODE QUALITY (Tier 2)
☐ mypy --strict passes (zero type errors)
☐ black --check passes (all formatting correct)
☐ flake8 passes (no linting violations)
☐ No circular imports
☐ No deprecated API usage
☐ Python 3.9+ syntax compatibility verified

FUNCTIONAL TESTING (Tier 3)
☐ Test Case 1: Single exam mode ✓
☐ Test Case 2: Comparative (no history) ✓
☐ Test Case 3: Comparative (with history) ✓
☐ Test Case 4: Multiple history (5+ exams) ✓
☐ Test Case 5: Master entry point flow ✓
☐ Test Case 6: Answer key loading ✓
☐ Test Case 7: Multi-student batch ✓
☐ Test Case 8: Mixed modes ✓

ERROR HANDLING
☐ Scenario 1: Missing PDF file ✓
☐ Scenario 2: Invalid PDF ✓
☐ Scenario 3: Missing answer key ✓
☐ Scenario 4: Corrupted answer key ✓
☐ Scenario 5: Missing student folder ✓
☐ Scenario 6: Empty Excel file ✓
☐ Scenario 7: Wrong column headers ✓
☐ Scenario 8: Duplicate student names ✓
☐ Scenario 9: Invalid mode choice ✓
☐ Scenario 10: Memory pressure ✓
☐ Scenario 11: Concurrent file access ✓
☐ Scenario 12: Partial upload ✓
☐ Scenario 13: Special characters ✓
☐ Scenario 14: Very long paths ✓
☐ Scenario 15: Read-only output ✓

INTEGRATION
☐ interactive_cli ↔ main.py works correctly
☐ History loader integrates seamlessly
☐ Report generators produce correct output
☐ Answer key auto-loading works
☐ Data flows correctly through pipeline
☐ No breaking changes to existing code

PERFORMANCE
☐ Single exam: < 10 seconds
☐ Comparative (5 exams): < 20 seconds
☐ Batch (5 students): < 30 seconds
☐ No memory leaks
☐ No performance regressions
☐ Consistent timing across multiple runs

DOCUMENTATION
☐ README updated with installation instructions (both platforms)
☐ Usage examples clear for both Windows and macOS
☐ Error messages documented
☐ Known limitations listed
☐ Troubleshooting guide included

DEPLOYMENT READINESS
☐ All above items checked ✓
☐ No outstanding issues
☐ Manual UAT completed (optional, if time permits)
☐ Ready for GitHub release
```

---

## Section 10: Input Format Validation & Flexibility (Critical)

### 10.1: Excel Answer Sheet Format Testing

**Current Expected Format:**
- Column A: Student Name
- Column B: Question Number  
- Column C: Student Answer
- Rows start at row 2 (row 1 = headers)

**Format Variations to Test:**

| Format | Example | Expected Behavior |
|--------|---------|-------------------|
| Standard | Headers row 1, data row 2+ | ✓ Parses correctly |
| No headers | Data starts immediately | Detect & handle (auto-skip if looks like header) |
| Extra columns | Name, Email, Question, Answer, Notes | Extract only needed, ignore extras |
| Different order | Question, Name, Answer (reordered) | Auto-detect column order by header name |
| Merged cells | Excel header cells merged | Handle gracefully |
| Multiple sheets | Data on different sheet names | Auto-detect correct sheet |
| Case variation | "student name" vs "Student Name" vs "STUDENT NAME" | Case-insensitive matching |
| Extra whitespace | " Student Name " with spaces | Trim whitespace from headers |
| Missing columns | Only has Name & Answer, no Question# | Error: "Missing Question# column" |
| Inconsistent types | Questions: "1", "Q2", "Question3" | Normalize to consistent format |

**Validation Strategy:**
```python
1. Load Excel file
2. Try to identify header row (look for common header names)
3. Auto-detect column mapping:
   - Search for: "Name", "Student", "ID"
   - Search for: "Question", "Q#", "Qnum"
   - Search for: "Answer", "Response", "A#"
4. If auto-detect fails → show error with expected format
5. Normalize data (trim, case-convert)
6. Validate: No duplicates, all questions have answers
7. Parse successfully or fail with clear guidance
```

**Test Cases:**
```
✓ Standard format works
✓ Auto-detect column order in random arrangement
✓ Handle sheets with extra columns
✓ Reject missing required columns with clear error
✓ Handle case-insensitive headers
✓ Strip whitespace from headers
✓ Detect and use correct sheet when multiple exist
```

---

### 10.2: Answer Key JSON Format Testing

**Current Expected Format:**
```json
{
  "1": "A",
  "2": "B,C",
  "3": "1-A,2-B,3-C",
  "4": "A,C,B,D"
}
```

**Format Variations to Test:**

| Format | Example | Expected Behavior |
|--------|---------|-------------------|
| Single letter | `"1": "A"` | ✓ Parses correctly |
| Multiple choice | `"2": "B,C"` | ✓ Multiple answers supported |
| Matching pairs | `"3": "1-A,2-B"` | ✓ Matching format recognized |
| Ordering | `"4": "A,C,B,D"` | ✓ Order sequence recognized |
| With spaces | `"1": " A "` or `"1": "A, B"` | Trim whitespace |
| Case variation | `"1": "a"` vs `"1": "A"` | Normalize to uppercase |
| Question key format | `"Q1"` vs `"Question1"` vs `"1"` | Auto-normalize to numeric |
| Missing questions | Only 1-50, not all 125 | Detect & warn "Missing 51-125" |
| Extra questions | Has 1-130 but exam is 125 | Warn but proceed with first 125 |
| Invalid characters | Contains special chars like `"!@#"` | Reject with error |
| Null/empty values | `"50": null` or `"50": ""` | Flag: "Question 50 missing answer" |
| Number keys | `{1: "A", 2: "B"}` instead of `{"1": "A"}` | Auto-convert to strings |

**Validation Strategy:**
```python
1. Load JSON
2. Validate all keys are numeric (or normalize if strings)
3. Normalize answer formats:
   - Convert lowercase to uppercase
   - Trim whitespace
   - Validate format (single letter, comma-separated, matching pairs)
4. Check completeness: Should have ~125 questions (warn if < 90%)
5. Validate answer values (only A-D, or number pairs, etc.)
6. If validation fails → show error with specific issue
```

**Test Cases:**
```
✓ Standard single-letter format
✓ Auto-normalize lowercase answers
✓ Handle multiple-choice format (comma-separated)
✓ Handle matching pairs format (1-A,2-B)
✓ Handle ordering format (A,C,B,D)
✓ Detect missing questions (< 90%)
✓ Detect extra questions (> expected)
✓ Reject invalid answer characters
✓ Flag empty/null values
✓ Handle string keys vs numeric keys
```

---

### 10.3: PDF Question Format Testing

**Current Expected Formats in PDFs:**

| Format | Example | Expected Behavior |
|--------|---------|-------------------|
| Simple numbering | "1. What is...\nA) ...\nB)..." | ✓ Parses correctly |
| Q-prefix | "Q1: What is...\nA)...\nB)..." | Detect & handle |
| Question-prefix | "Question 1: What is..." | Detect & handle |
| Bullet format | "• Question 1\n• Option A\n• Option B" | Detect & normalize |
| Two-column | Questions left, answers right | Try extract both columns |
| Multiple sections | "QUESTIONS (p1-20)" then "ANSWERS (p21-30)" | Auto-detect sections |
| Scanned PDFs | OCR'd text with errors like "l" vs "1" | Validate consistency |
| Missing questions | PDF has 100, not 125 | Detect & warn |
| Extra formatting | Bold/italic, special symbols | Extract text, ignore formatting |
| Mixed numbering | Some "1.", some "1)", some "Q1" | Normalize all to consistent |

**Validation Strategy:**
```python
1. Extract text from PDF
2. Auto-detect question numbering pattern:
   - Look for "1.", "Q1:", "Question 1", etc.
3. Auto-detect answer section:
   - Look for "Answer Key", "Solutions", "Answers"
   - Or detect by numbering pattern change
4. Extract questions and separate answers
5. Validate: Extracted ~125 questions
6. If format not recognized → show extracted text for manual review
```

**Test Cases:**
```
✓ Standard "1." numbering format
✓ "Q1:" numbering format
✓ "Question 1:" numbering format
✓ Mixed numbering normalization
✓ Two-section detection (questions vs answers)
✓ Handle scanned PDF text
✓ Detect missing questions
✓ Handle special characters/formatting
✓ Extract from multi-column layouts
```

---

### 10.4: Data Consistency Cross-Validation

When inputs are mismatched, program must detect:

| Mismatch | Scenario | Expected Detection |
|----------|----------|-------------------|
| Question count | PDF: 120 questions, Key: 125 | Warn: "Mismatch: PDF=120, Key=125" |
| Question gaps | PDF: 1-50, 52-125 (missing 51) | Detect: "Question 51 missing" |
| Extra answers | Key: 130 answers, PDF: 125 questions | Warn: "Extra answers (126-130) ignored" |
| Format inconsistency | Some "A", others "1-A,2-B" | Warn: "Mixed answer formats" |
| Student vs Key | Key: single letters, Excel: matching pairs | Detect & handle conversion |
| Encoding issues | UTF-8 vs Latin-1 encoding | Auto-detect and convert |

**Validation Strategy:**
```python
1. Compare PDF question count vs Answer Key count
2. Verify no gaps in question numbering
3. Verify Excel answers match PDF question count
4. Check answer format consistency
5. Flag any mismatches to user with specific details
```

---

### 10.5: Input Template Standardization Options

**Two Approaches:**

**Option A: Strict Template** (Current)
- Provide standard Excel template
- Require students to use exact template
- Pros: No ambiguity
- Cons: Less flexible, students struggle

**Option B: Auto-Detect Flexible** (Recommended)
- Accept any Excel format, auto-detect columns
- Accept multiple answer key formats, auto-normalize
- Accept multiple PDF formats, auto-extract
- Pros: Student-friendly, handles real-world data
- Cons: More complex validation

**Recommendation:** Implement **Option B** with clear error messages.

---

### 10.6: Error Messages & User Guidance

When input format errors occur:

```
❌ ERROR: Answer Key Validation Failed

File: exams/week1_answer_key.json
Issue: Question 50 is missing an answer
  Current: "50": null
  Expected: "50": "A" or "50": "B,C" or "50": "1-A,2-B"

Fix & Retry:
  1. Open exams/week1_answer_key.json
  2. Add answer for question 50
  3. Run analysis again

Or:
  - Continue without validation (not recommended)
  - Use PDF to extract answers automatically
```

---

### Section 10 Testing Checklist

```
EXCEL SHEET FORMATTING
☐ Standard format (headers in row 1)
☐ Auto-detect columns in different order
☐ Extra columns (auto-ignore)
☐ No headers (auto-detect)
☐ Case-insensitive headers
☐ Whitespace handling in headers
☐ Multiple sheets (auto-detect correct one)
☐ Merged cells handling
☐ Reject missing required columns (clear error)
☐ Normalize inconsistent data types

ANSWER KEY JSON FORMATTING
☐ Single-letter answers (A, B, C, D)
☐ Multiple-choice answers (B,C)
☐ Matching pairs (1-A,2-B,3-C)
☐ Ordering format (A,C,B,D)
☐ Lowercase answers (auto-normalize)
☐ Whitespace handling
☐ Numeric key format ("1" vs 1)
☐ Detect missing questions (< 90%)
☐ Detect extra questions (> expected)
☐ Reject invalid characters (clear error)
☐ Flag null/empty values

PDF QUESTION EXTRACTION
☐ Simple numbering (1. 2. 3.)
☐ Q-prefix numbering (Q1: Q2:)
☐ Question-prefix (Question 1:)
☐ Bullet format handling
☐ Multi-column layout extraction
☐ Two-section detection (questions + answers)
☐ Scanned PDF handling
☐ Special characters/formatting removal
☐ Detect missing questions
☐ Normalize mixed numbering

DATA CONSISTENCY CROSS-VALIDATION
☐ Question count mismatch detection
☐ Question number gaps detection
☐ Extra answers detection
☐ Answer format consistency check
☐ Student vs key format mismatch detection
☐ Encoding issue detection

ERROR MESSAGES & GUIDANCE
☐ Clear error messages for each format issue
☐ User guidance on how to fix
☐ Option to continue or retry
☐ Examples shown in error messages
☐ No technical jargon in user-facing errors
```

---

## Summary: Complete Testing Design

**Total Effort:** 8-10 hours  
**Platforms:** macOS + Windows  
**Python Versions:** 3.9, 3.10, 3.11, 3.12  
**Test Cases:** 8 functional modes  
**Error Scenarios:** 15 edge cases  
**Input Format Variations:** 40+ format combinations  
**Integration Paths:** 5 critical integration tests  
**Performance Benchmarks:** 5 scenarios  

**Success Criteria:**
- ✓ All tests pass on both platforms
- ✓ All Python versions supported
- ✓ Zero crashes or unhandled exceptions
- ✓ All error scenarios handled gracefully
- ✓ Input formats validated or auto-detected
- ✓ Performance benchmarks met
- ✓ Integration seamless across all modules
- ✓ Production-ready for GitHub deployment

---

**Status:** Design Complete ✅  
**Ready for:** Implementation Plan Creation  
**Next Step:** Invoke writing-plans skill to create detailed task breakdown
