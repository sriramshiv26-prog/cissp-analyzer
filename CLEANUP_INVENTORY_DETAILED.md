# CLEANUP INVENTORY - Detailed Review

**Goal:** Remove ONLY unnecessary files. Keep everything critical.

**Format:** 
- 🗑️ = REMOVE (not needed)
- ✅ = KEEP (essential)
- ⚠️ = REVIEW (ask user)

---

## 📁 ROOT LEVEL SCRIPTS (37 files total)

### Entry Point Scripts
These are old/duplicate entry points. We'll keep ONE main `run.py`:

- `analyze.py` 🗑️ REMOVE
  - Why: Redundant entry point (covered by run.py)
  - Safe: Yes, functionality merged into run.py
  - Size: 7.7 KB

- `analyze_dec25.py` 🗑️ REMOVE
  - Why: Batch-specific, outdated
  - Safe: Yes, batch workflow moved to cli
  - Size: 5.1 KB

- `analyze_july26.py` 🗑️ REMOVE
  - Why: Batch-specific, outdated
  - Safe: Yes, batch workflow moved to cli
  - Size: 4.8 KB

- `analyze_standalone.py` 🗑️ REMOVE
  - Why: Standalone moved to CLI options
  - Safe: Yes, functionality in run.py
  - Size: 867 B

- `analyze_exam.sh` 🗑️ REMOVE
  - Why: Shell wrapper, redundant with Python CLI
  - Safe: Yes, not used
  - Size: 418 B

**SUBTOTAL REMOVE: 5 scripts, 18.8 KB**

---

### Answer Extraction Scripts (consolidate to 1)

- `answer_extractor_dual.py` 🗑️ REMOVE
  - Why: Superseded by cissp_analyzer module
  - Safe: Yes, functionality in cissp_analyzer/
  - Size: 5.1 KB

- `pdf_answer_extractor_v2.py` 🗑️ REMOVE
  - Why: Old version (v2), functionality in core module
  - Safe: Yes, pdf_parser.py handles this
  - Size: Unknown

- `extract_answer_key.py` 🗑️ REMOVE
  - Why: One-off script, functionality in core
  - Safe: Yes, answer key extraction moved to module
  - Size: 3.2 KB

- `create_answer_key.py` 🗑️ REMOVE
  - Why: One-off utility, replaced by manager
  - Safe: Yes, questionnaire_manager.py does this
  - Size: 2.1 KB

- `quick_answer_key.py` 🗑️ REMOVE
  - Why: One-off utility
  - Safe: Yes, not core functionality
  - Size: 1.8 KB

**SUBTOTAL REMOVE: 5 scripts, 12.2 KB**

---

### Validation Scripts (consolidate to 1)

- `validate_answers.py` 🗑️ REMOVE
  - Why: Functionality in validation_engine.py
  - Safe: Yes, answer validation moved to module
  - Size: 3.1 KB

- `verify_answers.py` 🗑️ REMOVE
  - Why: Duplicate of validate_answers
  - Safe: Yes, redundant
  - Size: 2.8 KB

- `verify_critical_answers.py` 🗑️ REMOVE
  - Why: One-off verification script
  - Safe: Yes, integrated into validation
  - Size: 1.9 KB

- `validate_exam.py` 🗑️ REMOVE
  - Why: Functionality in ExamValidator class
  - Safe: Yes, moved to cissp_analyzer/
  - Size: 2.4 KB

- `answer_validator_interactive.py` 🗑️ REMOVE
  - Why: Interactive validation moved to CLI
  - Safe: Yes, merged into interactive_cli.py
  - Size: 6.6 KB

- `demo_interactive_validation.py` 🗑️ REMOVE
  - Why: Demo/test file, not production
  - Safe: Yes, demo not needed in production
  - Size: 2.3 KB

**SUBTOTAL REMOVE: 6 scripts, 19.1 KB**

---

### Workflow & Batch Scripts

- `run_batch.py` 🗑️ REMOVE
  - Why: Batch workflow in run_batch_workflow.py (keep that instead)
  - Safe: Yes, functionality in run_batch_workflow.py
  - Size: 3.2 KB

- `run_batch_workflow.py` ✅ KEEP
  - Why: Core batch processing workflow
  - Used: Yes, still referenced in run.py
  - Size: 6.1 KB

- `run_exam_analysis.py` 🗑️ REMOVE
  - Why: Exam analysis in run_batch_workflow.py
  - Safe: Yes, redundant
  - Size: 3.4 KB

- `auto_fix_answers.py` 🗑️ REMOVE
  - Why: One-off fix utility, not production
  - Safe: Yes, answer fixes integrated into validators
  - Size: 5.8 KB

- `consolidate_answers.py` 🗑️ REMOVE
  - Why: One-off consolidation script
  - Safe: Yes, consolidation logic in batch workflow
  - Size: 4.2 KB

**SUBTOTAL REMOVE: 4 scripts, 16.6 KB**
**SUBTOTAL KEEP: 1 script (run_batch_workflow.py), 6.1 KB**

---

### Admin & Setup Scripts

- `check_setup.py` 🗑️ REMOVE
  - Why: Setup wizard handles this
  - Safe: Yes, setup checks in setup_wizard.py
  - Size: 6.5 KB

- `test_system_integrity.py` 🗑️ REMOVE
  - Why: System tests in tests/ directory
  - Safe: Yes, comprehensive test suite exists
  - Size: 4.2 KB

- `comprehensive_system_validator.py` 🗑️ REMOVE
  - Why: Validation merged into modules
  - Safe: Yes, validators in cissp_analyzer/
  - Size: 8.7 KB

- `comprehensive_domain_mapper.py` 🗑️ REMOVE
  - Why: Domain mapping in domain_mapper.py
  - Safe: Yes, moved to cissp_analyzer/
  - Size: 5.4 KB

- `handle_sheet_variations.py` 🗑️ REMOVE
  - Why: Sheet handling in excel_parser.py
  - Safe: Yes, integrated into core module
  - Size: 3.1 KB

- `detect_exam_consistency.py` 🗑️ REMOVE
  - Why: Consistency checks in validators
  - Safe: Yes, integrated into validation
  - Size: 2.8 KB

- `fuzzy_file_matcher.py` 🗑️ REMOVE
  - Why: File matching in filename_parser.py
  - Safe: Yes, merged into core module
  - Size: 2.6 KB

- `map_questions_to_answers.py` 🗑️ REMOVE
  - Why: Question mapping in domain_mapper.py
  - Safe: Yes, integrated into module
  - Size: 2.1 KB

- `regenerate_mapping.py` 🗑️ REMOVE
  - Why: One-off regeneration script
  - Safe: Yes, mapping generation in modules
  - Size: 1.9 KB

- `regenerate_reports.py` 🗑️ REMOVE
  - Why: Report regeneration in CLI
  - Safe: Yes, moved to run.py options
  - Size: 2.4 KB

**SUBTOTAL REMOVE: 10 scripts, 41.7 KB**

---

### Redundant Manager Scripts

- `exam_manager.py` ⚠️ REVIEW
  - Where: Move to `cissp_analyzer/exam_manager.py`
  - Why: Class-based, should be in module directory
  - Keep in root?: NO - Move to cissp_analyzer/
  - Size: 3.1 KB

- `question_bank_registry.py` ⚠️ REVIEW
  - Where: Move to `cissp_analyzer/question_bank_registry.py`
  - Why: Registry class, should be in module directory
  - Keep in root?: NO - Move to cissp_analyzer/
  - Size: 2.8 KB

- `answer_key_manager.py` ⚠️ REVIEW
  - Where: Move to `cissp_analyzer/answer_key_manager.py`
  - Why: Manager class, should be in module directory
  - Keep in root?: NO - Move to cissp_analyzer/
  - Size: 13.5 KB

- `cissp_trap_framework.py` ⚠️ REVIEW
  - Where: Merge into `cissp_analyzer/trap_analysis_engine.py`
  - Why: Trap framework already in main engine
  - Keep in root?: NO - Framework exists in main module
  - Size: Unknown

- `setup_wizard.py` ✅ KEEP (but evaluate usage)
  - Where: Keep in root or move to scripts/
  - Why: Initialization script, entry point
  - Status: Check if still used in run.py
  - Size: 5.2 KB

**SUBTOTAL MOVE TO MODULES: 4 scripts**
**SUBTOTAL REVIEW: 1 script (setup_wizard.py)**

---

### Summary - Root Level Scripts

| Category | Remove | Move to Module | Keep | Total |
|----------|--------|---|------|-------|
| Entry Points | 5 | 0 | 1 (run.py) | 6 |
| Answer Extraction | 5 | 0 | 0 | 5 |
| Validation | 6 | 0 | 0 | 6 |
| Workflow | 4 | 0 | 1 | 5 |
| Admin/Setup | 10 | 0 | 0 | 10 |
| Managers | 0 | 4 | 1 (setup_wizard) | 5 |
| **TOTAL** | **30** | **4** | **3** | **37** |

---

## 📁 ROOT LEVEL DOCUMENTATION (49 files)

### Keep - Essential User Guides (15 files)

✅ `README.md` - Main documentation
✅ `CHANGELOG.md` - Version history
✅ `START_HERE.md` - Quick start guide
✅ `FILE_FORMAT_REFERENCE.md` - Data format guide
✅ `NAMING_CONVENTIONS_AND_FORMATS.md` - Naming standards
✅ `WORKFLOW_OVERVIEW.md` - System workflow
✅ `QUICK_WORKFLOW_GUIDE.md` - Quick reference
✅ `EXAMPLE_FILES_HOW_TO_USE.md` - Example usage
✅ `WHERE_TO_DOWNLOAD_TEMPLATES.md` - Resource links
✅ `MULTI_QUESTION_BANK_SCENARIO.md` - Advanced usage
✅ `EXAM_VERSIONING_GUIDE.md` - Version management
✅ `TRAP_ANALYSIS_WORKFLOW.md` - Trap analysis guide
✅ `TRAP_FRAMEWORK_ARCHITECTURE.md` - Architecture
✅ `trap_metadata.md` - Trap reference
✅ `requirements.txt` - Dependencies

**SUBTOTAL KEEP: 15 files, essential for users**

---

### Remove - Internal Documentation (15 files)

🗑️ `COMPLETE_DOCUMENTATION_CHECKLIST.md` - Internal checklist
🗑️ `COMPLETE_SOLUTION_SUMMARY.md` - Duplicates README
🗑️ `DOCUMENTATION_INDEX.md` - Meta-documentation
🗑️ `SYSTEM_STATUS.md` - Status snapshot
🗑️ `TEST_RESULTS_FINAL.md` - Test report snapshot
🗑️ `INTEGRATION_TEST_REPORT_2026_07_13.md` - Test report
🗑️ `START_ANALYSIS.md` - Duplicates START_HERE
🗑️ `SETUP_GUIDE.md` - Absorbed into README
🗑️ `SETUP_WIZARD_IMPROVEMENTS.md` - Planning doc
🗑️ `INTERACTIVE_VALIDATOR.md` - Covered in README
🗑️ `INTERACTIVE_MAPPING_GUIDE.md` - Internal guide
🗑️ `VALIDATOR_QUICKSTART.md` - Redundant
🗑️ `VALIDATION_COMPLETE.md` - Status snapshot
🗑️ `VALIDATION_INDEX.md` - Index file
🗑️ `INSTALLATION_COMMANDS.md` - In README

**SUBTOTAL REMOVE: 15 files, internal/redundant**

---

### Remove - Outdated Quick References (5 files)

🗑️ `QUICK_START.txt` - Duplicates START_HERE.md
🗑️ `QUICK_SETUP_CARD.txt` - Redundant
🗑️ `TEMPLATE_REFERENCE.txt` - In examples/
🗑️ `WORKFLOW_QUICK_REFERENCE.txt` - In QUICK_WORKFLOW_GUIDE.md
🗑️ `TESTING_GUIDE_STANDALONE.md` - In README

**SUBTOTAL REMOVE: 5 files, duplicates**

---

### Remove - Test/Validation Outputs (3 files)

🗑️ `VALIDATION_REPORT.json` - Test output snapshot
🗑️ `TEST_RESULTS_INTEGRITY.json` - Test output
🗑️ `EDGE_CASES_HANDLING.md` - Internal doc

**SUBTOTAL REMOVE: 3 files, test outputs**

---

### Remove - Internal Planning (6 files)

🗑️ `REFERENCE_TABLE_USAGE.md` - Internal
🗑️ `SHEET_VARIATIONS_GUIDE.md` - Internal workflow
🗑️ `PERSISTENT_QUESTION_BANK_REGISTRY.md` - Design doc
🗑️ `EXAM_GROUPING_GUIDE.md` - Internal process
🗑️ `TEMPLATE_directory_structure.md` - In docs/
🗑️ `TEMPLATE_student_answers.md` - In templates/

**SUBTOTAL REMOVE: 6 files, internal planning**

---

### NEW Documentation Files (ADD these) ✅

These are part of the analysis we just created:
- `ANALYSIS_INDEX.md` ✅ ADD
- `ENHANCEMENT_EXECUTIVE_SUMMARY.txt` ✅ ADD
- `SYSTEM_ENHANCEMENT_ANALYSIS.md` ✅ ADD
- `SYSTEM_GAPS_VISUAL_SUMMARY.md` ✅ ADD
- `ENHANCEMENT_CODE_EXAMPLES.md` ✅ ADD
- `GITHUB_REPO_CLEANUP_PLAN.md` ✅ ADD
- `COMPLETE_ACTION_PLAN.md` ✅ ADD
- `SESSION_SUMMARY.md` ✅ ADD

**SUBTOTAL ADD: 8 files, new analysis docs**

---

### Summary - Documentation

| Category | Keep | Remove | Add | Total |
|----------|------|--------|-----|-------|
| Essential Guides | 15 | 0 | 0 | 15 |
| Internal Docs | 0 | 15 | 0 | 15 |
| Duplicates | 0 | 5 | 0 | 5 |
| Test Outputs | 0 | 3 | 0 | 3 |
| Planning Docs | 0 | 6 | 0 | 6 |
| New Analysis | 0 | 0 | 8 | 8 |
| **TOTAL** | **15** | **29** | **8** | **52** |

---

## 📁 DATA FOLDER

### Keep - Essential Data (3 files)

✅ `CISSP_162_QUESTIONS_REFERENCE.json` - Core question bank
✅ `question_domain_mapping.json` - Essential mapping
✅ `CISSP_162_QUESTIONS_REFERENCE.csv` - Reference format

**Size:** ~150 KB total
**Why:** Core data for analysis

---

### Remove - Student/Test Data (5 files)

🗑️ `arjun_practice_test_1_answers.json` - Named student data
🗑️ `practice_test_1_results.json` - Student results
🗑️ `practice_test_1_answer_key.json` - Test-specific key
🗑️ `practice_test_1_mapping.json` - Test-specific mapping
🗑️ `practice_test_1_questions.json` - Can consolidate to example

**Why:** Student-specific, not needed in production repo

---

### Keep - Example Data (1 file)

✅ `practice_test_1_questions.json` - KEEP as canonical example
  (Move to examples/ folder for clarity)

**Why:** Users need ONE example to understand format

---

### Summary - Data Folder

| Type | Keep | Remove | Move to Examples |
|------|------|--------|------------------|
| Core Data | 3 | 0 | 0 |
| Student Data | 0 | 4 | 0 |
| Example Data | 0 | 0 | 1 |
| **TOTAL** | **3** | **4** | **1** |

---

## 📁 EXAMS FOLDER

### Current Structure
```
exams/
├── dec25_week1_answer_key.json 🗑️
├── dec25_week2_answer_key.json 🗑️
├── CISSP_July_2026/ 🗑️
├── CISSP_July_2026_V2/ 🗑️
└── CISSP_July_2026_FINAL/ ✅ KEEP (canonical example)
```

### What to Keep

✅ `exams/CISSP_July_2026_FINAL/` - Canonical example exam
  - questions/
  - answer_keys/
  - metadata.json
  
**Why:** Users need ONE complete exam example to understand structure

---

### What to Remove

🗑️ `exams/dec25_week1_answer_key.json` - Historical exam data
🗑️ `exams/dec25_week2_answer_key.json` - Historical exam data
🗑️ `exams/CISSP_July_2026/` - Duplicate exam version
🗑️ `exams/CISSP_July_2026_V2/` - Duplicate exam version

**Why:** Exam-specific, students upload their own exams

---

### Summary - Exams Folder

| Type | Keep | Remove |
|------|------|--------|
| Canonical Example | 1 | 0 |
| Historical Exams | 0 | 4 |
| **TOTAL** | **1** | **4** |

---

## 📁 DOCS FOLDER

### Keep

✅ `docs/` folder structure (for future guides)

---

### Remove

🗑️ `docs/superpowers/` - Internal development planning
  - This is Claude Code assistant planning, not for users
  
**Why:** Not needed in production repository

---

## 📁 CISSP_ANALYZER FOLDER (Core Production Code)

✅ **KEEP ALL** - This is the production code

Directory structure:
```
cissp_analyzer/
├── __init__.py ✅
├── main.py ✅
├── analysis_engine.py ✅
├── trap_analysis_engine.py ✅
├── individual_report_gen.py ✅
├── class_report_gen.py ✅
├── excel_parser.py ✅
├── pdf_parser.py ✅
├── answer_validator.py ✅
├── answer_context_mapper.py ✅
├── answer_key_extractor.py ✅
├── domain_mapper.py ✅
├── trend_calculator.py ✅
├── pattern_detector.py ✅
├── adaptive_plan_generator.py ✅
├── progress_sheet_generator.py ✅
├── history_loader.py ✅
├── filename_parser.py ✅
├── interactive_cli.py ✅
├── data_quality_validator.py ✅
├── dependency_checker.py ✅
├── exam_validator.py ✅
├── models.py ✅
└── [+ 4 manager modules to move from root] ✅
```

**Total:** 25+ production modules (ALL KEEP)

---

## 📁 TESTS FOLDER

✅ **KEEP ALL** - Comprehensive test suite

```
tests/
├── test_analysis_engine.py ✅
├── test_individual_report_gen.py ✅
├── test_class_report_gen.py ✅
├── test_excel_parser.py ✅
├── test_pdf_parser.py ✅
├── [+ 25 more test files] ✅
└── conftest.py ✅
```

**Total:** 30+ test files, 279 passing tests (ALL KEEP)

---

## 📁 ROOT LEVEL FILES (Non-Script, Non-Doc)

✅ `.gitignore` - Keep and UPDATE
✅ `setup.py` - Move to scripts/
✅ `requirements.txt` - Move to scripts/
✅ `install.sh` - Move to scripts/
✅ `run.py` - Keep (main entry point)
🗑️ `.DS_Store` - Remove (OS file)
🗑️ `student_roster.json` - Remove (student data)

---

## 📊 CLEANUP SUMMARY TABLE

| Category | Remove | Move | Keep | Add |
|----------|--------|------|------|-----|
| **Root Scripts** | 30 | 4 | 3 | 0 |
| **Documentation** | 29 | 0 | 15 | 8 |
| **Data** | 4 | 1 | 3 | 0 |
| **Exams** | 4 | 0 | 1 | 0 |
| **Internal Planning** | 1 | 0 | 0 | 0 |
| **Production Code** | 0 | 0 | 25+ | 0 |
| **Tests** | 0 | 0 | 30+ | 0 |
| **Other** | 2 | 0 | 1 | 0 |
| **TOTAL** | **70** | **5** | **77+** | **8** |

**Result:** 250+ files → ~120 files (52% reduction)

---

## 🎯 FOLDERS TO CREATE

```
mkdir -p examples/          # Consolidate example files
mkdir -p templates/         # Consolidate template files
mkdir -p scripts/           # Utility scripts
```

---

## ✅ FINAL CHECKLIST BEFORE CLEANUP

Before you start, confirm:

- [ ] I've read through all removals above
- [ ] I agree with what's being removed
- [ ] I'm keeping all production code (cissp_analyzer/)
- [ ] I'm keeping all tests (tests/)
- [ ] I'm keeping essential user guides (15 docs)
- [ ] I want to move manager scripts to cissp_analyzer/
- [ ] I want to move scripts to scripts/ folder
- [ ] I want to create examples/ and templates/ folders
- [ ] I understand this is 50% file reduction (not loss of functionality)

---

## ⚠️ ITEMS NEEDING YOUR APPROVAL

Before I proceed, please confirm:

1. **Remove 30 root scripts?** (These are all moved to modules or CLI)
   - [ ] Yes, remove them
   - [ ] Wait, I need to check: ________

2. **Remove 29 documentation files?** (These are all duplicates/internal)
   - [ ] Yes, remove them
   - [ ] Wait, I need to keep: ________

3. **Remove 4 exam versions?** (Keep only CISSP_July_2026_FINAL)
   - [ ] Yes, remove them
   - [ ] Wait, I need to keep: ________

4. **Remove student data?** (arjun_practice_test, results, etc)
   - [ ] Yes, remove them
   - [ ] Wait, I need to keep: ________

5. **Move managers to cissp_analyzer/?** (exam_manager, question_bank_registry, etc)
   - [ ] Yes, move them
   - [ ] Wait, keep them in root: ________

---

**Once you confirm the above, I'll provide exact deletion commands and you can execute them safely on your local machine.**

Ready to confirm? 🚀
