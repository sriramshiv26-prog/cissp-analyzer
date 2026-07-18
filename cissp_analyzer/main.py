import json
from pathlib import Path
from typing import List, Dict
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.excel_parser import ExcelParser
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.analysis_engine import AnalysisEngine
from cissp_analyzer.individual_report_gen import IndividualReportGenerator
from cissp_analyzer.class_report_gen import ClassReportGenerator
from cissp_analyzer.history_loader import HistoryLoader
from cissp_analyzer.answer_validator import AnswerValidator


class CISSPAnalyzer:
    """Main orchestrator for CISSP exam analysis pipeline"""

    def __init__(self, mapping_file: str = "data/question_domain_mapping.json"):
        self.domain_mapper = DomainMapper(mapping_file)
        self.analysis_engine = AnalysisEngine(self.domain_mapper)
        self.individual_gen = IndividualReportGenerator(
            self.domain_mapper, self.analysis_engine
        )
        self.class_gen = ClassReportGenerator(self.domain_mapper)

    def analyze(
        self,
        exam_pdf: str,
        answer_excel: str,
        student_names: List[str],
        output_dir: str,
    ) -> Dict:
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
        _ = pdf_parser.extract_questions()

        # Step 2: Get answer key (try JSON file first, then PDF)
        if not self.analysis_engine.answer_key:
            # Try loading from answer key JSON file
            answer_key_file = self._get_answer_key_file_path(exam_pdf)
            if answer_key_file and Path(answer_key_file).exists():
                print(f"Loading answer key from: {answer_key_file}")
                self.set_answer_key_from_file(answer_key_file)
            else:
                # Fall back to extracting from PDF
                print("No answer key file found, extracting from PDF...")
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
            "individual_reports": [
                str(output_path / f"CISSP_Individual_Report_{name}.xlsx")
                for name in student_names
            ],
            "class_report": str(class_report_file),
            "students_analyzed": len(student_names),
            "cohort_performance": cohort_performance,
        }

    def _get_answer_key_file_path(self, exam_pdf: str) -> str:
        """Construct answer key file path from exam PDF path"""
        pdf_path = Path(exam_pdf)
        # Convert "exams/dec25_week1.pdf" to "exams/dec25_week1_answer_key.json"
        answer_key_path = pdf_path.parent / f"{pdf_path.stem}_answer_key.json"
        return str(answer_key_path)

    def _extract_answer_key_from_pdf(self, pdf_parser: PDFParser) -> Dict[int, str]:
        """Extract the correct answer for each question from PDF using improved method."""
        try:
            # Use AnswerValidator for robust extraction that catches all questions
            # including edge cases like Q104, Q107, Q114, Q147
            pdf_path = pdf_parser.pdf_file if hasattr(pdf_parser, 'pdf_file') else None

            if pdf_path:
                validator = AnswerValidator(str(pdf_path))
                return validator.answer_key
            else:
                # Fallback: return empty dict (answer key can be set via set_answer_key_from_file)
                return {}
        except Exception as e:
            print(f"Note: Could not extract answer key from PDF: {str(e)}")
            # Fallback: return empty dict (answer key can be set via set_answer_key_from_file)
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
        try:
            with open(json_file, "r") as f:
                answer_key = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Answer key file not found: {json_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in answer key file: {str(e)}")

        # Convert string keys to integers if needed
        normalized_key = {}
        for k, v in answer_key.items():
            q_num = int(k) if isinstance(k, str) else k
            normalized_key[q_num] = str(v).upper()

        self.analysis_engine.set_answer_key(normalized_key)

    def analyze_student_with_history(
        self,
        exam_pdf: str,
        answer_excel: str,
        student_name: str,
        students_dir: str = "students",
    ) -> Dict:
        """
        Analyze a student's exam, load history, generate report with trends.

        Args:
            exam_pdf: Path to exam Q&A PDF
            answer_excel: Path to student answers Excel file
            student_name: Name of the student
            students_dir: Directory where student history is stored

        Returns:
            Dictionary with:
            - student_name: Name of the student
            - exam_number: The exam sequence number
            - report_path: Path to generated individual report
            - performance_data_path: Path to saved performance JSON
            - previous_exams_count: Number of previous exams in history
        """
        output_path = Path("output") / student_name
        output_path.mkdir(parents=True, exist_ok=True)

        # Step 1: Load history
        history_loader = HistoryLoader(students_dir)
        previous_exams = history_loader.load_previous_exams(student_name)
        exam_number = len(previous_exams) + 1

        # Step 2: Extract questions from PDF
        print(f"Analyzing {student_name}: Exam {exam_number}")
        print("  Extracting questions from PDF...")
        pdf_parser = PDFParser(exam_pdf)
        _ = pdf_parser.extract_questions()

        # Step 3: Get answer key (try JSON file first, then PDF)
        if not self.analysis_engine.answer_key:
            answer_key_file = self._get_answer_key_file_path(exam_pdf)
            if answer_key_file and Path(answer_key_file).exists():
                print(f"  Loading answer key from: {answer_key_file}")
                self.set_answer_key_from_file(answer_key_file)
            else:
                print("  No answer key file found, extracting from PDF...")
                answer_key = self._extract_answer_key_from_pdf(pdf_parser)
                self.analysis_engine.set_answer_key(answer_key)

        # Step 4: Parse student answers
        print("  Parsing student answers...")
        excel_parser = ExcelParser()
        answers = excel_parser.parse_answers(answer_excel, student_name)

        # Step 5: Evaluate student
        print("  Evaluating performance...")
        performance = self.analysis_engine.evaluate_student(answers, student_name)

        # Step 6: Export performance data
        print("  Saving performance data...")
        performance_data = {
            "exam_number": exam_number,
            "student_name": student_name,
            "score_percentage": performance.score_percentage,
            "correct_count": performance.correct_count,
            "wrong_count": performance.wrong_count,
            "by_domain": dict(performance.by_domain),
            "by_difficulty": dict(performance.by_difficulty),
            "by_question_type": dict(performance.by_question_type),
            "by_topic": dict(performance.by_topic),
            "by_exam_trick": dict(performance.by_exam_trick),
            "wrong_question_ids": performance.wrong_question_ids,
        }

        # Step 7: Save performance JSON
        performance_file = history_loader.save_exam_performance(
            student_name, exam_number, performance_data
        )

        # Step 8: Generate report with historical exams
        print("  Generating report with historical trends...")
        report_file = (
            output_path
            / f"CISSP_Individual_Report_{student_name}_Exam{exam_number}.xlsx"
        )
        self.individual_gen.generate(
            performance, str(report_file), historical_exams=previous_exams
        )
        print(f"  Report saved to {report_file}")

        return {
            "student_name": student_name,
            "exam_number": exam_number,
            "report_path": str(report_file),
            "performance_data_path": str(performance_file),
            "previous_exams_count": len(previous_exams),
        }
