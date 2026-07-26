# Metadata Auto-Generator — User Guide

**Version:** 2.1.0  
**Feature:** Automatic metadata generation for CISSP question banks

---

## What It Does

The Metadata Auto-Generator reads a CISSP exam PDF and automatically produces a structured `metadata.json` file containing per-question metadata:

| Field | Example Values |
|-------|----------------|
| `domain` | "Security and Risk Management", "Cryptography", "IAM" |
| `topic` | "Risk assessment", "AES-256", "MFA" |
| `difficulty` | "Easy", "Medium", "Hard" |
| `question_type` | "Knowledge", "Application", "Analysis" |
| `exam_trick` | Extracted from PDF tags if present |

The output is saved to `data/metadata/YYYY-MM-DD/{exam_id}/metadata.json` and can be loaded by `DomainMapper` for analytics.

---

## How to Run It

### Option 1: Via the Interactive Menu

Run the CISSP Analyzer and choose the "Generate Metadata for Question Bank" option:

```
[1] Process new answer sheets
[2] Generate class report
[3] Generate Metadata for Question Bank   <-- new option
[4] Back to main menu
```

You will be prompted for:
- **Exam ID** — a unique identifier for this exam (e.g. `cissp-2024-q1`)
- **PDF path** — full path to the exam question bank PDF

The generator will run automatically and display a summary:

```
Exam ID:         cissp-2024-q1
Total Questions: 125
Coverage:        100%
Method:          ai
Output:          data/metadata/2026-07-25/cissp-2024-q1/metadata.json
```

### Option 2: Programmatic API

```python
from cissp_analyzer.metadata_generator import MetadataGenerator

gen = MetadataGenerator(
    exam_id="cissp-2024-q1",
    pdf_path="/path/to/exam.pdf",
    output_dir="data/metadata",  # optional, default shown
)

result = gen.run(completion_method="auto")
print(result)
# {
#   "exam_id": "cissp-2024-q1",
#   "total_questions": 125,
#   "coverage": 1.0,
#   "method": "ai",
#   "output_path": "data/metadata/2026-07-25/cissp-2024-q1/metadata.json"
# }
```

### Option 3: During Answer Sheet Processing

```python
from cissp_analyzer.exam_processor import ExamProcessor

processor = ExamProcessor(exam_folder)
summary = processor.process_new_files(generate_metadata=True)
print(summary["metadata_result"])
```

---

## Completion Methods

The generator supports three ways to fill metadata gaps (questions without tags in the PDF):

### `auto` (recommended)
- If Ollama is running locally, it uses the `qwen2.5-coder:7b` model to classify each question.
- If Ollama is not available, falls back to `defaults` silently.

```python
result = gen.run(completion_method="auto")
```

### `defaults`
All gap questions receive placeholder metadata:
```json
{
  "domain": "Unmapped",
  "topic": "Unmapped",
  "difficulty": "Unknown",
  "question_type": "Unknown"
}
```
You can edit these later using `MetadataReviewer` or by editing the JSON directly.

```python
result = gen.run(completion_method="defaults")
```

### `manual`
Prompts for a CSV file path. The CSV must have columns:
```
question_number,domain,topic,difficulty,question_type
1,Cryptography,AES-256,Medium,Knowledge
2,IAM,MFA,Easy,Knowledge
```

```python
result = gen.run(completion_method="manual")
# Prompts: "Enter path to metadata CSV: "
```

---

## When to Use Ollama vs Defaults

| Situation | Recommendation |
|-----------|----------------|
| Quick setup, don't care about accuracy | Use `defaults` |
| Exam PDF has structured tags (`[Domain: X]`) | Use `auto` — extractor handles most questions |
| Exam PDF has no tags | Use `auto` with Ollama, or `manual` CSV |
| Batch processing overnight | Use `auto` — Ollama handles it silently |
| No Ollama installed | Use `defaults` or `manual` |
| High-accuracy requirement | Use `manual` CSV with expert-curated data |

### Checking if Ollama is Available

```python
from cissp_analyzer.ollama_analyzer import OllamaAnalyzer

analyzer = OllamaAnalyzer()
print(analyzer.get_status())
# "Ollama available (model: qwen2.5-coder:7b)"
# -- or --
# "Ollama unavailable (fallback mode)"
```

---

## Output Format

The generated `metadata.json` file contains:

```json
{
  "1": {
    "domain": "Security and Risk Management",
    "topic": "Risk assessment frameworks",
    "difficulty": "Medium",
    "question_type": "Analysis",
    "exam_trick": "Distractor B sounds correct but is a management concept"
  },
  "2": {
    "domain": "Cryptography",
    "topic": "Symmetric encryption",
    "difficulty": "Easy",
    "question_type": "Knowledge",
    "exam_trick": "None"
  }
}
```

The file is stored at:
```
data/
  metadata/
    2026-07-25/
      cissp-2024-q1/
        metadata.json
```

---

## Reviewing and Editing Metadata

Before saving, the pipeline displays a terminal summary. You can also programmatically review and edit using `MetadataReviewer`:

```python
from cissp_analyzer.metadata_reviewer import MetadataReviewer

reviewer = MetadataReviewer(metadata_dict)

# Display summary table
print(reviewer.display_summary())

# Edit a field
reviewer.edit_question(q_num=5, field="domain", value="Cryptography")
reviewer.edit_question(q_num=5, field="difficulty", value="Hard")

# Get summary of what was changed
print(reviewer.get_edit_summary())
# "2 question(s) edited:
#   Q5: domain='Cryptography', difficulty='Hard'
# Fields changed: {'difficulty': 1, 'domain': 1}"

# Get final metadata with edits applied
final = reviewer.get_reviewed_metadata()
```

---

## Loading Generated Metadata in DomainMapper

Once generated, the metadata is automatically picked up by `DomainMapper`:

```python
from cissp_analyzer.domain_mapper import DomainMapper

# Loads from data/metadata/YYYY-MM-DD/cissp-2024-q1/metadata.json
mapper = DomainMapper(exam_id="cissp-2024-q1")
```

`DomainMapper` searches for the most recent date folder containing your `exam_id`, so re-running the generator creates a new dated entry without overwriting old ones.

---

## Pipeline Architecture

```
PDF File
   |
   v
PDFMetadataExtractor
   - Reads PDF pages
   - Finds [Domain: X], [Difficulty: Y] tags
   - Returns: extracted_metadata + gaps list
   |
   v
MetadataCompleter
   - Fills gaps via: defaults / manual CSV / Ollama
   - Returns: combined_metadata (extracted + filled)
   |
   v
MetadataReviewer
   - Displays summary table in terminal
   - Tracks edits
   - Returns: reviewed_metadata
   |
   v
data/metadata/YYYY-MM-DD/{exam_id}/metadata.json
   |
   v
DomainMapper (reads back on demand)
```

---

## Troubleshooting

**"PDF not found"**
- Check the path is correct and the file exists.
- Use absolute paths to avoid working-directory issues.

**"Ollama unavailable (fallback mode)" but Ollama is installed**
- Make sure Ollama is running: `ollama serve`
- Check it responds: `curl http://localhost:11434/api/tags`

**Coverage is less than 100%**
- The PDF may not have domain tags for all questions.
- Run with `completion_method="manual"` and provide a CSV.
- Or accept the defaults and edit the JSON manually.

**Generated metadata.json has "Unmapped" entries**
- These are the gap questions that received default values.
- Open the file and edit, or re-run with Ollama or a manual CSV.
