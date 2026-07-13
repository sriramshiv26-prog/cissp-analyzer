# Persistent Question Bank Registry - Multi-Week Upload Scenario

**Your Question:** "If I upload a questionnaire last week and answer sheets this week, can it show me or reference that sheet?"

**Answer:** YES! The Registry remembers question bank PDFs across weeks/months and automatically suggests them when new answer sheets arrive.

---

## The Problem

**Week 1:**
```
You upload: CISSP_Exam_July12.pdf
System: Processes it, analyzes it
```

**Week 2:**
```
You upload: 5 new answer sheets for same exam
System: "What question bank do these belong to?"
You: "Ugh, same one from last week, let me find it..."
```

❌ **Without Registry:** Have to re-upload or manually reference

---

## The Solution: Question Bank Registry

**Week 1:**
```bash
python3 question_bank_registry.py --register july12
```
→ Registers: `CISSP_Exam_July12.pdf` in permanent catalog

**Week 2:**
```bash
python3 question_bank_registry.py --find-matches july26
```
→ Output:
```
student1.json:
  • CISSP_Exam_July12.pdf (similarity: 0.89) ← FOUND IT!

student2.json:
  • CISSP_Exam_July12.pdf (similarity: 0.91)
```

✅ **Automatically suggests the PDF from last week!**

---

## Real-World Scenario: Multi-Week Enrollment

### **Week 1: June Cohort**

**You have:**
```
answers/june_cohort/
├── CISSP_Exam.pdf          ← Main question bank
├── student1_june.json
└── student2_june.json
```

**You run:**
```bash
python3 question_bank_registry.py --register june_cohort

Output:
  ✓ Registered: CISSP_Exam.pdf (fingerprint: a1b2c3d4e5f6)
```

**Registry now remembers:**
```json
{
  "question_banks": {
    "CISSP_Exam.pdf": {
      "registered": "2026-07-01T10:30:00",
      "batches_used": ["answers/june_cohort"],
      "answer_sheets": ["student1_june.json", "student2_june.json"]
    }
  }
}
```

### **Week 3: July Cohort (Same Exam, Different Students)**

**You have:**
```
answers/july_cohort/
├── student3_july.json
├── student4_july.json
└── student5_july.json
```

**You want to know:** "Which question bank do these belong to?"

**You run:**
```bash
python3 question_bank_registry.py --find-matches july_cohort

Output:
  MATCHING QUESTION BANKS:

  student3_july.json:
    • CISSP_Exam.pdf (similarity: 0.92) ← Found from June!

  student4_july.json:
    • CISSP_Exam.pdf (similarity: 0.94)

  student5_july.json:
    • CISSP_Exam.pdf (similarity: 0.89)
```

✅ **System automatically suggests the same PDF from June!**

### **System Updates Registry:**

```json
{
  "question_banks": {
    "CISSP_Exam.pdf": {
      "registered": "2026-07-01T10:30:00",
      "batches_used": [
        "answers/june_cohort",
        "answers/july_cohort"  ← Added!
      ],
      "answer_sheets": [
        "student1_june.json",
        "student2_june.json",
        "student3_july.json",   ← Added!
        "student4_july.json",
        "student5_july.json"
      ]
    }
  }
}
```

---

## How the Registry Works

### **1. Registration (Week 1)**

```bash
python3 question_bank_registry.py --register july12
```

**What happens:**
- Scans batch directory for PDFs
- Creates fingerprint of each PDF (file size + modification time hash)
- Stores in persistent registry:
  - PDF name & path
  - When registered
  - Which batches use it
  - Which answer sheets belong to it

**Registry location:**
```
~/.claude/projects/-Users-sriram/question_bank_registry.json
```

### **2. Finding Matches (Week 2)**

```bash
python3 question_bank_registry.py --find-matches july26
```

**What happens:**
1. Scans batch directory for answer sheets
2. Compares answer sheet filenames to registered PDFs
3. Uses fuzzy matching (60%+ similarity threshold)
4. Returns suggestions ranked by similarity score
5. Shows: "These sheets likely belong to X PDF"

### **3. Listing All Registered PDFs**

```bash
python3 question_bank_registry.py --list
```

**Output:**
```
REGISTERED QUESTION BANKS
════════════════════════════════════════════════════════════════════════════════

PDF Name                                 Registered    Batches  Sheets
────────────────────────────────────────────────────────────────────────────────
CISSP_Exam.pdf                          2026-07-01    3        12
CISSP_Practice_Test.pdf                 2026-07-02    2        8
CISSP_Midterm.pdf                       2026-07-05    1        5
```

### **4. Showing Details of Specific PDF**

```bash
python3 question_bank_registry.py --show "CISSP_Exam.pdf"
```

**Output:**
```
QUESTION BANK: CISSP_Exam.pdf
════════════════════════════════════════════════════════════════════════════════

Path: /answers/july12/CISSP_Exam.pdf
Fingerprint: a1b2c3d4e5
Registered: 2026-07-01T10:30:45

📊 Usage:
  Batches: 3
    • answers/july12
    • answers/july26
    • answers/august12

  Answer Sheets: 12
    • student1.json
    • student2.json
    • ... (10 more)
```

---

## Multi-Week Timeline Example

### **July 1 (Week 1): Register Question Bank**

```
Step 1: Upload CISSP_July_Exam.pdf
Step 2: Register it
  $ python3 question_bank_registry.py --register july12

Step 3: Upload 3 answer sheets
  $ python3 map_questions_to_answers.py --batch july12
  (Map sheets to the PDF)

Step 4: Analyze
  $ python3 analyze.py
  (Select batch: july12)

Registry Status:
  ✓ CISSP_July_Exam.pdf registered
  ✓ 3 answer sheets mapped & analyzed
```

### **July 8 (Week 2): Same Exam, New Batch**

```
Step 1: Upload 5 NEW answer sheets (different students, same exam)
  No need to re-upload the PDF!

Step 2: Find matching question bank
  $ python3 question_bank_registry.py --find-matches july19

Output:
  student1.json:
    • CISSP_July_Exam.pdf (similarity: 0.93) ← Found from Week 1!

  student2.json:
    • CISSP_July_Exam.pdf (similarity: 0.94)

  ... (3 more)

Step 3: Confirm mapping
  $ python3 map_questions_to_answers.py --batch july19
  (Suggests: "Assign all sheets to CISSP_July_Exam.pdf? (y/n)")
  User: y

Step 4: Analyze
  $ python3 analyze.py
  (Select batch: july19)

Registry Status:
  ✓ CISSP_July_Exam.pdf updated
  ✓ Now has: 3 sheets from Week 1 + 5 sheets from Week 2 = 8 total
  ✓ Batches using it: [july12, july19]
```

### **July 15 (Week 3): Same Exam Again**

```
Step 1: Upload 4 more answer sheets

Step 2: Find matches
  $ python3 question_bank_registry.py --find-matches july26

Output:
  student1.json:
    • CISSP_July_Exam.pdf (similarity: 0.96) ← Still found!

  ... (3 more)

Step 3: Map & Analyze as before
  (System gets faster because it remembers the PDF)

Registry Status:
  ✓ CISSP_July_Exam.pdf updated again
  ✓ Now has: 8 sheets from previous weeks + 4 new = 12 total
  ✓ Batches: [july12, july19, july26]
  ✓ Usage history completely tracked
```

---

## Features

### **1. Multi-Batch Memory**

```bash
# Register PDF from one batch
python3 question_bank_registry.py --register batch1

# Later, find it from a different batch
python3 question_bank_registry.py --find-matches batch2
→ Finds the PDF from batch1!
```

### **2. Usage History**

Registry tracks:
- ✓ When each PDF was registered
- ✓ Which batches have used it
- ✓ How many answer sheets have been analyzed
- ✓ Complete audit trail

### **3. Fingerprinting**

Uses file fingerprints (size + modification time) to uniquely identify PDFs:
- ✓ Same PDF, different filename? Recognized!
- ✓ Different PDF, same name? Distinguished!

### **4. Fuzzy Matching**

Matches answer sheets to PDFs by filename similarity:
- ✓ `CISSP_July_Exam.pdf` matches `july_exam.json` (89% match)
- ✓ `CISSP_July_Exam.pdf` matches `july_exam_student1.xlsx` (92% match)
- ✓ Threshold: 60% (adjustable)

---

## Integration with Other Tools

### **Workflow: Using Registry with Mapping**

```
Step 1: Register question bank
  python3 question_bank_registry.py --register july12
  
Step 2: Weeks later, find matching sheets
  python3 question_bank_registry.py --find-matches july26
  
Step 3: Map sheets to found PDF
  python3 map_questions_to_answers.py --batch july26
  (System suggests: "Use CISSP_Exam.pdf from registry?")
  
Step 4: Validate & analyze
  python3 analyze.py
```

---

## Complete 6-Layer Validation Stack (Updated)

```
LAYER 0: Filename Similarity
    ↓
LAYER 0.25: Question Bank Registry ← NEW!
    ├─ Remembers PDFs across weeks/months
    ├─ Auto-suggests matching question banks
    └─ Tracks usage history
    ↓
LAYER 0.5: PDF → Answer Mapping
    ↓
LAYER 1: File & Format Validation
    ↓
LAYER 2: Sheet Variation Detection
    ↓
LAYER 3: Exam Consistency
    ↓
✅ READY FOR ANALYSIS
```

---

## Real Scenarios

### **Scenario 1: Annual Exam**

```
Year 1: Upload CISSP_Exam_2025.pdf
  python3 question_bank_registry.py --register 2025

Year 2: New cohort takes same exam
  python3 question_bank_registry.py --find-matches 2026
  → Finds: CISSP_Exam_2025.pdf (registered 1 year ago)
  → Suggests auto-mapping
  → Analysis uses exact same PDF as Year 1
  → Results comparable across years!
```

### **Scenario 2: Multiple Cohorts, Same Exam**

```
Cohort A (Jan): Upload Math_Placement_Test.pdf
  Register it

Cohort B (Feb): New cohort, same test
  Find matching PDF
  → Finds: Math_Placement_Test.pdf from Cohort A
  → Re-uses it automatically

Cohort C (Mar): Another cohort
  Find matching PDF
  → Finds: Math_Placement_Test.pdf
  → Re-uses it again

Registry tracks: [Cohort A, Cohort B, Cohort C] all used same test
```

### **Scenario 3: Version Control**

```
v1: Upload CISSP_Exam_v1.pdf
  Register it

Later: Upload CISSP_Exam_v2.pdf (updated version)
  Register it

Answer sheets: "Which version did students take?"
  Find matches
  → Some match v1 (90%), some match v2 (92%)
  → System separates them automatically
  → Clear audit trail of which version each student took
```

---

## Summary: Multi-Week Uploads

| Scenario | Without Registry | With Registry |
|----------|---|---|
| Upload PDF Week 1 | Stored locally | Registered in catalog ✓ |
| Upload sheets Week 2 | "Which PDF?" | Auto-suggests from catalog ✓ |
| Same exam Month later | Re-upload PDF | Found in registry ✓ |
| Different batches, same test | Manual matching | Auto-matched ✓ |
| Question bank history | Lost | Completely tracked ✓ |

---

## Using the Registry

### **Register PDFs (Do This First Time)**
```bash
python3 question_bank_registry.py --register batch_name
```

### **Find Matching PDFs (When New Sheets Arrive)**
```bash
python3 question_bank_registry.py --find-matches batch_name
```

### **View All Registered PDFs**
```bash
python3 question_bank_registry.py --list
```

### **View Details of Specific PDF**
```bash
python3 question_bank_registry.py --show "PDF_Name.pdf"
```

---

## Bottom Line

Upload a question bank PDF once, and the system **remembers it forever**. When you upload answer sheets weeks or months later, it automatically recognizes which question bank they belong to and suggests it. No re-uploading, no confusion, complete history! 🎯
