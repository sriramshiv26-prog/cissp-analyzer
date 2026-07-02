#!/usr/bin/env python3
"""
Analyze standalone/ad-hoc students interactively.
Usage: python3 analyze_standalone.py

Use this when you want to add individual students
who are not part of Dec-25 or July-26 batches.
"""

from cissp_analyzer.interactive_cli import main

print("\n" + "="*80)
print("STANDALONE STUDENT ANALYSIS (Ad-hoc / Individual)")
print("="*80)
print("\nFor individual students not in Dec-25 or July-26 batches")
print("Perfect for: one-off exams, practice tests, additional students\n")

main()
