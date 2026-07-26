# Changelog

All notable changes to the CISSP Analyzer project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-07-25

### Added: Metadata Auto-Generator Feature (Tasks 1-11)

#### New Modules
- **`cissp_analyzer/metadata_reviewer.py`** — Terminal display and inline editing of metadata
  - `MetadataReviewer.display_summary()`: formatted table (first 20 rows + totals)
  - `MetadataReviewer.edit_question()`: update a single field, tracked in `self.edited`
  - `MetadataReviewer.get_reviewed_metadata()`: returns metadata with all edits applied
  - `MetadataReviewer.get_edit_summary()`: reports N questions edited + field breakdown

- **`cissp_analyzer/ollama_analyzer.py`** — Optional Ollama enrichment with runtime detection
  - Auto-detects if Ollama is running (GET /api/tags, 2s timeout)
  - Classifies questions by domain, topic, difficulty, and question_type
  - Batch analysis: `analyze_batch({q_num: q_text})` → `{q_num_str: metadata}`
  - Graceful fallback: returns `None` / empty dict when Ollama is unavailable
  - Default model: `qwen2.5-coder:7b`

- **`cissp_analyzer/metadata_generator.py`** — Full pipeline orchestrator
  - `MetadataGenerator(exam_id, pdf_path, output_dir)` wires all modules together
  - `run(completion_method="auto")`: Extract → Complete → Review → Store
  - Saves to `data/metadata/YYYY-MM-DD/{exam_id}/metadata.json`
  - Returns coverage metrics, method used, and output path

#### Modified Modules
- **`cissp_analyzer/exam_processor.py`** — Added optional metadata generation
  - `process_new_files(generate_metadata=False)`: new optional parameter
  - When `True`, calls `MetadataGenerator` after processing answer sheets
  - Fully backward compatible — existing callers unaffected
  - `_run_metadata_generation()`: internal helper, graceful error handling

- **`cissp_analyzer/menu_controller.py`** — New "Generate Metadata" menu option
  - `show_generate_metadata_menu()`: interactive wizard (exam_id + PDF path)
  - Displays result summary (coverage, method, output path) after generation
  - `_build_metadata_generator()`: factory method for testability

#### New Tests (Tasks 4-9)
- `tests/test_metadata_reviewer.py` — 24 tests for MetadataReviewer
- `tests/test_ollama_analyzer.py` — 16 tests for OllamaAnalyzer (all HTTP mocked)
- `tests/test_metadata_generator.py` — 13 tests for MetadataGenerator
- `tests/test_metadata_integration.py` — 8 end-to-end pipeline integration tests
- `tests/test_exam_processor_metadata.py` — 6 tests for ExamProcessor hook
- `tests/test_menu_controller_metadata.py` — 8 tests for MenuController menu option

#### Documentation
- `docs/METADATA_GENERATOR_GUIDE.md` — User guide for the full feature
- `DOCUMENTATION_INDEX.md` — Updated with v2.1.0 Metadata Auto-Generator section
- `CHANGELOG.md` — This entry

### Previously Complete (Tasks 1-3)
- `cissp_analyzer/domain_mapper.py` — exam_id parameter for per-exam metadata loading
- `cissp_analyzer/pdf_metadata_extractor.py` — PDF tag extraction
- `cissp_analyzer/metadata_completer.py` — Gap-filling via defaults, manual CSV, or Ollama

---

## [1.0.1] - 2026-07-13

### ✨ Added (Major Features)

#### Question Bank Registry (Multi-Week Persistence)
- **question_bank_registry.py** - Persistent catalog of question bank PDFs
  - Register question banks once, remember them forever
  - Auto-suggest matching question banks when new answer sheets arrive
  - Fingerprinting system (file hash) to identify PDFs uniquely
  - Track usage history (which batches used which PDFs)
  - Find PDF details with complete audit trail
  - Supports 3+ to 10+ different question banks

#### Fuzzy File Matching (Flexible Filename Handling)
- **fuzzy_file_matcher.py** - Flexible filename similarity matching
  - Match filenames despite typos (Jul12 = july12 = JULY12)
  - Detect version patterns (v1, v2, practice, full)
  - 60-75% similarity threshold
  - Normalize filenames automatically
  - Handle special characters and spaces

#### Interactive Question Bank Mapper (Explicit Confirmation)
- **map_questions_to_answers.py** - Step-by-step PDF to answer sheet mapping
  - Interactive wizard for user confirmation
  - Auto-suggestions based on filename matching
  - Auto-match mode for unambiguous cases
  - Create audit trail of associations
  - Support multiple PDFs in single batch
  - Save mapping to JSON manifest file

#### Sheet Variation Detection (Excel Flexibility)
- **handle_sheet_variations.py** - Handle different Excel sheet naming patterns
  - Auto-detect answer sheet names (Answers, Sheet1, StudentName, etc.)
  - Normalize column headers
  - Check batch consistency
  - Fallback mechanisms for edge cases

#### Exam Consistency Checking (Quality Assurance)
- **detect_exam_consistency.py** - Verify answer sheets match question banks
  - Extract exam signatures (question count, content hash)
  - Group sheets by exam
  - Detect multiple question banks in single batch
  - Prevent analysis of mismatched sheets
  - Create manifest files for audit trail

### 📚 Documentation (Comprehensive Guides)

#### New Onboarding Guides
- **START_HERE.md** - Complete journey from Day 1 setup through ongoing use
  - Answers key user question: "Do I need to repeat setup commands?"
  - Day 1: One-time setup (5-10 minutes)
  - Week 1-4: Progression with real-world timelines
  - Ongoing: Simple 2-command activation workflow
  - Quick reference cheat sheet
  - Troubleshooting section

- **QUICK_WORKFLOW_GUIDE.md** - First-time setup vs subsequent usage
  - Comparison table: first time vs recurring
  - When to re-run setup
  - Daily workflow examples
  - Bash alias for faster activation

#### New Feature Guides
- **PERSISTENT_QUESTION_BANK_REGISTRY.md** - Multi-week upload scenario
  - How registry works
  - Real-world timeline examples
  - Usage history tracking
  - Integration with other tools

- **MULTI_QUESTION_BANK_SCENARIO.md** - Handling 3+ to 10+ different question banks
  - Perfect use case documentation
  - Real workflow with 6 question banks
  - Automatic separation demonstration
  - Registry benefits comparison

- **COMPLETE_SOLUTION_SUMMARY.md** - All 6 layers working together
  - 6-layer validation pipeline diagram
  - Tools & commands reference
  - Real-world timeline (Month 1-12)
  - Complete workflow automation

- **INTERACTIVE_MAPPING_GUIDE.md** - PDF to answer sheet mapping
  - Interactive wizard walkthrough
  - Auto-match feature explanation
  - Audit trail creation

### 🧪 Testing

- Added comprehensive tests for question bank registry
- Added fuzzy matching algorithm tests
- Added sheet variation detection tests
- Added exam consistency checking tests
- Added interactive mapper tests
- **Total tests:** 279 passing (up from 277)
- **Test coverage:** 100% for new modules

### 📊 Improvements

- Enhanced README with v1.0.1 feature highlights
- Updated version information in all references
- Updated test statistics (277 → 279)
- Updated last modified date (July 5 → July 13, 2026)
- Expanded documentation index
- Added new tools to CLI help

### 🔄 Integration

- Integrated all 5 new modules into main workflow
- Updated analyze.py to support new features
- Updated interactive CLI with new options
- Backward compatible with v1.0.0

---

## [1.0.0] - 2026-07-04

### ✨ Added (Initial Release)

#### Core Analysis Features
- Professional CISSP exam analysis with 7-sheet reports
- Single exam analysis (Standalone mode)
- Comparative analysis with history (Progress tracking)
- Batch analysis for multiple students
- Color-coded results by domain, difficulty, topic

#### Report Generation (7 Sheets)
1. Performance Summary
2. Q&A Breakdown
3. By Question Type
4. By Exam Tricks
5. By Domain
6. By Difficulty
7. Study Plan (adaptive recommendations)

#### Analysis Dimensions
- Domain analysis (8 CISSP domains)
- Topic analysis (20+ topics)
- Difficulty levels (Easy/Medium/Hard)
- Question types (Definition, Application, Scenario, Exception, Sequence)
- Exam tricks (MOST, BEST, FIRST, NOT, EXCEPT keywords)

#### Input Flexibility
- Multiple PDF formats supported
- Multiple Excel formats supported
- JSON answer key support
- CSV answer key support
- UTF-8 and special characters handling
- Flexible student name formats

#### Entry Points
- `analyze.py` - Main interactive CLI
- `analyze_standalone.py` - Standalone analysis
- `analyze_dec25.py` - Pre-configured Dec-25 batch
- `analyze_july26.py` - Pre-configured July-26 batch

#### Documentation (14 Guides)
- Installation guides (platform-specific)
- Setup guides
- Format and template guides
- Quick reference cards
- Troubleshooting guides
- Complete documentation index

#### Testing
- 277 comprehensive tests
- Environment validation
- Error handling for 15+ scenarios
- Performance benchmarks
- Integration tests

---

## Version History

| Version | Release Date | Status | Key Addition |
|---------|---|---|---|
| **1.0.1** | Jul 13, 2026 | Production | Multi-Question Bank Management |
| **1.0.0** | Jul 4, 2026 | Production | Initial Release |

---

## Roadmap (Future)

### Version 1.1 (Planned)
- [ ] Web dashboard for real-time analytics
- [ ] API server for remote analysis
- [ ] Database backend for large-scale deployments
- [ ] Mobile app for report viewing
- [ ] Advanced ML-based recommendations

### Version 1.2 (Planned)
- [ ] Integration with learning management systems (LMS)
- [ ] Multi-language support
- [ ] Custom question bank configuration
- [ ] Team collaboration features
- [ ] Advanced scheduling for batch analysis

---

## Support

- 📖 See [START_HERE.md](START_HERE.md) for complete onboarding
- 📖 See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for all guides
- 🐛 Open an issue on GitHub for bug reports
- 💡 Suggest features by opening a GitHub discussion

---

## License

MIT License - Free to use for any purpose
