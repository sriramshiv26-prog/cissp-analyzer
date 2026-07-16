#!/usr/bin/env python3
"""
CISSP Analyzer - Menu-driven CLI for exam analysis.
Entry point for Phase 2 unified system.

Usage: python run.py
"""

import sys
import logging
from pathlib import Path

from cissp_analyzer.menu_controller import MenuController
from cissp_analyzer.exam_folder_manager import ExamFolderManager
from cissp_analyzer.pdf_upload_handler import PDFUploadHandler
from cissp_analyzer.exam_processor import ExamProcessor
from cissp_analyzer.class_report_aggregator import ClassReportAggregator
from cissp_analyzer.processing_validator import ProcessingValidator

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class CISSPAnalyzerCLI:
    """Main CLI controller for CISSP Analyzer."""

    def __init__(self):
        """Initialize CLI with components."""
        self.menu = MenuController()
        self.exam_manager = ExamFolderManager()
        self.upload_handler = PDFUploadHandler(self.exam_manager)
        self.validator = ProcessingValidator()

    def run(self):
        """Run main menu loop."""
        try:
            while True:
                # Show main menu
                exams = self.exam_manager.list_exams()
                menu_output = self.menu.show_main_menu(exams)
                print(menu_output)

                # Get user choice
                max_option = len(exams) + 2
                choice = self.menu.get_user_choice(max_option)

                # Process choice
                if choice == str(len(exams) + 1):
                    # Upload new questionnaire
                    self._handle_pdf_upload()

                elif choice == str(len(exams) + 2):
                    # Exit
                    self.menu.show_info_message("Thank you for using CISSP Analyzer!")
                    break

                else:
                    # Select exam
                    try:
                        exam_idx = int(choice) - 1
                        if 0 <= exam_idx < len(exams):
                            self._handle_exam_selection(exams[exam_idx])
                    except (ValueError, IndexError):
                        self.menu.show_error_message("Invalid selection")

        except KeyboardInterrupt:
            print("\n")
            self.menu.show_warning_message("Interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            import traceback

            traceback.print_exc()
            sys.exit(1)

    def _handle_pdf_upload(self):
        """Handle PDF questionnaire upload workflow."""
        try:
            result = self.upload_handler.handle_pdf_upload()
            if result:
                exam_name, folder_path = result
                self.menu.show_success_message(
                    f"Questionnaire '{exam_name}' uploaded successfully!"
                )
        except Exception as e:
            self.menu.show_error_message(f"Upload failed: {str(e)}")

    def _handle_exam_selection(self, exam: dict):
        """Handle exam selection and sub-menu."""
        exam_id = exam.get("folder_id") or exam.get("exam_name", "Unknown")
        exam_path = exam.get("path")

        if not exam_path:
            self.menu.show_error_message("Invalid exam folder")
            return

        while True:
            # Show exam submenu
            exam_menu = self.menu.show_exam_menu(exam.get("exam_name", exam_id))
            print(exam_menu)

            exam_choice = self.menu.get_user_choice(3)

            if exam_choice == "1":
                # Process new answer sheets
                self._process_answer_sheets(exam_path, exam.get("exam_name"))

            elif exam_choice == "2":
                # Generate class report
                self._generate_class_report(exam_path, exam.get("exam_name"))

            elif exam_choice == "3":
                # Back to main menu
                break

    def _process_answer_sheets(self, exam_folder: str, exam_name: str):
        """Process new answer sheets for an exam."""
        try:
            # Validate folder structure
            is_valid, error_msg = self.validator.validate_folder_structure(Path(exam_folder))
            if not is_valid:
                self.menu.show_error_message(f"Folder validation failed: {error_msg}")
                return

            # Initialize processor
            processor = ExamProcessor(Path(exam_folder))

            # Detect new files
            new_files = processor.detect_new_answer_files()

            if not new_files:
                self.menu.show_info_message("No new answer sheets found.")
                return

            # Show summary and get confirmation
            all_files = self.exam_manager.get_new_answer_files(Path(exam_folder).name)
            if not self.menu.show_processing_summary(exam_name, new_files, len(all_files)):
                self.menu.show_warning_message("Processing cancelled.")
                return

            # Process files
            result = processor.process_new_files()

            # Show results
            processed_count = len(result.get("processed", []))
            failed_count = len(result.get("failed", []))
            skipped_count = len(result.get("skipped", []))

            self.menu.show_success_message(
                f"Processing complete! "
                f"Processed: {processed_count}, "
                f"Failed: {failed_count}, "
                f"Skipped: {skipped_count}"
            )

            if result.get("failed"):
                self.menu.show_warning_message("Some files failed to process:")
                for fail in result["failed"]:
                    print(f"  • {fail.get('filename')}: {fail.get('reason')}")

        except Exception as e:
            self.menu.show_error_message(f"Processing failed: {str(e)}")
            import traceback

            traceback.print_exc()

    def _generate_class_report(self, exam_folder: str, exam_name: str):
        """Generate class-level report for an exam."""
        try:
            aggregator = ClassReportAggregator(Path(exam_folder))

            # Validate reports exist
            is_valid, error_msg = aggregator.validate_before_aggregation()
            if not is_valid:
                self.menu.show_error_message(f"Cannot generate report: {error_msg}")
                return

            # Generate metrics
            metrics = aggregator.generate_class_metrics()

            # Show preview
            preview = aggregator.show_preview(metrics)
            print(preview)

            # Get confirmation
            if not self.menu.show_class_report_preview(
                [m["student_name"] for m in metrics.get("student_metrics", [])],
                {"Overall": metrics.get("average_score", 0)},
            ):
                self.menu.show_warning_message("Report generation cancelled.")
                return

            # Generate report
            report_path = aggregator.generate_class_report()
            if report_path:
                self.menu.show_success_message(f"Class report generated: {report_path}")
            else:
                self.menu.show_error_message("Failed to generate class report")

        except Exception as e:
            self.menu.show_error_message(f"Report generation failed: {str(e)}")
            import traceback

            traceback.print_exc()


def main():
    """Main entry point."""
    cli = CISSPAnalyzerCLI()
    cli.run()


if __name__ == "__main__":
    main()
