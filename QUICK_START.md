# CISSP Analyzer - Quick Start Guide

Get up and running in 2 minutes with automatic dependency installation.

## 30-Second Setup

```bash
# 1. Download/clone the project
cd cissp-analyzer

# 2. Run automated installer (handles ALL dependencies)
chmod +x install.sh
./install.sh

# 3. Start analyzing exams
python3 setup.py
```

That's it! The installer automatically:
- ✓ Verifies Python 3.9+
- ✓ Installs all required packages (openpyxl, pandas, pypdf)
- ✓ Verifies installation
- ✓ Shows dependency status

---

## What Happens After Setup?

The interactive setup wizard will guide you through:

1. **Exam PDF** - Path to your CISSP exam questions PDF
2. **Answer Key** - JSON file with correct answers (optional)
3. **Output Directory** - Where to save analysis reports
4. **Students** - Add each student's name and Excel answer file

Then it generates:
- Individual performance reports (.xlsx)
- Class analysis summary (.xlsx)
- Progress tracking with historical trends
- Adaptive study recommendations

---

## Manual Installation (If Not Using Script)

```bash
# Option A: Install from requirements.txt
pip install -r requirements.txt

# Option B: Install specific packages
pip install openpyxl pandas pypdf

# Option C: Install package with dependencies
pip install -e .
```

---

## Verify Installation

```bash
# Quick test
python3 -c "from cissp_analyzer import CISSPAnalyzer; print('✓ Ready to go!')"

# Detailed status
python3 -m cissp_analyzer.dependency_checker

# Run test suite
pytest tests/ -v
```

---

## Troubleshooting

### "Python 3.9 or higher required"
```bash
# Install latest Python from https://www.python.org/downloads/
python3 --version  # Should show 3.9+
```

### "pip: command not found"
```bash
# Use pip3 instead
pip3 install -r requirements.txt
```

### "Missing dependency: openpyxl"
```bash
# Reinstall all dependencies
pip install -r requirements.txt
```

### Tests fail after installation
```bash
# Verify all dependencies
python3 -m cissp_analyzer.dependency_checker

# If issues persist, create fresh environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Next Steps

1. **Prepare your files:**
   - CISSP mock exam PDF
   - Student answer Excel files
   - Answer key (JSON or auto-extract)

2. **Run interactive setup:**
   ```bash
   python3 setup.py
   ```

3. **Check outputs:**
   - Individual reports in `outputs/`
   - Class analysis summary
   - Historical trends (if multiple exams)

4. **Review results:**
   - Open .xlsx files in Excel/Sheets
   - Identify weak domains
   - Track progress over exams

---

## Key Features

- **Multi-Exam Tracking** - Analyze performance across unlimited exams
- **Progress Visualization** - See trends in domains, difficulty, question types
- **Adaptive Recommendations** - Momentum-based study suggestions
- **Class Analytics** - Class-level performance summaries
- **Automatic Dependency Management** - Zero friction setup
- **100% Test Coverage** - 73+ tests validate correctness

---

## File Structure

```
cissp-analyzer/
├── cissp_analyzer/           # Main package
│   ├── main.py              # Orchestrator
│   ├── pdf_parser.py        # PDF extraction
│   ├── excel_parser.py      # Answer parsing
│   ├── analysis_engine.py   # Scoring logic
│   ├── trend_calculator.py  # Progress tracking
│   └── dependency_checker.py # Automatic dependency validation
├── data/                     # Question mappings
├── tests/                    # Test suite (73+ tests)
├── requirements.txt          # All dependencies listed
├── install.sh               # Automated installer
└── setup.py                 # Interactive wizard
```

---

## Support

- **Installation issues:** See INSTALLATION.md
- **Usage questions:** Check README.md
- **Test coverage:** 73 tests, all passing
- **Dependencies:** Automatically managed and validated

---

**Ready to analyze CISSP exams? Run `./install.sh` now!**

*Version 1.0.0 | Last Updated: 2026-07-01*
