# CISSP Analyzer - Setup Wizard Guide

## Fastest Way to Get Started

Use the interactive setup wizard for a guided experience:

```bash
python3 setup.py
```

This wizard will:
1. Ask for exam PDF path
2. Ask for answer key JSON path (or auto-extract)
3. Ask for output directory
4. Ask for each student name + Excel file
5. Auto-generate config
6. Auto-extract answer key from PDF
7. Regenerate question mappings
8. Run full batch analysis
9. Generate individual + class reports

## Manual Workflow (Advanced)

If you prefer manual control:

**Step 1: Create config file**
```json
{
  "exam_pdf": "/path/to/exam.pdf",
  "answer_key": "/path/to/answer_key.json",
  "output_dir": "outputs",
  "students": [
    {"name": "Student1", "excel": "/path/to/student1.xlsx"},
    {"name": "Student2", "excel": "/path/to/student2.xlsx"}
  ]
}
```

**Step 2: Extract answer key from PDF**
```bash
python3 extract_answer_key.py "exam.pdf" "answer_key.json"
```

**Step 3: Regenerate mappings**
```bash
python3 regenerate_mapping.py
```

**Step 4: Run batch analysis**
```bash
python3 run_batch.py batch_config.json
```

## File Requirements

### Exam PDF
- Must contain questions and answers
- Questions extracted automatically
- Answer key auto-extracted from "Correct Answer" section

### Student Excel Files
- **Column A**: "Question" (values 1-125)
- **Column B**: Student name (their answers: A, B, C, D)

Example:
```
| Question | StudentName |
|----------|-------------|
| 1        | B           |
| 2        | C           |
| 3        | B           |
```

### Multi-Part Answers
For questions with multiple parts (e.g., SOC levels, cable types):
- Accepted formats: `1-B,2-A,3-C` or `1B2A3C` or `B,A,C` or `BAC`
- System auto-normalizes all formats

## Output Reports

After analysis, check `outputs/` folder:

### Individual Reports (per student)
- **Sheet 1**: Performance Summary (score, status, message)
- **Sheet 2**: Q&A Breakdown (question-by-question analysis)
- **Sheet 3**: By Question Type (Application/Exception/Scenario/Sequence)
- **Sheet 4**: By Exam Tricks (NOT, BEST, MOST, FIRST, ONLY)
- **Sheet 5**: By Domain (8 CISSP domains)
- **Sheet 6**: By Difficulty (Easy/Medium/Hard)
- **Sheet 7**: Study Plan (personalized recommendations)

### Class Report
- Class Overview (average, pass rate, high/low scores)
- Student Rankings (all students sorted by score)
- Weakness Analysis (topics needing improvement across class)
- Topic Analysis (topic-by-topic performance)

## Troubleshooting

### "File not found" error
- Use absolute paths (starting with `/`)
- Check file exists: `ls -la /path/to/file`

### Wrong scores
- Verify answer key extracted correctly
- Check student Excel file format

### Questions mapped incorrectly
- Edit `data/question_domain_mapping.json` manually, OR
- Update keywords in `question_analyzer.py` and re-run `regenerate_mapping.py`

## What's Automated

✅ Extract 125 questions from PDF
✅ Extract answer key from PDF
✅ Auto-analyze questions (domain, topic, difficulty, tricks)
✅ Parse student answers (handles multiple formats)
✅ Score all answers
✅ Generate individual reports (7 sheets each)
✅ Generate class analysis
✅ Personalized recommendations per student

## Next Exams

For each new exam:

```bash
python3 setup.py
```

That's it! The wizard handles everything.

---
**Version:** 2.1  
**Production Ready** ✅
