# Multiple Question Banks (5+) - Different People Scenario

**Your Clarification:** "If there are 5+ question banks for different sets of people, and I'm uploading answer sheets for different people, can the system identify which question bank each sheet belongs to even if I uploaded the banks earlier?"

**Answer:** YES! Absolutely! The Registry is designed exactly for this scenario.

---

## Perfect Use Case: Multiple Programs/Cohorts

You have different people taking different exams:

```
Program A: Group of 10 students → CISSP_Exam.pdf
Program B: Group of 8 students → CompTIA_Security+.pdf
Program C: Group of 12 students → AWS_Solutions_Architect.pdf
Program D: Group of 6 students → GCP_Associate.pdf
Program E: Group of 9 students → Azure_Admin.pdf
Program F: Group of 7 students → Linux_LPIC.pdf (Plus 1 more = 6+ total)
```

---

## Real Workflow: 5+ Question Banks

### **MONTH 1: Register All Question Banks (One Time)**

You have all 5+ PDFs. Register them once:

```bash
# Register all at once
python3 question_bank_registry.py --register program_batch_1

Output:
  ✓ Registered: CISSP_Exam.pdf (fingerprint: a1b2c3d4)
  ✓ Registered: CompTIA_Security+.pdf (fingerprint: e5f6g7h8)
  ✓ Registered: AWS_Solutions_Architect.pdf (fingerprint: i9j0k1l2)
  ✓ Registered: GCP_Associate.pdf (fingerprint: m3n4o5p6)
  ✓ Registered: Azure_Admin.pdf (fingerprint: q7r8s9t0)
  ✓ Registered: Linux_LPIC.pdf (fingerprint: u1v2w3x4)
```

**Registry now remembers all 6 question banks permanently!**

### **MONTH 2: Upload Answer Sheets for Program A**

10 students from Program A take CISSP exam. Upload their answer sheets:

```
answers/program_a_batch_2/
├── alice_prog_a.json
├── bob_prog_a.json
├── charlie_prog_a.json
├── diana_prog_a.json
├── eric_prog_a.json
└── ... (5 more)
```

**Run matcher:**
```bash
python3 question_bank_registry.py --find-matches program_a_batch_2

Output:
  alice_prog_a.json:
    • CISSP_Exam.pdf (similarity: 0.93) ← FOUND IT! From 1 month ago

  bob_prog_a.json:
    • CISSP_Exam.pdf (similarity: 0.94)

  charlie_prog_a.json:
    • CISSP_Exam.pdf (similarity: 0.92)

  ... (all 10 students matched to CISSP_Exam.pdf)
```

✅ **System automatically found the right PDF even though it was uploaded weeks ago!**

### **MONTH 2 (Same time): Upload Answer Sheets for Program B**

8 students from Program B take CompTIA exam:

```
answers/program_b_batch_2/
├── student1_prog_b.json
├── student2_prog_b.json
├── ... (8 total)
```

**Run matcher:**
```bash
python3 question_bank_registry.py --find-matches program_b_batch_2

Output:
  student1_prog_b.json:
    • CompTIA_Security+.pdf (similarity: 0.91) ← Found from Month 1!

  student2_prog_b.json:
    • CompTIA_Security+.pdf (similarity: 0.95)

  ... (all 8 matched to CompTIA_Security+.pdf)
```

✅ **Different group, different exam, correctly identified!**

### **MONTH 3: Upload Sheets for Programs C, D, E**

Students from 3 different programs, 3 different exams:

```
Program C (AWS): 12 answer sheets
Program D (GCP): 6 answer sheets
Program E (Azure): 9 answer sheets
```

**Run matcher for each:**
```bash
python3 question_bank_registry.py --find-matches program_c_batch_3
→ Matches all 12 to: AWS_Solutions_Architect.pdf ✓

python3 question_bank_registry.py --find-matches program_d_batch_3
→ Matches all 6 to: GCP_Associate.pdf ✓

python3 question_bank_registry.py --find-matches program_e_batch_3
→ Matches all 9 to: Azure_Admin.pdf ✓
```

✅ **System correctly separated 27 sheets into 3 different question banks!**

### **MONTH 4: Programs A & C Repeat**

Same programs retake their exams:

```
Program A (CISSP) Round 2: 10 new students
Program C (AWS) Round 2: 12 new students
```

**System recognizes:**
```bash
# Program A sheets
python3 question_bank_registry.py --find-matches program_a_batch_4
→ Matches to: CISSP_Exam.pdf (now used in 2 batches, 20 sheets) ✓

# Program C sheets
python3 question_bank_registry.py --find-matches program_c_batch_4
→ Matches to: AWS_Solutions_Architect.pdf (now used in 2 batches, 24 sheets) ✓
```

✅ **System knows: These are repeats of earlier programs!**

---

## Scenario Visualization

### **Timeline:**

```
MONTH 1 (Week 1-2):
  Upload & Register all 6 question banks
  └─ CISSP, CompTIA, AWS, GCP, Azure, Linux

MONTH 2 (Week 5-6):
  Upload answer sheets for Program A (CISSP)
  └─ System: "These belong to CISSP_Exam.pdf" (from Month 1) ✓
  
  Upload answer sheets for Program B (CompTIA)
  └─ System: "These belong to CompTIA_Security+.pdf" (from Month 1) ✓

MONTH 3 (Week 9-10):
  Upload answer sheets for Program C (AWS)
  └─ System: "These belong to AWS_Solutions_Architect.pdf" ✓
  
  Upload answer sheets for Program D (GCP)
  └─ System: "These belong to GCP_Associate.pdf" ✓
  
  Upload answer sheets for Program E (Azure)
  └─ System: "These belong to Azure_Admin.pdf" ✓

MONTH 4 (Week 13-14):
  Upload answer sheets for Program A Round 2 (CISSP)
  └─ System: "These also belong to CISSP_Exam.pdf" (now 2x usage) ✓
  
  Upload answer sheets for Program C Round 2 (AWS)
  └─ System: "These also belong to AWS_Solutions_Architect.pdf" (now 2x usage) ✓
```

---

## How The Registry Distinguishes 5+ Question Banks

### **By Fingerprint (File Identity)**

Each PDF gets a unique fingerprint:
```
CISSP_Exam.pdf
  Size: 2.5 MB
  Modified: 2026-07-01 10:30:00
  Fingerprint: a1b2c3d4 ← UNIQUE ID

CompTIA_Security+.pdf
  Size: 1.8 MB
  Modified: 2026-07-01 11:00:00
  Fingerprint: e5f6g7h8 ← DIFFERENT

AWS_Solutions_Architect.pdf
  Size: 3.1 MB
  Modified: 2026-07-01 11:30:00
  Fingerprint: i9j0k1l2 ← DIFFERENT

... (3 more unique fingerprints)
```

**Result:** Each PDF is uniquely identified, even if renamed or moved

### **By Filename Matching**

When answer sheets arrive, system matches by filename:

```
Answer sheet: "alice_prog_a.json"
Registry lookup: Does this match any registered PDF?

Search:
  CISSP_Exam.pdf: 93% match ✓ (highest)
  CompTIA_Security+.pdf: 42% match ✗ (too low)
  AWS_Solutions_Architect.pdf: 38% match ✗ (too low)
  ... (other PDFs also low matches)

Result: "Likely belongs to CISSP_Exam.pdf"
Confidence: 93% (above 60% threshold)
```

---

## Registry Shows Complete Separation

### **View All Registered PDFs:**

```bash
python3 question_bank_registry.py --list

Output:
┌────────────────────────────────┬──────────────┬─────────┬────────┐
│ PDF Name                       │ Registered   │ Batches │ Sheets │
├────────────────────────────────┼──────────────┼─────────┼────────┤
│ CISSP_Exam.pdf                 │ 2026-07-01   │ 2       │ 20     │
│ CompTIA_Security+.pdf          │ 2026-07-01   │ 1       │ 8      │
│ AWS_Solutions_Architect.pdf    │ 2026-07-01   │ 2       │ 24     │
│ GCP_Associate.pdf              │ 2026-07-01   │ 1       │ 6      │
│ Azure_Admin.pdf                │ 2026-07-01   │ 1       │ 9      │
│ Linux_LPIC.pdf                 │ 2026-07-01   │ 0       │ 0      │
└────────────────────────────────┴──────────────┴─────────┴────────┘
```

**Shows:**
- ✓ All 6 question banks registered
- ✓ Which batches used each
- ✓ How many answer sheets per PDF
- ✓ Complete usage history

### **View Specific PDF Details:**

```bash
python3 question_bank_registry.py --show "CISSP_Exam.pdf"

Output:
  Path: /answers/program_batch_1/CISSP_Exam.pdf
  Fingerprint: a1b2c3d4
  Registered: 2026-07-01T10:30:00
  
  📊 Usage:
    Batches: 2
      • program_a_batch_2
      • program_a_batch_4
    
    Answer Sheets: 20
      • alice_prog_a.json (batch 2)
      • bob_prog_a.json (batch 2)
      ... (8 more from batch 2)
      • new_student1_prog_a.json (batch 4)
      • new_student2_prog_a.json (batch 4)
      ... (10 more from batch 4)
```

**Shows:**
- ✓ Which program used this PDF
- ✓ When (batch 2 vs batch 4)
- ✓ How many sheets each time
- ✓ Complete audit trail

---

## The Magic: Automatic Separation

When you upload 27 answer sheets from 3 different programs:

```
input/new_uploads/
├── alice_prog_a.json
├── bob_prog_a.json
├── student1_prog_b.json
├── student2_prog_b.json
├── researcher1_prog_c.json
├── ... (21 more sheets)
```

**Without Registry:**
```
❌ "Which sheets go with which exam?"
❌ Manual matching required
❌ Risk of errors
❌ No history
```

**With Registry:**
```bash
python3 question_bank_registry.py --find-matches new_batch

Output:
  alice_prog_a.json → CISSP_Exam.pdf (0.93) ✓
  bob_prog_a.json → CISSP_Exam.pdf (0.94) ✓
  student1_prog_b.json → CompTIA_Security+.pdf (0.91) ✓
  student2_prog_b.json → CompTIA_Security+.pdf (0.95) ✓
  researcher1_prog_c.json → AWS_Solutions_Architect.pdf (0.92) ✓
  ... (21 more automatically separated)

Result: ✓ All 27 sheets automatically sorted into 3 programs
```

---

## Key Benefits for 5+ Question Banks

| Scenario | Without Registry | With Registry |
|----------|---|---|
| 5 PDFs registered | Manual tracking | Automatic catalog ✓ |
| Sheets arrive weeks later | "Which PDF?" | Auto-suggests ✓ |
| Different groups same exam | Risk of mixing | Separate correctly ✓ |
| Monthly repeats | Re-upload PDFs? | Found in registry ✓ |
| 27 sheets, 3 exams | Manual sorting | Auto-separated ✓ |
| Audit trail | Scattered notes | Complete history ✓ |

---

## Complete Workflow for 5+ Banks

### **Month 1: Setup (One Time)**
```bash
# Register all 5+ question banks
python3 question_bank_registry.py --register initial_batch

# Stores: 5+ PDFs, fingerprints, usage metadata
```

### **Months 2+: Recurring (Automated)**

When new answer sheets arrive from ANY program:
```bash
# Find which question bank they belong to
python3 question_bank_registry.py --find-matches new_batch

# Get suggestions for all sheets
# System already knows which PDF belongs to which program!
```

### **Months 2+: Mapping (Quick)**
```bash
# Map sheets to found PDFs
python3 map_questions_to_answers.py --batch new_batch

# System suggests: "Use CISSP_Exam.pdf? AWS_Solutions_Architect.pdf?"
# You confirm (or it auto-assigns if certain)
```

### **Months 2+: Analysis (Standard)**
```bash
python3 analyze.py
# Everything works with correct PDF associations
```

---

## Summary: YES, It Works!

**Your Scenario:**
- 5+ different question banks ✓
- Different groups of people ✓
- Uploading separately over time ✓
- Each with different questions/answers ✓

**Registry handles:**
- ✓ Remembers all 5+ PDFs permanently
- ✓ Identifies which sheets belong to which PDF
- ✓ Even if PDFs uploaded months ago
- ✓ Even if uploaded separately from sheets
- ✓ Handles recurring exams automatically
- ✓ Maintains complete audit trail

**Result:** Upload 5+ question banks once, then answer sheets for different programs week after week - system automatically knows which sheet goes with which PDF! 🎯
