#!/usr/bin/env python3
"""
Menu Controller - Interactive CLI menu system for CISSP Analyzer.
Provides formatted menus and user input handling with validation.
"""

import sys
from typing import Dict, List, Optional


class MenuController:
    """Manages interactive CLI menus and user input."""

    # ANSI Color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    def __init__(self):
        """Initialize MenuController with color support."""
        # Detect if terminal supports colors
        self.use_colors = sys.stdout.isatty()

    def _colorize(self, text: str, color: str) -> str:
        """
        Apply color to text if terminal supports it.

        Args:
            text: Text to colorize
            color: Color code

        Returns:
            Colored text or plain text
        """
        if not self.use_colors:
            return text
        return f"{color}{text}{self.RESET}"

    def show_main_menu(self, exams: List[Dict]) -> str:
        """
        Display main menu with list of available exams.

        Args:
            exams: List of exam dictionaries with name, created_date, etc

        Returns:
            Formatted menu string
        """
        menu = "\n"
        menu += self._colorize("=" * 70, self.BLUE) + "\n"
        menu += self._colorize(f"{self.BOLD}CISSP ANALYZER - Main Menu{self.RESET}", self.BOLD)
        menu += "\n"
        menu += self._colorize("=" * 70, self.BLUE) + "\n\n"

        if exams:
            menu += self._colorize("Available Questionnaires:\n", self.BOLD)
            for idx, exam in enumerate(exams, 1):
                exam_name = exam.get("exam_name", "Unknown")
                created = exam.get("created_date", "N/A")
                menu += f"  [{idx}] {exam_name}\n"
                menu += f"      Created: {created}\n\n"
        else:
            menu += self._colorize("No questionnaires found.\n\n", self.YELLOW)

        # Add options
        next_option = len(exams) + 1
        menu += self._colorize(f"[{next_option}] Upload NEW questionnaire\n", self.GREEN)
        menu += self._colorize(f"[{next_option + 1}] Exit\n", self.RED)
        menu += "\n"
        menu += self._colorize("=" * 70, self.BLUE) + "\n"

        return menu

    def get_user_choice(self, max_option: int) -> str:
        """
        Prompt user for menu choice and validate input.

        Args:
            max_option: Maximum valid option number

        Returns:
            Validated choice as string

        Raises:
            ValueError: If input is invalid
        """
        while True:
            choice = input(self._colorize("Choose option: ", self.BLUE)).strip()
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= max_option:
                    return choice
                else:
                    print(
                        self._colorize(
                            f"Invalid choice. Please enter 1-{max_option}",
                            self.RED,
                        )
                    )
            except ValueError:
                print(
                    self._colorize(
                        "Invalid input. Please enter a number.",
                        self.RED,
                    )
                )

    def show_exam_menu(self, exam_name: str) -> str:
        """
        Display submenu for exam operations.

        Args:
            exam_name: Name of the selected exam

        Returns:
            Formatted submenu string
        """
        menu = "\n"
        menu += self._colorize("=" * 70, self.BLUE) + "\n"
        menu += self._colorize(f"{self.BOLD}Exam: {exam_name}{self.RESET}", self.BOLD)
        menu += "\n"
        menu += self._colorize("=" * 70, self.BLUE) + "\n\n"
        menu += "  [1] Process new answer sheets\n"
        menu += "  [2] Generate class report\n"
        menu += "  [3] Back to main menu\n"
        menu += "\n"
        menu += self._colorize("=" * 70, self.BLUE) + "\n"

        return menu

    def show_processing_summary(
        self, exam_name: str, new_files: List[str], total_files: Optional[int] = None
    ) -> bool:
        """
        Show summary of files to be processed and ask for confirmation.

        Args:
            exam_name: Name of the exam
            new_files: List of new files to process
            total_files: Total files in exam (optional)

        Returns:
            True if user confirms, False if user cancels
        """
        print("\n" + self._colorize("=" * 70, self.BLUE))
        print(self._colorize(f"Processing Summary - {exam_name}", self.BOLD))
        print(self._colorize("=" * 70, self.BLUE) + "\n")

        if total_files:
            print(f"Total files in exam: {total_files}")

        print(f"New files to process: {self._colorize(str(len(new_files)), self.GREEN)}")
        if new_files:
            print("\nFiles:")
            for f in new_files:
                print(f"  • {f}")

        # Estimate time (roughly 5 seconds per file)
        estimated_time = max(1, len(new_files) * 5)
        print(f"\nEstimated time: ~{estimated_time} seconds\n")

        while True:
            choice = (
                input(self._colorize("Continue processing? (y/n): ", self.YELLOW)).strip().lower()
            )
            if choice in ["y", "yes"]:
                return True
            elif choice in ["n", "no"]:
                return False
            else:
                print(self._colorize("Please enter 'y' or 'n'", self.RED))

    def show_class_report_preview(self, students: List[str], domains: Dict) -> bool:
        """
        Show preview of class report and ask for confirmation.

        Args:
            students: List of student names
            domains: Dictionary of domains to be included in report

        Returns:
            True if user confirms, False if user cancels
        """
        print("\n" + self._colorize("=" * 70, self.BLUE))
        print(self._colorize("Class Report Preview", self.BOLD))
        print(self._colorize("=" * 70, self.BLUE) + "\n")

        print(f"Students to include: {self._colorize(str(len(students)), self.GREEN)}")
        if students:
            print("  Student names:")
            for student in sorted(students):
                print(f"    • {student}")

        print(f"\nDomains to analyze: {self._colorize(str(len(domains)), self.GREEN)}")
        if domains:
            print("  Domains:")
            for domain in sorted(domains.keys()):
                print(f"    • {domain}")

        print()

        while True:
            choice = (
                input(self._colorize("Generate class report? (y/n): ", self.YELLOW)).strip().lower()
            )
            if choice in ["y", "yes"]:
                return True
            elif choice in ["n", "no"]:
                return False
            else:
                print(self._colorize("Please enter 'y' or 'n'", self.RED))

    def show_success_message(self, message: str) -> None:
        """
        Display a success message with checkmark.

        Args:
            message: Success message to display
        """
        checkmark = "✓" if sys.stdout.isatty() else "[✓]"
        print(self._colorize(f"\n{checkmark} {message}\n", self.GREEN))

    def show_error_message(self, error: str) -> None:
        """
        Display an error message with X mark.

        Args:
            error: Error message to display
        """
        cross = "✗" if sys.stdout.isatty() else "[✗]"
        print(self._colorize(f"\n{cross} {error}\n", self.RED))

    def show_info_message(self, message: str) -> None:
        """
        Display an informational message.

        Args:
            message: Info message to display
        """
        print(self._colorize(f"\nℹ {message}\n", self.BLUE))

    def show_warning_message(self, message: str) -> None:
        """
        Display a warning message.

        Args:
            message: Warning message to display
        """
        warning = "⚠" if sys.stdout.isatty() else "[!]"
        print(self._colorize(f"\n{warning} {message}\n", self.YELLOW))
