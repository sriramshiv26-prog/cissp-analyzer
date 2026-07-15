#!/usr/bin/env python3
"""
Exam Dashboard - Generates visual dashboard showing all exams and results.
Supports HTML and text output formats.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List
from .exam_registry import ExamRegistry


class ExamDashboard:
    """Generates dashboard views of all exams and results"""

    def __init__(self):
        self.registry = ExamRegistry()

    def generate_html_dashboard(
        self, output_path: str = "output/exam_dashboard.html"
    ) -> str:
        """Generate HTML dashboard of all exams"""
        summary = self.registry.export_summary()

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CISSP Analyzer - Exam Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f5f5; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}

        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .stat {{ background: rgba(255,255,255,0.2); padding: 15px; border-radius: 6px; }}
        .stat-value {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; margin-top: 5px; }}

        .exams-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; }}
        .exam-card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .exam-card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.15); transition: box-shadow 0.3s; }}

        .exam-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px; }}
        .exam-name {{ font-size: 1.3em; font-weight: 600; color: #667eea; }}
        .exam-badge {{ background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; }}

        .exam-details {{ font-size: 0.9em; color: #666; line-height: 1.8; }}
        .exam-details strong {{ color: #333; }}

        .progress-bar {{ width: 100%; height: 8px; background: #eee; border-radius: 4px; margin-top: 10px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #667eea, #764ba2); width: var(--progress); }}

        .actions {{ margin-top: 15px; display: flex; gap: 10px; }}
        .btn {{ padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-size: 0.9em; text-decoration: none; }}
        .btn-primary {{ background: #667eea; color: white; }}
        .btn-primary:hover {{ background: #5568d3; }}
        .btn-secondary {{ background: #f0f0f0; color: #333; }}
        .btn-secondary:hover {{ background: #e0e0e0; }}

        .empty-state {{ text-align: center; padding: 40px; color: #999; }}
        .empty-state-icon {{ font-size: 3em; margin-bottom: 10px; }}

        footer {{ text-align: center; color: #999; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>📊 CISSP Analyzer Dashboard</h1>
                <p>Multi-Exam Results & Analysis Hub</p>
            </div>
            <div style="text-align: right; font-size: 0.9em; opacity: 0.9;">
                Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </header>

        <div class="summary">
            <div class="stat">
                <div class="stat-value">{summary['total_exams']}</div>
                <div class="stat-label">Exams Registered</div>
            </div>
            <div class="stat">
                <div class="stat-value">{summary['total_students_analyzed']}</div>
                <div class="stat-label">Students Analyzed</div>
            </div>
        </div>

        <h2 style="margin-top: 40px; margin-bottom: 20px;">All Exams</h2>

        {self._generate_exam_cards_html(summary['exams']) if summary['exams'] else '<div class="empty-state"><div class="empty-state-icon">📋</div><p>No exams registered yet. Upload a question bank to get started!</p></div>'}

        <footer>
            <p>CISSP Analyzer v2.0 | <a href="https://github.com/sriramshiv26-prog/cissp-analyzer" style="color: #667eea; text-decoration: none;">View on GitHub</a></p>
        </footer>
    </div>
</body>
</html>
"""

        # Save HTML
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(html)

        return str(output_file)

    def _generate_exam_cards_html(self, exams: List[Dict]) -> str:
        """Generate HTML cards for each exam"""
        cards = '<div class="exams-grid">'

        for exam in exams:
            # Calculate progress (students analyzed)
            progress = 0  # Could be enhanced with expected vs actual

            card = f"""
        <div class="exam-card">
            <div class="exam-header">
                <div class="exam-name">{exam['exam_name']}</div>
                <div class="exam-badge">{exam['num_questions']} Qs</div>
            </div>

            <div class="exam-details">
                <p><strong>Students Analyzed:</strong> {exam['students_analyzed']}</p>
                <p><strong>Questions:</strong> {exam['num_questions']}</p>
                <p><strong>Registered:</strong> {exam['registered_date'][:10]}</p>
                <p><strong>Output Folder:</strong> <code style="background: #f5f5f5; padding: 2px 6px; border-radius: 3px;">{exam['output_folder']}</code></p>
                <p><strong>Class Report:</strong> {'✅ Yes' if exam['class_result'] else '❌ No'}</p>
            </div>

            <div class="actions">
                <button class="btn btn-primary" onclick="window.location.href='{exam['output_folder']}'">View Results</button>
            </div>
        </div>
"""
            cards += card

        cards += "</div>"
        return cards

    def generate_text_dashboard(self) -> str:
        """Generate text-based dashboard"""
        summary = self.registry.export_summary()

        text = f"""
╔════════════════════════════════════════════════════════════════════╗
║         CISSP ANALYZER - EXAM DASHBOARD                           ║
║     Multi-Exam Results & Analysis Hub                             ║
╚════════════════════════════════════════════════════════════════════╝

📊 SUMMARY
──────────────────────────────────────────────────────────────────────
  Total Exams Registered:        {summary['total_exams']}
  Total Students Analyzed:       {summary['total_students_analyzed']}
  Last Updated:                  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 ALL EXAMS
──────────────────────────────────────────────────────────────────────
"""

        if not summary["exams"]:
            text += "\n  (No exams registered yet. Upload a question bank to get started!)\n"
        else:
            for i, exam in enumerate(summary["exams"], 1):
                text += f"""
  {i}. {exam['exam_name']}
     ├─ Questions: {exam['num_questions']}
     ├─ Students: {exam['students_analyzed']}
     ├─ Class Report: {'✅ Yes' if exam['class_result'] else '❌ No'}
     ├─ Registered: {exam['registered_date'][:10]}
     └─ Folder: {exam['output_folder']}
"""

        text += "\n" + "─" * 70 + "\n"
        text += "✨ Use 'python3 run.py --list-exams' to see detailed exam info\n"
        text += "✨ Use 'python3 run.py --dashboard' to view this dashboard\n"

        return text

    def print_dashboard(self) -> None:
        """Print dashboard to console"""
        print(self.generate_text_dashboard())

    def save_text_dashboard(
        self, output_path: str = "output/exam_dashboard.txt"
    ) -> str:
        """Save text dashboard to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(self.generate_text_dashboard())
        return str(output_file)
