# Adaptive Recommendations Feature - Complete Design Specification

**Date:** June 28, 2026  
**Status:** Design Approved  
**Scope:** Historical exam tracking + momentum-based recommendations for CISSP Analyzer

---

## Executive Summary

This feature transforms the CISSP Analyzer from single-exam analysis to **multi-exam tracking with adaptive recommendations**. Students can track progress across up to 10 exams, while teachers see class-wide analytics. The system uses a momentum-based algorithm to generate personalized study plans based on weakness + improvement trajectory.

**Key Design Decisions:**
- **Storage:** Local file-based (filename nomenclature: Mock1_Jun26_Sri.xlsx)
- **Scale:** Max 5-10 exams per student
- **Output:** 8-sheet individual reports + 3-sheet class reports
- **Trend Dimensions:** Domain accuracy + Difficulty progression + Question Type mastery
- **Recommendation Algorithm:** Momentum-based (weakness + improvement trajectory)

---

## Architecture Overview

### Data Storage

**Organization:**
```
cissp-analyzer/
├── students/
│   ├── Sri/
│   │   ├── Mock1_Jun26_Sri.xlsx (input)
│   │   ├── exam-1_performance.json (calculated)
│   │   ├── Mock2_Jun28_Sri.xlsx
│   │   ├── exam-2_performance.json
│   │   └── ... (max 10 exams)
│   └── Sam/
│       └── ... (same structure)
├── reports/
│   ├── Sri_progress_report.xlsx (8 sheets)
│   └── Sam_progress_report.xlsx
└── class_reports/
    ├── class_overview.xlsx
    ├── class_weakness_analysis.xlsx
    └── class_student_comparisons.xlsx
```

**Student Name Identification:**
1. Tool prompts on first run: "Enter student name?"
2. User types name (e.g., "Sri")
3. Tool creates `students/Sri/` folder
4. On subsequent runs, tool extracts student name from filename:
   - Pattern: `Mock[N]_[Date]_[StudentName].xlsx`
   - Example: `Mock1_Jun26_Sri.xlsx` → Extract "Sri"
   - Fallback: Case-insensitive + fuzzy matching with prompt confirmation

**Max Exam Limit:** 10 exams per student. Tool warns when limit is reached; users can archive older exams.

---

### Data Schema

**File: `exam-N_performance.json`**

Minimal schema storing only what's needed for trend calculations:

```json
{
  "exam_number": 2,
  "date": "2026-06-28",
  "student_name": "Sri",
  "total_questions": 125,
  "total_correct": 85,
  "overall_accuracy": 0.68,
  
  "by_domain": {
    "Security & Risk Management": {
      "correct": 12,
      "total": 16,
      "accuracy": 0.75
    },
    "Asset Security": {
      "correct": 10,
      "total": 14,
      "accuracy": 0.71
    }
    // ... 8 domains total
  },
  
  "by_difficulty": {
    "Easy": {"correct": 30, "total": 40, "accuracy": 0.75},
    "Medium": {"correct": 35, "total": 50, "accuracy": 0.70},
    "Hard": {"correct": 20, "total": 35, "accuracy": 0.57}
  },
  
  "by_question_type": {
    "Application": {"correct": 28, "total": 40, "accuracy": 0.70},
    "Scenario": {"correct": 30, "total": 50, "accuracy": 0.60},
    "Knowledge": {"correct": 27, "total": 35, "accuracy": 0.77}
  },
  
  "wrong_question_ids": [3, 7, 12, 25, ...]
}
```

---

## Report Structure

### Individual Student Report (8 Sheets)

**Sheets 1-6:** Existing (unchanged)
1. Summary
2. Q&A Breakdown
3. By Difficulty
4. By Type
5. By Trick
6. By Domain

**Sheet 7: Progress Over Time** *(NEW)*
Displays historical trends across all exams. Three visualizations:

- **A. Domain Accuracy Over Time:** Line chart, one line per domain
  - Example: Security Arch: 65% → 72% → 75%
  - Shows: All 8 CISSP domains with trend indicators

- **B. Difficulty Progression:** Grouped bar chart
  - Example: Easy 75% → 78% → 80% | Medium 65% → 68% → 70% | Hard 40% → 45% → 50%
  - Shows: Three difficulty levels across all exams

- **C. Question Type Mastery:** Line chart, one line per type
  - Example: Application 70% → 72% → 74% | Scenario 50% → 55% → 60%
  - Shows: All question types with trend indicators

**Drill-Down Capability:**
- Students click on a domain → Opens hidden subtopic-level sheet
- Shows: Kerberos, SAML, OAuth accuracies per exam with trend arrows
- Identifies: Which subtopics are improving vs stagnant

**Sheet 8: Adaptive Study Plan** *(NEW)*
Personalized, actionable study recommendations based on momentum algorithm.

Structure:
```
Priority 1: [Domain Name]
  Current: X% | Previous: Y% ([+/-]% momentum) | Study Need: High
  Focus areas:
    • Subtopic 1 (detail)
    • Subtopic 2 (detail with pattern)
    • Trick pattern: "You struggle with NOT keyword"
    • Wrong questions: [IDs linked to Q&A sheet]

Priority 2: [Domain Name]
  [Same structure]

For reference: Strengths to maintain
  [High-accuracy domains to avoid regression]
```

Each priority includes drill-down sections:
- Subtopic-level breakdown
- By difficulty (focus Medium/Hard first)
- By question type (identify weak patterns)
- Pattern analysis (generated insights)
- Wrong question IDs (hyperlinked to Sheet 2)

---

### Teacher Class Reports

Generated when analyzing a folder with multiple students.

**Sheet 1: Class Overview**
- Table with all students' latest exam scores
- Columns: Student Name | Exam 1 | Exam 2 | Exam 3 | Latest % | Ranking | Trend
- Shows: Class average, top/bottom performers, class momentum

**Sheet 2: Weakness Analysis**
- Aggregated by domain: Which topics are hardest for the class
- Format: Domain | Class Avg % | Range (Min-Max) | Recommendation
- Example: "Domain 3 avg 55% (40-70%) → recommend re-teach"

**Sheet 3: Student Comparisons**
- Side-by-side comparison of 2-3 struggling students vs class average
- Identifies: Specific domains where intervention is needed
- Shows: "Sam 40% vs Class 65%" highlighting gaps

---

## Momentum-Based Recommendation Algorithm

### Step 1: Calculate Priority Score Per Domain

```
For each domain:
  current_accuracy = exam-N accuracy percentage
  previous_accuracy = exam-(N-1) accuracy percentage (if exists)
  
  momentum = (current - previous) if history exists, else 0
  weakness = 100 - current
  priority_score = weakness + (momentum × 2)

Sort domains by priority_score descending
Recommend top 2-3 domains for focused study
```

### Step 2: Worked Example

| Domain | Exam 2 | Exam 3 | Weakness | Momentum | Priority | Rank |
|--------|--------|--------|----------|----------|----------|------|
| Identity & Access | 45% | 50% | 50 | +5 | **60** | 🥇 #1 |
| Soft Dev Security | 55% | 58% | 42 | +3 | **48** | 🥈 #2 |
| Security Arch | 72% | 75% | 25 | +3 | 31 | #5 |
| Cryptography | 80% | 78% | 22 | -2 | 18 | #8 |

**Key insight:** Cryptography declined but ranks #8 (low weakness). Identity & Access ranks #1 (high weakness + positive momentum).

### Step 3: Generate Drill-Down Recommendations

For top 2-3 domains, drill down to subtopics:
- Analyze accuracy by subtopic (Kerberos vs SAML vs OAuth)
- Detect patterns:
  - All wrong vs mixed accuracy
  - Accuracy by question type (Scenario vs Application)
  - Accuracy by exam trick (NOT, BEST, MOST keywords)
- Generate insights: "You struggle with OAuth in scenario context"

### Step 4: First-Time Students (No History)

**Fallback:** Use pure weakness ranking (momentum = 0)
- Message: "This is your starting point. Focus on weakest domains first."
- Same sheet structure, simpler recommendations
- After 2nd exam, momentum calculation kicks in

---

## System Workflow

### CLI Entry Points

**Mode 1: Analyze Single Student**
```bash
python run.py --mode analyze-student
→ Prompt: "Enter student name?" → User types "Sri"
→ Scan: students/Sri/ folder for existing exams
→ Load: exam-1_performance.json, exam-2_performance.json (if exist)
→ Parse: Mock3_Jul1_Sri.xlsx (current exam)
→ Calculate: 5-dimensional performance + momentum
→ Generate: Sri_progress_report.xlsx (8 sheets)
→ Store: exam-3_performance.json
```

**Mode 2: Analyze Class**
```bash
python run.py --mode analyze-class
→ Scan: students/ folder for all student subfolders
→ For each student: Calculate latest scores
→ Generate: class_reports/ with 3 sheets
→ Aggregate: Class-wide analytics
```

### Data Flow (Single Student Analysis)

```
Input File
  ├─ Mock3_Jul1_Sri.xlsx (125 questions, student answers)
  └─ Filename parsing: Extract "Sri" + "Jul1"

Parse Current Exam
  ├─ Extract: 125 questions, correct/wrong
  └─ Calculate: 5D performance (domain/topic/difficulty/type/trick)

Load Historical Data
  ├─ Read: students/Sri/exam-1_performance.json
  ├─ Read: students/Sri/exam-2_performance.json
  └─ In-memory cache for this run

Calculate Trends
  ├─ Compare: Exam 3 vs Exam 2 vs Exam 1 per dimension
  ├─ Calculate: Domain momentum scores
  ├─ Identify: Regressions, improvements, stagnation
  └─ Drill-down: Subtopic-level trends

Generate Recommendations
  ├─ Apply momentum algorithm
  ├─ Detect: Patterns (trick keywords, question types)
  └─ Rank: Top 2-3 domains to focus on

Generate Reports
  ├─ Sheet 1-6: Current exam detail (unchanged)
  ├─ Sheet 7: Progress Over Time (3 visualizations + drill-down)
  ├─ Sheet 8: Adaptive Study Plan (momentum-based)
  └─ Store: exam-3_performance.json for next run

Output
  └─ Sri_progress_report.xlsx (8 sheets)
```

---

## Error Handling & Edge Cases

| Scenario | Handling |
|----------|----------|
| **Malformed filename** (doesn't match Mock[N]_[Date]_[Name].xlsx) | Fallback to interactive prompt: "Student name?" |
| **Name case mismatch** (john vs John vs jon) | Case-insensitive folder lookup; prompt if ambiguous |
| **10+ exams already exist** | Tool warns: "Student has 10 exams (max limit). Archive older ones? (y/n)" |
| **First exam only (no history)** | Show single-exam data; Progress sheet: "Historical trends appear after 2nd exam" |
| **Negative momentum (regression)** | Visible in trend lines; Study Plan flags: "⚠️ Regression in [Domain]" |
| **Duplicate exam date** | Tool prompts: "Exam already exists for this date. Overwrite? (y/n)" |
| **Missing exam file** | Skip; load remaining exams. Show: "Found 2 of 3 expected exams" |

---

## Integration with Current System

### No Changes to Existing Sheets
Sheets 1-6 (Summary, Q&A, Difficulty, Type, Trick, Domain) remain **exactly the same**. They show single-exam data only.

### New Sheets Add, Don't Modify
- Sheet 7 (Progress Over Time): Pure addition, no interaction with existing logic
- Sheet 8 (Adaptive Study Plan): Pure addition, generated from momentum algorithm

### Backward Compatibility
- Reports for students with only 1 exam: Sheets 1-6 generate normally; Sheets 7-8 show "Only 1 exam so far"
- Existing students can add new exams: Tool automatically loads history and compares

### File Organization
- Existing: `exam-1_analysis.xlsx` (full report)
- New: `exam-1_performance.json` (performance data only, cached for next run)
- Both coexist; no migration needed

---

## Testing & Validation Strategy

### Unit Tests
1. **Data Schema:** Verify exam-N_performance.json structure
2. **Momentum Algorithm:** Test with known data (verify priority scoring)
3. **Trend Calculations:** Validate domain/difficulty/type trends
4. **Pattern Detection:** Verify subtopic drill-down accuracy
5. **Name Extraction:** Test filename parsing (patterns, edge cases)

### Integration Tests
1. **Multi-exam workflow:** Parse 3 exams, verify trends calculated correctly
2. **Historical loading:** Load exam-1 + exam-2, then parse exam-3, verify comparison
3. **Class analysis:** Multiple students, verify aggregations
4. **Error scenarios:** Malformed files, missing exams, name mismatches

### Edge Cases
- New student (1 exam) → verify fallback to weakness ranking
- Student regression (lower score) → verify algorithm still works
- Max 10 exams → verify limit enforcement
- Case mismatch (john vs John) → verify case-insensitive handling

### Success Criteria
✓ All trend visualizations generate without errors  
✓ Momentum algorithm produces logically correct rankings  
✓ Study Plan recommendations are actionable and specific  
✓ Teacher class reports aggregate correctly  
✓ File naming conventions work for >95% of filenames  
✓ Backward compatible (doesn't break existing 7-sheet reports)  

---

## Implementation Roadmap

**Phase 1: Core Infrastructure**
- Add exam-N_performance.json schema
- Implement historical data loading (multi-exam support)
- Update CLI: add --mode analyze-student / analyze-class

**Phase 2: Trend Calculations**
- Calculate trends for all 3 dimensions (domain, difficulty, type)
- Implement drill-down (subtopic-level data)
- Add Progress Over Time visualization framework

**Phase 3: Recommendation Engine**
- Implement momentum algorithm
- Build pattern detection (subtopic analysis, trick keywords)
- Generate Study Plan sheet with detailed recommendations

**Phase 4: Teacher Reports**
- Implement class-level aggregations
- Generate class_reports/ sheets
- Add class analytics and weakness analysis

**Phase 5: Polish & Testing**
- Comprehensive test suite
- Error handling for edge cases
- Documentation and user guide

---

## Assumptions & Constraints

**Assumptions:**
- Students follow filename nomenclature: Mock[N]_[Date]_[StudentName].xlsx
- Question metadata is stable (125 questions, same IDs across exams)
- Student names are reasonably unique (no "John" vs "John Smith" confusion)
- Exams are taken in order (exam-1, then exam-2, then exam-3)

**Constraints:**
- Max 10 exams per student (hard limit for local file management)
- Filename parsing relies on consistent naming (fallback to prompt if needed)
- Momentum calculation requires at least 2 exams (first-time students fall back to weakness ranking)
- Local file storage only (no cloud, no database)

---

## Questions for User Review

1. ✅ Data storage (local file-based) — Approved
2. ✅ Report structure (8 sheets for student, 3 for class) — Approved
3. ✅ Trend dimensions (A+B+C) — Approved
4. ✅ Recommendation algorithm (momentum-based) — Approved
5. ✅ Integration approach (2 new sheets, no changes to existing) — Approved

---

**Design Status:** Ready for Implementation Planning
