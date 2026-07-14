#!/usr/bin/env python3
"""
Student Answer Sheet Analyzer with Trap Category Integration

Loads student answer sheets (Excel format), compares with answer key,
and generates comprehensive reports with trap analysis.
"""

import json
from pathlib import Path
from openpyxl import load_workbook
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine


def load_answer_key():
    """Load the correct answer key from answer_key.json"""
    answer_key_path = Path("data/answer_key.json")
    if answer_key_path.exists():
        with open(answer_key_path, "r") as f:
            data = json.load(f)
            # Convert keys to integers if they're strings
            return {int(k): v for k, v in data.items()}
    return {}


def load_student_answers_from_excel(file_path):
    """Load student answers from Excel file"""
    wb = load_workbook(file_path)
    ws = wb.active

    answers = {}
    student_name = None

    # Extract student name from filename
    filename = Path(file_path).stem
    student_name = filename

    # Parse answers (skip header row)
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None or row[1] is None:
            continue
        try:
            q_num = int(row[0])
            answer = str(row[1]).strip().upper()
            answers[q_num] = answer
        except (ValueError, TypeError):
            continue

    return student_name, answers


def generate_student_report(student_name, answers, answer_key, engine):
    """Generate comprehensive report for a single student"""

    # Analyze answers
    results = engine.analyze_all_answers(answers, answer_key)

    # Calculate basic stats
    total_questions = len(results)
    correct = sum(1 for r in results if r.is_correct)
    wrong = total_questions - correct
    score_pct = (correct / total_questions * 100) if total_questions > 0 else 0

    # Summarize trap vulnerabilities
    vulnerabilities = engine.summarize_vulnerabilities(results)

    # Generate recommendations
    recommendations = engine.generate_recommendations(vulnerabilities)

    return {
        "student_name": student_name,
        "total_questions": total_questions,
        "correct": correct,
        "wrong": wrong,
        "score_percentage": round(score_pct, 1),
        "analysis_results": results,
        "vulnerabilities": vulnerabilities,
        "recommendations": recommendations,
    }


def print_student_report(report):
    """Print formatted student report"""
    student = report["student_name"]
    correct = report["correct"]
    total = report["total_questions"]
    score = report["score_percentage"]

    print(f"\n{'='*80}")
    print(f"STUDENT: {student}")
    print(f"{'='*80}")
    print(f"Score: {correct}/{total} ({score:.1f}%)")
    print(f"Status: {'PASS (≥70%)' if score >= 70 else 'NEEDS IMPROVEMENT (<70%)'}")

    # Show trap vulnerabilities
    vulnerabilities = report["vulnerabilities"]
    if vulnerabilities:
        print(f"\n🔴 TRAP VULNERABILITIES ({len(vulnerabilities)} identified):")
        for vuln in vulnerabilities[:5]:  # Top 5
            print(f"\n  {vuln.trap_category} - {vuln.trap_name}")
            print(f"  └─ Fell for this trap: {vuln.frequency_count} times")
            print(f"  └─ Questions: {vuln.affected_questions}")
            print(f"  └─ Success rate: {vuln.success_rate:.1f}%")

    # Show recommendations
    recs = report["recommendations"]
    if recs and "study_plan" in recs:
        print(f"\n📚 PERSONALIZED STUDY PLAN:")
        for i, plan in enumerate(recs["study_plan"][:3], 1):
            print(f"  {i}. {plan}")

    print(f"\n{'='*80}\n")


def main():
    """Main analysis workflow"""

    # Initialize trap analysis engine
    engine = TrapAnalysisEngine()

    # Load answer key
    answer_key = load_answer_key()
    if not answer_key:
        print("❌ Answer key not found in data/answer_key.json")
        return

    # Student files to process
    student_files = [
        "/Users/sriram/Downloads/kapil-july-12.xlsx",
        "/Users/sriram/Downloads/Mock Test Aman 11 july.xlsx",
        "/Users/sriram/Downloads/12 July 2026-Mock test 7 - Senthilraj.xlsx",
        "/Users/sriram/Downloads/Mock Test - 07 Jul - Praveena.xlsx",
    ]

    all_reports = []

    print("\n" + "="*80)
    print("CISSP ANALYZER - STUDENT ANSWER SHEET PROCESSING")
    print("="*80)

    # Process each student file
    for file_path in student_files:
        file_obj = Path(file_path)
        if not file_obj.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"\n📄 Processing: {file_obj.name}")

        try:
            # Load student answers
            student_name, answers = load_student_answers_from_excel(file_path)
            print(f"   ✅ Loaded {len(answers)} answers from {student_name}")

            # Generate report with trap analysis
            report = generate_student_report(student_name, answers, answer_key, engine)
            all_reports.append(report)

            # Print report
            print_student_report(report)

        except Exception as e:
            print(f"   ❌ Error processing {file_obj.name}: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    if all_reports:
        print("\n" + "="*80)
        print("CLASS SUMMARY")
        print("="*80)

        for report in all_reports:
            score = report["score_percentage"]
            status = "✅ PASS" if score >= 70 else "⚠️  NEEDS IMPROVEMENT"
            print(f"{report['student_name']:25s} {report['correct']:3d}/{report['total_questions']:3d} ({score:5.1f}%) {status}")

        # Class average
        avg_score = sum(r["score_percentage"] for r in all_reports) / len(all_reports)
        print(f"\n{'Class Average':25s} {avg_score:5.1f}%")

        print("="*80)

    return all_reports


if __name__ == "__main__":
    main()
