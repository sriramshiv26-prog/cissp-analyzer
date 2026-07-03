# Standalone Analysis Testing Guide
## Single Exam vs. Comparative Mode

**Date:** July 4, 2026  
**Purpose:** Validate dual-mode standalone analysis before GitHub deployment  
**Time Required:** 45-60 minutes

---

## Pre-Test Setup

### 1. Verify Test Environment
```bash
cd /Users/sriram/cissp-analyzer

# Check git status
git status

# Verify recent commit
git log --oneline -5

# Check Python environment
python3 --version
pip list | grep pandas openpyxl pypdf
```

### 2. Prepare Test Data

#### Test Data Set 1: New Student (No History)
```
Student Name: TestStudent1
History: None (first-time test)
Exam PDF: exams/dec25_week1.pdf
Answer Key: exams/dec25_week1_answer_key.json
Answer File: answers/dec25_batch/teststu1_week1.xlsx
```

#### Test Data Set 2: Existing Student (With History)
```bash
# Create fake history for TestStudent2
mkdir -p students/TestStudent2

# Create a fake previous exam performance file
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

# Verify history file created
ls -la students/TestStudent2/exam-1_performance.json
```

---

## Test Case 1: Single Exam Mode (Ad-hoc)

### Test 1.1: Basic Single Exam Analysis
```bash
# Run the main entry point
python3 analyze.py

# User Input:
# Choose: 2 (Standalone Analysis)
#   Sees explanation of modes [A] and [B]
# Choose: A (Single Exam)
# Enter exam number: 1
# Enter PDF path: exams/dec25_week1.pdf
# Enter answer key: exams/dec25_week1_answer_key.json
# Add student: TestStudent1
# Enter answer file: answers/dec25_batch/teststu1_week1.xlsx
# Done adding students: (press Enter)
# Output directory: outputs/test1
# Run analysis: Yes

# EXPECTED RESULTS:
# ✓ Mode displays: "Single Exam"
# ✓ Single report generated
# ✓ Report saved to: outputs/test1/
# ✓ No progress sheet (no history)
# ✓ Scores calculated correctly
```

### Verification Checklist 1.1
```bash
# Check if report was generated
ls -la outputs/test1/CISSP_Individual_Report_TestStudent1.xlsx

# Open Excel and verify:
# [ ] 9 sheets present
# [ ] Performance Summary sheet exists
# [ ] No "Progress Over Time" sheet (or empty)
# [ ] Scores populated (not 0%)
# [ ] Domain breakdown shown
```

---

## Test Case 2: Comparative Mode (No History)

### Test 2.1: New Student with Comparative Mode
```bash
# Run standalone analysis
python3 analyze_standalone.py

# User Input:
# Choose: B (Compare with Previous Exams)
# Enter exam number: 2
# Enter PDF path: exams/dec25_week2.pdf
# Enter answer key: exams/dec25_week2_answer_key.json
# Add student: TestStudent1 (new student, no history)
#   System detects: "No previous exam history found"
#   Asks: "Proceed as single exam analysis?"
#   User chooses: Yes
# Enter answer file: answers/dec25_batch/teststu1_week2.xlsx
# Done adding students: (press Enter)
# Output directory: outputs/test2a
# Run analysis: Yes

# EXPECTED RESULTS:
# ✓ System detects no history
# ✓ Warning message shown
# ✓ Falls back to single exam mode
# ✓ Single report generated
# ✓ Analysis completes successfully
```

### Verification Checklist 2.1
```bash
# Check if report was generated
ls -la outputs/test2a/CISSP_Individual_Report_TestStudent1.xlsx

# Verify fallback behavior:
# [ ] Report generated (fallback worked)
# [ ] 9 sheets present
# [ ] Scores populated
# [ ] No historical comparison (expected)
```

---

## Test Case 3: Comparative Mode (With History)

### Test 3.1: Existing Student with History
```bash
# Run standalone analysis
python3 analyze_standalone.py

# User Input:
# Choose: B (Compare with Previous Exams)
# Enter exam number: 2
# Enter PDF path: exams/dec25_week2.pdf
# Enter answer key: exams/dec25_week2_answer_key.json
# Add student: TestStudent2 (has history)
#   System detects: "Found 1 previous exam(s)"
#   Shows success message
# Enter answer file: answers/dec25_batch/teststu2_week2.xlsx
# Done adding students: (press Enter)
# Output directory: outputs/test3a
# Run analysis: Yes

# EXPECTED RESULTS:
# ✓ System detects history
# ✓ Success message shown: "Found 1 previous exam(s)"
# ✓ analyze_student_with_history() called
# ✓ Report with historical context generated
# ✓ Report saved to: output/TestStudent2/
```

### Verification Checklist 3.1
```bash
# Check if report was generated
ls -la output/TestStudent2/CISSP_Individual_Report_TestStudent2_Exam2.xlsx

# Verify historical comparison:
# [ ] Report generated
# [ ] 9 sheets present
# [ ] "Progress Over Time" sheet exists
# [ ] Shows comparison: Exam 1 vs Exam 2
# [ ] Trends displayed (improvement/regression)
# [ ] Adaptive recommendations shown
# [ ] Performance data saved to: students/TestStudent2/exam-2_performance.json
```

---

## Test Case 4: Master Entry Point Flow

### Test 4.1: Full Flow via analyze.py
```bash
# Run master entry point
python3 analyze.py

# STEP 1: Choose mode
# User chooses: 2 (Standalone Analysis)
#   Expected: Explanation of modes [A] and [B]

# STEP 2: Choose analysis type (NEW!)
# User chooses: B (Compare with Previous Exams)
#   Expected: "What type of analysis do you want?" menu

# STEP 3: Continue with analysis
# Enter exam number: 1
# Enter PDF path: exams/dec25_week1.pdf
# Enter answer key: (optional)
# Add student: TestStudent2 (has history)
#   Expected: "Found 1 previous exam(s)"
# Enter answer file: answers/dec25_batch/teststu2_week1.xlsx
# Done adding students: (press Enter)
# Output directory: outputs/test4
# Run analysis: Yes

# EXPECTED RESULTS:
# ✓ Master entry point routing works
# ✓ Mode selection menu appears
# ✓ Analysis type passed through
# ✓ Comparative analysis executes
# ✓ Report generated with history
```

### Verification Checklist 4.1
```bash
# Verify master entry point flow:
# [ ] python3 analyze.py shows welcome
# [ ] Choose [2] shows standalone explanation
# [ ] Analysis type menu appears
# [ ] Correct mode selected and passed through
# [ ] Reports generated correctly
```

---

## Test Case 5: Error Handling

### Test 5.1: Invalid Inputs
```bash
python3 analyze.py
# Choose: 2
# Choose: Z (invalid)
#   Expected: Error message "Please enter A or B"
#   System re-asks: "Choose [A/B]:"

# Choose: A (valid)
# Continue...
#   Expected: Proceeds normally
```

### Verification Checklist 5.1
```bash
# [ ] Invalid analysis type caught
# [ ] Clear error message shown
# [ ] Re-prompts user
# [ ] Accepts valid input on retry
```

### Test 5.2: Missing Files
```bash
python3 analyze.py
# Choose: 2
# Choose: B
# Enter exam number: 1
# Enter PDF path: exams/nonexistent.pdf
#   Expected: Error "File not found"
#   System re-asks for path

# Enter correct path: exams/dec25_week1.pdf
#   Expected: "PDF found"
```

### Verification Checklist 5.2
```bash
# [ ] Missing PDF detected
# [ ] Clear error message shown
# [ ] Re-prompts for valid path
# [ ] Accepts correct path on retry
```

---

## Test Case 6: Integration Test (All Modules)

### Test 6.1: Complete Workflow Single → Comparative
```bash
# Step 1: Analyze new student in single mode
python3 analyze.py
# Choose: 2 → A → ... → outputs/test_single/

# Step 2: Get student history from first exam
# Move report to history folder
mkdir -p students/IntegrationTest
cp output/IntegrationTest/exam-1_performance.json students/IntegrationTest/

# Step 3: Analyze same student in comparative mode
python3 analyze_standalone.py
# Choose: B → ... → IntegrationTest exists → "Found 1 previous exam(s)"

# EXPECTED RESULTS:
# ✓ Step 1: Single report generated
# ✓ Step 2: History saved correctly
# ✓ Step 3: History detected and loaded
# ✓ Comparative report includes trends
```

### Verification Checklist 6.1
```bash
# [ ] Single exam report generated (Step 1)
# [ ] Performance data saved (Step 2)
# [ ] History detected (Step 3)
# [ ] Comparative report generated
# [ ] Trends shown correctly
# [ ] All modules integrated
```

---

## Test Case 7: Data Consistency

### Test 7.1: Answer Key Loading
```bash
# Verify answer keys load correctly
python3 -c "
from cissp_analyzer.data_quality_validator import AnswerSheetAutoFixer
import json

# Load answer key manually
with open('exams/dec25_week1_answer_key.json') as f:
    key = json.load(f)
    
print(f'Answer key loaded: {len(key)} answers')
print('Sample answers:')
for i in [1, 11, 43, 109, 118, 125]:
    if str(i) in key:
        print(f'  Q{i}: {key[str(i)]}')
"

# EXPECTED OUTPUT:
# Answer key loaded: 125 answers
# Sample answers should show all formats
```

### Verification Checklist 7.1
```bash
# [ ] Answer key JSON loads correctly
# [ ] All 125 questions present
# [ ] Complex answers format correctly
# [ ] Single answers (A/B/C/D) present
# [ ] Matching answers format: 1-A,2-B,...
# [ ] Ordering answers format: A,C,B,D
```

---

## Performance Testing

### Test 8.1: Execution Time
```bash
# Time single exam analysis
time python3 analyze_standalone.py << 'EOF'
A
1
exams/dec25_week1.pdf
exams/dec25_week1_answer_key.json
TestStudent1
answers/dec25_batch/teststu1_week1.xlsx

outputs/perf_test

yes
EOF

# Expected: < 30 seconds for single exam
# [ ] Analysis completes within acceptable time
# [ ] No hangs or delays
# [ ] Reports generated quickly
```

### Test 8.2: Memory Usage
```bash
# Monitor memory during analysis
/usr/bin/time -v python3 analyze_standalone.py << 'EOF'
A
1
exams/dec25_week1.pdf
exams/dec25_week1_answer_key.json
TestStudent1
answers/dec25_batch/teststu1_week1.xlsx

outputs/memory_test

yes
EOF

# Expected: < 500MB memory usage
# [ ] Reasonable memory footprint
# [ ] No memory leaks detected
```

---

## Final Verification Checklist

### Code Quality
- [ ] No syntax errors in interactive_cli.py
- [ ] No syntax errors in analyze.py
- [ ] No syntax errors in analyze_standalone.py
- [ ] No console errors or warnings (except deprecation warnings)
- [ ] Clean console output

### Functional Requirements
- [ ] Single exam mode works without history
- [ ] Comparative mode detected history
- [ ] Fallback to single mode when no history
- [ ] Master entry point routes correctly
- [ ] All 4 test cases pass
- [ ] Error handling works

### Integration
- [ ] interactive_cli.py integrates with main.py
- [ ] HistoryLoader integrates seamlessly
- [ ] analyze_student_with_history() used correctly
- [ ] No breaking changes to existing code
- [ ] All dependent modules work together

### Documentation
- [ ] Updated help text in analyze.py
- [ ] Updated docstrings in analyze_standalone.py
- [ ] STANDALONE_ENHANCEMENT_PLAN.md complete
- [ ] Test results documented

---

## Test Execution Summary

### Test Results Template
```
TEST CASE 1 - Single Exam Mode
  Sub-test 1.1: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 2 - Comparative (No History)
  Sub-test 2.1: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 3 - Comparative (With History)
  Sub-test 3.1: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 4 - Master Entry Point
  Sub-test 4.1: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 5 - Error Handling
  Sub-test 5.1: ✓ PASS / ✗ FAIL
  Sub-test 5.2: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 6 - Integration
  Sub-test 6.1: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 7 - Data Consistency
  Sub-test 7.1: ✓ PASS / ✗ FAIL
  Notes: _____________________

TEST CASE 8 - Performance
  Sub-test 8.1: ✓ PASS / ✗ FAIL
  Sub-test 8.2: ✓ PASS / ✗ FAIL
  Notes: _____________________

OVERALL: ✓ READY FOR GITHUB / ✗ NEEDS FIXES
```

---

## If Tests Fail

### Debugging Steps
1. Check error message in console
2. Verify test data files exist
3. Check git diff for recent changes
4. Review STANDALONE_ENHANCEMENT_PLAN.md
5. Check interactive_cli.py for syntax errors
6. Run affected test case in isolation
7. Document error and fix

### Common Issues
- **HistoryLoader not found**: Verify import in interactive_cli.py
- **Scores showing 0%**: Check answer key format
- **Report not generated**: Check output directory path
- **Mode not passed through**: Verify function signatures updated
- **No history detected**: Verify students directory structure

---

## Success Criteria

✅ **All 8 Test Cases Pass**
✅ **No Breaking Changes**
✅ **Error Handling Works**
✅ **Integration Complete**
✅ **Documentation Updated**
✅ **Ready for GitHub Deployment**

---

## Next Steps (After Testing)

1. If all tests pass:
   - Commit test results
   - Push to GitHub
   - Create release

2. If tests fail:
   - Fix issues
   - Re-run affected tests
   - Verify fixes
   - Then proceed to GitHub

---

**Testing Date:** July 4, 2026  
**Estimated Duration:** 45-60 minutes  
**Tester:** [You]  
**Status:** Ready for testing
