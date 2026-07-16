# Phase 2 - Hybrid Execution Plan

**Strategy:** 90% Ollama + 10% Claude Review  
**Timeline:** 18 hours  
**Cost:** $0.50 (Claude review only)  
**Status:** Ready to execute

---

## ✅ Pre-Flight Checklist

Before starting, verify:

```bash
# 1. Check Ollama is installed
ollama --version

# 2. Check GPU/CPU VRAM
nvidia-smi        # (GPU)
free -h            # (RAM)

# 3. Pull required models
ollama pull qwen2.5-coder:7b      # ~4.7GB (core model)
ollama pull qwen2.5-coder:1.5b    # ~980MB (fast tasks)
ollama pull gemma2:latest         # ~5.2GB (review)
ollama pull llama2:7b             # ~3.8GB (docs)

# 4. Start Ollama service
ollama serve
# (Keep this terminal open while running tasks)

# 5. Test in new terminal
ollama list
# Should show all 4 models downloaded
```

---

## 📋 PHASE 2A: Exam Folder Management (3.5 hours)

### Task 2A-1: ExamFolderManager Class (2 hours)

**File:** `cissp_analyzer/exam_folder_manager.py`

```bash
# Use 1.5b for speed (simple data structures)
ollama run qwen2.5-coder:1.5b << 'EOF'
Write a Python class called ExamFolderManager with these methods:

1. __init__(self, base_dir="exams")
   - Create base_dir if doesn't exist

2. list_exams() -> List[Dict]
   - Return list of all exam folders
   - Each dict has: name, path, created_date, student_count

3. get_exam_metadata(exam_id) -> Dict
   - Read .exam_metadata.json from folder
   - Return exam info

4. create_exam_folder(exam_name: str, pdf_path: str) -> Path
   - Create folder: exams/EXAM_NAME_TIMESTAMP/
   - Copy PDF to folder
   - Create .exam_metadata.json with:
     * exam_name
     * pdf_path
     * created_date
     * total_questions (extract from PDF)
   - Return folder path

5. get_new_answer_files(exam_id) -> List[str]
   - Check exams/EXAM_ID/ for .xlsx files
   - Return list of filenames

6. _sanitize_name(name: str) -> str
   - Remove special chars
   - Max 50 chars

Include docstrings and type hints.
Use pathlib.Path.
No external dependencies except json/datetime.
EOF
```

**Quality Check:**
- [ ] Copy output to `cissp_analyzer/exam_folder_manager.py`
- [ ] Check syntax: `python3 -m py_compile cissp_analyzer/exam_folder_manager.py`
- [ ] Review for edge cases

---

### Task 2A-2: StateTracker Class (1.5 hours)

**File:** `cissp_analyzer/state_tracker.py`

```bash
ollama run qwen2.5-coder:1.5b << 'EOF'
Write a Python class called ProcessedFileTracker with these methods:

1. __init__(self, exam_folder: Path)
   - Load .processed.json from exam_folder (if exists)
   - Initialize empty if not exists

2. is_processed(filename: str) -> bool
   - Check if filename in processed list
   - Return True/False

3. mark_processed(filename: str, report_path: str, timestamp: str)
   - Add to processed list with metadata
   - Save to .processed.json

4. get_unprocessed_files(all_files: List[str]) -> List[str]
   - Compare all_files with processed
   - Return only new files

5. get_processing_history() -> List[Dict]
   - Return list of all processed files with timestamps

.processed.json schema:
{
  "processed_files": [
    {
      "filename": "Alice.xlsx",
      "report_path": "reports/Alice.xlsx",
      "processed_date": "2026-07-15T14:30:00"
    }
  ],
  "last_updated": "2026-07-15T14:30:00"
}

Include error handling for missing files.
EOF
```

**Quality Check:**
- [ ] Copy output to `cissp_analyzer/state_tracker.py`
- [ ] Verify JSON schema handling
- [ ] Test with mock data

---

## 📋 PHASE 2B: Interactive Menu System (3.5 hours)

### Task 2B-1: MenuController Class (2 hours)

**File:** `cissp_analyzer/menu_controller.py`

```bash
ollama run qwen2.5-coder:7b << 'EOF'
Write a Python class called MenuController for interactive CLI:

1. __init__(self)
   - Initialize terminal colors/formatting

2. show_main_menu(exams: List[Dict]) -> str
   - Display:
     * Title "CISSP ANALYZER - Main Menu"
     * List of exams with [1], [2], etc
     * For each: name, student_count, last_updated
     * [n+1] Upload NEW questionnaire
     * [n+2] Exit
   - Return formatted string

3. get_user_choice() -> str
   - Prompt user: "Choose option: "
   - Validate input (1-N range)
   - Return choice as string

4. show_exam_menu(exam_id: str) -> str
   - Show submenu:
     * Process new answer sheets
     * Generate class report
     * Back to main menu
   - Return formatted menu

5. show_processing_summary(exam_name: str, new_files: List[str])
   - Show:
     * Files found
     * Files to process
     * Estimate time
   - Ask "Continue? (y/n)"

6. show_class_report_preview(students: List[str], domains: Dict)
   - Preview what will be in class report
   - Show: student names, domains being averaged
   - Ask "Generate class report? (y/n)"

7. show_success_message(message: str)
   - Pretty print with ✓ checkmark

8. show_error_message(error: str)
   - Pretty print with ✗ error mark

Use colors (green for success, red for error, blue for info).
Use clear separators and formatting.
EOF
```

**Quality Check:**
- [ ] Copy to `cissp_analyzer/menu_controller.py`
- [ ] Test menu display in terminal
- [ ] Verify input validation

---

### Task 2B-2: PDF Upload Handler (1.5 hours)

**File:** `cissp_analyzer/pdf_upload_handler.py`

```bash
ollama run qwen2.5-coder:7b << 'EOF'
Write a Python function handle_pdf_upload() and related helpers:

1. handle_pdf_upload() -> Tuple[str, str]
   - Prompt user: "Enter PDF file path (or drag/drop): "
   - Get file path from user
   - Call validate_pdf(path)
   - If valid, call prompt_exam_metadata()
   - Create exam folder
   - Return (exam_name, folder_path)

2. validate_pdf(pdf_path: str) -> bool
   - Check file exists
   - Check file is .pdf
   - Try to open with pypdf (basic validation)
   - Return True/False with error message

3. extract_question_count(pdf_path: str) -> int
   - Use pdf_parser.PDFParser to extract questions
   - Count total questions
   - Handle errors gracefully

4. prompt_exam_metadata() -> Dict
   - Prompt: "Exam name (e.g., CISSP_June_2026): "
   - Prompt: "Description (optional): "
   - Prompt: "Confirm? (y/n): "
   - Return dict with exam_name, description

5. create_exam_folder(exam_name: str, pdf_path: str, question_count: int) -> Path
   - Call ExamFolderManager.create_exam_folder()
   - Copy PDF
   - Create metadata
   - Return folder path

Include error handling for:
- File not found
- Invalid PDF
- User cancel
EOF
```

**Quality Check:**
- [ ] Copy to `cissp_analyzer/pdf_upload_handler.py`
- [ ] Test with sample PDF
- [ ] Verify user prompts are clear

---

## 📋 PHASE 2C: Processing Pipeline (5.5 hours)

### Task 2C-1: ExamProcessor Class (2 hours)

**File:** `cissp_analyzer/exam_processor.py`

```bash
ollama run qwen2.5-coder:7b << 'EOF'
Write a Python class called ExamProcessor:

1. __init__(self, exam_folder: Path)
   - Load exam metadata
   - Initialize StateTracker
   - Load extracted questions

2. detect_new_answer_files() -> List[str]
   - Get all .xlsx files in exam_folder
   - Use StateTracker to find unprocessed
   - Return list of new files

3. process_new_files() -> Dict
   - For each new file:
     * Validate Excel format
     * Extract student name from filename
     * Match answers to questions
     * Generate individual report
     * Mark as processed
   - Return summary: {processed: [], failed: [], skipped: []}

4. process_single_file(excel_path: str) -> Dict
   - Load Excel file
   - Extract student name and answers
   - Call student_answer_analyzer.analyze()
   - Generate individual report
   - Return report metadata

5. skip_already_processed() -> List[str]
   - Get already processed files from StateTracker
   - Log which files are skipped
   - Return list of skipped filenames

6. validate_answers_match_questions(answers: Dict, questions: List) -> bool
   - Check all question IDs in answers match questions
   - Check all answers are A-D format
   - Return True/False with error details

Include error handling and logging.
EOF
```

**Quality Check:**
- [ ] Copy to `cissp_analyzer/exam_processor.py`
- [ ] Integrate with existing analyzers
- [ ] Test with sample data

---

### Task 2C-2: ClassReportGenerator (2 hours)

**File:** `cissp_analyzer/class_report_generator.py`

```bash
ollama run qwen2.5-coder:7b << 'EOF'
Write a Python class called ClassReportGenerator:

1. __init__(self, exam_folder: Path)
   - Load all student reports from exam_folder/reports/
   - Load exam metadata

2. get_all_student_reports() -> List[Dict]
   - Find all CISSP_Individual_Report_*.xlsx files
   - Extract student name and scores
   - Return list of dicts: {name, score, domain_scores, etc}

3. validate_before_aggregation() -> Tuple[bool, str]
   - Check reports exist
   - Check all have same number of domains
   - Check no duplicate names
   - Return (is_valid, error_message)

4. generate_class_metrics() -> Dict
   - Calculate:
     * Average score per student
     * Average score per domain
     * Min/max scores
     * Standard deviation
     * Students passing (>75%)
   - Return metrics dict

5. generate_class_report() -> Path
   - Call class_report_gen.ClassReportGenerator (existing)
   - Pass aggregated data
   - Return path to generated report

6. show_preview(metrics: Dict) -> str
   - Display:
     * Number of students
     * Average score
     * Domain averages
     * Pass rate
   - Return formatted string

Include validation and error handling.
EOF
```

**Quality Check:**
- [ ] Copy to `cissp_analyzer/class_report_generator.py`
- [ ] Verify metrics calculations
- [ ] Test with multiple students

---

### Task 2C-3: Validation Layer (1.5 hours)

**File:** `cissp_analyzer/processing_validator.py`

```bash
ollama run qwen2.5-coder:7b << 'EOF'
Write a Python class called ProcessingValidator:

1. __init__(self)
   - Initialize validation rules

2. validate_answer_sheet(excel_path: str) -> Tuple[bool, str]
   - Check file exists
   - Check file is .xlsx
   - Check has required columns
   - Check no empty rows
   - Return (is_valid, error_message)

3. validate_question_match(answers: Dict, questions: List) -> Tuple[bool, List]
   - Check answer question IDs exist in questions
   - Check no extra question IDs
   - Check answer format (A-D)
   - Return (is_valid, mismatches)

4. check_duplicate_student_names(names: List[str]) -> List[str]
   - Find duplicate names
   - Return list of duplicates

5. validate_folder_structure(exam_folder: Path) -> Tuple[bool, str]
   - Check required files/folders exist
   - Check metadata.json is valid
   - Return (is_valid, errors)

6. validate_pdf(pdf_path: str) -> Tuple[bool, str]
   - Check file exists
   - Check is valid PDF
   - Check can extract questions
   - Return (is_valid, error)

Include helpful error messages for users.
EOF
```

**Quality Check:**
- [ ] Copy to `cissp_analyzer/processing_validator.py`
- [ ] Test with invalid inputs
- [ ] Verify error messages are clear

---

## 📋 PHASE 2D: Integration (2.5 hours)

### Task 2D-1: Update run.py (1.5 hours)

**File:** `cissp_analyzer/run.py` (REFACTOR)

```bash
ollama run qwen2.5-coder:7b << 'EOF'
Refactor the existing run.py to use new components:

Replace main() with:

def main():
    menu = MenuController()
    exam_manager = ExamFolderManager()
    
    while True:
        # Show main menu
        exams = exam_manager.list_exams()
        menu.show_main_menu(exams)
        
        choice = menu.get_user_choice()
        
        if choice == "upload":
            exam_name, folder = pdf_upload_handler.handle_pdf_upload()
            menu.show_success_message(f"Questionnaire uploaded: {exam_name}")
        
        elif choice in range(1, len(exams)+1):
            exam = exams[choice-1]
            handle_exam_processing(exam)
        
        elif choice == "exit":
            break

def handle_exam_processing(exam: Dict):
    menu = MenuController()
    processor = ExamProcessor(exam['path'])
    
    new_files = processor.detect_new_answer_files()
    
    if new_files:
        menu.show_processing_summary(exam['name'], new_files)
        if menu.get_confirmation():
            result = processor.process_new_files()
            menu.show_success_message(f"Processed {len(result['processed'])} files")
    else:
        print("No new answer sheets found")
    
    # Ask about class report
    ask_for_class_report(exam)

def ask_for_class_report(exam: Dict):
    generator = ClassReportGenerator(exam['path'])
    is_valid, msg = generator.validate_before_aggregation()
    
    if not is_valid:
        menu.show_error_message(msg)
        return
    
    metrics = generator.generate_class_metrics()
    preview = generator.show_preview(metrics)
    
    if menu.get_confirmation("Generate class report?"):
        report_path = generator.generate_class_report()
        menu.show_success_message(f"Class report generated: {report_path}")

Integrate all new components.
Keep existing analysis logic.
EOF
```

**Quality Check:**
- [ ] Copy output to `cissp_analyzer/run.py`
- [ ] Verify imports are correct
- [ ] Test menu flow

---

### Task 2D-2: E2E Integration Test (1 hour)

**Use Claude (faster for test writing):**

```
Generate comprehensive integration tests for Phase 2:
- Test PDF upload workflow
- Test exam folder creation
- Test new file detection
- Test individual report generation
- Test class report generation
- Test error handling
- Test state tracking
- Test menu interaction
```

**Will do this with Claude review phase**

---

## 📋 PHASE 2E: Documentation (1 hour)

### Task 2E-1: User Documentation (30 min)

```bash
ollama run llama2:7b << 'EOF'
Write a comprehensive PHASE_2_USER_GUIDE.md documenting:

1. New Workflow:
   - Single command: python3 run.py
   - Menu-driven interface
   - Upload questionnaire
   - Add answer sheets
   - Generate reports
   - Class aggregation

2. Step-by-step examples:
   - First time use (upload PDF)
   - Adding students (multiple answer sheets)
   - Generating class report
   - Multiple exams

3. FAQ:
   - "Where do I place answer sheets?"
   - "How does it detect new files?"
   - "Can I process same exam twice?"
   - "What happens if I change an answer sheet?"

4. Troubleshooting:
   - Common errors
   - How to fix them

Make it beginner-friendly with examples.
EOF
```

---

### Task 2E-2: Code Polish (30 min)

```bash
# Format all new files
black cissp_analyzer/exam_folder_manager.py
black cissp_analyzer/state_tracker.py
black cissp_analyzer/menu_controller.py
black cissp_analyzer/pdf_upload_handler.py
black cissp_analyzer/exam_processor.py
black cissp_analyzer/class_report_generator.py
black cissp_analyzer/processing_validator.py

# Type check
python3 -m mypy cissp_analyzer/*.py --ignore-missing-imports
```

---

## 🔄 PHASE 2D: Claude Final Review (1 hour)

**This is where you use Claude ($0.50 cost):**

```
Review entire Phase 2 implementation:

1. Architecture review
   - Are all components properly integrated?
   - Are dependencies correct?
   - Is error handling comprehensive?

2. Code quality review
   - Type hints complete?
   - Docstrings present?
   - Edge cases handled?

3. Integration testing
   - Full workflow works?
   - Menu interaction intuitive?
   - Error messages helpful?

4. Performance review
   - No bottlenecks?
   - File detection efficient?

5. Final recommendations
   - Any improvements?
   - Security issues?
   - Best practices?
```

---

## ✅ Execution Checklist

### Pre-Work
- [ ] Ollama installed and models downloaded
- [ ] Ollama service running (`ollama serve`)
- [ ] Terminal window for Ollama (keep open)
- [ ] New terminal for development

### Phase 2A
- [ ] 2A-1: ExamFolderManager created
- [ ] 2A-2: StateTracker created
- [ ] Both tested with mock data

### Phase 2B
- [ ] 2B-1: MenuController created
- [ ] 2B-2: PDFUploadHandler created
- [ ] Menu displays correctly

### Phase 2C
- [ ] 2C-1: ExamProcessor created
- [ ] 2C-2: ClassReportGenerator created
- [ ] 2C-3: ProcessingValidator created
- [ ] All integrated with existing code

### Phase 2D
- [ ] run.py refactored
- [ ] E2E tests written
- [ ] All tests passing (should be 345+ tests)

### Phase 2E
- [ ] User documentation written
- [ ] Code formatted with black
- [ ] Type hints verified

### Claude Review
- [ ] Code sent for final review
- [ ] Feedback incorporated
- [ ] Phase 2 complete!

---

## 📊 Expected Timeline

```
Day 1 (4 hours):
  - 2A-1: ExamFolderManager
  - 2A-2: StateTracker
  
Day 2 (4 hours):
  - 2B-1: MenuController
  - 2B-2: PDFUploadHandler
  
Day 3 (5 hours):
  - 2C-1: ExamProcessor
  - 2C-2: ClassReportGenerator
  - 2C-3: ProcessingValidator
  
Day 4 (4 hours):
  - 2D-1: Integration
  - 2D-2: E2E Testing
  - 2E: Docs & Polish
  
Day 5 (1 hour):
  - Claude final review
  - Feedback incorporation
```

---

## 🚀 Ready to Start?

Execute in order:
1. Run Ollama pre-flight checklist
2. Start with Task 2A-1
3. Follow the Ollama commands exactly
4. Save output to specified files
5. Quality check each task
6. Move to next task

**Let's begin!** Should we start with Task 2A-1?
