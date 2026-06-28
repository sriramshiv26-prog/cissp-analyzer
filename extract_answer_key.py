#!/usr/bin/env python3
"""Extract complete answer key from PDF, including multi-part answers"""
import re
import json
from pypdf import PdfReader

pdf_path = "/Users/sriram/Downloads/Jun28th- Exam 2 with Answers.pdf"
reader = PdfReader(pdf_path)

all_text = ""
for page in reader.pages:
    all_text += page.extract_text() + "\n"

# Find answer key section
answer_section_start = all_text.lower().find("correct answer")
answer_section = all_text[answer_section_start:]

answers = {}

# Extract all answer lines: "N. X." or "N. X, Y, Z." format
lines = answer_section.split('\n')
for line in lines:
    line = line.strip()
    
    # Try to match Q#. with answers (single or multi-part)
    # Pattern: "43. 1-B, 2-A, 3-C" or "123. A."
    match = re.match(r'^(\d+)\.\s+(.+?)(?:\s+\.|$)', line)
    if match:
        q_num = match.group(1)
        answer_part = match.group(2).strip()
        
        # Clean up the answer
        answer_part = answer_part.rstrip('.')
        answers[q_num] = answer_part

# Normalize all answers
from cissp_analyzer.excel_parser import ExcelParser
normalized = {}
for q_num, raw_answer in answers.items():
    normalized_answer = ExcelParser.normalize_answer(raw_answer)
    normalized[q_num] = normalized_answer
    
    if int(q_num) in [43, 64, 123, 124, 125]:
        print(f"Q{q_num}: '{raw_answer}' → '{normalized_answer}'")

print(f"\nExtracted {len(normalized)} answers")

# Save
with open('/Users/sriram/Downloads/answer_key.json', 'w') as f:
    json.dump(normalized, f, indent=2)

print("Saved to answer_key.json")
