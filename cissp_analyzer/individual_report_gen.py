from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from cissp_analyzer.models import StudentPerformance
from cissp_analyzer.domain_mapper import DomainMapper
from cissp_analyzer.analysis_engine import AnalysisEngine


class IndividualReportGenerator:
    """Generates individual performance reports for each student"""

    def __init__(self, domain_mapper: DomainMapper, analysis_engine: AnalysisEngine):
        self.mapper = domain_mapper
        self.engine = analysis_engine

    def generate(self, performance: StudentPerformance, output_file: str):
        """Generate comprehensive individual report"""
        wb = Workbook()
        wb.remove(wb.active)

        self._create_performance_summary(wb, performance)
        self._create_qa_breakdown(wb, performance)
        self._create_by_difficulty(wb, performance)
        self._create_by_question_type(wb, performance)
        self._create_by_exam_tricks(wb, performance)
        self._create_by_domain(wb, performance)

        wb.save(output_file)

    def _create_performance_summary(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 1: Performance Summary"""
        ws = wb.create_sheet('Performance Summary')

        ws['A1'] = f"CISSP Individual Report: {perf.student_name}"
        ws['A1'].font = Font(bold=True, size=14)

        ws['A3'] = 'Score'
        ws['B3'] = f"{perf.correct_count}/125 ({perf.score_percentage:.1f}%)"

        ws['A4'] = 'Status'
        status = 'EXAM READY' if perf.score_percentage >= 70 else 'NEEDS WORK'
        ws['B4'] = status

        ws['A5'] = 'Gap to Pass (70%)'
        gap = max(0, 70 - perf.score_percentage)
        ws['B5'] = f"{gap:+.1f}%"

        ws['A6'] = 'Questions Wrong'
        ws['B6'] = perf.wrong_count

        ws.column_dimensions['A'].width = 20
        ws.column_dimensions['B'].width = 30

    def _create_qa_breakdown(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 2: Q&A Breakdown (all 125 questions)"""
        ws = wb.create_sheet('Q&A Breakdown')

        ws['A1'] = 'Question'
        ws['B1'] = 'Result'
        ws['C1'] = 'Domain'
        ws['D1'] = 'Topic'
        ws['E1'] = 'Difficulty'

        for col in ['A', 'B', 'C', 'D', 'E']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')

        row = 2
        for q_num in range(1, 126):
            is_wrong = q_num in perf.wrong_question_ids
            meta = self.mapper.get_question_metadata(q_num)

            ws[f'A{row}'] = q_num
            ws[f'B{row}'] = 'WRONG' if is_wrong else 'CORRECT'

            if meta:
                ws[f'C{row}'] = meta.get('domain', '')
                ws[f'D{row}'] = meta.get('topic', '')
                ws[f'E{row}'] = meta.get('difficulty', '')

                fill_color = 'FF0000' if is_wrong else '00B050'
                ws[f'B{row}'].fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type='solid')
                ws[f'B{row}'].font = Font(color='FFFFFF', bold=True)

            row += 1

        for col in ['A', 'B', 'C', 'D', 'E']:
            ws.column_dimensions[col].width = 15

    def _create_by_difficulty(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 3: By Difficulty"""
        ws = wb.create_sheet('By Difficulty')
        self._create_dimension_sheet(ws, perf.by_difficulty, 'Difficulty')

    def _create_by_question_type(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 4: By Question Type"""
        ws = wb.create_sheet('By Question Type')
        self._create_dimension_sheet(ws, perf.by_question_type, 'Question Type')

    def _create_by_exam_tricks(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 5: By Exam Tricks"""
        ws = wb.create_sheet('By Exam Tricks')
        self._create_dimension_sheet(ws, perf.by_exam_trick, 'Exam Trick')

    def _create_by_domain(self, wb: Workbook, perf: StudentPerformance):
        """Sheet 6: By Domain"""
        ws = wb.create_sheet('By Domain')
        self._create_dimension_sheet(ws, perf.by_domain, 'Domain')

    def _create_dimension_sheet(self, ws, dimension_data: dict, dim_name: str):
        """Helper to create any dimension sheet"""
        ws['A1'] = dim_name
        ws['B1'] = 'Correct'
        ws['C1'] = 'Wrong'
        ws['D1'] = 'Total'
        ws['E1'] = 'Percentage'

        for col in ['A', 'B', 'C', 'D', 'E']:
            ws[f'{col}1'].font = Font(bold=True)
            ws[f'{col}1'].fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')

        row = 2
        for category, data in sorted(dimension_data.items()):
            ws[f'A{row}'] = category
            ws[f'B{row}'] = data['correct']
            ws[f'C{row}'] = data['wrong']
            ws[f'D{row}'] = data['total']
            ws[f'E{row}'] = f"{data['percentage']:.1f}%"
            row += 1

        ws.column_dimensions['A'].width = 20
        for col in ['B', 'C', 'D', 'E']:
            ws.column_dimensions[col].width = 12
