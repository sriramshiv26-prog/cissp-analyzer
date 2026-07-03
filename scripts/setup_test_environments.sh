#!/bin/bash

################################################################################
# setup_test_environments.sh
#
# Multi-Python Environment Setup Script for CISSP Analyzer
#
# Purpose:
#   Create isolated Python virtual environments for testing the CISSP Analyzer
#   across multiple Python versions (3.9, 3.10, 3.11, 3.12) on macOS, Windows,
#   and Linux.
#
# Features:
#   - Automatic OS detection (macOS/Darwin, Windows, Linux)
#   - Python version checking and installation guidance
#   - Virtual environment creation for Python 3.9, 3.10, 3.11, 3.12
#   - Automatic dependency installation from requirements.txt
#   - Environment activation instructions
#   - Comprehensive error handling and reporting
#
# Usage:
#   bash scripts/setup_test_environments.sh
#   sh scripts/setup_test_environments.sh
#
# Requirements:
#   - Python 3.9 or higher installed
#   - pip installed for each Python version
#   - Bash or POSIX shell (sh)
#   - 2+ GB disk space for virtual environments
#
# Author: CISSP Analyzer Project
# Date: 2026-07-03
#
################################################################################

set -e  # Exit on first error

# ============================================================================
# CONFIGURATION
# ============================================================================

# Color codes for output (disable on non-TTY)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'  # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_ENVS_DIR="${PROJECT_ROOT}/test_environments"
PYTHON_VERSIONS=("3.9" "3.10" "3.11" "3.12")
REQUIREMENTS_FILE="${PROJECT_ROOT}/requirements.txt"

# ============================================================================
# FUNCTIONS
# ============================================================================

print_header() {
    echo ""
    echo "${BLUE}=================================${NC}"
    echo "${BLUE}$1${NC}"
    echo "${BLUE}=================================${NC}"
    echo ""
}

print_success() {
    echo "${GREEN}✓ $1${NC}"
}

print_error() {
    echo "${RED}✗ Error: $1${NC}"
}

print_warning() {
    echo "${YELLOW}⚠ Warning: $1${NC}"
}

print_info() {
    echo "${BLUE}ℹ $1${NC}"
}

detect_os() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            echo "windows"
            ;;
        Linux*)
            echo "linux"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

check_python_version() {
    local version=$1
    local py_cmd="python${version}"

    if command -v "$py_cmd" &> /dev/null; then
        local installed=$($py_cmd --version 2>&1 | awk '{print $2}')
        print_success "Python ${version} found: ${installed}"
        return 0
    else
        print_warning "Python ${version} not found (${py_cmd})"
        return 1
    fi
}

check_pip_available() {
    local py_cmd=$1

    if $py_cmd -m pip --version &> /dev/null; then
        print_success "pip available for $($py_cmd --version 2>&1 | awk '{print $2}')"
        return 0
    else
        print_error "pip not available for $($py_cmd --version 2>&1 | awk '{print $2}')"
        return 1
    fi
}

create_venv() {
    local python_version=$1
    local venv_path="${TEST_ENVS_DIR}/venv-${python_version}"
    local py_cmd="python${python_version}"

    if [ -d "$venv_path" ]; then
        print_warning "Virtual environment already exists at ${venv_path}"
        print_info "Skipping creation (remove directory to recreate)"
        return 0
    fi

    print_info "Creating virtual environment for Python ${python_version}..."

    if ! $py_cmd -m venv "$venv_path" 2>/dev/null; then
        print_error "Failed to create virtual environment at ${venv_path}"
        return 1
    fi

    print_success "Virtual environment created at ${venv_path}"
    return 0
}

install_requirements() {
    local python_version=$1
    local venv_path="${TEST_ENVS_DIR}/venv-${python_version}"
    local activate_script="${venv_path}/bin/activate"

    if [ ! -f "$activate_script" ]; then
        print_error "Activation script not found at ${activate_script}"
        return 1
    fi

    if [ ! -f "$REQUIREMENTS_FILE" ]; then
        print_error "requirements.txt not found at ${REQUIREMENTS_FILE}"
        return 1
    fi

    print_info "Installing requirements for Python ${python_version}..."

    # Use Python directly instead of sourcing activation script
    local pip_cmd="${venv_path}/bin/pip"

    if ! $pip_cmd install -q -r "$REQUIREMENTS_FILE" 2>/dev/null; then
        print_error "Failed to install requirements for Python ${python_version}"
        return 1
    fi

    print_success "Requirements installed for Python ${python_version}"
    return 0
}

run_tests_in_venv() {
    local python_version=$1
    local venv_path="${TEST_ENVS_DIR}/venv-${python_version}"
    local pytest_cmd="${venv_path}/bin/pytest"

    if [ ! -f "$pytest_cmd" ]; then
        print_warning "pytest not found in ${python_version} environment (install skipped?)"
        return 1
    fi

    print_info "Running tests in Python ${python_version} environment..."

    cd "$PROJECT_ROOT"
    if $pytest_cmd tests/test_environment_validation.py -v 2>/dev/null; then
        print_success "All tests passed in Python ${python_version} environment"
        return 0
    else
        print_error "Some tests failed in Python ${python_version} environment"
        return 1
    fi
}

print_activation_instructions() {
    echo ""
    print_header "ENVIRONMENT ACTIVATION INSTRUCTIONS"
    echo ""
    echo "To activate a specific Python version environment, run:"
    echo ""

    for version in "${PYTHON_VERSIONS[@]}"; do
        local venv_path="${TEST_ENVS_DIR}/venv-${version}"
        if [ -d "$venv_path" ]; then
            echo "  ${BLUE}Python ${version}:${NC}"
            echo "    source ${venv_path}/bin/activate"
            echo ""
        fi
    done

    echo "To deactivate an environment, run:"
    echo "    deactivate"
    echo ""
}

print_summary() {
    echo ""
    print_header "SETUP SUMMARY"
    echo ""
    echo "Test environments directory: ${TEST_ENVS_DIR}"
    echo ""
    echo "Available environments:"

    local env_count=0
    for version in "${PYTHON_VERSIONS[@]}"; do
        local venv_path="${TEST_ENVS_DIR}/venv-${version}"
        if [ -d "$venv_path" ]; then
            echo "  ${GREEN}✓${NC} Python ${version}: ${venv_path}"
            env_count=$((env_count + 1))
        else
            echo "  ${RED}✗${NC} Python ${version}: Not created"
        fi
    done

    echo ""
    if [ "$env_count" -gt 0 ]; then
        print_success "${env_count} environment(s) ready for testing"
    else
        print_error "No environments were created"
    fi

    echo ""
}

print_installation_guidance() {
    local os=$1
    echo ""
    print_header "PYTHON INSTALLATION GUIDANCE"
    echo ""
    echo "Missing Python versions detected. Here's how to install them:"
    echo ""

    case "$os" in
        macos)
            echo "${BLUE}macOS (via Homebrew):${NC}"
            echo "  brew install python@3.9 python@3.10 python@3.11 python@3.12"
            echo ""
            ;;
        windows)
            echo "${BLUE}Windows:${NC}"
            echo "  1. Visit: https://www.python.org/downloads/"
            echo "  2. Download installers for Python 3.9, 3.10, 3.11, 3.12"
            echo "  3. Run each installer, check 'Add Python to PATH'"
            echo "  4. Verify with: python --version"
            echo ""
            ;;
        linux)
            echo "${BLUE}Linux (Ubuntu/Debian):${NC}"
            echo "  sudo apt update"
            echo "  sudo apt install python3.9 python3.10 python3.11 python3.12"
            echo ""
            echo "${BLUE}Linux (Fedora/RHEL):${NC}"
            echo "  sudo dnf install python3.9 python3.10 python3.11 python3.12"
            echo ""
            ;;
        *)
            echo "Please visit: https://www.python.org/downloads/"
            echo ""
            ;;
    esac
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header "CISSP Analyzer - Multi-Python Test Environment Setup"

    # Detect OS
    local detected_os
    detected_os=$(detect_os)
    print_info "Detected OS: ${detected_os}"

    # Create test environments directory
    print_info "Setting up test environments directory..."
    mkdir -p "$TEST_ENVS_DIR"
    print_success "Test environments directory ready: ${TEST_ENVS_DIR}"

    # Check for available Python versions
    echo ""
    print_info "Checking for Python installations..."
    local available_versions=()
    local missing_versions=()

    for version in "${PYTHON_VERSIONS[@]}"; do
        if check_python_version "$version"; then
            available_versions+=("$version")
        else
            missing_versions+=("$version")
        fi
    done

    # Provide guidance if Python versions are missing
    if [ ${#missing_versions[@]} -gt 0 ]; then
        echo ""
        print_warning "Some Python versions not found: ${missing_versions[*]}"
        print_installation_guidance "$detected_os"
    fi

    # Create virtual environments and install dependencies
    echo ""
    local setup_count=0
    for version in "${available_versions[@]}"; do
        echo ""
        print_info "Processing Python ${version}..."

        # Check pip availability
        if ! check_pip_available "python${version}"; then
            print_error "Skipping Python ${version} due to missing pip"
            continue
        fi

        # Create venv
        if ! create_venv "$version"; then
            print_error "Skipping Python ${version} due to venv creation failure"
            continue
        fi

        # Install requirements
        if ! install_requirements "$version"; then
            print_error "Skipping Python ${version} due to requirements installation failure"
            continue
        fi

        setup_count=$((setup_count + 1))
    done

    # Print activation instructions
    print_activation_instructions

    # Print summary
    print_summary

    # Run tests (optional)
    echo ""
    read -p "Would you like to run tests in all environments? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        print_info "Running tests in all environments..."
        local test_count=0
        for version in "${available_versions[@]}"; do
            local venv_path="${TEST_ENVS_DIR}/venv-${version}"
            if [ -d "$venv_path" ]; then
                echo ""
                if run_tests_in_venv "$version"; then
                    test_count=$((test_count + 1))
                fi
            fi
        done
        echo ""
        print_success "Test run complete (${test_count}/${setup_count} environments tested)"
    fi

    echo ""
}

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

# Run main function
main "$@"

exit 0
