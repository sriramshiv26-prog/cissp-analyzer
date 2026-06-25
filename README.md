# CISSP Analysis Tool

A standalone Python program that analyzes CISSP exam results and generates comprehensive performance reports across multiple dimensions.

## Features

- **PDF Question Extraction**: Automatically extracts questions from exam PDFs using pypdf
- **Excel Answer Parsing**: Reads student answer sheets with flexible column matching
- **Multi-Dimensional Analysis**: 
  - By Domain (8 CISSP domains)
  - By Topic (50+ topics)
  - By Difficulty Level (Easy, Medium, Hard)
  - By Question Type (Definition, Scenario, Comparison, Exception, Sequence, Managerial)
  - By Exam Tricks (Negation, Superlative, Absolute, Scenario, Trap)
- **Individual Student Reports**: 6-sheet Excel reports per student
- **Class-Level Reports**: 4-sheet Excel analysis for class performance
- **Answer Key Integration**: Optional JSON-based answer key for accuracy scoring

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo_url>
cd cissp-analyzer
pip install -r requirements.txt
```

## Quick Start

### Command-Line Usage

```bash
python run.py <exam_pdf> <answers_excel> <students> <output_dir> [answer_key_json]
```

#### Example

```bash
python run.py \
  exam.pdf \
  student_answers.xlsx \
  "Senthil,Kapil,Praveena,Aman,Thameem" \
  ./reports/ \
  answer_key.json
```

#### Arguments

- `exam_pdf` - Path to exam PDF containing CISSP questions
- `answers_excel` - Excel file with student answers (see format below)
- `students` - Comma-separated list of student names (must match Excel column names)
- `output_dir` - Directory where reports will be saved
- `answer_key_json` - (Optional) JSON file mapping question numbers to correct answers

### Programmatic Usage

```python
from cissp_analyzer.main import CISSPAnalyzer

# Initialize analyzer
analyzer = CISSPAnalyzer()

# Load answer key (optional)
analyzer.set_answer_key_from_file('answer_key.json')

# Run analysis
results = analyzer.analyze(
    exam_pdf='exam.pdf',
    answer_excel='student_answers.xlsx',
    student_names=['Senthil', 'Kapil', 'Praveena'],
    output_dir='./reports/'
)

# Access results
print(f"Students analyzed: {results['students_analyzed']}")
print(f"Individual reports: {len(results['individual_reports'])}")
print(f"Class report: {results['class_report']}")
```

## Input Formats

### Excel Answer Sheet

Create an Excel file with the following structure:

- Column A: `Question` (question numbers 1-125)
- Other columns: Student names matching your student list

Example:

```
Question | Senthil | Kapil | Praveena | Aman | Thameem
---------|---------|-------|----------|------|----------
1        | A       | B     | A        | C    | B
2        | B       | A     | C        | A    | B
3        | C       | C     | C        | B    | A
...
125      | D       | D     | A        | D    | D
```

Notes:
- Student names must match exactly between the command and Excel columns
- Valid answers: A, B, C, D
- All 125 questions should be present

### Answer Key (Optional)

JSON file mapping question numbers to correct answers:

```json
{
  "1": "A",
  "2": "B",
  "3": "C",
  "4": "A",
  ...
  "125": "D"
}
```

## Output Files

### Individual Student Reports

For each student, creates `CISSP_Individual_Report_<StudentName>.xlsx` with 6 sheets:

1. **Performance Summary**: Overall scores, domain breakdown, topic breakdown
2. **Q&A Breakdown**: All 125 questions with student answers, correct answers, and metadata
3. **By Difficulty**: Score distribution across Easy, Medium, Hard
4. **By Question Type**: Score distribution across question types (Definition, Scenario, etc.)
5. **By Exam Tricks**: Score distribution across exam trick categories
6. **By Domain**: Score distribution across 8 CISSP domains

### Class-Level Report

Single file `CISSP_Class_Analysis.xlsx` with 4 sheets:

1. **Class Overview**: Overall statistics, score distribution, performance metrics
2. **Student Rankings**: Ranked performance across all metrics
3. **Weakness Analysis**: Top weaknesses by domain, topic, and difficulty
4. **Topic Analysis**: Performance by topic with student rankings

## Testing

Run the test suite:

```bash
# All tests
pytest -v

# Specific test file
pytest tests/test_analysis_engine.py -v

# With coverage
pytest --cov=cissp_analyzer --cov-report=html
```

Current test status: 26 tests passing, 3 skipped

Test files:
- `test_domain_mapper.py` - Domain and topic metadata
- `test_pdf_parser.py` - PDF question extraction
- `test_excel_parser.py` - Answer sheet parsing
- `test_analysis_engine.py` - Multi-dimensional analysis
- `test_individual_report_gen.py` - Student report generation
- `test_class_report_gen.py` - Class report generation
- `test_integration.py` - Full pipeline integration

## Architecture

The tool is organized into modular components:

```
cissp_analyzer/
├── models.py              # Data classes (Question, StudentAnswer, AnalysisResult)
├── domain_mapper.py       # CISSP domain, topic, difficulty, and type mappings
├── pdf_parser.py          # PDF extraction using pypdf
├── excel_parser.py        # Excel parsing using pandas and openpyxl
├── analysis_engine.py     # Multi-dimensional analysis logic
├── individual_report_gen.py   # Student report generation
├── class_report_gen.py        # Class report generation
├── main.py               # Orchestrator (CISSPAnalyzer class)
└── __init__.py
```

### Key Classes

- **CISSPAnalyzer**: Main orchestrator class
  - `analyze()` - Run complete pipeline
  - `set_answer_key_from_file()` - Load answer key

- **DomainMapper**: Maps question metadata
  - `get_question_metadata()` - Retrieve metadata for a question
  - All 125 CISSP questions pre-mapped to domains, topics, difficulty, types, and tricks

- **PDFParser**: Extracts questions from PDF
  - `extract_questions()` - Get all questions

- **ExcelParser**: Parses student answers
  - `parse_student_answers()` - Load answer sheet

- **AnalysisEngine**: Multi-dimensional analysis
  - `evaluate_answers()` - Calculate performance metrics

- **IndividualReportGenerator**: Creates student reports
  - `generate_report()` - Create 6-sheet report

- **ClassReportGenerator**: Creates class reports
  - `generate_class_report()` - Create 4-sheet report

## Data Model

### Question Metadata (from DomainMapper)

Each of the 125 questions has:
- Domain: One of 8 CISSP domains
- Topic: Specific topic within domain
- Difficulty: Easy, Medium, or Hard
- Type: Definition, Scenario, Comparison, Exception, Sequence, Managerial
- Tricks: Lists of exam trick patterns (Negation, Superlative, Absolute, Scenario, Trap)

### Student Performance

For each student:
- Overall score (% correct)
- Score breakdown by: domain, topic, difficulty, type, tricks
- Detailed Q&A tracking: which questions answered correctly/incorrectly

## Requirements

- Python 3.8+
- pandas 2.2.1
- openpyxl 3.1.2
- pypdf 4.1.0
- python-dotenv 1.0.0
- pytest 7.4.3 (for testing)

## Standards Met

This tool implements industry best practices for assessment analysis:

- **Dimensional Analysis**: Breaks performance into meaningful categories
- **Actionable Insights**: Identifies specific weak areas (domains, topics, types)
- **Individual + Class Views**: Supports both student and instructor needs
- **Reproducibility**: Deterministic output for any input set
- **Error Handling**: Validates inputs and provides clear error messages

## Troubleshooting

### "No module named 'cissp_analyzer'"

Ensure you're running from the project root directory:
```bash
cd /path/to/cissp-analyzer
export PYTHONPATH=/path/to/cissp-analyzer:$PYTHONPATH
python run.py ...
```

### Excel parsing errors

Check that:
- Column names match student names exactly
- All question numbers 1-125 are present
- Valid answer values are A, B, C, or D

### PDF extraction fails

Ensure:
- PDF file exists and is readable
- PDF contains searchable text (not scanned images)
- Questions are formatted as expected

## Future Enhancements

Potential areas for expansion:
- Support for multiple exam formats
- Statistical significance testing
- Comparative cohort analysis
- Visual dashboard integration
- Performance prediction models

## License

Proprietary - Internal Use Only

## Support

For issues, enhancements, or questions, contact the development team.
