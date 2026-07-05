#!/usr/bin/env python3
"""
CISSP Analyzer - Master Entry Point

Smart analysis routing for batch or standalone mode.
GitHub users can just run: python3 analyze.py

Then choose:
  [1] Batch Analysis (Multiple students, one or more exams)
  [2] Standalone Analysis (Single student, one exam)
  [3] Full Batch Workflow (Automated pipeline: validate → fix → consolidate → analyze)
"""

import sys
import json
from pathlib import Path


def show_welcome():
    """Show welcome screen"""
    print("\n" + "=" * 80)
    print("CISSP EXAM ANALYZER")
    print("=" * 80)
    print()


def show_menu():
    """Show main menu"""
    print("What do you want to do?\n")
    print("  [1] Batch Analysis")
    print("       Analyze multiple students from a cohort")
    print("       Example: Dec-25 batch, July-26 batch, etc.")
    print()
    print("  [2] Standalone Analysis")
    print("       Analyze a single student (one-time exam)")
    print("       Example: Make-up exam, new student, quick analysis")
    print()
    print("  [3] Full Batch Workflow")
    print("       Complete automated pipeline for entire batch")
    print("       Includes: validation → auto-fix → consolidation → analysis")
    print()
    choice = input("Choose [1/2/3]: ").strip()
    return choice


def batch_analysis():
    """Route to batch analysis"""
    print("\n" + "=" * 80)
    print("BATCH ANALYSIS")
    print("=" * 80)
    print()

    # Load roster to show existing batches
    try:
        with open("student_roster.json") as f:
            roster = json.load(f)
        existing_batches = [b for b in roster["batches"].keys() if b != "standalone"]
        print(f"Existing batches: {', '.join(existing_batches)}\n")
    except FileNotFoundError:
        existing_batches = []
        print("⚠ Note: student_roster.json not found\n")

    # Get batch name
    batch_name = (
        input("Enter batch name (e.g., dec25, july26, aug26): ").strip().lower()
    )

    if not batch_name:
        print("❌ Batch name required")
        return False

    # Run appropriate analysis script
    print(f"\n📊 Starting analysis for batch: {batch_name}")
    print()

    import subprocess

    # Check if batch-specific script exists
    script_name = f"analyze_{batch_name}.py"
    if Path(script_name).exists():
        print(f"Running: {script_name}")
        result = subprocess.run(
            [sys.executable, script_name], capture_output=False, text=True
        )
        return result.returncode == 0
    else:
        # Fall back to generic workflow
        print(f"⚠ {script_name} not found")
        print(f"Running: run_batch_workflow.py --batch {batch_name} --full")
        print()

        result = subprocess.run(
            [sys.executable, "run_batch_workflow.py", "--batch", batch_name, "--full"],
            capture_output=False,
            text=True,
        )
        return result.returncode == 0


def standalone_analysis():
    """Route to standalone analysis"""
    print("\n" + "=" * 80)
    print("STANDALONE ANALYSIS")
    print("=" * 80)
    print("""
Two analysis modes for individual students:

[A] Single Exam (Ad-hoc / One-time)
    • Analyze just this exam
    • Perfect for: practice tests, new students, quick analysis
    • No history or trends needed

[B] Compare with Previous Exams (Trending)
    • Show progress over time
    • Compare against previous attempts
    • Adaptive recommendations based on history
    • Perfect for: tracking improvement, retakes, trend analysis

When you run the analysis, you'll be asked which mode you want.
    """)

    import subprocess

    result = subprocess.run(
        [sys.executable, "analyze_standalone.py"], capture_output=False, text=True
    )
    return result.returncode == 0


def full_batch_workflow():
    """Route to full batch workflow"""
    print("\n" + "=" * 80)
    print("FULL BATCH WORKFLOW")
    print("=" * 80)
    print()

    # Get batch name
    batch_name = (
        input("Enter batch name (e.g., dec25, july26, aug26): ").strip().lower()
    )

    if not batch_name:
        print("❌ Batch name required")
        return False

    print(f"\n⚙️  Starting full workflow for batch: {batch_name}")
    print("Pipeline: Validate → Auto-Fix → Consolidate → Analyze → Verify")
    print()

    import subprocess

    result = subprocess.run(
        [sys.executable, "run_batch_workflow.py", "--batch", batch_name, "--full"],
        capture_output=False,
        text=True,
    )
    return result.returncode == 0


def show_help():
    """Show help message"""
    print("""
CISSP Analyzer - Quick Start

Usage:
  python3 analyze.py                    # Interactive menu
  python3 analyze.py --help             # Show this help

Interactive Mode (Recommended):
  python3 analyze.py

  Then choose:
    [1] Batch Analysis
    [2] Standalone Analysis
    [3] Full Batch Workflow

Direct Mode (If you know what you want):
  python3 analyze_dec25.py              # Run Dec-25 batch analysis
  python3 analyze_july26.py             # Run July-26 batch analysis
  python3 analyze_standalone.py         # Analyze single student
  python3 run_batch_workflow.py --batch july26 --full

Tools (If needed):
  python3 auto_fix_answers.py --batch july26
  python3 consolidate_answers.py --batch july26

Setup:
  1. Copy exam PDFs to: exams/
  2. Copy student answer files to: answers/<batch>/
  3. Update student_roster.json with batch info
  4. Run: python3 analyze.py

That's it! No configuration needed.
""")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        show_help()
        sys.exit(0)

    show_welcome()

    choice = show_menu()

    success = False
    if choice == "1":
        success = batch_analysis()
    elif choice == "2":
        success = standalone_analysis()
    elif choice == "3":
        success = full_batch_workflow()
    else:
        print("❌ Invalid choice. Please enter 1, 2, or 3")
        sys.exit(1)

    # Show summary
    print("\n" + "=" * 80)
    if success:
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nResults saved to: reports/")
        print("\nNext steps:")
        print("  1. Check the generated Excel reports")
        print("  2. Review student performance data")
        print("  3. Use insights for personalized recommendations")
        print()
    else:
        print("⚠️  ANALYSIS COMPLETED WITH WARNINGS")
        print("=" * 80)
        print("\nCheck the output above for details")
        print()

    sys.exit(0 if success else 1)
