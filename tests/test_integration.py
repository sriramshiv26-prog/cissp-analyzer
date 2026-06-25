import pytest
import json
from pathlib import Path
from cissp_analyzer.main import CISSPAnalyzer


@pytest.fixture
def analyzer():
    return CISSPAnalyzer()


@pytest.fixture
def pdf_path():
    return Path('/Users/sriram/Downloads/June 21st Test 1.Updated.pdf')


@pytest.fixture
def excel_path():
    return Path('/Users/sriram/Downloads/CISSP Test Answers.xlsx')


def test_analyzer_initializes(analyzer):
    """Test that analyzer initializes with all components"""
    assert analyzer is not None
    assert analyzer.domain_mapper is not None
    assert analyzer.analysis_engine is not None
    assert analyzer.individual_gen is not None
    assert analyzer.class_gen is not None


def test_full_pipeline(analyzer, pdf_path, excel_path, tmp_path):
    """Test complete pipeline: PDF → parsing → analysis → reports"""

    if not pdf_path.exists():
        pytest.skip("Test PDF not found")

    if not excel_path.exists():
        pytest.skip("Test Excel not found")

    students = ['Senthil', 'Kapil', 'Praveena']
    output_dir = str(tmp_path / 'reports')

    # Run analysis
    results = analyzer.analyze(
        exam_pdf=str(pdf_path),
        answer_excel=str(excel_path),
        student_names=students,
        output_dir=output_dir
    )

    # Verify results structure
    assert 'individual_reports' in results
    assert 'class_report' in results
    assert 'students_analyzed' in results
    assert 'cohort_performance' in results

    # Verify counts
    assert results['students_analyzed'] == 3
    assert len(results['individual_reports']) == 3
    assert len(results['cohort_performance']) == 3


def test_individual_reports_generated(analyzer, pdf_path, excel_path, tmp_path):
    """Test that individual reports are generated for each student"""

    if not pdf_path.exists():
        pytest.skip("Test PDF not found")

    if not excel_path.exists():
        pytest.skip("Test Excel not found")

    students = ['Senthil', 'Kapil']
    output_dir = str(tmp_path / 'reports')

    results = analyzer.analyze(
        exam_pdf=str(pdf_path),
        answer_excel=str(excel_path),
        student_names=students,
        output_dir=output_dir
    )

    # Verify each report file exists
    for report_path in results['individual_reports']:
        assert Path(report_path).exists(), f"Report not found: {report_path}"
        assert report_path.endswith('.xlsx')


def test_class_report_generated(analyzer, pdf_path, excel_path, tmp_path):
    """Test that class-level report is generated"""

    if not pdf_path.exists():
        pytest.skip("Test PDF not found")

    if not excel_path.exists():
        pytest.skip("Test Excel not found")

    students = ['Senthil']
    output_dir = str(tmp_path / 'reports')

    results = analyzer.analyze(
        exam_pdf=str(pdf_path),
        answer_excel=str(excel_path),
        student_names=students,
        output_dir=output_dir
    )

    # Verify class report file exists
    class_report = results['class_report']
    assert Path(class_report).exists(), f"Class report not found: {class_report}"
    assert class_report.endswith('.xlsx')


def test_answer_key_from_file(analyzer, tmp_path):
    """Test loading answer key from JSON file"""

    # Create test answer key
    answer_key = {
        "1": "A",
        "2": "B",
        "3": "C"
    }

    key_file = tmp_path / 'answer_key.json'
    with open(key_file, 'w') as f:
        json.dump(answer_key, f)

    # Load it
    analyzer.set_answer_key_from_file(str(key_file))

    # Verify it was loaded
    assert analyzer.analysis_engine.answer_key is not None
    assert len(analyzer.analysis_engine.answer_key) == 3
