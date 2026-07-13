# Exam Versioning & Multiple Question Papers

**Question:** How does the analyzer know which student answered which exam paper?

**Answer:** By **question numbering** (Q1, Q2, Q3...) and exam metadata.

---

## Current Design

### Single Exam Version (Default)

**Assumption:** All students in batch took the SAME exam paper.

```
Batch: july12
├── Exam PDF: exams/july12_exam.pdf
│   ├── Q1: "Which of the following..."
│   ├── Q2: "Consider this scenario..."
│   └── ... Q125
│
└── Student Answers:
    ├── john_doe.json → {"answers": {"Q1": "A", "Q2": "B", ...}}
    ├── jane_smith.json → {"answers": {"Q1": "C", "Q2": "A", ...}}
    └── bob_wilson.json → {"answers": {"Q1": "B", "Q2": "D", ...}}
```

**The Link:** Question numbering (Q1 = Q1 = Q1)

✅ **This works perfectly when:** All students took identical exam

---

## Multiple Exam Versions

### Scenario: Different Students, Different Exam Papers

What if:
- **Student 1** took **Version A** (questions ordered 1-125)
- **Student 2** took **Version B** (same questions, different order)
- **Student 3** took **Practice Test** (similar but different questions)

❌ **Without versioning:** Answers get matched to wrong questions!

---

## Solution: Exam Versioning

Add metadata to link students to their exam version:

### Method 1: Multiple Exam Files (Recommended)

```
exams/
├── july12_v1_exam.pdf    (Version A - 125 questions)
├── july12_v2_exam.pdf    (Version B - 125 questions, reordered)
└── july12_practice_exam.pdf

student_roster.json:
{
  "batches": {
    "july12": {
      "name": "July 12 Batch",
      "students": [
        {
          "name": "John Doe",
          "exam_version": "july12_v1_exam.pdf"
        },
        {
          "name": "Jane Smith",
          "exam_version": "july12_v2_exam.pdf"
        },
        {
          "name": "Bob Wilson",
          "exam_version": "july12_practice_exam.pdf"
        }
      ]
    }
  }
}
```

### Method 2: Embed Exam Version in Answer Sheet

```json
{
  "student_name": "John Doe",
  "exam_version": "july12_v1",
  "exam_date": "2026-07-12",
  "answers": {
    "Q1": "A",
    "Q2": "B"
  }
}
```

### Method 3: Naming Convention

```
Batch directory:
answers/july12/
├── v1/
│   ├── john_doe.json
│   └── alice_brown.json
├── v2/
│   ├── jane_smith.json
│   └── charlie_davis.json
└── practice/
    └── bob_wilson.json
```

---

## How Linking Works

### Single Version (Current Implementation)

```
Input:
  john_doe.json: {"answers": {"Q1": "A", "Q2": "B", ...}}
  july12_exam.pdf: contains Q1, Q2, Q3, ..., Q125

Process:
  1. Extract Q1 from PDF → Get definition of Q1
  2. Get student's answer to Q1 → "A"
  3. Compare → Correct/Incorrect
  4. Repeat for Q2...Q125

Result: Accurate scoring
```

### Multiple Versions (Requires Metadata)

```
Input:
  john_doe.json: {
    "exam_version": "july12_v1_exam.pdf",
    "answers": {"Q1": "A", "Q2": "B", ...}
  }
  july12_v1_exam.pdf: Q1="Which of...", Q2="Consider..."
  july12_v2_exam.pdf: Q1="Consider...", Q2="Which of..." (reordered)

Process:
  1. Read student's exam_version → "july12_v1_exam.pdf"
  2. Load that specific PDF
  3. Extract Q1 from july12_v1 → "Which of..."
  4. Compare to student's Q1 answer → "A"
  5. Score based on july12_v1 answer key

Result: Accurate scoring using correct exam version
```

---

## Implementing Exam Versioning

### Step 1: Prepare Exam PDFs

If students took different versions:

```bash
# Create exam files with version identifiers
cp exam_original.pdf exams/july12_v1_exam.pdf
cp exam_reordered.pdf exams/july12_v2_exam.pdf
cp practice_test.pdf exams/july12_practice_exam.pdf
```

### Step 2: Add Metadata to Student Roster

```json
{
  "batches": {
    "july12": {
      "name": "July 12 Batch",
      "exam_file": "exams/july12_v1_exam.pdf",  # Default/primary
      "students": [
        {
          "id": "S001",
          "name": "John Doe",
          "exam_version": "july12_v1_exam.pdf",  # Specific version
          "email": "john@example.com"
        },
        {
          "id": "S002",
          "name": "Jane Smith",
          "exam_version": "july12_v2_exam.pdf",  # Different version
          "email": "jane@example.com"
        }
      ]
    }
  }
}
```

### Step 3: Add Version to Answer Files

```json
{
  "student_name": "John Doe",
  "exam_version": "july12_v1_exam.pdf",
  "answers": {
    "Q1": "A",
    "Q2": "B"
  }
}
```

### Step 4: Analyzer Automatically Uses Correct Version

```
Process:
1. Read student's exam_version → "july12_v1_exam.pdf"
2. Load that PDF's question definitions
3. Extract Q1, Q2, Q3... from correct version
4. Match student answers to correct questions
5. Score accurately
```

---

## Implementation Checklist

### For Single Exam Version (Current)
- [ ] All students took same exam
- [ ] Exam PDF named: `exams/{batch}_exam.pdf`
- [ ] Answer sheets use Q1, Q2, Q3... (Q125)
- [ ] No version metadata needed

### For Multiple Exam Versions
- [ ] Create separate PDF for each version
  - `exams/july12_v1_exam.pdf`
  - `exams/july12_v2_exam.pdf`
- [ ] Add `exam_version` field to student_roster.json
- [ ] Add `exam_version` field to each answer JSON file
- [ ] Verify all questions are numbered consistently (Q1...Q125)

### For Mixed Scenarios
- [ ] Some students took Version A → `exam_version: "v1"`
- [ ] Some students took practice test → `exam_version: "practice"`
- [ ] Have a question mapping for each version

---

## Question Mapping & Answer Keys

### Current System
Uses built-in question metadata:

```python
question_metadata = {
  "Q1": {"domain": "Security & Risk", "type": "scenario"},
  "Q2": {"domain": "Asset Security", "type": "definition"},
  ...
}
```

### For Multiple Versions
Create version-specific mappings:

```json
{
  "july12_v1_exam": {
    "Q1": {"domain": "Security & Risk", "answer": "B"},
    "Q2": {"domain": "Asset Security", "answer": "C"},
    ...
  },
  "july12_v2_exam": {
    "Q1": {"domain": "Asset Security", "answer": "C"},
    "Q2": {"domain": "Security & Risk", "answer": "B"},
    ...
  }
}
```

---

## Common Questions

### Q: What if students took identical exams but submitted with different question numbering?

**Example:** 
- Student 1: Q1, Q2, Q3...
- Student 2: 1, 2, 3... (without "Q" prefix)

**Answer:** The auto-fixer normalizes this:
```bash
python3 auto_fix_answers.py --batch july12
# Converts: 1, 2, 3 → Q1, Q2, Q3
```

### Q: What if exam has questions in different order?

**Example:**
- Exam PDF: Questions 1, 2, 3, 4, 5
- Student answers: Q1="A", Q2="B", Q3="C"
- But student answered: PDF-Q5="A", PDF-Q2="B", PDF-Q3="C"

**Answer:** This requires explicit mapping (not auto-detected):

Add question mapping to answer sheet:
```json
{
  "student_name": "John Doe",
  "answer_mapping": {
    "Q1": "PDF-Q5",
    "Q2": "PDF-Q2",
    "Q3": "PDF-Q3"
  },
  "answers": {
    "Q1": "A",
    "Q2": "B"
  }
}
```

### Q: What if different students took completely different exams?

**Answer:** Treat as separate batches:

```
exams/
├── july12_beginners_exam.pdf
├── july12_advanced_exam.pdf

answers/
├── july12_beginners/
│   ├── student1.json
│   └── student2.json
└── july12_advanced/
    ├── student3.json
    └── student4.json

Run analysis separately:
  python3 analyze.py → batch: july12_beginners
  python3 analyze.py → batch: july12_advanced
```

---

## Real-World Scenarios

### Scenario 1: All Students Same Exam
```
july12_exam.pdf
├── student1.json (answers: Q1-Q125)
├── student2.json (answers: Q1-Q125)
└── student3.json (answers: Q1-Q125)

✅ Works out of box
```

### Scenario 2: Multiple Versions in Same Batch
```
july12_v1_exam.pdf
july12_v2_exam.pdf

student_roster.json:
  john_doe: exam_version = "v1"
  jane_smith: exam_version = "v2"

john_doe.json: exam_version: "july12_v1", answers: Q1-Q125
jane_smith.json: exam_version: "july12_v2", answers: Q1-Q125

✅ Works with metadata
```

### Scenario 3: Students Took Different Exams Entirely
```
july12_beginners_exam.pdf
july12_advanced_exam.pdf

student_roster.json splits them:
  "july12_beginners" batch: student1, student2
  "july12_advanced" batch: student3, student4

Run analysis for each batch separately

✅ Works by batch separation
```

### Scenario 4: Make-Up Exams (Different Dates)
```
july12_exam_v1_20260712.pdf  (original test)
july12_exam_makeup_20260714.pdf  (make-up version)

student_roster.json:
  john_doe: exam_version = "v1"
  jane_smith (makeup): exam_version = "makeup"

✅ Works with version metadata
```

---

## Summary

| Scenario | Solution | Effort |
|----------|----------|--------|
| All same exam | Default (no config) | ✅ Automatic |
| Multiple versions, same batch | Add `exam_version` metadata | ⚠️ Config file edit |
| Completely different exams | Create separate batches | ⚠️ Split into multiple runs |
| Question reordering | Add explicit mapping | ❌ Manual per student |
| Auto-fix formats (1,2,3 → Q1,Q2,Q3) | Run auto-fixer | ✅ One command |

**Bottom Line:**
- **Same exam?** Automatic ✅
- **Different versions?** Add metadata ⚠️
- **Different exams?** Different batches ✅
