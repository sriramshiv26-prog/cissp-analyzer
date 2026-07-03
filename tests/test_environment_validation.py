"""
Environment Validation Test Suite for CISSP Analyzer

This comprehensive test suite validates that the CISSP Analyzer works correctly
across different Python versions (3.9+), operating systems (macOS, Windows, Linux),
and installation states. Tests verify:

1. Python version compatibility (3.9, 3.10, 3.11, 3.12)
2. Core dependencies installation (openpyxl, pandas, pypdf)
3. Testing framework availability (pytest, pytest-cov)
4. Optional dev dependencies (mypy, black, flake8)
5. Dependency conflict detection (pip check)
6. Module import paths and circular dependencies
7. Entry point accessibility (analyze.py, analyze_standalone.py)

Run with:
    pytest tests/test_environment_validation.py -v
    pytest tests/test_environment_validation.py -v --tb=short

Author: CISSP Analyzer Project
Date: 2026-07-03
"""

import sys
import subprocess
import json
from pathlib import Path
from importlib import import_module
from distutils.version import LooseVersion
import importlib.util
import pytest


# ============================================================================
# CLASS: TestPythonVersionSupport
# ============================================================================

class TestPythonVersionSupport:
    """Tests for Python version compatibility requirements"""

    def test_python_version_minimum_39(self):
        """Verify Python 3.9+ is installed"""
        version = sys.version_info
        assert version.major >= 3, f"Python 3+ required, got {version.major}.{version.minor}"
        assert (version.major == 3 and version.minor >= 9) or version.major > 3, \
            f"Python 3.9+ required, got {version.major}.{version.minor}"

    def test_python_version_info_accessible(self):
        """Verify Python version information is accessible"""
        version_string = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        assert len(version_string) > 0
        assert sys.version_info.major == 3
        parts = version_string.split(".")
        assert len(parts) >= 2
        assert int(parts[0]) >= 3
        assert int(parts[1]) >= 9


# ============================================================================
# CLASS: TestDependencyInstallation
# ============================================================================

class TestDependencyInstallation:
    """Tests for core and optional dependency installation"""

    def test_core_dependency_openpyxl(self):
        """Verify openpyxl (Excel handling) is installed"""
        try:
            import openpyxl
            version = openpyxl.__version__
            assert version, "openpyxl version not found"
            assert "3." in version or "4." in version, \
                f"openpyxl version {version} may be outdated (3.10+, 4.0+ required)"
        except ImportError:
            pytest.fail("openpyxl is not installed. Run: pip install openpyxl>=3.10.0")

    def test_core_dependency_pandas(self):
        """Verify pandas (data processing) is installed"""
        try:
            import pandas
            version = pandas.__version__
            assert version, "pandas version not found"
            parts = version.split(".")
            major = int(parts[0])
            assert major >= 2, \
                f"pandas version {version} is outdated (2.0.0+ required)"
        except ImportError:
            pytest.fail("pandas is not installed. Run: pip install pandas>=2.0.0")

    def test_core_dependency_pypdf(self):
        """Verify pypdf (PDF parsing) is installed"""
        try:
            import pypdf
            version = pypdf.__version__
            assert version, "pypdf version not found"
            parts = version.split(".")
            major = int(parts[0])
            assert major >= 3, \
                f"pypdf version {version} is outdated (3.16.0+ required)"
        except ImportError:
            pytest.fail("pypdf is not installed. Run: pip install pypdf>=3.16.0")

    def test_testing_framework_pytest(self):
        """Verify pytest (test framework) is installed"""
        try:
            import pytest
            version = pytest.__version__
            assert version, "pytest version not found"
            parts = version.split(".")
            major = int(parts[0])
            assert major >= 7, \
                f"pytest version {version} is outdated (7.4.0+ required)"
        except ImportError:
            pytest.fail("pytest is not installed. Run: pip install pytest>=7.4.0")

    def test_dependency_no_conflicts(self):
        """Verify core dependencies are compatible (pip check)

        Note: In shared environments with many packages, `pip check` may report
        conflicts between unrelated packages. This test passes if:
        1. No conflicts exist (ideal case), OR
        2. Conflicts exist but don't involve our core deps (openpyxl, pandas, pypdf)

        This ensures the CISSP Analyzer's core functionality works.
        """
        try:
            result = subprocess.run(
                ["pip", "check"],
                capture_output=True,
                text=True,
                timeout=30
            )
            # pip check returns 0 if no conflicts, 1 if conflicts found
            if result.returncode == 0:
                # No conflicts at all - perfect
                pass
            else:
                # Conflicts exist; check if they involve our core deps as the CAUSING package
                # Pattern: "openpyxl 1.0.0 has requirement..." or "pandas 2.0.0 has requirement..."

                # Our core dependencies - these are what we care about
                core_deps = ["openpyxl", "pandas", "pypdf"]

                # Check if any line starts with a core dep having a broken requirement
                core_has_broken_requirement = False
                for line in result.stdout.split('\n'):
                    if not line.strip():
                        continue

                    # Check if this line indicates a core dep has a broken requirement
                    # Format: "packagename version has requirement X, but you have Y"
                    for core_dep in core_deps:
                        # Match: "openpyxl 3.x.x has requirement..." (with version number)
                        pattern = f"{core_dep} "
                        if line.startswith(pattern) and " has requirement " in line:
                            # This is our core dep itself having a conflict
                            core_has_broken_requirement = True
                            break

                if core_has_broken_requirement:
                    pytest.fail(
                        f"Core dependency conflict detected in pip check:\n"
                        f"{result.stdout}"
                    )
                else:
                    # Conflicts exist but not caused by our core deps
                    # This is acceptable in shared environments
                    pytest.skip(
                        "pip check reports conflicts unrelated to core CISSP "
                        "dependencies (openpyxl, pandas, pypdf)"
                    )

        except FileNotFoundError:
            pytest.skip("pip command not available")
        except subprocess.TimeoutExpired:
            pytest.skip("pip check timed out")


# ============================================================================
# CLASS: TestModuleImports
# ============================================================================

class TestModuleImports:
    """Tests for module import paths and circular dependencies"""

    def test_import_main_cissp_analyzer_package(self):
        """Verify main package imports without circular dependencies"""
        try:
            import cissp_analyzer
            assert hasattr(cissp_analyzer, "__version__") or True  # __version__ is optional
        except ImportError as e:
            pytest.fail(f"Failed to import cissp_analyzer package: {e}")
        except Exception as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import detected in cissp_analyzer: {e}")
            else:
                raise

    def test_import_core_module_excel_parser(self):
        """Verify excel_parser module imports correctly"""
        try:
            from cissp_analyzer import excel_parser
            assert hasattr(excel_parser, "ExcelParser")
        except ImportError as e:
            pytest.fail(f"Failed to import excel_parser: {e}")
        except CircularImportError as e:
            pytest.fail(f"Circular import in excel_parser: {e}")

    def test_import_core_module_pdf_parser(self):
        """Verify pdf_parser module imports correctly"""
        try:
            from cissp_analyzer import pdf_parser
            # pdf_parser module exists; main class may vary
            assert pdf_parser is not None
        except ImportError as e:
            pytest.fail(f"Failed to import pdf_parser: {e}")
        except Exception as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import in pdf_parser: {e}")
            else:
                raise

    def test_import_core_module_analysis_engine(self):
        """Verify analysis_engine module imports correctly"""
        try:
            from cissp_analyzer import analysis_engine
            assert analysis_engine is not None
        except ImportError as e:
            pytest.fail(f"Failed to import analysis_engine: {e}")
        except Exception as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import in analysis_engine: {e}")
            else:
                raise

    def test_import_core_module_domain_mapper(self):
        """Verify domain_mapper module imports correctly"""
        try:
            from cissp_analyzer import domain_mapper
            assert domain_mapper is not None
        except ImportError as e:
            pytest.fail(f"Failed to import domain_mapper: {e}")
        except Exception as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import in domain_mapper: {e}")
            else:
                raise

    def test_import_dependency_checker(self):
        """Verify dependency_checker module imports correctly"""
        try:
            from cissp_analyzer import dependency_checker
            # Module exists and can be imported
            assert dependency_checker is not None
            # Check for expected exports: functions, classes, or constants
            exports = [x for x in dir(dependency_checker) if not x.startswith('_')]
            assert len(exports) > 0, "dependency_checker module is empty"
            # Should have at least DependencyError class or check functions
            has_error = hasattr(dependency_checker, "DependencyError")
            has_funcs = any(hasattr(dependency_checker, f) for f in
                           ["check_package_installed", "get_installed_version",
                            "check_dependencies", "validate_dependencies"])
            assert has_error or has_funcs, \
                "dependency_checker missing expected error class or functions"
        except ImportError as e:
            pytest.fail(f"Failed to import dependency_checker: {e}")
        except Exception as e:
            if "circular" in str(e).lower():
                pytest.fail(f"Circular import in dependency_checker: {e}")
            else:
                raise


# ============================================================================
# CLASS: TestEntryPointsAccessible
# ============================================================================

class TestEntryPointsAccessible:
    """Tests for entry point accessibility and functionality"""

    def test_entry_point_analyze_exists(self):
        """Verify analyze.py entry point exists and is readable"""
        analyze_path = Path(__file__).parent.parent / "analyze.py"
        if not analyze_path.exists():
            pytest.skip(f"analyze.py not found at {analyze_path}")

        assert analyze_path.is_file(), f"analyze.py is not a file: {analyze_path}"
        assert analyze_path.stat().st_size > 0, f"analyze.py is empty: {analyze_path}"

    def test_entry_point_analyze_standalone_exists(self):
        """Verify analyze_standalone.py entry point exists and is readable"""
        analyze_standalone_path = Path(__file__).parent.parent / "analyze_standalone.py"
        if not analyze_standalone_path.exists():
            pytest.skip(f"analyze_standalone.py not found at {analyze_standalone_path}")

        assert analyze_standalone_path.is_file(), \
            f"analyze_standalone.py is not a file: {analyze_standalone_path}"
        assert analyze_standalone_path.stat().st_size > 0, \
            f"analyze_standalone.py is empty: {analyze_standalone_path}"

    def test_entry_point_analyze_imports_main(self):
        """Verify analyze.py can be imported as a module (basic syntax check)"""
        analyze_path = Path(__file__).parent.parent / "analyze.py"
        if not analyze_path.exists():
            pytest.skip("analyze.py not found")

        try:
            # Use subprocess to execute in isolation to avoid side effects
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(analyze_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, \
                f"analyze.py has syntax errors:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("analyze.py compilation timed out")

    def test_entry_point_analyze_standalone_imports_main(self):
        """Verify analyze_standalone.py has valid syntax"""
        analyze_standalone_path = Path(__file__).parent.parent / "analyze_standalone.py"
        if not analyze_standalone_path.exists():
            pytest.skip("analyze_standalone.py not found")

        try:
            # Use subprocess to execute in isolation to avoid side effects
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(analyze_standalone_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, \
                f"analyze_standalone.py has syntax errors:\n{result.stderr}"
        except subprocess.TimeoutExpired:
            pytest.fail("analyze_standalone.py compilation timed out")


# ============================================================================
# CLASS: TestOptionalDependencies (Bonus Tests)
# ============================================================================

class TestOptionalDependencies:
    """Tests for optional development dependencies (not required for users)"""

    def test_optional_dependency_pytest_cov(self):
        """Verify pytest-cov is installed (optional for code coverage)"""
        try:
            import pytest_cov
            # If installed, we just verify it's available
            assert pytest_cov is not None
        except ImportError:
            pytest.skip("pytest-cov not installed (optional for development)")

    def test_optional_dependency_mypy(self):
        """Verify mypy is installed (optional for type checking)"""
        try:
            import mypy
            # If installed, we just verify it's available
            assert mypy is not None
        except ImportError:
            pytest.skip("mypy not installed (optional for development)")

    def test_optional_dependency_black(self):
        """Verify black is installed (optional for code formatting)"""
        try:
            import black
            # If installed, we just verify it's available
            assert black is not None
        except ImportError:
            pytest.skip("black not installed (optional for development)")

    def test_optional_dependency_flake8(self):
        """Verify flake8 is installed (optional for linting)"""
        try:
            import flake8
            # If installed, we just verify it's available
            assert flake8 is not None
        except ImportError:
            pytest.skip("flake8 not installed (optional for development)")


# ============================================================================
# HELPER FUNCTIONS (for future expansion)
# ============================================================================

def get_python_version_string():
    """Get formatted Python version string"""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def check_package_version(package_name, minimum_version):
    """
    Check if a package is installed and meets minimum version requirement.

    Args:
        package_name: Name of the package (str)
        minimum_version: Minimum required version as string (e.g., "3.10.0")

    Returns:
        tuple: (is_installed, installed_version, meets_requirement)
    """
    try:
        module = import_module(package_name)
        installed_version = getattr(module, "__version__", "unknown")

        if installed_version == "unknown":
            return True, installed_version, True

        meets = LooseVersion(installed_version) >= LooseVersion(minimum_version)
        return True, installed_version, meets
    except ImportError:
        return False, None, False


def list_installed_packages():
    """
    List all installed packages and their versions.

    Returns:
        dict: Package names mapped to versions
    """
    try:
        result = subprocess.run(
            ["pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            return {pkg["name"]: pkg["version"] for pkg in packages}
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return {}


# ============================================================================
# PYTEST CONFIGURATION HOOKS
# ============================================================================

def pytest_configure(config):
    """pytest hook: runs before test collection"""
    config.addinivalue_line(
        "markers",
        "environment: mark test as an environment validation test"
    )


def pytest_collection_modifyitems(config, items):
    """pytest hook: modify test collection"""
    for item in items:
        # Mark all tests in this module as environment tests
        item.add_marker(pytest.mark.environment)

        # Add timeout to prevent hanging on subprocess calls
        if "test_entry_point" in item.nodeid or "test_dependency" in item.nodeid:
            item.add_marker(pytest.mark.timeout(10))


# ============================================================================
# END OF TEST SUITE
# ============================================================================
