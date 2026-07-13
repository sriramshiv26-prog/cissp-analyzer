# START HERE - Complete Step-by-Step Guide

**Your Complete Journey from Day 1 to Ongoing Use** 🚀

---

## What You're Getting

A complete system with **6 validation layers** that:
- ✅ Handles question banks uploaded at different times
- ✅ Recognizes answer sheets from different groups/dates
- ✅ Automatically matches sheets to correct question banks
- ✅ Remembers everything (no re-uploading needed)
- ✅ Works for months/years automatically

---

## DAY 1: INITIAL SETUP (One Time Only)

### Step 1: Open Terminal

```bash
cd /Users/sriram/cissp-analyzer
```

### Step 2: Run Setup Commands (5-10 minutes)

```bash
# Create isolated Python environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify (optional)
pytest -v
```

**✅ Done!** Everything is installed. Your terminal now shows `(venv)` prefix.

---

## WEEK 1: First Time Using the System

### Upload Your Question Banks

Place all your question bank PDFs in one batch directory:

```bash
mkdir -p answers/july12
cd answers/july12

# Copy all your question bank PDFs here
cp /path/to/CISSP_Exam.pdf .
cp /path/to/CompTIA_Security+.pdf .
cp /path/to/AWS_Solutions_Architect.pdf .
# ... (add all your 3+ to 10+ PDFs)
```

### Register Question Banks (Remember Forever)

```bash
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

python3 question_bank_registry.py --register july12

# Output:
#   ✓ Registered: CISSP_Exam.pdf
#   ✓ Registered: CompTIA_Security+.pdf
#   ✓ Registered: AWS_Solutions_Architect.pdf
#   ... (all banks registered)
```

**✅ Done!** All question banks are now registered permanently. Never upload them again.

---

## WEEK 2: First Batch of Answer Sheets

### Upload Answer Sheets for First Program

```bash
mkdir -p answers/program_a_batch_1
# Place answer sheets (JSON or Excel) here
cp /path/to/student1.json answers/program_a_batch_1/
cp /path/to/student2.json answers/program_a_batch_1/
# ... (add all 50-100 sheets)
```

### Find Matching Question Bank

```bash
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

python3 question_bank_registry.py --find-matches program_a_batch_1

# Output:
#   student1.json → CISSP_Exam.pdf (0.93) ✓
#   student2.json → CISSP_Exam.pdf (0.94) ✓
#   ... (all sheets matched)
```

### Map Sheets to Question Bank

```bash
python3 map_questions_to_answers.py --batch program_a_batch_1

# Interactive wizard:
#   QUESTION BANK 1/1: CISSP_Exam.pdf
#   Which sheets? (e.g., 1 2 3 4 5) → user enters: 1 2 3 4 5
#   ✓ Mapped all sheets to CISSP_Exam.pdf
```

### Run Analysis

```bash
python3 analyze.py

# Choose: [1] Batch Analysis
# Enter batch: program_a_batch_1
# ✓ Analysis complete! Reports saved to reports/
```

**✅ Week 2 Complete!** First program analyzed.

---

## WEEK 3: Second Program (Different Question Bank)

### Upload Answer Sheets for Second Program

```bash
mkdir -p answers/program_b_batch_1
# Place sheets for Program B here
cp /path/to/program_b_student1.json answers/program_b_batch_1/
# ... (80 sheets, all for CompTIA exam)
```

### Find & Map (Automatic!)

```bash
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

# Find matching bank
python3 question_bank_registry.py --find-matches program_b_batch_1

# Output:
#   program_b_student1.json → CompTIA_Security+.pdf (0.91) ✓
#   ... (all matched to CompTIA_Security+.pdf)

# Map them
python3 map_questions_to_answers.py --batch program_b_batch_1
# Choose: CompTIA_Security+.pdf ✓

# Analyze
python3 analyze.py
```

**✅ Week 3 Complete!** Second program analyzed with different question bank.

---

## WEEK 4+: Rinse & Repeat

Same workflow repeats:

```bash
# 1. Upload answer sheets for next program
mkdir -p answers/program_c_batch_1
cp /path/to/sheets/* answers/program_c_batch_1/

# 2. Find matching bank (auto-finds from registry!)
source venv/bin/activate
python3 question_bank_registry.py --find-matches program_c_batch_1

# 3. Map (confirm or auto-assign)
python3 map_questions_to_answers.py --batch program_c_batch_1

# 4. Analyze
python3 analyze.py
```

**Key Point:** Question banks registered in Week 1 are still remembered!

---

## ONGOING USE (Months 2+)

### Daily Workflow

```bash
# Start of day:
cd /Users/sriram/cissp-analyzer
source venv/bin/activate

# Do your work:
python3 question_bank_registry.py --find-matches new_batch
python3 map_questions_to_answers.py --batch new_batch
python3 analyze.py

# End of day:
deactivate  # (optional - just close terminal if you want)
```

### Monthly Check

```bash
# View all registered banks
python3 question_bank_registry.py --list

# Output shows:
#   Bank Name                Registered    Batches    Sheets
#   CISSP_Exam.pdf          2026-07-01    3          75
#   CompTIA_Security+.pdf   2026-07-01    2          80
#   AWS_Solutions_Arch...   2026-07-01    2          120
#   ...
```

---

## When Programs Repeat

### Same Program, Different Cohort

```bash
# Program A Round 2 (3 months later)
mkdir -p answers/program_a_batch_2
# Place new sheets here

# System recognizes it's the same program!
python3 question_bank_registry.py --find-matches program_a_batch_2

# Output:
#   student_new_1.json → CISSP_Exam.pdf (0.94) ✓
#   ... (finds same bank from 3 months ago!)
```

**✅ No re-upload needed!** Registry remembers.

---

## Key Files to Know

### After Setup, These Are Your Main Tools:

```
1. question_bank_registry.py ← Register & find question banks
2. map_questions_to_answers.py ← Map sheets to PDFs
3. analyze.py ← Run complete analysis
4. fuzzy_file_matcher.py ← Debug filename issues
5. detect_exam_consistency.py ← Verify question counts match
```

---

## Documentation to Read

### In Order:

1. **This file** - You're reading it! ✅
2. **QUICK_WORKFLOW_GUIDE.md** - Setup vs recurring use
3. **PERSISTENT_QUESTION_BANK_REGISTRY.md** - How registry works
4. **MULTI_QUESTION_BANK_SCENARIO.md** - Your exact use case
5. **COMPLETE_SOLUTION_SUMMARY.md** - Everything together
6. **INTERACTIVE_MAPPING_GUIDE.md** - Mapping details

---

## The 6-Layer Validation Stack

Everything you need is built in:

```
Layer 0.25: Question Bank Registry
    ↓ Remembers banks, auto-suggests matches
Layer 0: Filename Similarity
    ↓ Groups files despite typos/variations
Layer 0.5: PDF → Answer Mapping
    ↓ User confirms associations
Layer 1: File & Format Validation
    ↓ Checks structure
Layer 2: Sheet Variation Detection
    ↓ Handles Excel variations
Layer 3: Exam Consistency
    ↓ Confirms content matches
✅ READY FOR ANALYSIS
```

---

## Complete Timeline Example

```
MONTH 1 WEEK 1:
  Action: Upload 6 question banks
  Command: python3 question_bank_registry.py --register initial
  Result: ✓ All registered permanently

MONTH 1 WEEK 2:
  Action: Program A uploads 100 sheets (CISSP)
  Commands:
    python3 question_bank_registry.py --find-matches program_a_batch_1
    python3 map_questions_to_answers.py --batch program_a_batch_1
    python3 analyze.py
  Result: ✓ Program A analyzed

MONTH 1 WEEK 3:
  Action: Program B uploads 80 sheets (CompTIA)
  Commands: (same as above for program_b_batch_1)
  Result: ✓ Program B analyzed (different bank, correctly separated)

MONTH 2 WEEK 1:
  Action: Program C uploads 120 sheets (AWS)
  Commands: (same workflow)
  Result: ✓ Program C analyzed

MONTH 3:
  Action: Program A retakes (100 new students, same CISSP exam)
  Command: python3 question_bank_registry.py --find-matches program_a_batch_2
  Result: ✓ Finds CISSP_Exam.pdf from Month 1 (no re-upload!)

MONTHS 4-12: Repeat as needed
  → System automatically handles everything
  → Never re-upload question banks
  → Complete history tracked
```

---

## Quick Reference

### Commands Cheat Sheet

```bash
# Register question banks (ONE TIME)
python3 question_bank_registry.py --register batch_name

# Find matching banks when sheets arrive
python3 question_bank_registry.py --find-matches batch_name

# View all registered banks
python3 question_bank_registry.py --list

# View details of specific bank
python3 question_bank_registry.py --show "CISSP_Exam.pdf"

# Map sheets to PDFs
python3 map_questions_to_answers.py --batch batch_name

# View saved mapping
python3 map_questions_to_answers.py --batch batch_name --show-mapping

# Run full analysis
python3 analyze.py

# Check file groupings
python3 fuzzy_file_matcher.py --batch batch_name

# Verify exam consistency
python3 detect_exam_consistency.py --batch batch_name
```

---

## Troubleshooting Quick Answers

**Q: "Do I need to re-run setup every time?"**
A: NO! Just `source venv/bin/activate` then run commands.

**Q: "Do I need to re-upload question banks?"**
A: NO! Register once, they're remembered forever.

**Q: "How do I know which bank a sheet belongs to?"**
A: Run `python3 question_bank_registry.py --find-matches batch_name` - system tells you!

**Q: "Can it handle 10+ different question banks?"**
A: YES! That's exactly what it's designed for.

**Q: "What if programs retake the same exam?"**
A: System recognizes it's the same bank, no confusion.

---

## You're Ready! 🚀

### Day 1:
- ✅ Run setup commands (5-10 min, one time only)

### Week 1:
- ✅ Upload question banks
- ✅ Register them (never again)

### Week 2+:
- ✅ Upload sheets → Find bank → Map → Analyze
- ✅ Repeat as needed, no manual work

### You Get:
- ✅ No re-uploading
- ✅ Automatic matching
- ✅ Complete history
- ✅ Works for months/years

---

## Next Steps

1. **Do Day 1 setup** (5-10 minutes)
2. **Read PERSISTENT_QUESTION_BANK_REGISTRY.md** (understand how it works)
3. **Upload your question banks** (Week 1)
4. **Start using!** (Week 2+)

**That's it!** Everything else is automated. 🎯
