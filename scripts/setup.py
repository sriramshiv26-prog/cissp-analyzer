#!/usr/bin/env python3
"""
Interactive setup wizard for CISSP Analyzer
Guides user through configuring and running batch analysis
"""

import json
import subprocess
from pathlib import Path

def prompt(message, default=None):
    """Prompt user for input"""
    if default:
        msg = f"{message} [{default}]: "
    else:
        msg = f"{message}: "

    response = input(msg).strip()
    return response if response else default

def validate_file(path):
    """Check if file exists"""
    if not Path(path).exists():
        print(f"❌ File not found: {path}")
        return False
    return True

def run_command(cmd, description):
    """Run command safely"""
    print(f"\n⚙️  {description}...")
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("CISSP ANALYZER - SETUP WIZARD")
    print("="*70)
    print("\nThis wizard will configure your exam analysis.\n")

    # Step 1: Exam PDF
    print("STEP 1: Exam PDF")
    print("-" * 70)
    while True:
        pdf_path = prompt("Enter path to exam PDF (with questions and answers)")
        if validate_file(pdf_path):
            break

    # Step 2: Answer Key
    print("\n✓ PDF found")
    print("\nSTEP 2: Answer Key")
    print("-" * 70)
    answer_key_path = prompt("Enter path to answer key JSON (or leave blank to auto-extract)",
                             "/Users/sriram/Downloads/answer_key.json")

    if not Path(answer_key_path).exists():
        print(f"\n⚙️  Answer key will be auto-extracted from PDF")
        auto_extract = True
    else:
        print(f"✓ Answer key found: {answer_key_path}")
        auto_extract = False

    # Step 3: Output directory
    print("\nSTEP 3: Output Directory")
    print("-" * 70)
    output_dir = prompt("Where to save reports", "outputs")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Step 4: Students
    print("\nSTEP 4: Students")
    print("-" * 70)
    num_students = int(prompt("How many students", "1"))

    students = []
    for i in range(num_students):
        print(f"\nStudent {i+1}/{num_students}:")
        name = prompt("  Student name")

        while True:
            excel_path = prompt("  Excel file path")
            if validate_file(excel_path):
                break

        students.append({
            "name": name,
            "excel": excel_path
        })

    # Step 5: Generate config
    print("\n" + "="*70)
    print("GENERATING CONFIGURATION")
    print("="*70)

    config = {
        "exam_pdf": pdf_path,
        "answer_key": answer_key_path,
        "output_dir": output_dir,
        "students": students
    }

    config_file = "batch_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"\n✓ Config saved: {config_file}")

    # Step 6: Regenerate mapping
    print("\n" + "="*70)
    print("RUNNING BATCH ANALYSIS")
    print("="*70)

    run_command(["python3", "regenerate_mapping.py"], "Regenerating question domain mapping")
    run_command(["python3", "run_batch.py", config_file], "Analyzing all students")

    print("\n" + "="*70)
    print("✓ SETUP COMPLETE!")
    print("="*70)
    print(f"\nReports saved to: {output_dir}/")
    print(f"  - CISSP_Individual_Report_[StudentName].xlsx")
    print(f"  - CISSP_Class_Analysis.xlsx")
    print("\n" + "="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
