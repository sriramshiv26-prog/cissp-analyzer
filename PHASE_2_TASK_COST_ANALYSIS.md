# Phase 2: Unified Questionnaire System - Task Cost Analysis

**Goal:** Single command (`python3 run.py`) for upload, manage, and analyze any questionnaire

**Total Effort:** 18-22 hours  
**Complexity:** Medium  
**Priority:** P1 (Core functionality)

---

## 📋 Task Breakdown

### **PHASE 2A: Exam Folder Management (4-5 hours)**

#### Task 2A-1: ExamFolderManager Class (2.5 hours)
```python
class ExamFolderManager:
    def __init__(self, base_dir="exams")
    def list_exams() → List[Dict]          # Get all exam folders
    def get_exam_metadata(exam_id) → Dict  # Read metadata
    def create_exam_folder(name, pdf_path) → Path
    def get_new_answer_files(exam_id) → List[str]  # Detect new files
```

**Subtasks:**
- [ ] Read existing exam folders (2A-1a) - 30 min
- [ ] Parse exam metadata files (2A-1b) - 30 min
- [ ] Create folder structure (2A-1c) - 45 min
- [ ] Write/read metadata JSON (2A-1d) - 30 min

**Complexity:** Low  
**Dependencies:** None  
**Test coverage:** 8 unit tests

---

#### Task 2A-2: State Tracking System (1.5 hours)
```python
class ProcessedFileTracker:
    def __init__(self, exam_id)
    def is_processed(filename) → bool
    def mark_processed(filename, report_path)
    def get_unprocessed_files() → List[str]
    def get_processing_history() → Dict
```

**Subtasks:**
- [ ] Create .processed.json schema (2A-2a) - 20 min
- [ ] Implement tracker read/write (2A-2b) - 40 min
- [ ] Detect duplicates (2A-2c) - 30 min

**Complexity:** Low  
**Dependencies:** 2A-1  
**Test coverage:** 6 unit tests

---

### **PHASE 2B: Interactive Menu System (4-5 hours)**

#### Task 2B-1: Main Menu Controller (2.5 hours)
```python
class MenuController:
    def show_main_menu()
    def show_exam_menu(exams: List[Dict])
    def handle_user_choice(choice) → Action
    def prompt_for_input(message, options) → str
```

**Subtasks:**
- [ ] Display formatted menu (2B-1a) - 45 min
- [ ] Handle menu navigation (2B-1b) - 1 hour
- [ ] Input validation (2B-1c) - 30 min
- [ ] Error handling (2B-1d) - 15 min

**Complexity:** Medium  
**Dependencies:** 2A-1, 2A-2  
**Test coverage:** 10 unit tests + 5 integration tests

---

#### Task 2B-2: PDF Upload Handler (1.5 hours)
```python
def handle_pdf_upload():
    # Get PDF from user (drag/drop or file path)
    # Validate PDF format
    # Extract number of questions
    # Prompt for exam name/metadata
    # Create folder and store metadata
```

**Subtasks:**
- [ ] File input handling (2B-2a) - 30 min
- [ ] PDF validation (2B-2b) - 30 min
- [ ] Metadata prompt flow (2B-2c) - 30 min

**Complexity:** Medium  
**Dependencies:** pdf_parser.py (existing)  
**Test coverage:** 6 unit tests

---

### **PHASE 2C: Exam Processing Pipeline (6-7 hours)**

#### Task 2C-1: Single Exam Processor (2.5 hours)
```python
class ExamProcessor:
    def __init__(self, exam_id)
    def detect_new_answer_files() → List[str]
    def process_new_files()
    def skip_already_processed()
    def generate_individual_reports()
```

**Subtasks:**
- [ ] Detect new files (2C-1a) - 45 min
- [ ] Skip processed files (2C-1b) - 30 min
- [ ] Generate individual reports (2C-1c) - 1 hour
- [ ] Update processed tracker (2C-1d) - 15 min

**Complexity:** Medium  
**Dependencies:** 2A-1, 2A-2, main.py (existing)  
**Test coverage:** 10 unit tests

---

#### Task 2C-2: Class Report Generator (2 hours)
```python
class ClassReportGenerator:
    def __init__(self, exam_id)
    def get_all_student_reports() → List[Dict]
    def validate_before_aggregation()
    def generate_class_report()
    def show_preview(students_count, domains_avg)
```

**Subtasks:**
- [ ] Aggregate student data (2C-2a) - 45 min
- [ ] Generate class metrics (2C-2b) - 45 min
- [ ] Create preview output (2C-2c) - 30 min

**Complexity:** Medium  
**Dependencies:** 2A-1, class_report_gen.py (existing)  
**Test coverage:** 8 unit tests

---

#### Task 2C-3: Validation Layer (2 hours)
```python
class ProcessingValidator:
    def validate_answer_sheet(excel_path) → bool
    def validate_question_match(answers, extracted_questions) → bool
    def check_duplicate_student_names() → List[str]
    def validate_folder_structure() → bool
```

**Subtasks:**
- [ ] Excel format validation (2C-3a) - 30 min
- [ ] Question ID matching (2C-3b) - 45 min
- [ ] Duplicate detection (2C-3c) - 30 min
- [ ] Folder structure check (2C-3d) - 15 min

**Complexity:** Medium  
**Dependencies:** data_quality_validator.py (existing)  
**Test coverage:** 12 unit tests

---

### **PHASE 2D: Integration & Main Entry Point (3-4 hours)**

#### Task 2D-1: Update run.py (2 hours)
```python
def main():
    menu = MenuController()
    while True:
        exams = ExamFolderManager.list_exams()
        menu.show_main_menu(exams)
        choice = menu.get_user_choice()
        
        if choice == "upload":
            handle_pdf_upload()
        elif choice == "process":
            ExamProcessor(exam_id).process()
        elif choice == "class_report":
            ClassReportGenerator(exam_id).generate()
        elif choice == "exit":
            break
```

**Subtasks:**
- [ ] Refactor existing run.py (2D-1a) - 45 min
- [ ] Integrate menu controller (2D-1b) - 45 min
- [ ] Add flow logic (2D-1c) - 30 min

**Complexity:** Medium  
**Dependencies:** All Phase 2A-C tasks  
**Test coverage:** 5 integration tests

---

#### Task 2D-2: End-to-End Testing (1.5 hours)
```
Test scenarios:
- [x] Upload new questionnaire
- [x] Add answer sheets to existing exam
- [x] Detect new files automatically
- [x] Skip already processed files
- [x] Generate individual reports
- [x] Generate class report with preview
- [x] Error handling (wrong PDF format, Excel mismatch)
- [x] Multiple exams simultaneously
```

**Complexity:** Medium  
**Dependencies:** All Phase 2A-D tasks  
**Test coverage:** 15 integration tests

---

### **PHASE 2E: Documentation & Polish (1-2 hours)**

#### Task 2E-1: User Documentation (1 hour)
- [ ] Update README with new workflow (30 min)
- [ ] Create USAGE.md with screenshots/examples (30 min)

#### Task 2E-2: Code Quality (0.5 hours)
- [ ] Black formatting (10 min)
- [ ] Type hints completion (20 min)

---

## 📊 Task Summary Table

| Phase | Task | Hours | Complexity | Dependencies |
|-------|------|-------|-----------|---|
| 2A-1 | ExamFolderManager | 2.5 | Low | None |
| 2A-2 | StateTracker | 1.5 | Low | 2A-1 |
| 2B-1 | MenuController | 2.5 | Medium | 2A-1, 2A-2 |
| 2B-2 | PDFUpload | 1.5 | Medium | existing |
| 2C-1 | ExamProcessor | 2.5 | Medium | 2A, 2B |
| 2C-2 | ClassReportGen | 2 | Medium | 2A, existing |
| 2C-3 | Validator | 2 | Medium | existing |
| 2D-1 | Integration | 2 | Medium | All 2A-C |
| 2D-2 | E2E Testing | 1.5 | Medium | All 2A-D |
| 2E-1 | Documentation | 1 | Low | All |
| 2E-2 | Polish | 0.5 | Low | All |
| **TOTAL** | | **19** | **Medium** | |

---

## 🔄 Execution Order

```
Sequential (dependencies force this):
1. 2A-1 (ExamFolderManager) → 2.5h
2. 2A-2 (StateTracker) → 1.5h
3. 2B-1 (MenuController) → 2.5h
4. 2B-2 (PDFUpload) → 1.5h
5. 2C-1 (ExamProcessor) → 2.5h
6. 2C-2 (ClassReportGen) → 2h
7. 2C-3 (Validator) → 2h
8. 2D-1 (Integration) → 2h
9. 2D-2 (E2E Testing) → 1.5h
10. 2E (Docs + Polish) → 1.5h
```

**Parallel opportunities:**
- 2C-2 and 2C-3 can run in parallel (1 hour savings)
- 2E can start after 2D-1

**Optimized timeline: 18 hours (with parallelization)**

---

## 💰 Token Cost Analysis

### Claude AI (Current Strategy)
| Phase | Files | Complexity | Est. Tokens | Notes |
|-------|-------|-----------|------------|-------|
| 2A | 2 new | Low | 8K | Simple data structures |
| 2B | 2 new | Medium | 12K | UI/interaction logic |
| 2C | 3 new | Medium | 15K | Core processing |
| 2D | 1 modified | Medium | 10K | Integration + tests |
| 2E | 2 updated | Low | 3K | Documentation |
| **TOTAL** | | | **48K** | Cost: ~$1.44 @ $0.03/1K |

**Token efficiency:** ~2,500 tokens per hour (good ratio)

---

### 🚀 Ollama Local LLM Strategy (COST: $0)

**Recommended Model Allocation:**

| Task | Ollama Model | Why | Speed | Cost |
|------|--------------|-----|-------|------|
| **2A-1** ExamFolderManager | qwen2.5-coder:7b | Pure code, straightforward | Fast | $0 |
| **2A-2** StateTracker | qwen2.5-coder:1.5b | Simple JSON logic | Very Fast | $0 |
| **2B-1** MenuController | qwen2.5-coder:7b | Complex UI logic, needs reasoning | Medium | $0 |
| **2B-2** PDFUpload | qwen2.5-coder:7b | File handling, edge cases | Medium | $0 |
| **2C-1** ExamProcessor | qwen2.5-coder:7b | Core logic, many functions | Medium | $0 |
| **2C-2** ClassReportGen | qwen2.5-coder:7b | Complex aggregation logic | Medium | $0 |
| **2C-3** Validator | qwen2.5-coder:7b | Error handling, validation rules | Medium | $0 |
| **2D-1** Integration | gemma2:latest | Code review, connecting pieces | Slow | $0 |
| **2D-2** E2E Testing | qwen2.5-coder:7b | Test case generation | Fast | $0 |
| **2E** Docs + Polish | llama2:7b | Documentation, natural language | Medium | $0 |

---

### **Ollama Model Selection Rationale**

#### **qwen2.5-coder:7b** (Primary for code)
- ✅ Excellent Python code generation
- ✅ Handles complex logic well
- ✅ Fast iteration (~5-10 tokens/sec GPU)
- ✅ Good for 70% of Phase 2 tasks
- ⚠️ Resource: ~16GB VRAM if running on GPU

#### **qwen2.5-coder:1.5b** (Simple utilities)
- ✅ Very fast (~30 tokens/sec)
- ✅ Sufficient for simple data structures
- ✅ Lower resource (4GB VRAM)
- ✅ Perfect for 2A-2 (StateTracker)

#### **gemma2:latest** (Code review)
- ✅ Good reasoning capabilities
- ✅ Excellent for integration testing logic
- ✅ Understanding complex flows
- ❌ Slower than Qwen (~3-5 tokens/sec)
- Use for: 2D-1 final integration review

#### **llama2:7b** (Documentation)
- ✅ Natural language fluency
- ✅ Creates readable documentation
- ✅ Good explanations
- ✅ Good balance of speed/quality

---

### **Cost Comparison**

| Strategy | Total Cost | Setup Time | Speed |
|----------|-----------|-----------|-------|
| Claude API | $1.44 | 0 min | Fast |
| Ollama (local) | $0 | 30 min | Medium |
| **Savings** | **$1.44** | | |

**Plus:** No rate limits, no internet dependency, full privacy

---

### **Ollama Execution Strategy**

**Phase 2A (Folder Management):**
```bash
# Simple structures - use 1.5b for speed
ollama run qwen2.5-coder:1.5b "Write ExamFolderManager class..."
ollama run qwen2.5-coder:1.5b "Write StateTracker class..."
```
**Time: 45 min | Speed: Very Fast | Quality: Excellent**

---

**Phase 2B (Menu System):**
```bash
# Complex UI - use 7b for better logic
ollama run qwen2.5-coder:7b "Write MenuController class..."
ollama run qwen2.5-coder:7b "Write PDFUpload handler..."
```
**Time: 1.5 hours | Speed: Medium | Quality: Excellent**

---

**Phase 2C (Processing):**
```bash
# Core logic - definitely 7b
ollama run qwen2.5-coder:7b "Write ExamProcessor class..."
ollama run qwen2.5-coder:7b "Write ClassReportGenerator..."
ollama run qwen2.5-coder:7b "Write ProcessingValidator..."
```
**Time: 2 hours | Speed: Medium | Quality: Excellent**

---

**Phase 2D (Integration):**
```bash
# Use Qwen for main integration
ollama run qwen2.5-coder:7b "Refactor run.py to integrate all..."

# Use Gemma for review
ollama run gemma2:latest "Review the integration logic..."
```
**Time: 1.5 hours | Speed: Medium | Quality: Very Good**

---

**Phase 2E (Docs):**
```bash
# Natural language - use Llama2
ollama run llama2:7b "Write user documentation for Phase 2..."
```
**Time: 30 min | Speed: Medium | Quality: Good**

---

### **Hybrid Strategy (Recommended)**

Use **Ollama for 90% of work**, Claude for final review:

```
1. Generate all code with Ollama (16 hours)
   └─ qwen2.5-coder:7b (main)
   └─ qwen2.5-coder:1.5b (simple tasks)
   
2. Write tests with Ollama (2 hours)
   └─ qwen2.5-coder:7b
   
3. Final code review with Claude (1 hour)
   └─ Check architecture
   └─ Verify integration
   └─ Quality assurance
   
TOTAL COST: ~$0.50 (Claude review only)
SAVINGS: $0.94 vs pure Claude
```

---

### **Hardware Requirements for Ollama**

```
Minimum: 4GB VRAM (use 1.5b model only)
Recommended: 8GB VRAM (7b model runs smoothly)
Ideal: 16GB VRAM (run multiple models in parallel)

Current system: Check with:
  nvidia-smi (GPU VRAM)
  or
  free -h (CPU RAM)
```

---

### **Command Examples**

```bash
# Start Ollama service
ollama serve

# In another terminal, run code generation
ollama run qwen2.5-coder:7b "Generate Python class for..."

# Save output to file
ollama run qwen2.5-coder:7b "..." > output.py

# Chain multiple generations
for task in 2A-1 2A-2 2B-1; do
  ollama run qwen2.5-coder:7b "Generate code for $task"
done
```

---

### **Timeline with Ollama**

| Phase | Hours | Model | Speed |
|-------|-------|-------|-------|
| 2A | 3.5h | qwen2.5-coder (1.5b+7b) | Very Fast |
| 2B | 3.5h | qwen2.5-coder:7b | Medium |
| 2C | 5.5h | qwen2.5-coder:7b | Medium |
| 2D | 2.5h | qwen2.5-coder:7b → gemma2 | Medium |
| 2E | 1h | llama2:7b | Medium |
| **Human Review/Debug** | 2h | Manual | - |
| **TOTAL** | 18h | - | - |

**Same timeline, $0 cost instead of $1.44**

---

## ✅ Deliverables

After Phase 2:
- ✅ Single command for all operations
- ✅ Auto-detection of new answer sheets
- ✅ State tracking (no re-processing)
- ✅ Class report aggregation
- ✅ Multi-exam support
- ✅ PDF upload workflow
- ✅ Full test coverage (40+ new tests)
- ✅ Clean documentation

---

## 🎯 Success Criteria

1. **Functionality**
   - [ ] `python3 run.py` shows menu with all exams
   - [ ] Upload new PDF creates labeled folder
   - [ ] Auto-detects new Excel files
   - [ ] Skip already-processed files
   - [ ] Class report shows all students + metrics
   - [ ] Error messages are clear

2. **Reliability**
   - [ ] 40+ tests pass (new tests)
   - [ ] 332+ existing tests still pass
   - [ ] No data loss from re-processing
   - [ ] Handles edge cases (wrong formats, duplicates)

3. **UX**
   - [ ] Menu is intuitive
   - [ ] Clear prompts
   - [ ] Preview before actions
   - [ ] Progress indication

---

## 📅 Timeline Estimate

**Best case:** 18 hours (with parallelization)  
**Realistic case:** 20-22 hours (with breaks, debugging)  
**Recommended pace:** 4-5 hours/day = 4-5 days

---

## 🚀 Ready to Start?

This is a solid, well-defined scope. All tasks are concrete, testable, and have clear dependencies.

Should we proceed with Phase 2?
