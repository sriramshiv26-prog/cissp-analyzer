# Standalone Analysis Enhancement Plan
## Single Exam vs. Comparative Analysis with History

**Date:** July 4, 2026  
**Scope:** Add history detection and comparative analysis to standalone mode  
**Impact Level:** Medium (affects interactive_cli.py, analyze.py, analyze_standalone.py)

---

## Problem Statement

Currently, standalone analysis only supports:
- Single exam, single student, no history

Missing capability:
- Comparative analysis (current exam vs. previous exams)
- Trend detection (improvement/regression)
- Historical context in recommendations

**User Question:** "How will it know if it's ad-hoc vs. comparative?"

**Solution:** Add interactive choice at startup

---

## Current Architecture Analysis

### Current Flow
```
analyze.py [2] Standalone
    ↓
analyze_standalone.py
    ↓
interactive_cli.main()
    ├─ Asks exam number
    ├─ Asks exam PDF
    ├─ Asks answer key
    ├─ Asks students
    └─ Calls analyzer.analyze() (single exam only)
```

### Available Methods
- `CISSPAnalyzer.analyze()` - Single exam, no history
- `CISSPAnalyzer.analyze_student_with_history()` - Single exam with historical context
- `HistoryLoader.load_previous_exams()` - Loads student history

### Current Data Flow (analyze_student_with_history)
```
1. Load history via HistoryLoader
2. Get previous exam count
3. Extract PDF questions
4. Load answer key
5. Parse student answers
6. Evaluate student
7. Save performance data
8. Generate report WITH historical trends
```

---

## Proposed Enhancement

### New User Flow
```
python3 analyze.py
[2] Standalone Analysis
    ↓
    "How do you want to analyze?"
    
    [A] Single Exam (Ad-hoc)
        └─ No history check
        └─ Single report
    
    [B] Compare with Previous Exams (Trending)
        └─ Load student history
        └─ Show trends/progress
        └─ Adaptive recommendations
```

### Implementation Strategy

#### Phase 1: Detection & Routing
**File:** `interactive_cli.py`

1. Add function: `ask_analysis_type()` → returns "single" or "comparative"
2. After getting student name:
   - If "comparative": Check if history exists
   - If no history: Warn user, ask to proceed as single
   - If history exists: Proceed with historical analysis
3. Route to appropriate analyzer method based on choice

#### Phase 2: Analysis Logic
**File:** `interactive_cli.py` - run_analysis()

1. If `"single"` mode:
   - Call `analyzer.analyze()` (current behavior)
   
2. If `"comparative"` mode:
   - Call `analyzer.analyze_student_with_history()` instead
   - Auto-loads previous exams
   - Generates report with trends

#### Phase 3: User Interface Updates
**Files:** `analyze.py`, `analyze_standalone.py`

1. Update help text in analyze.py
2. Update docstrings in analyze_standalone.py
3. Add clarification in interactive prompts

#### Phase 4: Data Integration
**Files:** `history_loader.py`, `main.py`

- No changes needed (already supports both methods)
- history_loader already handles missing histories
- analyzer.analyze_student_with_history() already exists

---

## Detailed Implementation

### 1. Update `interactive_cli.py`

#### New Function: `ask_analysis_type()`
```python
def ask_analysis_type() -> str:
    """Ask user if they want single exam or comparative analysis.
    
    Returns:
        "single" - Single exam (ad-hoc)
        "comparative" - With history/trending
    """
    print("\n" + Colors.header("-" * 70))
    print(Colors.header("ANALYSIS TYPE"))
    print(Colors.header("-" * 70))
    print("\nWhat type of analysis do you want?\n")
    print("  [A] Single Exam (Ad-hoc / One-time)")
    print("       • Analyze just this exam")
    print("       • No history or trends")
    print("       • Perfect for: practice tests, new students")
    print()
    print("  [B] Compare with Previous Exams (Trending)")
    print("       • Show progress over time")
    print("       • Compare to previous attempts")
    print("       • Adaptive recommendations based on history")
    print("       • Perfect for: tracking improvement")
    
    while True:
        choice = input("\nChoose [A/B]: ").strip().upper()
        if choice in ['A', 'B']:
            return "single" if choice == 'A' else "comparative"
        print(Colors.error("Please enter A or B"))
```

#### New Function: `check_student_history()`
```python
def check_student_history(student_name: str) -> bool:
    """Check if student has previous exam history.
    
    Args:
        student_name: Name of student
        
    Returns:
        True if history exists, False otherwise
    """
    from cissp_analyzer.history_loader import HistoryLoader
    
    history_loader = HistoryLoader()
    previous_exams = history_loader.load_previous_exams(student_name)
    return len(previous_exams) > 0
```

#### Updated `add_students()` Function
```python
# In add_students(), after getting student name but before asking for file:

# If comparative mode, check history
if analysis_type == "comparative":
    has_history = check_student_history(student_name)
    
    if not has_history:
        print(Colors.warning(f"No previous exam history found for {student_name}"))
        
        if not prompt_yes_no("Proceed as single exam analysis?", default=True):
            print(Colors.info("Skipping this student"))
            continue
        else:
            # Fall back to single mode for this student
            analysis_type = "single"
    else:
        num_previous = len(history_loader.load_previous_exams(student_name))
        print(Colors.info(f"Found {num_previous} previous exam(s) for {student_name}"))
```

#### Updated `run_analysis()` Function
```python
def run_analysis(
    pdf: str,
    students: List[Dict],
    output: str,
    answer_key: Optional[str],
    analysis_type: str = "single"
):
    """Run analysis with optional history tracking.
    
    Args:
        analysis_type: "single" or "comparative"
    """
    
    # ... existing code ...
    
    # Determine which analyzer method to use
    if analysis_type == "comparative":
        # Use history-aware analysis
        print(Colors.info("Analyzing with historical context..."))
        
        for student_name in student_names:
            print(f"\n{Colors.BOLD}Analyzing {student_name}...{Colors.END}")
            
            result = analyzer.analyze_student_with_history(
                exam_pdf=pdf,
                answer_excel=students[0]['excel'],
                student_name=student_name,
                students_dir="students"
            )
            
            print(Colors.success(f"Report saved: {result['report_path']}")
            if result['previous_exams_count'] > 0:
                print(Colors.info(f"Compared with {result['previous_exams_count']} previous exam(s)"))
    else:
        # Use single-exam analysis
        print(Colors.info("Analyzing single exam..."))
        
        result = analyzer.analyze(
            exam_pdf=pdf,
            answer_excel=students[0]['excel'],
            student_names=student_names,
            output_dir=output
        )
        
        # ... display results ...
```

#### Updated `main()` Function
```python
def main():
    """Main interactive CLI flow."""
    try:
        # Welcome
        print("\n" + Colors.header("╔" + "═" * 68 + "╗"))
        print(Colors.header("║" + " " * 15 + "CISSP ANALYZER - INTERACTIVE SETUP" + " " * 19 + "║"))
        print(Colors.header("╚" + "═" * 68 + "╝"))

        # STEP 1: Analysis type (NEW!)
        analysis_type = ask_analysis_type()

        # STEP 2: Exam selection
        exam_num = select_exam_number()

        # ... rest of existing flow ...
        
        # Pass analysis_type to run_analysis
        run_analysis(exam_pdf, students, output_dir, answer_key, analysis_type)
```

---

### 2. Update `analyze.py` (Master Entry Point)

#### Enhanced Help Text
```python
def standalone_analysis():
    """Route to standalone analysis"""
    print("\n" + "="*80)
    print("STANDALONE ANALYSIS")
    print("="*80)
    print("""
Two analysis modes:

[A] Single Exam (Ad-hoc / One-time)
    • Analyze just this exam
    • Perfect for: practice tests, new students
    • No history or trends needed

[B] Compare with Previous Exams (Trending)
    • Show progress over time
    • Compare against previous attempts
    • Adaptive recommendations based on history
    • Perfect for: tracking improvement, retakes
    
When you run the analysis, you'll be asked which mode you want.
    """)
```

---

### 3. Dependent Module Integration

#### `history_loader.py` - No changes needed
- Already handles missing histories gracefully
- `load_previous_exams()` returns empty list if no history

#### `main.py` - No changes needed
- `analyze_student_with_history()` already exists
- Already integrates with individual_report_gen
- Already saves performance data

#### `individual_report_gen.py` - No changes needed
- Already accepts historical_exams parameter
- Already generates progress sheet when history present

#### `interactive_cli.py` - Key changes
- Add `ask_analysis_type()` function
- Add `check_student_history()` function
- Update `add_students()` to check history for comparative mode
- Update `run_analysis()` to route to correct analyzer method
- Update `main()` to call analysis_type flow

#### `analyze_standalone.py` - Minor updates
- Update docstring to explain both modes
- Update help text

---

## Testing Plan

### Test Case 1: Single Exam Mode (Ad-hoc)
```
1. Run: python3 analyze.py → [2] Standalone
2. Choose: [A] Single Exam
3. Provide: Exam PDF, answer key, student name, answer file
4. Verify:
   - No history check performed
   - Single report generated (9 sheets)
   - No progress sheet (no history data)
```

### Test Case 2: Comparative Mode (No History)
```
1. Run: python3 analyze.py → [2] Standalone
2. Choose: [B] Compare with Previous Exams
3. For new student (no history):
   - System detects no history
   - Warns user
   - Asks: "Proceed as single exam?"
   - If YES: Generates single report
   - If NO: Skips student
```

### Test Case 3: Comparative Mode (With History)
```
1. Create fake history: students/<name>/exam-1_performance.json
2. Run: python3 analyze.py → [2] Standalone
3. Choose: [B] Compare with Previous Exams
4. Provide: Exam PDF (for exam 2), answer key, student name, answer file
5. Verify:
   - System detects history (1 previous exam)
   - Loads previous exam data
   - Generates report with progress tracking
   - Progress sheet shows: Exam 1 vs Exam 2 comparison
   - Adaptive recommendations based on trends
```

### Test Case 4: Multiple Students Mixed Modes
```
1. Run comparative analysis
2. Student A: Has history → full comparative report
3. Student B: No history → falls back to single
4. Verify: Both reports generated correctly
```

---

## Files Affected

### Modified
1. `cissp_analyzer/interactive_cli.py` — Add analysis type selection + history detection
2. `analyze.py` — Update help text
3. `analyze_standalone.py` — Update docstring

### No Changes Needed
- `main.py` (already has both methods)
- `history_loader.py` (already handles missing history)
- `individual_report_gen.py` (already supports history)
- `data_quality_validator.py`
- `consolidate_answers.py`
- Other modules

---

## Implementation Checklist

- [ ] Add `ask_analysis_type()` function to interactive_cli.py
- [ ] Add `check_student_history()` function to interactive_cli.py
- [ ] Update `add_students()` for history checking
- [ ] Update `run_analysis()` for dual-mode execution
- [ ] Update `main()` to call new analysis_type flow
- [ ] Update `analyze.py` help text
- [ ] Update `analyze_standalone.py` docstring
- [ ] Test Case 1: Single exam mode
- [ ] Test Case 2: Comparative with no history
- [ ] Test Case 3: Comparative with history
- [ ] Test Case 4: Mixed students
- [ ] Verify all modules integrate correctly
- [ ] Document in memory

---

## Benefits

✅ **Clear User Intent** — Users explicitly choose their analysis type  
✅ **No Code Duplication** — Uses existing analyze_student_with_history()  
✅ **Graceful Fallback** — No history → suggests single mode  
✅ **Full Integration** — Works with all existing report features  
✅ **Backward Compatible** — Old flows still work  
✅ **Minimal Changes** — Only interactive_cli.py needs major updates  

---

## Estimated Effort

- Implementation: 2-3 hours
- Testing: 1-2 hours
- Total: 3-5 hours

---

## Success Criteria

✅ User can choose between single and comparative analysis  
✅ System detects student history automatically  
✅ Comparative reports show historical trends  
✅ All 4 test cases pass  
✅ No breaking changes to existing functionality  
✅ Clear error messages and guidance  
