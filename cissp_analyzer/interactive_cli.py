#!/usr/bin/env python3
"""
Interactive CLI for CISSP Analyzer - Simple step-by-step setup.

Guides users through analyzing exams by asking for:
- Which exam (Mock 1, Mock 2, etc.)
- Exam PDF location
- Student names
- Student answer files
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from cissp_analyzer.main import CISSPAnalyzer
from cissp_analyzer.filename_parser import FilenameParser


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def header(text: str) -> str:
        return f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}"

    @staticmethod
    def success(text: str) -> str:
        return f"{Colors.GREEN}✓ {text}{Colors.END}"

    @staticmethod
    def error(text: str) -> str:
        return f"{Colors.RED}✗ {text}{Colors.END}"

    @staticmethod
    def warning(text: str) -> str:
        return f"{Colors.YELLOW}⚠ {text}{Colors.END}"

    @staticmethod
    def info(text: str) -> str:
        return f"{Colors.BLUE}ℹ {text}{Colors.END}"


def prompt(question: str, default: Optional[str] = None, required: bool = True) -> str:
    """Prompt user for input.

    Args:
        question: Question to ask
        default: Default value if user presses Enter
        required: If True, keep asking until user provides non-empty answer

    Returns:
        User input or default value
    """
    while True:
        if default:
            msg = f"{Colors.BOLD}{question}{Colors.END} [{default}]: "
        else:
            msg = f"{Colors.BOLD}{question}{Colors.END}: "

        response = input(msg).strip()

        if response:
            return response
        elif default:
            return default
        elif not required:
            return ""
        else:
            print(Colors.warning("This field is required. Please enter a value."))


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        question: Question to ask
        default: Default answer if user presses Enter

    Returns:
        True if yes, False if no
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{Colors.BOLD}{question}{Colors.END} [{default_str}]: ").strip().lower()

    if not response:
        return default
    return response in ['y', 'yes']


def validate_file(filepath: str) -> bool:
    """Check if file exists.

    Args:
        filepath: Path to file

    Returns:
        True if file exists, False otherwise
    """
    return Path(filepath).exists()


def select_exam_number() -> int:
    """Ask user which exam number they're analyzing.

    Returns:
        Exam number (1, 2, 3, etc.)
    """
    print("\n" + Colors.header("=" * 70))
    print(Colors.header("CISSP ANALYZER - EXAM SELECTION"))
    print(Colors.header("=" * 70))

    print("\nWhich exam are you analyzing?")
    print("  Examples: 1 (Mock 1), 2 (Mock 2), 3 (Practice Test 3), etc.")

    while True:
        try:
            exam_num = int(prompt("Exam number"))
            if exam_num > 0:
                return exam_num
            else:
                print(Colors.error("Exam number must be positive"))
        except ValueError:
            print(Colors.error("Please enter a valid number"))


def get_exam_pdf() -> str:
    """Prompt for exam PDF file path.

    Returns:
        Path to exam PDF
    """
    print("\n" + Colors.header("-" * 70))
    print(Colors.header("STEP 1: EXAM PDF"))
    print(Colors.header("-" * 70))
    print("Provide the path to your CISSP exam PDF")
    print("(Should contain questions and answer key)")

    while True:
        pdf_path = prompt("Path to exam PDF file")
        if validate_file(pdf_path):
            print(Colors.success(f"PDF found: {pdf_path}"))
            return pdf_path
        else:
            print(Colors.error(f"File not found: {pdf_path}"))
            print(Colors.info("Try using the full path, e.g. /Users/name/exams/mock1.pdf"))


def get_answer_key() -> Optional[str]:
    """Prompt for answer key file or offer auto-extraction.

    Returns:
        Path to answer key JSON, or special marker "__AUTO_EXTRACT__" for auto-extraction, or None
    """
    print("\n" + Colors.header("-" * 70))
    print(Colors.header("STEP 2: ANSWER KEY (Optional)"))
    print(Colors.header("-" * 70))
    print("Do you have an answer key file? (JSON format)")
    print("Format: {'1': 'A', '2': 'B', ...}")
    print("OR: We can auto-extract answers from the exam PDF")
    print("(Auto-extract also uses answer text to improve domain classification)")

    answer_key = prompt("Path to answer key (optional)", required=False)

    if answer_key:
        if validate_file(answer_key):
            print(Colors.success(f"Answer key found: {answer_key}"))
            return answer_key
        else:
            print(Colors.warning(f"File not found: {answer_key}"))
            if prompt_yes_no("Try auto-extract instead?", default=True):
                return "__AUTO_EXTRACT__"
            else:
                return get_answer_key()
    else:
        if prompt_yes_no("Auto-extract answers from PDF?", default=True):
            return "__AUTO_EXTRACT__"
        else:
            print(Colors.info("Will proceed without answer key"))
            return None


def add_students() -> List[Dict[str, str]]:
    """Interactively add students and their answer files.

    Returns:
        List of dicts with 'name' and 'excel' keys
    """
    print("\n" + Colors.header("-" * 70))
    print(Colors.header("STEP 3: ADD STUDENTS"))
    print(Colors.header("-" * 70))

    students = []
    student_num = 1

    while True:
        print(f"\n{Colors.BOLD}Student {student_num}:{Colors.END}")

        # Get student name
        student_name = prompt("Student name (or press Enter if done adding)", required=False)
        if not student_name:
            if student_num == 1:
                print(Colors.warning("At least one student is required"))
                continue
            else:
                break

        # Get student answer file
        while True:
            answer_file = prompt(f"Excel file for {student_name}")
            if validate_file(answer_file):
                students.append({
                    "name": student_name,
                    "excel": answer_file
                })
                print(Colors.success(f"Added: {student_name}"))
                break
            else:
                print(Colors.error(f"File not found: {answer_file}"))
                if not prompt_yes_no("Try again?", default=True):
                    break

        student_num += 1

    return students


def get_output_directory() -> str:
    """Prompt for output directory.

    Returns:
        Path to output directory
    """
    print("\n" + Colors.header("-" * 70))
    print(Colors.header("STEP 4: OUTPUT DIRECTORY"))
    print(Colors.header("-" * 70))

    output_dir = prompt("Where to save reports", default="outputs")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    print(Colors.success(f"Output directory: {output_dir}"))
    return output_dir


def display_summary(exam_num: int, pdf: str, students: List[Dict], output: str):
    """Display configuration summary before running analysis.

    Args:
        exam_num: Exam number
        pdf: Path to exam PDF
        students: List of students
        output: Output directory
    """
    print("\n" + Colors.header("=" * 70))
    print(Colors.header("CONFIGURATION SUMMARY"))
    print(Colors.header("=" * 70))

    print(f"\n{Colors.BOLD}Exam:{Colors.END} Mock {exam_num}")
    print(f"{Colors.BOLD}PDF:{Colors.END} {pdf}")
    print(f"{Colors.BOLD}Students:{Colors.END} {len(students)}")
    for student in students:
        print(f"  • {student['name']}: {student['excel']}")
    print(f"{Colors.BOLD}Output:{Colors.END} {output}")

    print("\n" + "=" * 70)


def run_analysis(pdf: str, students: List[Dict], output: str, answer_key: Optional[str]):
    """Run the CISSP Analyzer on the provided data.

    Args:
        pdf: Path to exam PDF
        students: List of students with their answer files
        output: Output directory
        answer_key: Optional path to answer key JSON, or "__AUTO_EXTRACT__" marker
    """
    print("\n" + Colors.header("=" * 70))
    print(Colors.header("RUNNING ANALYSIS"))
    print(Colors.header("=" * 70))

    try:
        # Initialize analyzer
        print("\n" + Colors.info("Initializing analyzer..."))
        analyzer = CISSPAnalyzer(mapping_file='data/question_domain_mapping.json')

        # Load or auto-extract answer key
        if answer_key == "__AUTO_EXTRACT__":
            print(Colors.info("Auto-extracting answers with domain context enhancement..."))
            from cissp_analyzer.pdf_parser import PDFParser
            from cissp_analyzer.answer_key_extractor import AnswerKeyExtractor

            try:
                # Extract with answer context
                print(Colors.info("Analyzing question-answer pairs..."))
                parser = PDFParser(pdf)

                # Extract text from PDF
                from pypdf import PdfReader
                reader = PdfReader(pdf)
                pdf_text = ""
                for page in reader.pages:
                    pdf_text += page.extract_text() + "\n"

                # Use the static method for enhanced extraction
                enhanced_context = PDFParser.extract_with_answer_context(pdf_text)

                if enhanced_context:
                    extracted_count = len(enhanced_context)
                    print(Colors.success(f"Extracted and analyzed {extracted_count} questions"))

                    # Warn if extraction seems incomplete (expecting at least 30 questions)
                    if extracted_count < 30:
                        print(Colors.warning(f"Only {extracted_count} questions found. Auto-extract may be incomplete."))
                        if not prompt_yes_no("Continue with incomplete extraction?", default=False):
                            print(Colors.info("Skipping auto-extract, continuing without answer key"))
                            answer_key = None
                            extracted_answers = {}

                    # Count domain hints from answer text
                    domains_found = set()
                    for q_num, context in enhanced_context.items():
                        if context.get("suggested_domain"):
                            domains_found.add(context["suggested_domain"])

                    if domains_found:
                        print(Colors.info(f"Domains identified: {', '.join(sorted(domains_found)[:3])}..."))

                    # Save extracted answers (full text for reference)
                    temp_key_path = Path(output) / ".answer_key_extracted.json"
                    extractor = AnswerKeyExtractor()

                    # Get answers from enhanced context
                    answer_map = {}
                    for q_num, context in enhanced_context.items():
                        if context.get("answer_letter"):
                            answer_map[q_num] = {
                                "letter": context["answer_letter"],
                                "text": context.get("answer_text", "")
                            }

                    # Save full version for reference
                    if answer_map:
                        extractor.answers = answer_map
                        extractor.save_as_json(str(temp_key_path), include_text=True)
                        print(Colors.success(f"Answer key saved to: {temp_key_path}"))

                        # Extract letters only for analyzer
                        letters_only = {q: data["letter"] for q, data in answer_map.items()}
                        # Normalize to integers for analyzer
                        normalized_key = {}
                        for q_num, letter in letters_only.items():
                            q_int = int(q_num) if isinstance(q_num, str) else q_num
                            normalized_key[q_int] = letter

                        # Validate normalized key
                        for q_num, letter in normalized_key.items():
                            assert isinstance(q_num, int), f"Question number must be int, got {type(q_num)}"
                            assert letter in ["A", "B", "C", "D", "E"], f"Invalid answer letter: {letter}"

                        analyzer.analysis_engine.set_answer_key(normalized_key)
                else:
                    print(Colors.warning("No answers found in PDF"))

            except Exception as e:
                print(Colors.warning(f"Auto-extraction failed: {str(e)}"))
                print(Colors.info("Continuing analysis without answer key..."))

        elif answer_key:
            print(Colors.info(f"Loading answer key from {answer_key}"))
            analyzer.set_answer_key_from_file(answer_key)

        # Extract student names
        student_names = [s['name'] for s in students]

        # Run analysis
        print(Colors.info(f"Analyzing {len(students)} student(s)..."))
        result = analyzer.analyze(
            exam_pdf=pdf,
            answer_excel=students[0]['excel'],  # First student's file
            student_names=student_names,
            output_dir=output
        )

        # Display results
        print("\n" + Colors.header("=" * 70))
        print(Colors.header("ANALYSIS COMPLETE!"))
        print(Colors.header("=" * 70))

        print(f"\n{Colors.success('Individual reports:')}")
        for report in result.get('individual_reports', []):
            print(f"  • {report}")

        print(f"\n{Colors.success('Class report:')}")
        print(f"  • {result.get('class_report', 'N/A')}")

        print(f"\n{Colors.success('Students analyzed:')} {result.get('students_analyzed', 0)}")

        print("\n" + "=" * 70)
        print(Colors.success("Reports saved to: " + output))
        print("=" * 70 + "\n")

    except Exception as e:
        print("\n" + Colors.error(f"Analysis failed: {str(e)}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main interactive CLI flow."""
    try:
        # Welcome
        print("\n" + Colors.header("╔" + "═" * 68 + "╗"))
        print(Colors.header("║" + " " * 15 + "CISSP ANALYZER - INTERACTIVE SETUP" + " " * 19 + "║"))
        print(Colors.header("╚" + "═" * 68 + "╝"))

        # Step 1: Exam selection
        exam_num = select_exam_number()

        # Step 2: Exam PDF
        exam_pdf = get_exam_pdf()

        # Step 3: Answer key
        answer_key = get_answer_key()

        # Step 4: Add students
        students = add_students()

        # Step 5: Output directory
        output_dir = get_output_directory()

        # Display summary
        display_summary(exam_num, exam_pdf, students, output_dir)

        # Confirm before running
        if not prompt_yes_no("Run analysis now?", default=True):
            print(Colors.info("Analysis cancelled"))
            sys.exit(0)

        # Run analysis
        run_analysis(exam_pdf, students, output_dir, answer_key)

    except KeyboardInterrupt:
        print("\n\n" + Colors.warning("Setup cancelled by user"))
        sys.exit(0)
    except Exception as e:
        print("\n" + Colors.error(f"Unexpected error: {str(e)}"))
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
