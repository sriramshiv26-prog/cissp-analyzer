# Installation Guide

Complete step-by-step setup for **Windows**, **Mac**, or **Linux**.

---

## Prerequisites

- **Python 3.11 or higher** (download from https://www.python.org/downloads/)
- **Git** (to clone the repository)
- **Internet connection** (to download dependencies)

---

## Installation Steps (All Platforms)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer
```

### Step 2: Create Virtual Environment (Optional but Recommended)

**Why?** Keeps dependencies isolated from your system Python.

#### Mac / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows (Command Prompt):
```bash
python -m venv venv
venv\Scripts\activate
```

#### Windows (PowerShell):
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
pytest -v
```

Expected output:
```
=============================== test session starts =======================================
collected 29 items

tests/test_analysis_engine.py::test_evaluate_answers_senthil PASSED               [  3%]
...
================================ 26 passed, 3 skipped ===================================
```

✅ **Installation successful!** You're ready to use CISSP Analyzer.

---

## Platform-Specific Setup

### macOS

**Requirements:** Python 3.11+, Homebrew (optional)

```bash
# Using Homebrew (optional, if not already installed)
brew install python@3.11

# Clone and setup
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
pytest -v
```

### Windows

**Requirements:** Python 3.11+

```bash
# Download Python from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Open Command Prompt or PowerShell
cd your-download-folder

# Clone repository
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Command Prompt:
venv\Scripts\activate
# OR on PowerShell:
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify
pytest -v
```

**Troubleshooting Windows:**
- If `python` command not found, try `python3`
- If PowerShell scripts disabled: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Linux (Ubuntu/Debian)

**Requirements:** Python 3.11+

```bash
# Install Python and pip (if not already installed)
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# Clone repository
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
pytest -v
```

### Linux (Fedora/RHEL)

```bash
# Install Python
sudo dnf install python3.11 python3.11-devel

# Clone repository
git clone https://github.com/yourusername/cissp-analyzer.git
cd cissp-analyzer

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
pytest -v
```

---

## Verify Installation

Run this command to confirm everything works:

```bash
python3 -c "
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.analysis_engine import AnalysisEngine
mapper = DomainMapper('data/question_domain_mapping.json')
engine = AnalysisEngine(mapper)
print('✓ Installation successful!')
"
```

Expected output:
```
✓ Installation successful!
```

---

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Problem: "Python command not found"

**Solution:** Check your Python version
```bash
python3 --version  # or python --version
```

If neither works, install Python 3.11+:
- **Mac:** `brew install python@3.11`
- **Windows:** Download from https://www.python.org/downloads/
- **Linux:** `sudo apt-get install python3.11`

### Problem: "pytest command not found"

**Solution:** Install it manually
```bash
pip install pytest
```

### Problem: Virtual environment not activating (Windows)

**Solution:** If PowerShell gives execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### Problem: Permission denied on macOS/Linux

**Solution:** Add execute permission
```bash
chmod +x run.py
```

---

## Next Steps

Once installation is complete:

1. **Read** [QUICKSTART.md](QUICKSTART.md) to learn how to run the program
2. **Prepare** your exam PDF and student answer Excel file
3. **Generate** your first report!

---

## Need Help?

- Check the [README.md](README.md) for overview
- Review test files in `tests/` for usage examples
- Open an issue on GitHub with your problem

---

**Happy analyzing!**
