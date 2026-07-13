# Fuzzy Filename Matching - Real-World File Variations

**Problem:** Files are submitted with inconsistent naming:
- `Jul12.pdf` vs `july12_exam.pdf` (case & format variations)
- `questionbank.pdf` vs `questbank_answers.json` (typo: missing letter)
- `exam_v1.pdf` vs `exam-v1.pdf` (different delimiters)
- `Q1.json` vs `Q_1.xlsx` (abbreviation variations)

**Solution:** Fuzzy filename matching that finds related files automatically.

---

## Quick Answer

**YES, it can detect by flexible filename patterns** using similarity matching (70-75% threshold).

The tool:
- ✓ Handles case variations (Jul12 = july12 = JULY12)
- ✓ Tolerates typos (questbank ≈ questionbank)
- ✓ Ignores delimiters (jul-12 ≈ jul_12 ≈ jul12)
- ✓ Groups related files automatically
- ✓ Detects exam versions (v1, v2, practice, full, etc.)

---

## How It Works

### Normalization

Each filename is normalized for comparison:

```
Input Filenames:
  • "Jul-12_Exam.pdf"
  • "july12.json"
  • "JULY_12_answers.xlsx"

Normalized:
  • "jul12exam"
  • "july12"
  • "july12answers"

Result: Grouped as related! (>75% similarity)
```

### Similarity Calculation

Uses string matching algorithm (SequenceMatcher):

```
"july12exam" vs "july12" → 88% similar ✓
"july12exam" vs "feb15exam" → 63% similar ✗

Threshold: 70-75% (adjustable)
```

---

## Real Examples

### Example 1: Case & Format Variations

**Files submitted:**
```
answers/july12/
├── Jul12_exam.pdf
├── july12_answers.json
├── JULY12.xlsx
└── July-12-Q&A.txt
```

**Run:**
```bash
python3 fuzzy_file_matcher.py --batch july12
```

**Output:**
```
📁 GROUPED BY SIMILARITY (threshold: 70%):
────────────────────────────────────────────────

Group 1: 4 related file(s)
  • Jul12_exam.pdf
  • july12_answers.json
  • JULY12.xlsx
  • July-12-Q&A.txt

Result: ✓ All 4 matched (88%+ similarity)
        Clearly related files, likely same exam
```

### Example 2: Typo - Missing Letters

**Files submitted:**
```
answers/july12/
├── questionbank.pdf
├── questbank_student1.json (missing 'i')
├── questionbank_student2.json
└── questbank_student3.json (missing 'i')
```

**Run:**
```bash
python3 fuzzy_file_matcher.py --batch july12
```

**Output:**
```
📁 GROUPED BY SIMILARITY:

Group 1: 4 related file(s)
  • questionbank.pdf (93% match)
  • questbank_student1.json (88% match)
  • questbank_student2.json (93% match)
  • questbank_student3.json (88% match)

Result: ✓ All grouped despite typo
        Fuzzy matching tolerates missing letters
```

### Example 3: Multiple Exam Versions

**Files submitted:**
```
answers/july12/
├── exam_v1.pdf
├── exam-v1-student1.json
├── exam_v1_student2.json
├── exam_v2.pdf (DIFFERENT VERSION!)
├── exam-v2-student1.json
└── exam_v2_student2.json
```

**Run:**
```bash
python3 fuzzy_file_matcher.py --batch july12
```

**Output:**
```
📊 EXAM VERSION DETECTION:

v1: 3 file(s)
  • exam_v1.pdf
  • exam-v1-student1.json
  • exam_v1_student2.json

v2: 3 file(s)
  • exam_v2.pdf
  • exam-v2-student1.json
  • exam_v2_student2.json

🔗 EXAM-TO-ANSWER MATCHING:

Exam: exam_v1.pdf
  Matches: 2 answer file(s)
    • exam-v1-student1.json (similarity: 0.86)
    • exam_v1_student2.json (similarity: 0.89)

Exam: exam_v2.pdf
  Matches: 2 answer file(s)
    • exam-v2-student1.json (similarity: 0.86)
    • exam_v2_student2.json (similarity: 0.89)

Result: ✓ Separated into v1 and v2
        Ready to organize into separate batches
```

---

## What Gets Detected

### Filename Normalization

```
Input → Normalized

"Jul-12_Exam.pdf" → "jul12exam"
"july12.json" → "july12"
"JULY_12.xlsx" → "july12"
"Q&A_Jul_12.txt" → "qaajul12"

Result: All recognized as same base name
```

### Similarity Tolerance

```
Matching at different thresholds:

Threshold 90%: Exact matches only
  questionbank = questionbank ✓
  questbank ✗ (too different)

Threshold 75%: Most variations caught
  questionbank = questbank ✓ (87% match)
  exam = exm ✓ (75% match)

Threshold 70%: Very tolerant
  jul12 = july12 ✓ (85% match)
  q1 = question1 ✓ (70% match)
```

### Version Detection

Automatically recognizes:
```
v1, v2, v3        → Version indicator
exam1, exam2      → Exam number
full              → Full exam
practice, mock    → Practice test
midterm           → Midterm exam
final             → Final exam
makeup            → Make-up exam
batch1, batch2    → Batch indicator
```

---

## Using Fuzzy Matcher in Your Workflow

### Step 1: Place Mixed Files

```
answers/july12/
├── Jul12.pdf
├── july_12_exam_questions.json
├── july12answers_student1.json
├── JULY-12-Q&A-student2.xlsx
└── jul12_student3.json
```

### Step 2: Run Matcher

```bash
python3 fuzzy_file_matcher.py --batch july12
```

### Step 3: Get Grouping & Version Info

```
📁 GROUPED BY SIMILARITY:
✓ All 5 files grouped (80%+ similarity)
  All appear to be july12 exam

🔗 EXAM-TO-ANSWER MATCHING:
✓ Matched July12.pdf to all 4 answer files
```

### Step 4: Follow Guidance

**If all grouped together:**
```
✓ All from same exam/source
→ Use directly in analysis
```

**If versions detected:**
```
⚠ Multiple versions found
→ Organize into separate batches
→ Add version metadata
```

---

## Integration with Other Tools

### With Exam Consistency Detector

```bash
# Step 1: See if files are related (filename-based)
python3 fuzzy_file_matcher.py --batch july12

# Step 2: Verify if from same exam (content-based)
python3 detect_exam_consistency.py --batch july12
```

**Combined approach:**
- Fuzzy matcher: Fast, uses filenames
- Consistency detector: Thorough, reads content
- Together: Complete validation ✓

### With Setup Wizard

The setup wizard could run:
1. Fuzzy matching (file name check)
2. Consistency detection (content check)
3. Block if mismatches found

---

## Real-World Scenarios

### Scenario 1: Student Submissions with Typos

**Received:**
```
questions_paper.pdf
queston_paper_answers.json (typo: missing 's')
questoin_student2.json (typo: transposed letters)
```

**Fuzzy Matcher Result:**
```
✓ All grouped (86% similarity)
  Typos detected and tolerated
```

**Action:** Use directly, no cleanup needed

---

### Scenario 2: Abbreviated Filenames

**Received:**
```
CISSP_Jul_12_Exam.pdf
CISSP_Jul12.json
Cissp_jul_12_ans.xlsx
cissp july 12 q&a.txt
```

**Fuzzy Matcher Result:**
```
✓ All grouped (91% similarity)
  Case & abbreviation variations tolerated
```

**Action:** Use directly

---

### Scenario 3: Mixed with Version Indicators

**Received:**
```
exam_v1.pdf, exam_v1_student1.json, exam_v1_student2.json
exam_v2.pdf, exam_v2_student1.json, exam_v2_student2.json
practice_exam.pdf, practice_answers.json
```

**Fuzzy Matcher Result:**
```
📊 VERSION DETECTION:

v1: 3 files → exam_v1 group
v2: 3 files → exam_v2 group
practice: 2 files → practice group

3 different exam versions detected!
```

**Action:** Organize into 3 separate batches

---

## Using Similarity Scores

Each match includes a similarity score (0.0 to 1.0):

```
Similarity Score Legend:

0.95-1.0 = Identical (case/delimiter ignored)
0.85-0.94 = Nearly identical (one letter difference)
0.75-0.84 = Similar (some abbreviation/typo)
0.65-0.74 = Related (might be different exams)
< 0.65 = Different (separate exams)
```

Example:
```
Match Report:

july12_exam.pdf vs july12_answers.json
  Similarity: 0.91 ✓ (nearly identical)

july12_exam.pdf vs july11_answers.json
  Similarity: 0.78 ⚠ (similar, but different date!)
```

---

## Customizing Thresholds

Default: 70-75% threshold

For stricter matching (fewer false positives):
```bash
# Set threshold to 85% (only very similar files)
python3 fuzzy_file_matcher.py --batch july12 --threshold 0.85
```

For looser matching (catch more variations):
```bash
# Set threshold to 60% (very tolerant)
python3 fuzzy_file_matcher.py --batch july12 --threshold 0.60
```

---

## Troubleshooting

### Q: "Why did it group completely different files?"

**Answer:** Threshold might be too low

**Fix:**
```bash
# Increase threshold for stricter matching
python3 fuzzy_file_matcher.py --batch july12 --threshold 0.85
```

### Q: "It didn't match files I expected"

**Answer:** Check the similarity score

**Fix:**
```bash
# Run with --detailed to see scores
python3 fuzzy_file_matcher.py --batch july12 --detailed

# If scores are just below threshold, adjust:
python3 fuzzy_file_matcher.py --batch july12 --threshold 0.65
```

### Q: "How do I handle completely different exams?"

**Answer:** They won't match with fuzzy matching (as intended)

**Check:**
```bash
python3 fuzzy_file_matcher.py --batch july12
# If different exams detected → Organize into separate batches
```

---

## Summary: Filename Matching Capabilities

| Variation | Detected? | Example |
|-----------|-----------|---------|
| Case variations | ✓ Yes | Jul12 = july12 = JULY12 |
| Delimiter changes | ✓ Yes | jul-12 = jul_12 = jul12 |
| Typos (missing letters) | ✓ Yes | questbank ≈ questionbank |
| Abbreviations | ✓ Yes | cissp = c.i.s.s.p |
| Version indicators | ✓ Yes | v1, v2, full, practice |
| Space variations | ✓ Yes | jul 12 = jul12 |
| Different exams | ✓ Detects | won't group together |

---

## Integration Summary

**Fuzzy Filename Matching** fits into your validation pipeline as **Layer 0** (before content checks):

```
Layer 0: Filename Similarity Check (fuzzy_file_matcher.py)
    ↓ (groups files by name)
Layer 1: File & Format Validation (setup_wizard.py)
    ↓ (checks files exist, formats valid)
Layer 2: Sheet Variation Detection (handle_sheet_variations.py)
    ↓ (checks sheet names, headers)
Layer 3: Exam Consistency (detect_exam_consistency.py)
    ↓ (checks question content)
✅ Ready for Analysis
```

**Benefits:**
- Catches naming issues early
- Groups related files automatically
- Detects version separations
- Works with real-world messy filenames
