# Interactive Question Bank → Answer Sheet Mapping

**Problem:** Multiple question bank PDFs in one batch. User uploads answer sheets but forgets which belongs to which PDF. Gets confused.

**Solution:** Interactive wizard that explicitly maps each answer sheet to its question bank PDF.

---

## The Problem Scenario

You have files in batch directory:

```
answers/july12/
├── CISSP_Full_Exam_125Q.pdf      ← Question Bank 1
├── CISSP_Practice_Test_50Q.pdf   ← Question Bank 2
├── student1_answers.json         ← Belongs to which?
├── student2_answers.json         ← Belongs to which?
├── student3_answers.json         ← Belongs to which?
├── student4_answers.json         ← Belongs to which?
└── student5_answers.json         ← Belongs to which?
```

❌ **Without mapping:** Confusion, wrong scoring, invalid comparisons

✅ **With mapping:** Crystal clear which answers go with which exam

---

## The Solution: Interactive Mapper

### **What It Does**

```
Step 1: Scan directory for PDFs (question banks)
         ↓
Step 2: Scan directory for answer sheets (JSON/Excel)
         ↓
Step 3: For EACH PDF, ask user:
        "Which answer sheets belong to this PDF?"
         ↓
Step 4: User selects answer sheets
         ↓
Step 5: Save explicit mapping to file
         ↓
✅ Clear audit trail showing PDF → Answer Sheets
```

---

## Walkthrough Example

### **Scenario: 2 Question Banks, 5 Answer Sheets**

#### **Files in Directory:**
```
answers/july12/
├── CISSP_Full_Exam.pdf          (125 questions)
├── CISSP_Practice.pdf           (50 questions)
├── john_doe.json
├── jane_smith.json
├── alice_brown.json
├── bob_wilson.json
└── charlie_davis.json
```

#### **Run Interactive Mapper:**
```bash
python3 map_questions_to_answers.py --batch july12
```

#### **Step 1: System Detects**
```
📋 STEP 1: DETECTING QUESTION BANKS
────────────────────────────────────────────────

✓ Found 2 question bank PDF(s):

  1. CISSP_Full_Exam.pdf
  2. CISSP_Practice.pdf
```

#### **Step 2: System Detects Answer Sheets**
```
📄 STEP 2: DETECTING ANSWER SHEETS
────────────────────────────────────────────────

✓ Found 5 answer sheet(s):

  1. john_doe.json
  2. jane_smith.json
  3. alice_brown.json
  4. bob_wilson.json
  5. charlie_davis.json
```

#### **Step 3a: Map First PDF**
```
🔗 STEP 3: MAPPING ANSWER SHEETS TO QUESTION BANKS
────────────────────────────────────────────────────

================================================================================
QUESTION BANK 1/2: CISSP_Full_Exam.pdf
================================================================================

Answer sheets for this question bank:

📌 Suggested matches:
   1. john_doe.json
   2. jane_smith.json
   3. alice_brown.json

📋 All available answer sheets:
   1. [ ] john_doe.json
   2. [ ] jane_smith.json
   3. [ ] alice_brown.json
   4. [ ] bob_wilson.json
   5. [ ] charlie_davis.json

❓ Which answer sheets belong to 'CISSP_Full_Exam.pdf'?
   Enter numbers separated by spaces (e.g., 1 2 3)
   Press Enter to skip: 1 2 3
```

#### **User Selects: 1 2 3**
```
✓ Mapped 3 answer sheet(s) to CISSP_Full_Exam.pdf
```

#### **Step 3b: Map Second PDF**
```
================================================================================
QUESTION BANK 2/2: CISSP_Practice.pdf
================================================================================

Answer sheets for this question bank:

📌 Suggested matches:
   1. bob_wilson.json
   2. charlie_davis.json

📋 All available answer sheets:
   1. [✓] john_doe.json      (already mapped)
   2. [✓] jane_smith.json    (already mapped)
   3. [✓] alice_brown.json   (already mapped)
   4. [ ] bob_wilson.json
   5. [ ] charlie_davis.json

❓ Which answer sheets belong to 'CISSP_Practice.pdf'?
   Enter numbers separated by spaces (e.g., 1 2 3)
   Press Enter to skip: 4 5
```

#### **User Selects: 4 5**
```
✓ Mapped 2 answer sheet(s) to CISSP_Practice.pdf
```

#### **Step 4: Summary**
```
✓ STEP 4: MAPPING SUMMARY
────────────────────────────────────────────────

📊 Summary:
   Question banks: 2
   Answer sheets: 5
   Mapped: 5
   Unmapped: 0

💾 Mapping saved to: ANSWER_MAPPING_MANIFEST.json
```

#### **Output File Created: ANSWER_MAPPING_MANIFEST.json**
```json
{
  "batch": "answers/july12",
  "created": "2026-07-13T10:30:45.123456",
  "question_banks": {
    "CISSP_Full_Exam.pdf": {
      "answer_sheets": [
        "john_doe.json",
        "jane_smith.json",
        "alice_brown.json"
      ],
      "count": 3,
      "mapped_by": "user_interactive"
    },
    "CISSP_Practice.pdf": {
      "answer_sheets": [
        "bob_wilson.json",
        "charlie_davis.json"
      ],
      "count": 2,
      "mapped_by": "user_interactive"
    }
  },
  "unmapped_answers": [],
  "notes": []
}
```

---

## Features

### **1. Interactive Wizard (Recommended)**
```bash
python3 map_questions_to_answers.py --batch july12
```

User-guided step-by-step mapping with selections

### **2. Auto-Match by Filename**
```bash
python3 map_questions_to_answers.py --batch july12 --auto-match
```

Automatically matches by filename similarity (60%+ threshold)

### **3. View Saved Mapping**
```bash
python3 map_questions_to_answers.py --batch july12 --show-mapping
```

Display existing `ANSWER_MAPPING_MANIFEST.json`

---

## Complete Workflow: 5-6 Sheets Submitted

### **Step 1: Place Files**
```bash
mkdir -p answers/july12
# Copy question bank PDFs
cp question_bank_*.pdf answers/july12/
# Copy answer sheets
cp student_answers_*.json answers/july12/
```

### **Step 2: Run Mapper**
```bash
python3 map_questions_to_answers.py --batch july12
```

Follow prompts to assign each answer sheet to a PDF

### **Step 3: Verify Mapping**
```bash
python3 map_questions_to_answers.py --batch july12 --show-mapping
```

View the saved mapping

### **Step 4: Run Other Validators**
```bash
# Fuzzy filename check
python3 fuzzy_file_matcher.py --batch july12

# Exam consistency check  
python3 detect_exam_consistency.py --batch july12

# Setup wizard (automatic)
python3 analyze.py
```

### **Step 5: Analyze**
```bash
python3 analyze.py
# All mappings and validations confirmed
# Analysis runs with correct PDF→Answer associations ✓
```

---

## Real Scenarios

### **Scenario 1: Single Question Bank, Multiple Students**

**Files:**
```
CISSP_Exam.pdf
john_doe.json
jane_smith.json
alice_brown.json
```

**Mapper Output:**
```
✓ Found 1 question bank PDF
✓ Found 3 answer sheets

QUESTION BANK 1/1: CISSP_Exam.pdf
  All 3 sheets suggested as matches
  
User selects: 1 2 3 (all sheets)

✓ Mapping: CISSP_Exam.pdf → 3 answer sheets
```

---

### **Scenario 2: Multiple Question Banks, Needs Clarification**

**Files:**
```
Full_Exam.pdf
Practice_Test.pdf
student1.json  ← Could be either?
student2.json  ← Could be either?
student3.json  ← Could be either?
```

**Interactive Mapper:**
```
QUESTION BANK 1/2: Full_Exam.pdf
  Suggestions: student1, student2, student3
  User selects: 1 2
  ✓ Mapped to Full Exam

QUESTION BANK 2/2: Practice_Test.pdf
  Suggestions: student3
  User selects: 3
  ✓ Mapped to Practice Test

Result: Clear mapping, no confusion!
```

---

### **Scenario 3: Some Files Don't Match**

**Files:**
```
July12_Exam.pdf
July26_Exam.pdf   (different month!)
student1.json     (july12)
student2.json     (july12)
old_practice.json (unknown origin)
```

**Mapper Output:**
```
Question Banks: 2
Answer Sheets: 3
Mapped: 2
Unmapped: 1

⚠️ UNMAPPED ANSWER SHEETS:
   • old_practice.json

User must manually decide what to do with old_practice.json
```

---

## Integration: Complete 5-Layer Validation

Now you have **5 validation layers**:

### **Layer 0: Filename Similarity** (fuzzy_file_matcher.py)
```
Groups files by filename similarity
Detects version patterns (v1, v2, practice, etc.)
Speed: ⚡ Fast (no file reading)
```

### **Layer 0.5: Question Bank Mapping** (map_questions_to_answers.py) ← **NEW!**
```
Interactive mapping of PDF → Answer Sheets
Prevents confusion with multiple question banks
Creates explicit audit trail
Speed: ⚡⚡ Moderate (user interaction required)
```

### **Layer 1: File & Format Validation** (setup_wizard.py)
```
Checks files exist, directories valid, formats correct
Speed: ⚡ Fast
```

### **Layer 2: Sheet Variation Detection** (handle_sheet_variations.py)
```
Detects Excel sheet names, column headers
Speed: ⚡⚡ Moderate
```

### **Layer 3: Exam Consistency** (detect_exam_consistency.py)
```
Validates question counts, patterns match
Speed: ⚡⚡⚡ Slow (reads all questions)
```

---

## Output: ANSWER_MAPPING_MANIFEST.json

The manifest file created contains:

```json
{
  "batch": "answers/july12",
  "created": "2026-07-13T10:30:45",
  
  "question_banks": {
    "question_bank_1.pdf": {
      "answer_sheets": ["student1.json", "student2.json"],
      "count": 2,
      "mapped_by": "user_interactive"
    },
    "question_bank_2.pdf": {
      "answer_sheets": ["student3.json"],
      "count": 1,
      "mapped_by": "user_interactive"
    }
  },
  
  "unmapped_answers": ["unknown_file.json"],
  "notes": ["⚠ unknown_file.json: No matching PDF"]
}
```

**Used by:**
- Other validation tools (reference which PDF each sheet belongs to)
- Analysis tools (score sheets against correct PDF)
- Audit trail (shows exactly what user confirmed)

---

## Key Benefits

| Without Mapping | With Mapping |
|---|---|
| ❌ Confusion about which sheet belongs to which PDF | ✅ Explicit associations saved |
| ❌ Risk of mixing different exam types | ✅ Clear separation by PDF |
| ❌ Wrong scoring if PDFs mixed | ✅ Correct PDF used for each sheet |
| ❌ No audit trail | ✅ Manifest shows exactly what user confirmed |
| ❌ User has to remember | ✅ System remembers for them |

---

## Workflow Summary

```
Receive 5-6 Answer Sheets + Multiple Question Banks
    ↓
Run: python3 map_questions_to_answers.py --batch july12
    ↓
Interactive Wizard:
  - Detect all PDFs
  - Detect all answer sheets
  - For each PDF, ask user to select related sheets
    ↓
Verify: python3 map_questions_to_answers.py --show-mapping
    ↓
Mapping Manifest Created:
  - PDF 1 → Answer Sheets 1, 2, 3
  - PDF 2 → Answer Sheets 4, 5
  - Unmapped: None
    ↓
Proceed to Analysis with Confidence ✅
```

---

## Summary

**The Interactive Mapper solves:**
- ✅ Multiple question banks confusion
- ✅ Explicit user confirmation of mappings
- ✅ Clear audit trail
- ✅ Prevents wrong PDF-answer associations
- ✅ Easy reference via saved manifest
- ✅ Handles unmapped sheets gracefully

**When you have 5-6 sheets from unknown source, this layer ensures you know exactly which question bank each answer belongs to.** 🎯
