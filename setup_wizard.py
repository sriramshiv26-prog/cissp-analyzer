#!/usr/bin/env python3
"""
CISSP Analyzer - Interactive Setup Wizard

Guides users through creating required files and setting up directory structure
for batch analysis. Creates templates and validates all inputs.
"""

import json
import os
from pathlib import Path


def create_sample_roster():
    """Create a sample student_roster.json if it doesn't exist"""
    sample_roster = {
        "batches": {
            "standalone": {
                "name": "Standalone (One-time exams)",
                "students": []
            },
            "july12": {
                "name": "July 12, 2026 Batch",
                "students": [
                    {"id": "S001", "name": "Student Name 1", "email": "student1@example.com"},
                    {"id": "S002", "name": "Student Name 2", "email": "student2@example.com"}
                ],
                "exam_file": "exams/july12_exam.pdf",
                "answer_dir": "answers/july12"
            }
        }
    }
    return sample_roster


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def check_and_create_roster(auto_create=False):
    """Check if student_roster.json exists, create if needed"""
    roster_path = Path("student_roster.json")

    if roster_path.exists():
        try:
            with open(roster_path) as f:
                roster = json.load(f)
            print("\n✓ Found: student_roster.json")
            return roster
        except json.JSONDecodeError:
            print("\n✗ Error: student_roster.json is corrupted")
            return None

    print("\n✗ Missing: student_roster.json")

    if auto_create:
        # Auto-create in batch mode
        roster = create_sample_roster()
        with open(roster_path, 'w') as f:
            json.dump(roster, f, indent=2)
        print("✓ Created: student_roster.json (template)")
        print("  → Edit this file to add your students and batch info")
        return roster
    else:
        # Ask in interactive mode
        print("\nWould you like to create a template? (y/n): ", end="")
        try:
            if input().strip().lower() == 'y':
                roster = create_sample_roster()
                with open(roster_path, 'w') as f:
                    json.dump(roster, f, indent=2)
                print("✓ Created: student_roster.json")
                print("  → Edit this file to add your students and batch info")
                return roster
        except EOFError:
            # No stdin available, auto-create
            print("(auto-creating)")
            roster = create_sample_roster()
            with open(roster_path, 'w') as f:
                json.dump(roster, f, indent=2)
            print("✓ Created: student_roster.json (template)")
            print("  → Edit this file to add your students and batch info")
            return roster

    return None


def check_directories():
    """Check and create required directories"""
    dirs = {
        'exams': 'Exam PDFs',
        'answers': 'Student answer files',
        'reports': 'Analysis reports'
    }

    print("\n📁 Checking directory structure...\n")

    for dir_name, description in dirs.items():
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✓ {dir_name}/ ({description})")
        else:
            dir_path.mkdir(exist_ok=True)
            print(f"  ✓ Created: {dir_name}/ ({description})")


def get_batch_files(batch_name):
    """Guide user through setting up files for a specific batch"""
    print_section(f"SETUP: {batch_name.upper()} BATCH")

    print(f"\nTo analyze the '{batch_name}' batch, you need:")
    print("  1. Exam PDF file(s)")
    print("  2. Student answer file(s)")
    print("  3. (Optional) Answer key\n")

    # Check for exam files
    exam_dir = Path("exams")
    exam_files = list(exam_dir.glob(f"{batch_name}*.pdf"))

    if exam_files:
        print(f"✓ Found exam PDFs for '{batch_name}':")
        for f in exam_files:
            print(f"    - {f.name}")
    else:
        print(f"✗ No exam PDFs found matching: exams/{batch_name}*.pdf")
        print(f"  → Place your exam PDF as: exams/{batch_name}_exam.pdf")

    # Check for answer files
    answer_dir = Path(f"answers/{batch_name}")
    if answer_dir.exists():
        answer_files = list(answer_dir.glob("*.json"))
        if answer_files:
            print(f"\n✓ Found answer files for '{batch_name}':")
            for f in answer_files:
                print(f"    - {f.name}")
        else:
            print(f"\n✗ No answer files found in: answers/{batch_name}/")
            print(f"  → Place student answer files (.json) in: answers/{batch_name}/")
    else:
        print(f"\n✗ Missing directory: answers/{batch_name}/")
        print(f"  → Create directory and add student answer files there")

    # Show expected format
    print("\n📋 Expected File Format:")
    print("  Answer files should be JSON with structure like:")
    print("""    {
      "student_name": "John Doe",
      "answers": {
        "Q1": "A",
        "Q2": "B",
        "Q3": "C",
        ...
      }
    }""")

    return validate_batch_files(batch_name)


def validate_batch_files(batch_name):
    """Validate that all required files exist for a batch"""
    errors = []
    warnings = []

    # Check exam files
    exam_files = list(Path("exams").glob(f"{batch_name}*.pdf"))
    if not exam_files:
        errors.append(f"No exam PDFs found in exams/ matching: {batch_name}*.pdf")

    # Check answer directory
    answer_dir = Path(f"answers/{batch_name}")
    if not answer_dir.exists():
        errors.append(f"Answer directory missing: answers/{batch_name}/")
    else:
        answer_files = list(answer_dir.glob("*.json"))
        if not answer_files:
            errors.append(f"No answer files in: answers/{batch_name}/")

    # Check student roster
    roster_path = Path("student_roster.json")
    if not roster_path.exists():
        warnings.append("student_roster.json not found (optional but recommended)")

    return errors, warnings


def show_setup_summary(batch_name, errors, warnings):
    """Show summary of what's needed"""
    print_section("SETUP VALIDATION")

    if not errors:
        print(f"\n✓ All required files found for '{batch_name}' batch!")
        print("  Ready to run analysis.\n")
        return True

    print(f"\n✗ Missing files for '{batch_name}' batch:\n")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

    if warnings:
        print(f"\n⚠ Warnings:\n")
        for warning in warnings:
            print(f"  • {warning}")

    print("\n📖 Next steps:")
    print("  1. Prepare your exam PDFs and answer files")
    print("  2. Place them in the directories shown above")
    print("  3. Run: python3 analyze.py")
    print()

    return False


def run_setup_wizard(batch_name=None):
    """Run the complete setup wizard"""
    print_section("CISSP ANALYZER - SETUP WIZARD")

    print("\nLet's set up your CISSP analyzer...\n")

    # Step 1: Check roster (auto-create if batch_name provided)
    print("Step 1: Student Roster")
    roster = check_and_create_roster(auto_create=bool(batch_name))

    if not roster:
        print("\n⚠️  Cannot proceed without student_roster.json")
        return False

    # Step 2: Create directories
    print("\nStep 2: Directory Structure")
    check_directories()

    # Step 3: Setup batch files (if specified)
    if batch_name:
        print("\nStep 3: Batch Files")
        errors, warnings = get_batch_files(batch_name)
        return show_setup_summary(batch_name, errors, warnings)
    else:
        print("\nStep 3: Batch Files")
        print("\nExisting batches in student_roster.json:")
        if roster and "batches" in roster:
            for batch_key in roster["batches"].keys():
                if batch_key != "standalone":
                    print(f"  • {batch_key}")
        print("\nSetup will verify files when you select a batch during analysis.")
        print("\n✓ Setup complete! Ready to run analysis.")
        return True


if __name__ == "__main__":
    import sys

    batch_name = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_setup_wizard(batch_name)
    sys.exit(0 if success else 1)
