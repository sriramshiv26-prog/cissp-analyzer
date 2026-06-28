#!/usr/bin/env python3
"""
Regenerate question_domain_mapping.json by analyzing actual question text
"""
import json
from pathlib import Path
from cissp_analyzer.pdf_parser import PDFParser
from cissp_analyzer.question_analyzer import QuestionAnalyzer


def regenerate_mapping(pdf_path: str, output_path: str = 'data/question_domain_mapping.json'):
    """Extract questions from PDF and generate mapping"""

    print("=" * 70)
    print("REGENERATING QUESTION DOMAIN MAPPING FROM PDF")
    print("=" * 70)

    # Extract questions
    print("\nExtracting questions from PDF...")
    parser = PDFParser(pdf_path)
    questions = parser.extract_questions()
    print(f"Extracted {len(questions)} questions")

    # Analyze each question
    print("\nAnalyzing questions...")
    mapping = {}

    for q in questions:
        analysis = QuestionAnalyzer.analyze(
            q['number'],
            q['text'],
            q['options']
        )

        # Format for storage
        mapping[str(q['number'])] = {
            'domain': analysis['domain'],
            'topic': analysis['topic'],
            'subtopic': analysis['subtopic'],
            'difficulty': analysis['difficulty'],
            'question_type': analysis['question_type'],
            'exam_trick': analysis['exam_trick'],
        }

        if q['number'] <= 5 or q['number'] > 120:  # Show first 5 and last 5
            print(f"\nQ{q['number']}:")
            print(f"  Topic: {analysis['topic']}")
            print(f"  Domain: {analysis['domain']}")
            print(f"  Type: {analysis['question_type']}")
            print(f"  Difficulty: {analysis['difficulty']}")
            print(f"  Trick: {analysis['exam_trick']}")

    # Save mapping
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"\n{'='*70}")
    print(f"✓ Saved {len(mapping)} questions to {output_path}")
    print(f"{'='*70}\n")

    return mapping


if __name__ == '__main__':
    pdf_path = "/Users/sriram/Downloads/Jun28th- Exam 2 with Answers.pdf"
    regenerate_mapping(pdf_path)
