# Answer Sheet Grouping & Exam Consistency

**Problem:** You have 5-6 answer sheets submitted. How do you know if they're all from the same question paper or if some are from different exam versions?

**Solution:** Automatic exam detection and grouping.

---

## Quick Answer

**The analyzer automatically detects if answer sheets belong to the same exam** by comparing:
- ✓ Question count (50, 100, 125 questions?)
- ✓ Question pattern (Q1-Q125, 1-50, Q.1-Q.25?)
- ✓ Column structure (same headers?)

If all sheets match → **Same exam ✓**  
If sheets differ → **Different exams detected ⚠️** → Groups them for you

---

## How It Works

### Exam Signature Extraction

Each answer sheet gets a "signature":

```
john_doe.json
├─ Questions: Q1, Q2, Q3, ..., Q125
├─ Count: 125
├─ Pattern: Q-prefixed
└─ Signature Hash: 12345abc

jane_smith.json
├─ Questions: Q1, Q2, Q3, ..., Q125
├─ Count: 125
├─ Pattern: Q-prefixed
└─ Signature Hash: 12345abc  ← SAME!

bob_wilson.json
├─ Questions: Q1, Q2, Q3, ..., Q50
├─ Count: 50
├─ Pattern: Q-prefixed
└─ Signature Hash: 67890def  ← DIFFERENT!
```

**Matching hashes = Same exam**  
**Different hashes = Different exams**

---

## Scenario: 5-6 Sheets from Same Exam

**Directory:**
```
answers/july12/
├── john_doe.json       (125 questions)
├── jane_smith.json     (125 questions)
├── alice_brown.json    (125 questions)
├── bob_wilson.json     (125 questions)
├── charlie_davis.json  (125 questions)
└── diana_evans.json    (125 questions)
```

**Run:**
```bash
python3 detect_exam_consistency.py --batch july12
```

**Output:**
```
📊 EXAM CONSISTENCY CHECK: JULY12
════════════════════════════════════════════════════════════════════════════════

Files checked: 6
Groups found: 1

📊 GROUP DETAILS:
────────────────────────────────────────────────────────────────────────────────

Group 1:
  Files: 6
  Questions: 125
  Pattern: Q-prefixed
  Files:
    • john_doe.json
    • jane_smith.json
    • alice_brown.json
    • bob_wilson.json
    • charlie_davis.json
    • diana_evans.json

📋 RECOMMENDATIONS:
  ✓ All 6 files are from SAME exam

════════════════════════════════════════════════════════════════════════════════
```

✅ **All 6 sheets are from the same exam!** Ready to analyze.

---

## Scenario: Mixed - 5-6 Sheets from DIFFERENT Exams

**Directory:**
```
answers/july12/
├── john_doe.json       (125 questions - Full exam)
├── jane_smith.json     (125 questions - Full exam)
├── alice_brown.json    (125 questions - Full exam)
├── bob_wilson.json     (50 questions - Practice test)
├── charlie_davis.json  (50 questions - Practice test)
└── diana_evans.json    (50 questions - Practice test)
```

**Run:**
```bash
python3 detect_exam_consistency.py --batch july12
```

**Output:**
```
📊 EXAM CONSISTENCY CHECK: JULY12
════════════════════════════════════════════════════════════════════════════════

Files checked: 6
Groups found: 2

📊 GROUP DETAILS:
────────────────────────────────────────────────────────────────────────────────

Group 1:
  Files: 3
  Questions: 125
  Pattern: Q-prefixed
  Files:
    • john_doe.json
    • jane_smith.json
    • alice_brown.json

Group 2:
  Files: 3
  Questions: 50
  Pattern: Q-prefixed
  Files:
    • bob_wilson.json
    • charlie_davis.json
    • diana_evans.json

⚠️  ISSUES:
  • Found 2 different exam versions

📋 RECOMMENDATIONS:
  Group 1: 3 file(s) with 125 questions
  Group 2: 3 file(s) with 50 questions

⚠️  Multiple exam versions detected!
  Option 1: Move to separate batch directories
  Option 2: Add exam_version metadata to each file
```

⚠️ **Detected 2 different exam types!** Need to organize.

---

## Using Group Organization

### Automatic Group Manifests

```bash
python3 detect_exam_consistency.py --batch july12 --fix-groups
```

Creates manifest files:

```
answers/july12/
├── GROUP_1_manifest.json
├── GROUP_2_manifest.json
└── EXAM_GROUPS_SUMMARY.json
```

**GROUP_1_manifest.json:**
```json
{
  "group": 1,
  "exam_signature": {
    "question_count": 125,
    "question_pattern": "Q-prefixed",
    "questions_sample": ["Q1", "Q2", "Q3", "Q4", "Q5"]
  },
  "files": [
    "john_doe.json",
    "jane_smith.json",
    "alice_brown.json"
  ],
  "file_count": 3
}
```

**EXAM_GROUPS_SUMMARY.json:**
```json
{
  "total_groups": 2,
  "total_files": 6,
  "groups": [
    {
      "group": 1,
      "file_count": 3,
      "question_count": 125,
      "manifest": "GROUP_1_manifest.json"
    },
    {
      "group": 2,
      "file_count": 3,
      "question_count": 50,
      "manifest": "GROUP_2_manifest.json"
    }
  ]
}
```

---

## Organizing Mixed Exams

### Option 1: Separate Batch Directories (Recommended)

If you have 5-6 sheets from different exams:

**BEFORE:**
```
answers/july12/
├── john_doe.json       (full exam)
├── jane_smith.json     (full exam)
├── alice_brown.json    (full exam)
├── bob_wilson.json     (practice)
├── charlie_davis.json  (practice)
└── diana_evans.json    (practice)
```

**AFTER:** Split into logical batches

```
answers/july12_full_exam/
├── john_doe.json
├── jane_smith.json
└── alice_brown.json

answers/july12_practice_test/
├── bob_wilson.json
├── charlie_davis.json
└── diana_evans.json
```

**Run analysis separately:**
```bash
python3 analyze.py
# Choose: july12_full_exam
# Later: python3 analyze.py
# Choose: july12_practice_test
```

### Option 2: Add Exam Version Metadata

Keep in same batch, add version info:

**student_roster.json:**
```json
{
  "batches": {
    "july12": {
      "students": [
        {
          "name": "John Doe",
          "exam_version": "july12_full_exam.pdf"
        },
        {
          "name": "Jane Smith",
          "exam_version": "july12_full_exam.pdf"
        },
        {
          "name": "Bob Wilson",
          "exam_version": "july12_practice_test.pdf"
        }
      ]
    }
  }
}
```

**Each answer file:**
```json
{
  "student_name": "John Doe",
  "exam_version": "july12_full_exam",
  "answers": { "Q1": "A", ... }
}
```

---

## Integration with Setup Wizard

The setup wizard now automatically checks:

```bash
python3 analyze.py
# Choose: [1] Batch Analysis
# Enter: july12

Setup wizard output:
✓ Found 6 answer files for 'july12'

🔍 Checking exam consistency...
  ✓ Analyzing file signatures...
  
  ✓ Group 1: 3 files, 125 questions
  ✗ Group 2: 3 files, 50 questions

⚠️  Multiple exam versions detected!
  Run: python3 detect_exam_consistency.py --batch july12 --detailed
  Use: --fix-groups to organize
  
❌ Setup validation failed. Please fix the issues above.
```

**Analysis blocked until you organize sheets!**

---

## Detailed Analysis

```bash
python3 detect_exam_consistency.py --batch july12 --detailed
```

Shows per-file breakdown:

```
FILE: john_doe.json
  Questions: 125
  Pattern: Q-prefixed
  Hash: 12345abc
  Status: ✓ Consistent with Group 1

FILE: bob_wilson.json
  Questions: 50
  Pattern: Q-prefixed
  Hash: 67890def
  Status: ⚠️ Different - Group 2
```

---

## Supported Answer Formats

The detector recognizes these question patterns:

| Format | Example | Detection |
|--------|---------|-----------|
| Q-prefixed | Q1, Q2, Q3...Q125 | ✓ Detects |
| Numeric | 1, 2, 3...125 | ✓ Detects |
| With Dots | Q.1, Q.2, Q.3 | ✓ Detects |
| Custom | Q01, Q02, Q03 | ✓ Detects |
| Mixed | 1Q, 2Q, 3Q | ⚠ Flags as unusual |

---

## What Gets Compared

### Matching Detection (Same Exam)

✅ **SAME if:**
- Question count matches (both 125)
- Question pattern matches (both Q-prefixed)
- Column structure matches
- All questions in same order

### Different Detection (Different Exams)

❌ **DIFFERENT if:**
- Question count differs (125 vs 50)
- Question pattern differs (Q-prefixed vs numeric)
- Column structure differs
- Any significant variation

---

## Complete Workflow

### 1. Place 5-6 Answer Sheets

```
answers/july12/
├── sheet1.json (125 Q)
├── sheet2.json (125 Q)
├── sheet3.json (125 Q)
├── sheet4.json (50 Q)
├── sheet5.json (50 Q)
└── sheet6.json (50 Q)
```

### 2. Run Setup Wizard

```bash
python3 analyze.py
# Choose batch: july12
# Wizard checks exam consistency
# Detects 2 different exam types
# ❌ Blocks analysis until fixed
```

### 3. Check What's Different

```bash
python3 detect_exam_consistency.py --batch july12 --detailed
# Shows which sheets belong to which exam
```

### 4. Organize Sheets

**Option A:** Create separate batches
```bash
mkdir answers/july12_exam1 answers/july12_exam2
mv sheet1.json sheet2.json sheet3.json answers/july12_exam1/
mv sheet4.json sheet5.json sheet6.json answers/july12_exam2/
```

**Option B:** Add metadata to student roster
```json
{
  "name": "Student 1",
  "exam_version": "july12_exam1.pdf"
}
```

### 5. Verify Consistency

```bash
python3 detect_exam_consistency.py --batch july12_exam1
# Output: ✓ All 3 files are from SAME exam
```

### 6. Run Analysis

```bash
python3 analyze.py
# Choose: july12_exam1
# ✅ All sheets match → Analysis proceeds
```

---

## Troubleshooting

### Q: "Multiple exam versions detected" - What does this mean?

**Answer:** The sheets have different question counts or patterns.

**Fix:** Use `--detailed` to see which sheets are different
```bash
python3 detect_exam_consistency.py --batch july12 --detailed
```

### Q: Can I analyze mixed exams together?

**Answer:** ❌ Not recommended. Use separate batches instead.

**Why:** Different question counts = incomparable scores

### Q: My sheets look identical but detector says different?

**Answer:** Check:
- [ ] All have same number of questions (Q1-Q125)?
- [ ] Same question naming (all Q-prefixed)?
- [ ] Same column count and names?

**Fix:** Run detailed analysis
```bash
python3 detect_exam_consistency.py --batch july12 --detailed
```

### Q: How does it handle Excel files vs JSON?

**Answer:** Extracts question count and pattern from both:
- **JSON:** Counts "answers" keys (Q1, Q2, etc.)
- **Excel:** Counts rows in first column

---

## Summary

| Scenario | Detection | Action |
|----------|-----------|--------|
| 6 sheets, same exam | ✓ Group 1 | ✅ Analyze directly |
| 6 sheets, 2 exams | ✓ Group 1 + 2 | ⚠️ Organize first |
| 6 sheets, mixed formats | ✓ Detected | ⚠️ Standardize formats |
| 6 sheets, irregular | ⚠ Flagged | ❌ Investigate |

**Bottom Line:** Know what you're analyzing before running it. The detector ensures sheets are from the same exam.
