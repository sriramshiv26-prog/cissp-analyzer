# Quick Installation & Setup Commands

**Choose your platform below:**

---

## 🍎 macOS & Linux

```bash
# 1. Clone repository
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation (run tests)
pytest -v

# 6. Run the tool
python3 analyze.py
```

**Expected Output:**
```
✓ pytest shows "277 passed"
✓ analyze.py shows interactive menu
```

---

## 🪟 Windows (Command Prompt)

```bash
# 1. Clone repository
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation (run tests)
pytest -v

# 6. Run the tool
python analyze.py
```

**Expected Output:**
```
✓ pytest shows "277 passed"
✓ analyze.py shows interactive menu
```

---

## 🐧 Windows (PowerShell)

```powershell
# 1. Clone repository
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git
cd cissp-analyzer

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation (run tests)
pytest -v

# 6. Run the tool
python analyze.py
```

---

## ⚡ Quick Copy-Paste (macOS/Linux)

```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git && \
cd cissp-analyzer && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt && \
pytest -v && \
echo "✅ Setup complete! Run: python3 analyze.py"
```

---

## ⚡ Quick Copy-Paste (Windows CMD)

```bash
git clone https://github.com/sriramshiv26-prog/cissp-analyzer.git && cd cissp-analyzer && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && pytest -v && echo ✅ Setup complete! Run: python analyze.py
```

---

## 📋 What Each Command Does

| Command | Purpose | Platform |
|---------|---------|----------|
| `git clone ...` | Download code | All |
| `cd cissp-analyzer` | Enter directory | All |
| `python -m venv venv` | Create environment | All |
| `source venv/bin/activate` | Activate (macOS/Linux) | macOS/Linux |
| `venv\Scripts\activate` | Activate (Windows CMD) | Windows CMD |
| `venv\Scripts\Activate.ps1` | Activate (Windows PS) | Windows PowerShell |
| `pip install -r requirements.txt` | Install dependencies | All |
| `pytest -v` | Run 277 tests (verify) | All |
| `python3 analyze.py` | Run the tool | macOS/Linux |
| `python analyze.py` | Run the tool | Windows |

---

## ✅ Verification Steps

After running all commands, you should see:

### 1. After `pytest -v`:
```
================================ test session starts =================================
collected 281 items

tests/test_adaptive_plan_generator.py::test_generate_study_plan_sheet PASSED  [  0%]
tests/test_analysis_engine.py::test_evaluate_answers_senthil PASSED            [  1%]
... (many more tests)

================================ 277 passed in 9.60s ==================================
```

**What this means:** ✅ All dependencies installed correctly

### 2. After `python3 analyze.py`:
```
================================================================================
CISSP ANALYZER - MAIN MENU
================================================================================

Select Analysis Mode:
  [1] Batch Analysis (Multiple students in cohort)
  [2] Standalone Analysis (Individual student)

Enter choice (1 or 2):
```

**What this means:** ✅ Tool is ready to use

---

## 🆘 Troubleshooting

### Problem: "python not found"
**Solution:**
```bash
# Try python3 instead
python3 -m venv venv
python3 -m pip install -r requirements.txt
python3 analyze.py
```

### Problem: "Permission denied" (macOS/Linux)
**Solution:**
```bash
chmod +x analyze.py
python3 analyze.py
```

### Problem: "No module named pytest"
**Solution:**
```bash
pip install -r requirements.txt
pytest -v  # Try again
```

### Problem: Virtual environment not activating
**Windows:**
```bash
# Make sure you're in the project directory
cd cissp-analyzer
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd cissp-analyzer
source venv/bin/activate
```

---

## 📊 Installation Time

| Step | Time |
|------|------|
| Clone repo | ~30 seconds |
| Create venv | ~5 seconds |
| Install deps | ~1-2 minutes |
| Run tests | ~10 seconds |
| **TOTAL** | **~2-3 minutes** |

---

## 🎯 Next Steps (After Successful Setup)

Once you see the interactive menu, you can:

### Option 1: Try with Example Files
```bash
# The tool includes example files:
# - EXAMPLE_answer_key.json (30 sample questions)
# - EXAMPLE_student_answers.xlsx (4 students, 20 questions)

# Use these to test before using real data
```

### Option 2: Read the Guide
```bash
# Print the quick reference card
cat QUICK_SETUP_CARD.txt

# Or read the complete guide
cat FORMATS_AND_TEMPLATES_GUIDE.md
```

### Option 3: Start Analysis
```bash
# Follow the interactive prompts
# Provide your exam PDF, answer key, and student responses
```

---

## 💡 Pro Tips

**Tip 1: Reuse Virtual Environment**
```bash
# After first setup, just do:
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# No need to recreate!
```

**Tip 2: Keep Requirements Updated**
```bash
# If requirements.txt changes:
pip install -r requirements.txt --upgrade
```

**Tip 3: Check Python Version**
```bash
python3 --version  # Should be 3.9+
```

---

## ✅ Success Checklist

After running all commands:

- [ ] `git clone` - Code downloaded
- [ ] `cd cissp-analyzer` - In correct directory
- [ ] `python -m venv venv` - Virtual environment created
- [ ] `source/venv\Scripts\activate` - Environment activated
- [ ] `pip install -r requirements.txt` - Dependencies installed
- [ ] `pytest -v` - 277 tests passed
- [ ] `python analyze.py` - Tool starts successfully
- [ ] See interactive menu - Ready to use!

---

## 🚀 You're Ready!

Once all commands complete successfully, you can:

✅ Run analyses on CISSP exams  
✅ Get professional 7-sheet reports  
✅ Track student performance across 5 dimensions  
✅ Generate adaptive study recommendations  
✅ Process batch exams for entire classes  

---

**Version:** 1.0 | **Date:** July 5, 2026 | **Status:** Production Ready
