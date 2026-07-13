# Trap Analysis Workflow - For Every New Exam

**CRITICAL:** This process MUST be run on EVERY new exam questionnaire.  
**Last Updated:** 2026-07-13  
**Status:** 🔴 REQUIRED FOR EVERY EXAM - NO EXCEPTIONS

---

## PURPOSE

This workflow ensures that EVERY new exam questionnaire is analyzed using the **standardized CISSP trap framework** before student reports are generated.

**Why This Matters:**
- Trap patterns change slightly between exams
- New confusing questions emerge
- Framework improves over time
- Students need specific feedback, not generic labels

---

## TRAP FRAMEWORK TO APPLY (NON-NEGOTIABLE)

### Core Trap Codes (Simplified - Required for Every Exam):

```
🔴 CRITICAL (Always Analyze):
   NEG    - Negative modifiers (NOT, EXCEPT, LEAST, NEVER)
   ROLE   - Job title/perspective mismatch (Manager vs Analyst)
   ORDER  - Process sequence (BCP → BIA first, IR → Contain first)
   ETHIC  - Professional ethics (ISC2 Code of Ethics)
   ALL    - Umbrella effect (Pick broadest strategic answer)

🟡 HIGH (Always Analyze):
   ABS    - Absolute language (Always, Never, All, Completely)
   SCOPE  - Cloud/boundary confusion (Consumer vs Provider, IaaS/PaaS/SaaS)
   GOLD   - Shiny object (Technically correct, wrong question)

🟢 MEDIUM (Refine Sub-Categories):
   CONCEPT - General concept (DEF, PURP, APP, CALC, COMP, FRAME)
```

### Concept Sub-Categories (For "CONCEPT" Questions):

```
DEF    - Pure definition (What is X?)
PURP   - Purpose/use case (When to use X?)
APP    - Scenario application (Apply to situation)
CALC   - Calculation/metrics (Compute value)
COMP   - Comparison (Distinguish X from Y)
FRAME  - Framework/model (Know structure/phases)
```

---

## STEP-BY-STEP WORKFLOW (DO NOT SKIP)

### PHASE 1: EXTRACT & PREPARE

**Input:** New exam PDF file  
**Output:** Structured question data

```bash
# Step 1: Save new PDF to standard location
cp /path/to/new_exam.pdf exams/CISSP_[DATE]/questions/

# Step 2: Extract all questions
python3 scripts/extract_questions.py \
    --input exams/CISSP_[DATE]/questions/exam.pdf \
    --output exams/CISSP_[DATE]/questions/extracted.json
```

**What Gets Extracted:**
- Question number (1-N)
- Full question text
- All 4 options (A/B/C/D)
- Correct answer
- Official explanation

---

### PHASE 2: ASSIGN TRAP CODES (AUTOMATED + MANUAL REVIEW)

**Input:** Extracted questions  
**Output:** Questions with assigned trap codes

```bash
# Step 1: Auto-assign trap codes
python3 cissp_trap_framework.py \
    --input exams/CISSP_[DATE]/questions/extracted.json \
    --output exams/CISSP_[DATE]/questions/trap_assigned.json \
    --framework trap_codes_simplified.json

# Step 2: Manual review for edge cases
# (See manual review checklist below)

# Step 3: Update reference table
python3 scripts/update_reference_table.py \
    --input exams/CISSP_[DATE]/questions/trap_assigned.json \
    --output EXAM_DATE_QUESTIONS_REFERENCE.json
```

**Trap Assignment Process:**

1. **Keyword Detection** (Automated)
   ```
   IF "NOT" OR "EXCEPT" OR "LEAST" → Add NEG
   IF "ALWAYS" OR "NEVER" OR "COMPLETELY" → Add ABS
   IF "MANAGER" OR "OWNER" OR "DIRECTOR" → Add ROLE
   IF "CLOUD" OR "CONSUMER" OR "PROVIDER" → Add SCOPE
   IF "ETHIC" OR "LEGAL" OR "MORAL" → Add ETHIC
   IF "PHASE" OR "FIRST STEP" OR "ORDER" → Add ORDER
   ELSE → Add CONCEPT (requires sub-categorization)
   ```

2. **Explanation Analysis** (Automated)
   ```
   IF explanation contains "definition is" → DEF
   IF explanation contains "purpose" or "used for" → PURP
   IF explanation contains "long scenario" → APP
   IF explanation contains "calculate" or "formula" → CALC
   IF explanation contains "difference" or "distinguish" → COMP
   IF explanation contains "model" or "framework" → FRAME
   ```

3. **Manual Review** (Human Override)
   - Check multi-trap questions (are both traps valid?)
   - Verify CONCEPT sub-categorization
   - Look for "ALL" and "GOLD" patterns not caught by keywords
   - Flag ambiguous questions

---

### PHASE 3: QUALITY ASSURANCE

**Checklist Before Using with Students:**

- [ ] All questions have trap codes assigned
- [ ] Multi-trap questions reviewed and confirmed (≥2 traps)
- [ ] Answer key verified against PDF (no extraction errors)
- [ ] Explanation matches trap code assignment
- [ ] Statistics generated and reviewed

**Key Metrics to Check:**

```
Total questions: Should match PDF count exactly
Trap distribution: Should follow pattern (NEG 10-15%, ABS 3-5%, etc.)
Multi-trap count: Should be 5-10% (flag if 0 or >20%)
CONCEPT %: Should be 70-80% (needs sub-categorization)
```

---

### PHASE 4: GENERATE REFERENCE TABLE (For GitHub & Reports)

**Input:** Validated trap assignments  
**Output:** Production-ready reference files

```bash
# Create all reference files
python3 scripts/generate_reference_tables.py \
    --input exams/CISSP_[DATE]/questions/trap_assigned.json \
    --output-json CISSP_[DATE]_QUESTIONS_REFERENCE.json \
    --output-csv CISSP_[DATE]_QUESTIONS_REFERENCE.csv \
    --output-stats CISSP_[DATE]_TRAP_STATISTICS.json

# Validate output
python3 scripts/validate_reference_tables.py \
    --json CISSP_[DATE]_QUESTIONS_REFERENCE.json \
    --csv CISSP_[DATE]_QUESTIONS_REFERENCE.csv
```

**Files Generated:**

1. **CISSP_[DATE]_QUESTIONS_REFERENCE.json**
   - Used by report generator
   - Query interface for per-question trap data
   - Indexed by question number

2. **CISSP_[DATE]_QUESTIONS_REFERENCE.csv**
   - Commit to GitHub
   - Used for documentation
   - Browseable in Excel

3. **CISSP_[DATE]_TRAP_STATISTICS.json**
   - Analytics data
   - Improvement tracking
   - Dashboard metrics

---

### PHASE 5: INTEGRATE WITH REPORT GENERATION

**Input:** Reference tables + student answers  
**Output:** Student reports with trap feedback

```bash
# Update report generator to use new reference table
python3 regenerate_reports.py \
    --reference-table CISSP_[DATE]_QUESTIONS_REFERENCE.json \
    --student-answers exams/CISSP_[DATE]/student_answers/ \
    --output exams/CISSP_[DATE]/reports/
```

**Report Integration Points:**

1. **Q&A Breakdown Sheet**
   ```
   Add columns:
   - Trap Code (from reference table)
   - Complexity (from reference table)
   - Study Focus (derived from trap code)
   ```

2. **Student Summary**
   ```
   "You struggled with these traps:
    - NEG (3/22 questions) 
    - SCOPE (2/5 questions)
    - CONCEPT/PURP (8/20 questions)"
   ```

3. **Study Recommendations**
   ```
   "Focus Areas (by trap code):
    1. NEG - Drill 22 negative modifier questions
    2. SCOPE - Study cloud responsibility matrix
    3. [Others based on struggles]"
   ```

---

### PHASE 6: COMMIT TO GITHUB (PERMANENT RECORD)

```bash
# Stage reference files
git add CISSP_[DATE]_QUESTIONS_REFERENCE.*

# Commit with detailed message
git commit -m "feat: Add trap analysis for CISSP_[DATE] exam (N questions)

Trap distribution:
- NEG: X questions (Y%)
- ABS: X questions (Y%)
- etc.

Multi-trap questions: X
Complexity: X% HIGH, X% MEDIUM, X% LOW

Reference tables ready for report generation.
Analysis performed using trap_codes_simplified.json framework.

Files:
- CISSP_[DATE]_QUESTIONS_REFERENCE.json (query)
- CISSP_[DATE]_QUESTIONS_REFERENCE.csv (github docs)
- CISSP_[DATE]_TRAP_STATISTICS.json (analytics)
"

# Push to GitHub
git push origin main
```

---

## AUTOMATION SCRIPT (SEMI-AUTOMATIC WORKFLOW)

**File:** `scripts/analyze_new_exam.py`

```python
#!/usr/bin/env python3
"""
One-command analysis of new exam questionnaire
Usage: python3 analyze_new_exam.py --pdf new_exam.pdf --date 2026-08-01
"""

import argparse
import json
from datetime import datetime
from cissp_trap_framework import identify_trap_code

def analyze_exam(pdf_path, exam_date):
    """Complete trap analysis workflow"""
    
    print(f"Starting trap analysis for {exam_date}...")
    
    # Phase 1: Extract
    questions = extract_from_pdf(pdf_path)
    print(f"✓ Extracted {len(questions)} questions")
    
    # Phase 2: Assign traps
    for q_num, q_data in questions.items():
        traps = identify_trap_code(
            q_data['question'],
            q_data['explanation']
        )
        q_data['trap_codes'] = traps
    
    print(f"✓ Assigned trap codes to all questions")
    
    # Phase 3: Validate
    validation = validate_trap_assignments(questions)
    if not validation['passed']:
        print(f"⚠️  Validation warnings:")
        for warning in validation['warnings']:
            print(f"   - {warning}")
    else:
        print(f"✓ Validation passed")
    
    # Phase 4: Generate reference tables
    generate_reference_tables(questions, exam_date)
    print(f"✓ Generated reference tables")
    
    # Phase 5: Print summary
    print_summary(questions)
    
    print(f"\n✅ Analysis complete!")
    print(f"Next step: python3 regenerate_reports.py --date {exam_date}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to new exam PDF")
    parser.add_argument("--date", required=True, help="Exam date (YYYY-MM-DD)")
    args = parser.parse_args()
    
    analyze_exam(args.pdf, args.date)
```

---

## CHECKLIST: BEFORE GENERATING STUDENT REPORTS

**DO NOT generate reports until ALL of these are done:**

- [ ] PDF extracted successfully (N questions found)
- [ ] Trap codes assigned (auto + manual review)
- [ ] Answer key verified (correct answers match PDF)
- [ ] Multi-trap questions reviewed (≥2 traps per question)
- [ ] CONCEPT sub-categories assigned (DEF/PURP/APP/CALC/COMP/FRAME)
- [ ] Reference table generated (JSON + CSV)
- [ ] Reference table validated (correct format, all fields)
- [ ] Reference table committed to GitHub (versioned)
- [ ] Report generator updated to use new reference table
- [ ] Test reports generated (spot check trap feedback)
- [ ] Student reports regenerated (using new trap data)

---

## STORAGE & VERSIONING

### File Naming Convention:

```
CISSP_[DATE]_QUESTIONS_REFERENCE.json
CISSP_[DATE]_QUESTIONS_REFERENCE.csv
CISSP_[DATE]_TRAP_STATISTICS.json

Examples:
- CISSP_2026_07_13_QUESTIONS_REFERENCE.json (July 2026 exam)
- CISSP_2026_08_15_QUESTIONS_REFERENCE.json (August 2026 exam)
- CISSP_2026_12_01_QUESTIONS_REFERENCE.json (December 2026 exam)
```

### Version Control:

```
All reference files committed to GitHub:
/CISSP_[DATE]_QUESTIONS_REFERENCE.*

Allows tracking of:
- How trap patterns change between exams
- Improvement in analysis accuracy
- Evolution of framework
- Comparative analysis (exam 1 vs exam 2)
```

### Archive Location:

```
exams/CISSP_[DATE]/
├── questions/
│   ├── exam.pdf (original)
│   ├── extracted.json (questions)
│   └── trap_assigned.json (with trap codes)
├── student_answers/
│   ├── student1.xlsx
│   ├── student2.xlsx
│   └── ...
└── reports/
    ├── [Student]_Report.xlsx
    └── Class_Report.xlsx
```

---

## ANNUAL FRAMEWORK REVIEW

**Every 12 months, review and update the framework:**

- [ ] Do the 8 core trap codes still apply? (NEG, ROLE, ORDER, SCOPE, ALL, GOLD, ABS, ETHIC)
- [ ] Have new trap patterns emerged?
- [ ] Should CONCEPT sub-categories be refined? (DEF/PURP/APP/CALC/COMP/FRAME)
- [ ] Are multi-trap questions increasing or decreasing?
- [ ] What patterns help students most?
- [ ] Update trap_codes_simplified.json if needed
- [ ] Commit framework updates to GitHub

---

## FAILURE MODES (WHAT GOES WRONG)

| Failure | Impact | Prevention |
|---------|--------|-----------|
| Analysis skipped | Reports lack trap feedback | Checklist is REQUIRED |
| Wrong reference table | Students get outdated trap data | Use date-stamped files |
| CONCEPT not sub-categorized | Feedback stays too vague | Manual review step mandatory |
| Answer key wrong | Trap assignment incorrect | Verify extraction against PDF |
| Reference table not on GitHub | No historical record | Auto-commit in workflow |
| Multi-trap questions missed | High-risk questions unmarked | Manual review pass required |

---

## MAINTENANCE SCHEDULE

| Frequency | Task | Owner |
|-----------|------|-------|
| **Every Exam** | Extract + analyze + reference tables | You |
| **Every Exam** | Commit reference tables to GitHub | You |
| **Quarterly** | Review trap statistics | You |
| **Annually** | Refresh framework + update patterns | You |
| **As Needed** | Fix edge cases or add new traps | You |

---

## SUPPORT & EXAMPLES

### How to Access Historical Analysis:

```bash
# List all exam analyses
ls -la CISSP_*_QUESTIONS_REFERENCE.json

# Compare two exams
diff CISSP_2026_07_13_TRAP_STATISTICS.json \
     CISSP_2026_08_15_TRAP_STATISTICS.json

# Load specific exam in Python
import json
with open('CISSP_2026_07_13_QUESTIONS_REFERENCE.json') as f:
    reference = json.load(f)
    q1_traps = reference['questions']['1']['trap_codes']
```

### How to Debug Failed Analysis:

```bash
# Validate trap assignments
python3 scripts/validate_trap_assignments.py \
    --input exams/CISSP_[DATE]/questions/trap_assigned.json

# Show questions missing trap codes
python3 scripts/find_unassigned_traps.py

# Show multi-trap questions for review
python3 scripts/show_multi_trap_questions.py \
    --input exams/CISSP_[DATE]/questions/trap_assigned.json
```

---

## SIGN-OFF

**This workflow is:**
- ✅ Mandatory for every new exam
- ✅ Non-negotiable (no exceptions)
- ✅ Documented and reproducible
- ✅ Automated where possible
- ✅ Version controlled on GitHub
- ✅ Auditable (every exam has permanent record)

**If this workflow is NOT followed:**
- ❌ Student reports won't have trap feedback
- ❌ Trap patterns won't be tracked over time
- ❌ Framework improvement will stall
- ❌ Historical analysis will be lost

**Status:** 🔴 **CRITICAL - IMPLEMENT IMMEDIATELY**

---

**Last Updated:** 2026-07-13  
**Framework Version:** 2.1  
**Next Review:** 2027-07-13 (Annual)
