"""
Dependency checker for CISSP Analyzer.

Verifies that all required packages are installed and provides helpful
installation instructions if any are missing.
"""

import sys
import importlib.util
from typing import List, Tuple, Optional


# Required dependencies with their import names and minimum versions
REQUIRED_DEPENDENCIES = {
    "openpyxl": ("openpyxl", "3.10.0", "Excel file handling"),
    "pandas": ("pandas", "2.0.0", "Data processing and analysis"),
    "pypdf": ("pypdf", "3.16.0", "PDF parsing and extraction"),
}

# Optional development dependencies
OPTIONAL_DEPENDENCIES = {
    "pytest": ("pytest", "7.4.0", "Testing framework (for development)"),
    "mypy": ("mypy", "1.5.0", "Type checking (for development)"),
    "black": ("black", "23.0.0", "Code formatting (for development)"),
}


class DependencyError(ImportError):
    """Raised when a required dependency is missing"""
    pass


def check_package_installed(package_name: str) -> bool:
    """Check if a package is installed.

    Args:
        package_name: Name of the package (import name)

    Returns:
        True if package is installed, False otherwise
    """
    return importlib.util.find_spec(package_name) is not None


def get_installed_version(package_name: str) -> Optional[str]:
    """Get the installed version of a package.

    Args:
        package_name: Name of the package (import name)

    Returns:
        Version string if found, None otherwise
    """
    try:
        module = importlib.import_module(package_name)
        # Try common version attributes
        for attr in ["__version__", "VERSION", "version"]:
            if hasattr(module, attr):
                return str(getattr(module, attr))
        return None
    except ImportError:
        return None


def compare_versions(installed: str, required: str) -> bool:
    """Compare version strings (simple comparison).

    Args:
        installed: Installed version string
        required: Required minimum version string

    Returns:
        True if installed >= required, False otherwise
    """
    try:
        installed_parts = [int(x) for x in installed.split(".")[:3]]
        required_parts = [int(x) for x in required.split(".")[:3]]

        # Pad with zeros if needed
        while len(installed_parts) < len(required_parts):
            installed_parts.append(0)
        while len(required_parts) < len(installed_parts):
            required_parts.append(0)

        return installed_parts >= required_parts
    except (ValueError, AttributeError):
        # If we can't parse versions, assume it's ok
        return True


def check_required_dependencies(verbose: bool = False) -> Tuple[List[str], List[str]]:
    """Check all required dependencies.

    Args:
        verbose: If True, print missing dependencies information

    Returns:
        Tuple of (missing_packages, version_issues)
        - missing_packages: List of packages that are not installed
        - version_issues: List of packages with version mismatches
    """
    missing = []
    version_issues = []

    for package_name, (import_name, min_version, description) in REQUIRED_DEPENDENCIES.items():
        if not check_package_installed(import_name):
            missing.append((package_name, min_version, description))
        else:
            installed = get_installed_version(import_name)
            if installed and not compare_versions(installed, min_version):
                version_issues.append((package_name, installed, min_version, description))

    if verbose and missing:
        print_missing_dependencies(missing)

    return missing, version_issues


def check_optional_dependencies() -> List[Tuple[str, str, str]]:
    """Check optional dependencies (for development).

    Returns:
        List of missing optional packages (name, min_version, description)
    """
    missing = []

    for package_name, (import_name, min_version, description) in OPTIONAL_DEPENDENCIES.items():
        if not check_package_installed(import_name):
            missing.append((package_name, min_version, description))

    return missing


def print_missing_dependencies(missing: List[Tuple[str, str, str]]):
    """Print installation instructions for missing dependencies.

    Args:
        missing: List of (package_name, min_version, description)
    """
    if not missing:
        return

    print("\n" + "=" * 70)
    print("MISSING DEPENDENCIES")
    print("=" * 70)

    for package, version, description in missing:
        print(f"\n  ❌ {package} (>={version}) - {description}")

    print("\n" + "-" * 70)
    print("Installation options:")
    print("-" * 70)

    print("\nOption 1: Install from requirements.txt")
    print("  pip install -r requirements.txt")

    print("\nOption 2: Install specific package(s)")
    packages_str = " ".join([m[0] for m in missing])
    print(f"  pip install {packages_str}")

    print("\nOption 3: Install with setup.py")
    print("  pip install -e .")

    print("\nOption 4: Install with development dependencies")
    print("  pip install -e '.[dev]'")

    print("\n" + "=" * 70 + "\n")


def print_version_issues(issues: List[Tuple[str, str, str, str]]):
    """Print information about version mismatches.

    Args:
        issues: List of (package_name, installed_version, required_version, description)
    """
    if not issues:
        return

    print("\n" + "=" * 70)
    print("VERSION WARNINGS")
    print("=" * 70)

    for package, installed, required, description in issues:
        print(f"\n  ⚠️  {package}")
        print(f"     Installed: {installed}")
        print(f"     Required:  >={required}")
        print(f"     ({description})")

    print("\n" + "-" * 70)
    print("To update packages:")
    packages_str = " ".join([issue[0] for issue in issues])
    print(f"  pip install --upgrade {packages_str}")
    print("\n" + "=" * 70 + "\n")


def ensure_dependencies() -> bool:
    """Check all dependencies and raise error if critical ones are missing.

    Returns:
        True if all dependencies OK, False if only optional missing

    Raises:
        DependencyError: If required dependencies are missing
    """
    missing, version_issues = check_required_dependencies()

    if missing:
        print_missing_dependencies(missing)
        raise DependencyError(
            f"Missing required dependencies: {', '.join(m[0] for m in missing)}\n"
            "Run 'pip install -r requirements.txt' to install."
        )

    if version_issues:
        print_version_issues(version_issues)
        # Warn but don't fail for version mismatches

    # Check optional dependencies quietly
    optional_missing = check_optional_dependencies()
    if optional_missing:
        # Silently skip - these are just for development
        pass

    return True


def print_dependency_status():
    """Print a summary of all dependencies (required and optional)."""
    print("\n" + "=" * 70)
    print("CISSP ANALYZER - DEPENDENCY STATUS")
    print("=" * 70)

    print("\nREQUIRED DEPENDENCIES:")
    print("-" * 70)
    for package, (import_name, min_version, description) in REQUIRED_DEPENDENCIES.items():
        if check_package_installed(import_name):
            version = get_installed_version(import_name) or "unknown"
            print(f"  ✓ {package:<20} {version:<15} {description}")
        else:
            print(f"  ✗ {package:<20} NOT INSTALLED     {description}")

    print("\nOPTIONAL DEPENDENCIES (Development):")
    print("-" * 70)
    for package, (import_name, min_version, description) in OPTIONAL_DEPENDENCIES.items():
        if check_package_installed(import_name):
            version = get_installed_version(import_name) or "unknown"
            print(f"  ✓ {package:<20} {version:<15} {description}")
        else:
            print(f"  - {package:<20} NOT INSTALLED     {description}")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    # If run directly, print status
    print_dependency_status()
