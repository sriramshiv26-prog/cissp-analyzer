"""
CISSP Analyzer - Adaptive Exam Analysis and Recommendation Engine

A comprehensive tool for analyzing CISSP exam performance across multiple
exams with momentum-based adaptive study recommendations.

Example usage:
    from cissp_analyzer.main import CISSPAnalyzer

    analyzer = CISSPAnalyzer(mapping_file='data/question_domain_mapping.json')
    result = analyzer.analyze_student_with_history(
        exam_pdf='exams/mock_exam.pdf',
        answer_excel='answers/student_responses.xlsx',
        student_name='StudentName'
    )
    print(f"Report saved to: {result['report_path']}")
"""

__version__ = "1.0.0"
__author__ = "Sriram"
__email__ = "sriramshiv26@gmail.com"

# Check dependencies on import (non-blocking warnings for missing optional packages)
try:
    from cissp_analyzer.dependency_checker import check_required_dependencies
    missing, version_issues = check_required_dependencies(verbose=False)
    if missing:
        raise ImportError(
            f"Missing required dependencies: {', '.join(m[0] for m in missing)}\n"
            "Run 'pip install -r requirements.txt' to install."
        )
except ImportError as e:
    if "Missing required dependencies" in str(e):
        raise
    # If dependency_checker itself fails, try to continue
    # This allows basic functionality even if dependency checker has issues
    pass

# Export main classes for convenient importing
from cissp_analyzer.main import CISSPAnalyzer
from cissp_analyzer.models import StudentPerformance, StudentAnswer

__all__ = [
    "CISSPAnalyzer",
    "StudentPerformance",
    "StudentAnswer",
]
