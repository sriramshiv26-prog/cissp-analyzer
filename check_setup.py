#!/usr/bin/env python3
"""
CISSP Analyzer - Setup Prerequisite Checker

Run this FIRST after installation to verify your setup is complete.
Usage: python3 check_setup.py
"""

import sys
import json
from pathlib import Path


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✓{Colors.END} {text}"

    @staticmethod
    def error(text):
        return f"{Colors.RED}✗{Colors.END} {text}"

    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠{Colors.END} {text}"

    @staticmethod
    def info(text):
        return f"{Colors.BLUE}ℹ{Colors.END} {text}"

    @staticmethod
    def header(text):
        return f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}"


def check_python_version():
    """Check Python version is 3.9+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(Colors.success(f"Python version: {version.major}.{version.minor}.{version.micro}"))
        return True
    else:
        print(Colors.error(f"Python {version.major}.{version.minor} detected - need 3.9+"))
        return False


def check_dependencies():
    """Check required packages are installed"""
    required = ['pandas', 'openpyxl', 'pypdf']
    all_ok = True

    for package in required:
        try:
            __import__(package)
            print(Colors.success(f"Package installed: {package}"))
        except ImportError:
            print(Colors.error(f"Package missing: {package}"))
            print(Colors.info("  Fix: pip install -r requirements.txt"))
            all_ok = False

    return all_ok


def check_directories():
    """Check required directories exist"""
    dirs = ['cissp_analyzer', 'tests', 'data', 'outputs']
    all_ok = True

    for d in dirs:
        if Path(d).exists():
            print(Colors.success(f"Directory exists: {d}/"))
        else:
            print(Colors.error(f"Directory missing: {d}/"))
            all_ok = False

    return all_ok


def check_example_files():
    """Check example files are available"""
    examples = [
        ('EXAMPLE_answer_key.json', 'Example answer key'),
        ('EXAMPLE_student_answers.xlsx', 'Example student answers'),
        ('TEMPLATE_answer_key.json', 'Template for custom answer key'),
    ]
    all_ok = True

    print(f"\n{Colors.header('Example/Template Files:')}")
    for filename, description in examples:
        if Path(filename).exists():
            print(Colors.success(f"{description}: {filename}"))
        else:
            print(Colors.warning(f"{description} missing: {filename}"))
            all_ok = False

    return all_ok


def check_entry_points():
    """Check entry point scripts exist"""
    scripts = [
        ('analyze.py', 'Main entry point'),
        ('analyze_standalone.py', 'Standalone analysis'),
    ]
    all_ok = True

    print(f"\n{Colors.header('Entry Points:')}")
    for script, description in scripts:
        if Path(script).exists():
            print(Colors.success(f"{description}: {script}"))
        else:
            print(Colors.error(f"{description} missing: {script}"))
            all_ok = False

    return all_ok


def check_documentation():
    """Check documentation files exist"""
    docs = [
        ('README.md', 'Main documentation'),
        ('INSTALLATION_COMMANDS.md', 'Installation guide'),
        ('QUICK_SETUP_CARD.txt', 'Quick start (printable)'),
        ('DOCUMENTATION_INDEX.md', 'Documentation index'),
    ]
    all_ok = True

    print(f"\n{Colors.header('Documentation:')}")
    for filename, description in docs:
        if Path(filename).exists():
            print(Colors.success(f"{description}: {filename}"))
        else:
            print(Colors.warning(f"{description} missing: {filename}"))

    return all_ok


def suggest_next_steps():
    """Show next steps for user"""
    print(f"\n{Colors.header('='*70)}")
    print(Colors.header("NEXT STEPS"))
    print(Colors.header('='*70))
    print()
    print("1. READ the quick start:")
    print(f"   {Colors.BOLD}cat QUICK_SETUP_CARD.txt{Colors.END}")
    print()
    print("2. TRY with example files first:")
    print(f"   {Colors.BOLD}python3 analyze.py{Colors.END}")
    print(f"   Then select: [2] Standalone Analysis")
    print()
    print("3. PREPARE your own files:")
    print(f"   • Exam PDF (your test file)")
    print(f"   • Student answers Excel (see EXAMPLE_student_answers.xlsx format)")
    print(f"   • See FORMATS_AND_TEMPLATES_GUIDE.md for file format details")
    print()
    print("4. DOCUMENTATION:")
    print(f"   • README.md (overview)")
    print(f"   • INSTALLATION_COMMANDS.md (platform-specific setup)")
    print(f"   • DOCUMENTATION_INDEX.md (complete guide index)")
    print()


def main():
    """Run all checks"""
    print()
    print(Colors.header("="*70))
    print(Colors.header("CISSP ANALYZER - SETUP VERIFICATION"))
    print(Colors.header("="*70))
    print()

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Entry Points", check_entry_points),
        ("Documentation", check_documentation),
        ("Example Files", check_example_files),
    ]

    results = {}
    for name, check_func in checks:
        print(f"\n{Colors.header(name + ':')}")
        results[name] = check_func()

    # Summary
    print()
    print(Colors.header("="*70))
    print(Colors.header("SETUP SUMMARY"))
    print(Colors.header("="*70))
    print()

    all_ok = all(results.values())

    if all_ok:
        print(Colors.success("All checks passed! ✓"))
        print()
        print(Colors.info("Your setup is ready. You can now run:"))
        print(f"  {Colors.BOLD}python3 analyze.py{Colors.END}")
        print()
    else:
        failed = [name for name, ok in results.items() if not ok]
        print(Colors.error(f"Setup incomplete. Issues with: {', '.join(failed)}"))
        print()
        print(Colors.info("Fix these issues:"))
        print("  1. Run: pip install -r requirements.txt")
        print("  2. Check that all directories exist")
        print("  3. Verify example files are present")
        print()

    suggest_next_steps()

    print(Colors.header("="*70))
    print()

    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
