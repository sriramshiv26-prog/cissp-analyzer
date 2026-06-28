import json
from pathlib import Path
from typing import List, Dict
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.class_report_gen import ClassReportGenerator


class CISSPAnalyzer:
    """Main orchestrator for CISSP exam analysis pipeline"""

    def __init__(self, mapping_file: str = 'data/question_domain_mapping.json'):
        self.domain_mapper = DomainMapper(mapping_file)
        self.analysis_engine = AnalysisEngine(self.domain_mapper)
        self.individual_gen = IndividualReportGenerator(self.domain_mapper, self.analysis_engine)
        self.class_gen = ClassReportGenerator(self.domain_mapper)

    def analyze(self,
                exam_pdf: str,
                answer_excel: str,
                student_names: List[str],
                output_dir: str) -> Dict:
        """
        Complete analysis pipeline

        Args:
            exam_pdf: Path to exam Q&A PDF
            answer_excel: Path to student answers Excel file
            student_names: List of student names (must match column names in Excel)
            output_dir: Directory to save reports

        Returns:
            Dictionary with paths to all generated reports
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Step 1: Extract questions from PDF
        print("Extracting questions from PDF...")
        pdf_parser = PDFParser(exam_pdf)
        questions = pdf_parser.extract_questions()

        # Step 2: Get answer key (only extract from PDF if not already set)
        if not self.analysis_engine.answer_key:
            answer_key = self._extract_answer_key_from_pdf(pdf_parser)
            self.analysis_engine.set_answer_key(answer_key)

        # Step 3: Parse student answers
        print("Parsing student answers...")
        excel_parser = ExcelParser()

        # Step 4: Analyze each student
        print("Analyzing student performance...")
        cohort_performance = []

        for student_name in student_names:
            print(f"  Analyzing {student_name}...")
            answers = excel_parser.parse_answers(answer_excel, student_name)
            performance = self.analysis_engine.evaluate_student(answers, student_name)
            cohort_performance.append(performance)

            # Generate individual report
            report_file = output_path / f"CISSP_Individual_Report_{student_name}.xlsx"
            self.individual_gen.generate(performance, str(report_file))
            print(f"     Report saved to {report_file}")

        # Step 5: Generate class reports
        print("Generating class-level reports...")
        class_report_file = output_path / "CISSP_Class_Analysis.xlsx"
        self.class_gen.generate(cohort_performance, str(class_report_file))
        print(f"  Class report saved to {class_report_file}")

        return {
            'individual_reports': [
                str(output_path / f"CISSP_Individual_Report_{name}.xlsx")
                for name in student_names
            ],
            'class_report': str(class_report_file),
            'students_analyzed': len(student_names),
            'cohort_performance': cohort_performance
        }

    def _extract_answer_key_from_pdf(self, pdf_parser: PDFParser) -> Dict[int, str]:
        """Extract the correct answer for each question (if provided in PDF)"""
        # TODO: Parse answer key from PDF if available
        # For now, return empty dict (answer key can be set via set_answer_key_from_file)
        return {}

    def set_answer_key_from_file(self, json_file: str):
        """Load answer key from JSON file

        Expected format:
        {
            "1": "A",
            "2": "B",
            ...
        }

        Or with integer keys:
        {
            1: "A",
            2: "B",
            ...
        }
        """
        with open(json_file, 'r') as f:
            answer_key = json.load(f)

        # Convert string keys to integers if needed
        normalized_key = {}
        for k, v in answer_key.items():
            q_num = int(k) if isinstance(k, str) else k
            normalized_key[q_num] = str(v).upper()

        self.analysis_engine.set_answer_key(normalized_key)
