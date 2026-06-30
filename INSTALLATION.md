# CISSP Analyzer - Installation Guide

## Prerequisites

Before installing CISSP Analyzer, ensure you have:
- **Python 3.9 or higher** ([download](https://www.python.org/downloads/))
- **pip** (included with Python)
- **git** (optional, for cloning the repository)

### Verify Prerequisites

```bash
# Check Python version
python3 --version

# Check pip
pip3 --version
```

Both should return version information without errors.

---

## Installation Methods

### Method 1: Automated Installation (Recommended)

The easiest way to install CISSP Analyzer with all dependencies.

```bash
# Make install script executable
chmod +x install.sh

# Run the installer
./install.sh
```

The script will:
- ✓ Verify Python 3.9+ is installed
- ✓ Upgrade pip to the latest version
- ✓ Optionally create a virtual environment
- ✓ Install all required dependencies
- ✓ Install CISSP Analyzer package
- ✓ Verify the installation

---

### Method 2: Manual Installation

If you prefer manual control over the installation process:

#### Step 1: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install specific packages
pip install openpyxl pandas pypdf
```

#### Step 3: Install CISSP Analyzer

```bash
# Install in development mode (recommended for development)
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Or standard installation
pip install .
```

---

### Method 3: Using setup.py

```bash
# Install directly
python3 -m pip install -e .

# With all development tools
python3 -m pip install -e ".[dev]"
```

---

## Verify Installation

### Quick Verification

```bash
python3 -c "from cissp_analyzer import CISSPAnalyzer; print('✓ CISSP Analyzer installed successfully')"
```

### Detailed Status Report

```bash
# View dependency status
python3 -m cissp_analyzer.dependency_checker

# Or in Python:
from cissp_analyzer.dependency_checker import print_dependency_status
print_dependency_status()
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_trend_calculator.py -v

# Run with coverage report
pytest tests/ --cov=cissp_analyzer
```

---

## Troubleshooting

### Issue: "Python 3.9 or higher required"

Install latest Python from https://www.python.org/downloads/

### Issue: "pip command not found"

Use `pip3 install` or `python3 -m pip install`

### Issue: Virtual environment conflicts

Create a fresh virtual environment and reinstall dependencies

### Issue: "ModuleNotFoundError: No module named 'openpyxl'"

Run: `pip install -r requirements.txt`

---

## Next Steps

After installation, run the interactive setup wizard:

```bash
python3 setup.py
```

This will guide you through configuring your exam analysis.

**Version:** 1.0.0  
**Last Updated:** 2026-07-01
