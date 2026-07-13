# Quick Workflow Guide - First Time vs Subsequent Times

**TL;DR:** Setup once. After that, just activate the environment and run commands. Takes 30 seconds.

---

## FIRST TIME SETUP (One Time Only)

This is the complete installation:

```bash
# Step 1: Clone/enter project directory
cd /Users/sriram/cissp-analyzer

# Step 2: Create virtual environment (Python isolation)
python3 -m venv venv

# Step 3: Activate virtual environment
source venv/bin/activate

# Step 4: Install all dependencies
pip install -r requirements.txt

# Step 5: Verify installation (optional)
pytest -v  # Should show 277+ tests passing

# You're done! Everything is installed.
```

**Time:** ~5-10 minutes  
**Frequency:** Once per machine/installation

---

## SUBSEQUENT TIMES (Months 2+)

Much simpler! You just need 2 commands:

```bash
# Step 1: Go to project directory
cd /Users/sriram/cissp-analyzer

# Step 2: Activate virtual environment
source venv/bin/activate

# That's it! Now run your commands:
python3 question_bank_registry.py --find-matches july26
python3 map_questions_to_answers.py --batch july26
python3 analyze.py
```

**Time:** ~30 seconds  
**Frequency:** Every time you use the analyzer

---

## Daily Workflow (After Setup)

### **Start of Work Day:**
```bash
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

# You're ready! (venv is now active - notice terminal shows "(venv)")
```

### **Use the Tools:**
```bash
# Register question banks (Month 1)
python3 question_bank_registry.py --register batch_name

# Find matches (Months 2+)
python3 question_bank_registry.py --find-matches new_batch

# Map sheets to PDFs
python3 map_questions_to_answers.py --batch batch_name

# Run full analysis
python3 analyze.py

# List registered banks
python3 question_bank_registry.py --list
```

### **End of Work Day:**
```bash
# Deactivate virtual environment (optional)
deactivate

# Or just close the terminal - doesn't matter
```

---

## Side-by-Side Comparison

| Task | First Time | Subsequent Times |
|------|---|---|
| **Setup venv** | `python3 -m venv venv` | ✗ Already done |
| **Activate venv** | `source venv/bin/activate` | `source venv/bin/activate` |
| **Install deps** | `pip install -r requirements.txt` | ✗ Already installed |
| **Run tests** | `pytest -v` | ✗ Optional |
| **Run analyzer** | ✓ Works | ✓ Works |

---

## When Do You Need to Re-run Setup?

### **You DON'T need to re-run setup if:**
- ✓ Same computer
- ✓ Same Python version
- ✓ Just using existing tools
- ✓ Adding data (new batches, sheets, etc.)

### **You DO need to re-run setup if:**
- ❌ Switching to a different computer
- ❌ Python version changed significantly
- ❌ `requirements.txt` was updated
- ❌ Getting "ModuleNotFoundError" (dependencies missing)
- ❌ Virtual environment was deleted

**If unsure:** Just run `source venv/bin/activate`. If it works, you're good!

---

## Real-World Example

### **Monday (First Time)**
```bash
# Full setup
cd /Users/sriram/cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v

# Now start working
python3 question_bank_registry.py --register july12
```

### **Tuesday (Next Day)**
```bash
# Just activate and work
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

# Run commands
python3 question_bank_registry.py --find-matches july19
python3 map_questions_to_answers.py --batch july19
python3 analyze.py
```

### **Wednesday (Next Week)**
```bash
# Same as Tuesday!
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

# More work
python3 analyze.py
```

---

## What Each Command Does

### **python3 -m venv venv**
Creates isolated Python environment (dependencies don't conflict with system)
- **Only needed:** First time
- **Does:** Creates `venv/` directory with Python copy

### **source venv/bin/activate**
Activates the isolated environment
- **Needed:** Every time you start working
- **Does:** Changes terminal to use venv Python
- **Sign:** Terminal shows `(venv)` prefix

### **pip install -r requirements.txt**
Installs all dependencies into venv
- **Only needed:** First time (unless requirements change)
- **Does:** Reads `requirements.txt` and installs everything

### **pytest -v**
Runs all tests (optional verification)
- **Only needed:** First time (to verify installation)
- **Does:** Tests all 277+ tests to ensure everything works

---

## Troubleshooting

### ❌ "command not found: python3"
**Fix:** Install Python 3.9+ or use full path

### ❌ "ModuleNotFoundError: No module named 'openpyxl'"
**Fix:** Activate venv and re-run `pip install -r requirements.txt`

### ❌ "(venv) is not showing in terminal"
**Fix:** Re-run `source venv/bin/activate`

### ❌ "venv not found"
**Fix:** venv was deleted. Re-run full setup (it's safe)

---

## Quick Reference Card

### **Print this out! 📋**

```
═══════════════════════════════════════════════════════════════

FIRST TIME SETUP (Do this once)
───────────────────────────────────────────────────────────────
cd /Users/sriram/cissp-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v


EVERY OTHER TIME (Just 2 commands)
───────────────────────────────────────────────────────────────
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

# Then run analyzer commands:
python3 analyze.py


COMMON COMMANDS (After activation)
───────────────────────────────────────────────────────────────
# Register question banks
python3 question_bank_registry.py --register batch_name

# Find matching banks
python3 question_bank_registry.py --find-matches batch_name

# Map sheets to PDFs
python3 map_questions_to_answers.py --batch batch_name

# Run analysis
python3 analyze.py

# View registered banks
python3 question_bank_registry.py --list


DEACTIVATE WHEN DONE (Optional)
───────────────────────────────────────────────────────────────
deactivate

═══════════════════════════════════════════════════════════════
```

---

## Automation: Add to .bashrc or .zshrc (Optional)

If you want to make it even faster, add this to your shell config:

```bash
# Add to ~/.zshrc or ~/.bashrc
alias cissp='cd /Users/sriram/cissp-analyzer && source venv/bin/activate'
```

Then just type:
```bash
cissp
# You're immediately in the project with venv activated!
```

---

## Summary

| When | Action | Time |
|---|---|---|
| **Computer 1, First Use** | Run full setup | 10 min |
| **Computer 1, Days 2+** | Activate venv + run | 30 sec |
| **Computer 2, First Use** | Run full setup | 10 min |
| **Computer 2, Days 2+** | Activate venv + run | 30 sec |

**The venv is smart:** It stays installed until you delete it. Just activate when you need it!

---

## Golden Rule

**Remember 2 things:**
1. ✅ First time: Full setup (5-10 min)
2. ✅ Every other time: Just activate + run (30 sec)

That's it! 🎯
