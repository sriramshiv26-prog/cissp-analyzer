#!/usr/bin/env python3
"""Tests for exam registry, dashboard, and auto-folder management"""

import pytest
import json
from pathlib import Path
from cissp_analyzer.exam_registry import ExamRegistry
from cissp_analyzer.exam_dashboard import ExamDashboard
from cissp_analyzer.auto_folder_manager import AutoFolderManager


class TestExamRegistry:
    """Test exam registration and tracking"""

    def test_register_exam(self, tmp_path):
        """Test registering a new exam"""
        # Use temp directory for testing
        ExamRegistry.REGISTRY_FILE = tmp_path / "registry.json"

        registry = ExamRegistry()
        exam_id = registry.register_exam(
            exam_name="CISSP_June_2026",
            question_bank_path="data/questions/cissp_june.json",
            num_questions=162,
            description="June 2026 CISSP practice test",
        )

        assert exam_id is not None
        assert "CISSP_June_2026" in exam_id

        # Verify exam was saved
        exam = registry.get_exam(exam_id)
        assert exam is not None
        assert exam["exam_name"] == "CISSP_June_2026"
        assert exam["num_questions"] == 162

    def test_list_exams(self, tmp_path):
        """Test listing all registered exams"""
        ExamRegistry.REGISTRY_FILE = tmp_path / "registry.json"

        registry = ExamRegistry()
        registry.register_exam("CISSP_June", "path1", 162)
        registry.register_exam("CISSP_July", "path2", 162)

        exams = registry.list_exams()
        assert len(exams) == 2

    def test_add_student_result(self, tmp_path):
        """Test adding student result to exam"""
        ExamRegistry.REGISTRY_FILE = tmp_path / "registry.json"

        registry = ExamRegistry()
        exam_id = registry.register_exam("CISSP_June", "path", 162)

        registry.add_student_result(exam_id, "Alice", "output/CISSP_Report_Alice.xlsx")

        exam = registry.get_exam(exam_id)
        assert len(exam["student_results"]) == 1
        assert exam["student_results"][0]["student_name"] == "Alice"

    def test_export_summary(self, tmp_path):
        """Test exporting exam summary"""
        ExamRegistry.REGISTRY_FILE = tmp_path / "registry.json"

        registry = ExamRegistry()
        exam_id = registry.register_exam("CISSP_June", "path", 162)
        registry.add_student_result(exam_id, "Alice", "path1")
        registry.add_student_result(exam_id, "Bob", "path2")

        summary = registry.export_summary()
        assert summary["total_exams"] == 1
        assert summary["total_students_analyzed"] == 2


class TestExamDashboard:
    """Test dashboard generation"""

    def test_generate_html_dashboard(self, tmp_path):
        """Test HTML dashboard generation"""
        ExamRegistry.REGISTRY_FILE = tmp_path / "registry.json"

        registry = ExamRegistry()
        registry.register_exam("CISSP_June", "path", 162)

        dashboard = ExamDashboard()
        html_file = tmp_path / "dashboard.html"
        dashboard.generate_html_dashboard(str(html_file))

        assert html_file.exists()
        content = html_file.read_text()
        assert "CISSP Analyzer Dashboard" in content
        assert "CISSP_June" in content

    def test_generate_text_dashboard(self, tmp_path):
        """Test text dashboard generation"""
        ExamRegistry.REGISTRY_FILE = tmp_path / "registry.json"

        registry = ExamRegistry()
        registry.register_exam("CISSP_June", "path", 162)

        dashboard = ExamDashboard()
        text = dashboard.generate_text_dashboard()
        assert "CISSP ANALYZER - EXAM DASHBOARD" in text
        assert "CISSP_June" in text


class TestAutoFolderManager:
    """Test automatic folder management"""

    def test_create_exam_folder(self, tmp_path):
        """Test creating exam folder"""
        manager = AutoFolderManager(str(tmp_path))
        exam_folder = manager.create_exam_folder("CISSP_June_2026")

        assert exam_folder.exists()
        assert "CISSP_June_2026" in exam_folder.name
        assert (exam_folder / ".exam_metadata.json").exists()

    def test_create_student_folder(self, tmp_path):
        """Test creating student folder"""
        manager = AutoFolderManager(str(tmp_path))
        exam_folder = manager.create_exam_folder("CISSP_June")
        student_folder = manager.create_student_report_folder(exam_folder, "Alice")

        assert student_folder.exists()
        assert "Alice" in student_folder.name
        assert exam_folder.name in str(student_folder)

    def test_create_class_folder(self, tmp_path):
        """Test creating class report folder"""
        manager = AutoFolderManager(str(tmp_path))
        exam_folder = manager.create_exam_folder("CISSP_June")
        class_folder = manager.create_class_report_folder(exam_folder)

        assert class_folder.exists()
        assert "class_analysis" in class_folder.name

    def test_get_exam_folder_by_name(self, tmp_path):
        """Test finding exam folder by name"""
        manager = AutoFolderManager(str(tmp_path))
        created_folder = manager.create_exam_folder("CISSP_June")

        found_folder = manager.get_exam_folder_by_name("CISSP_June")
        assert found_folder is not None
        assert found_folder.name == created_folder.name

    def test_list_exam_folders(self, tmp_path):
        """Test listing all exam folders"""
        manager = AutoFolderManager(str(tmp_path))
        manager.create_exam_folder("CISSP_June")
        manager.create_exam_folder("CISSP_July")

        folders = manager.list_exam_folders()
        assert len(folders) == 2
        names = [f["metadata"]["exam_name"] for f in folders]
        assert "CISSP_June" in names
        assert "CISSP_July" in names

    def test_sanitize_name(self, tmp_path):
        """Test name sanitization"""
        manager = AutoFolderManager(str(tmp_path))

        # Test special characters are converted to underscores
        sanitized = manager._sanitize_name("CISSP June 2026!@#")
        assert "CISSP" in sanitized
        assert "June" in sanitized
        assert "2026" in sanitized
        assert manager._sanitize_name("Test-Exam_123") == "Test-Exam_123"

    def test_generate_folder_guide(self, tmp_path):
        """Test folder structure guide generation"""
        manager = AutoFolderManager(str(tmp_path))
        exam_folder = manager.create_exam_folder("CISSP_June")

        guide = manager.generate_folder_structure_guide(exam_folder)
        assert "EXAM FOLDER STRUCTURE" in guide
        assert "students/" in guide
        assert "class_analysis/" in guide
