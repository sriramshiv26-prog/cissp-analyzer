#!/usr/bin/env python3
"""
Analyze standalone/ad-hoc students interactively.
Usage: python3 analyze_standalone.py

Use this when you want to analyze individual students:

Mode [A] - Single Exam (Ad-hoc):
  • One-time exam analysis
  • No history or trends
  • Perfect for: practice tests, new students

Mode [B] - Comparative (With History):
  • Compare current exam to previous exams
  • Show progress and trends
  • Adaptive recommendations based on history
  • Perfect for: tracking improvement, retakes

When prompted, choose your analysis mode.
"""

from cissp_analyzer.interactive_cli import main

print("\n" + "=" * 80)
print("STANDALONE STUDENT ANALYSIS (Ad-hoc / Individual)")
print("=" * 80)
print("\nFor individual students not in Dec-25 or July-26 batches")
print("Perfect for: one-off exams, practice tests, additional students\n")

main()
