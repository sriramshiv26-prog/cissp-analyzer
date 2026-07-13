# Interactive Answer Key Validator

## Overview

The **Interactive Validator** improves answer key extraction accuracy by:
1. ✓ Automatically accepting high-confidence answers (95%+)
2. ⚠ Asking you to review low-confidence answers (<75%)
3. 📝 Recording all corrections for audit trail
4. 🎯 Preventing analysis from running on wrong answer keys

## How It Works

### Confidence Scoring

Each extracted answer gets a confidence score (0-100%):

```
"correct answer is B" in context  → 95% (strong pattern)
"answer" keyword found nearby      → 75% (moderate pattern)
Ambiguous/weak pattern             → 50% (requires review)
```

### Workflow

```
PDF Extraction
    ↓
Confidence Calculation
    ↓
Split: High (95%+) vs Low (<75%)
    ↓
Auto-Accept High Confidence
    ↓
Interactive Review of Low Confidence
    ├─ [C]onfirm  → Accept extracted answer
    ├─ [A/B/C/D]  → Correct to different answer
    ├─ [S]kip     → Omit this question
    └─ [Q]uit     → Stop validation
    ↓
Save Answer Key + Validation Report
```

## Using Interactive Validator

### Option 1: Automatic (Recommended)

The validator runs automatically when you use `run_exam_analysis.py`:

```bash
python3 run_exam_analysis.py
```

When asked for PDF, it will:
1. Extract all answers
2. Show confidence summary
3. Ask to review low-confidence questions
4. Generate validated answer key

### Option 2: Manual Validation

Create a test exam and run validation:

```python
from answer_key_manager import AnswerKeyManager
from pathlib import Path

exam_folder = Path('exams/TEST_EXAM')
exam_folder.mkdir(exist_ok=True)
(exam_folder / 'answer_keys').mkdir(exist_ok=True)

manager = AnswerKeyManager(exam_folder)
answer_key = manager.load_answer_key(
    '/path/to/exam.pdf',
    interactive=True,
    use_validator=True
)
```

## Example Session

```
================================================================================
ANSWER KEY MANAGER
================================================================================

Step 1: Attempting automatic extraction from PDF...
Extracted: 161 answers
Confidence: 95%

Step 2: Interactive validation of extracted answers...
Review 161 extracted answers.
Confidence < 75% will need your confirmation.

✓ Auto-accepted: 155 (confidence ≥ 75%)
⚠ Need review: 6 (confidence < 75%)

================================================================================
LOW-CONFIDENCE ANSWERS - PLEASE REVIEW
================================================================================

Q45: Confidence 65%
  Context: ... encryption algorithm is A. AES B. RSA C. SHA-256 D. TLS ...
  Extracted: C

  [C]onfirm | [S]kip | [A/B/C/D] to correct | [Q]uit: D
  ✓ Corrected to D

Q87: Confidence 72%
  Context: ... network segmentation A. Firewall B. VLAN C. MAC filtering ...
  Extracted: A

  [C]onfirm | [S]kip | [A/B/C/D] to correct | [Q]uit: C
  ✓ Corrected to C

[... more questions ...]

================================================================================
VALIDATION COMPLETE
================================================================================
Auto-accepted:      155
Manual confirmed:   3
Corrected:          2
Skipped:            1
Total validated:    161

Corrections made:
  Q45: C → D
  Q87: A → C

✓ Validation report saved: answer_keys/validation_report.json
```

## Validation Report

After validation, a `validation_report.json` is saved:

```json
{
  "timestamp": "2026-07-13T19:30:00",
  "summary": {
    "total_questions": 161,
    "auto_accepted": 155,
    "manual_confirmed": 3,
    "corrected": 2,
    "skipped": 1
  },
  "corrections": {
    "45": ["C", "D"],
    "87": ["A", "C"]
  },
  "skipped_questions": [92],
  "confidence_scores": {
    "1": 0.95,
    "2": 0.95,
    ...
    "45": 0.65,
    ...
  }
}
```

## When to Use Each Option

| Scenario | Option | Why |
|----------|--------|-----|
| First time with PDF | Use validator | Catches errors before analysis |
| High confidence (95%+) | Skip validator | Safe to use auto-extracted |
| Unsure about answers | Manual entry | Full control, no extraction |
| Edit existing answers | Review & correct | Modify specific questions |

## Keyboard Commands

During interactive review:

```
[C]onfirm    → Accept extracted answer as-is
[A/B/C/D]    → Replace with different answer
[S]kip       → Omit this question (it won't be scored)
[Q]uit       → Stop validation now
```

## Benefits

✅ **Catches errors early** — Before analysis runs  
✅ **Shows context** — See PDF text around each answer  
✅ **Fast approval** — High-confidence answers auto-accepted  
✅ **Auditable** — Validation report tracks all changes  
✅ **Flexible** — Can skip, correct, or confirm per question  
✅ **Non-destructive** — Can re-extract if needed  

## Tips

1. **First exam**: Always use validator to verify extraction works
2. **Tricky PDFs**: Lower confidence threshold if many false positives
3. **Batch exams**: Run validator once, then can skip for similar PDFs
4. **Corrections**: Review validation_report.json to learn what went wrong

## Troubleshooting

**Q: All answers showing low confidence**
→ PDF format is unusual. Use manual entry or upload JSON file.

**Q: Can't see context clearly**
→ Context is truncated. Use [C]onfirm to accept or [A/B/C/D] to correct.

**Q: Want to skip validator**
→ Run `run_exam_analysis.py` and choose option "2) Use extracted" when asked.

**Q: Need to fix answer key after validation**
→ Edit `answer_keys/answer_key.json` manually and re-run analysis.
