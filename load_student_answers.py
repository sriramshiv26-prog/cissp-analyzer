#!/usr/bin/env python3
"""
Load complete student answer sets from Excel files
"""

import openpyxl
import json
from pathlib import Path

def load_student_excel(filepath):
    """Load student answers from Excel file"""

    workbook = openpyxl.load_workbook(filepath)
    worksheet = workbook.active

    # Get header row
    headers = [cell.value for cell in worksheet[1]]
    print(f"  Headers: {headers}")

    answers = {}

    # Detect column mapping - match exact headers and common variants
    q_col = None
    a_col = None

    for idx, header in enumerate(headers):
        if header:
            h_str = str(header).strip()
            # Match question columns
            if h_str in ['Questions', 'Question No', 'Q', 'Question', 'Qnum', 'Q No']:
                q_col = idx
            # Match answer columns
            if h_str in ['Answers', 'Answer', 'A', 'StudentAnswer']:
                a_col = idx

    print(f"  Q column index: {q_col}, A column index: {a_col}")

    # Extract answers from rows
    for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=False), start=2):
        if q_col is not None and a_col is not None:
            q_cell = row[q_col]
            a_cell = row[a_col]

            if q_cell.value is not None and a_cell.value is not None:
                q_num = int(q_cell.value) if isinstance(q_cell.value, (int, float)) else None
                answer = str(a_cell.value).strip().upper() if a_cell.value else None

                if q_num and answer and answer in ['A', 'B', 'C', 'D']:
                    answers[q_num] = answer

    return answers

def main():
    # Answer key
    answer_key = {
        1: "D", 2: "B", 3: "B", 4: "C", 5: "C", 6: "B", 7: "A", 8: "C", 9: "D", 10: "D",
        11: "D", 12: "C", 13: "C", 14: "D", 15: "C", 16: "A", 17: "B", 18: "C", 19: "D", 20: "A",
        21: "B", 22: "D", 23: "B", 24: "C", 25: "A", 26: "B", 27: "A", 28: "D", 29: "C", 30: "A",
        31: "B", 32: "D", 33: "B", 34: "C", 35: "C", 36: "B", 37: "A", 38: "D", 39: "A", 40: "B",
        41: "B", 42: "B", 43: "C", 44: "A", 45: "D", 46: "C", 47: "C", 48: "B", 49: "C", 50: "C",
        51: "B", 52: "A", 53: "C", 54: "A", 55: "C", 56: "A", 57: "D", 58: "D", 59: "C", 60: "C",
        61: "B", 62: "A", 63: "B", 64: "D", 65: "A", 66: "D", 67: "B", 68: "C", 69: "D", 70: "B",
        71: "A", 72: "B", 73: "B", 74: "B", 75: "C", 76: "D", 77: "A", 78: "A", 79: "C", 80: "C",
        81: "C", 82: "C", 83: "A", 84: "B", 85: "A", 86: "B", 87: "B", 88: "C", 89: "D", 90: "B",
        91: "A", 92: "B", 93: "B", 94: "B", 95: "B", 96: "B", 97: "A", 98: "A", 99: "B", 100: "D",
        101: "C", 102: "C", 103: "B", 104: "C", 105: "D", 106: "D", 107: "A", 108: "B", 109: "C", 110: "C",
        111: "D", 112: "C", 113: "B", 114: "B", 115: "B", 116: "A", 117: "B", 118: "D", 119: "C", 120: "B",
        121: "A", 122: "C", 123: "C", 124: "D", 125: "C", 126: "D", 127: "D", 128: "B", 129: "A", 130: "A",
        131: "B", 132: "D", 133: "B", 134: "A", 135: "D", 136: "D", 137: "D", 138: "C", 139: "D", 140: "C",
        141: "A", 142: "B", 143: "D", 144: "A", 145: "C", 146: "A", 147: "A", 148: "C", 149: "C", 150: "D",
        151: "B", 152: "D", 153: "A", 154: "B", 155: "B", 156: "C", 157: "D", 158: "B", 159: "D", 160: "C",
        161: "A", 162: "C"
    }

    # Student files
    student_files = {
        "Kapil": "/Users/sriram/Downloads/kapil-july-12.xlsx",
        "Aman": "/Users/sriram/Downloads/Mock Test Aman 11 july.xlsx",
        "Senthilraj": "/Users/sriram/Downloads/12 July 2026-Mock test 7 - Senthilraj.xlsx",
        "Praveena": "/Users/sriram/Downloads/Mock Test - 07 Jul - Praveena.xlsx"
    }

    all_data = {
        "answer_key": answer_key,
        "students": []
    }

    for student_name, filepath in student_files.items():
        print(f"\nLoading: {student_name}")
        if Path(filepath).exists():
            answers = load_student_excel(filepath)
            print(f"  Loaded {len(answers)} answers")

            # Calculate score
            if len(answers) == 0:
                print(f"  ❌ No answers found in file")
                continue

            correct = sum(1 for q, a in answers.items() if a == answer_key.get(q, ""))
            total = len(answers)

            # Find wrong questions
            wrong_questions = []
            for q_num in range(1, 163):
                if q_num in answers:
                    student_ans = answers[q_num]
                    expected_ans = answer_key[q_num]
                    if student_ans != expected_ans:
                        wrong_questions.append({
                            "q": q_num,
                            "expected": expected_ans,
                            "given": student_ans
                        })

            print(f"  Score: {correct}/{total} ({correct/total*100:.1f}%)")
            print(f"  Wrong: {len(wrong_questions)} questions")

            all_data["students"].append({
                "name": student_name,
                "total_questions": total,
                "correct": correct,
                "wrong": len(wrong_questions),
                "score_percentage": round(correct / total * 100, 1),
                "score_display": f"{correct}/{total} ({correct/total*100:.1f}%)",
                "answers": answers,
                "wrong_questions": wrong_questions
            })
        else:
            print(f"  ❌ File not found: {filepath}")

    # Save complete data
    with open('students_complete_answers.json', 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"\n✅ Saved complete student data to: students_complete_answers.json")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for student in all_data["students"]:
        print(f"{student['name']:15} | {student['score_display']:20} | Wrong: {student['wrong']:2}")

if __name__ == "__main__":
    main()
