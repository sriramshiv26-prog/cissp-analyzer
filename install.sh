#!/bin/bash

# CISSP Analyzer Installation Script
# This script automatically checks and installs all required dependencies

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    CISSP ANALYZER - INSTALLATION AND SETUP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
python3_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: ${python3_version}"

# Check if Python 3.9+
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" || {
    echo -e "${RED}✗ Python 3.9 or higher is required${NC}"
    exit 1
}
echo -e "${GREEN}✓ Python version OK${NC}"

# Check pip
echo -e "\n${YELLOW}Checking pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 not found. Please install pip.${NC}"
    exit 1
fi
pip_version=$(pip3 --version)
echo "pip version: ${pip_version}"
echo -e "${GREEN}✓ pip found${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip to latest version...${NC}"
pip3 install --upgrade pip setuptools wheel

# Create virtual environment (optional)
read -p "Do you want to create a virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    venv_name="venv"
    if [ ! -d "$venv_name" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv "$venv_name"
        source "$venv_name/bin/activate"
        echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
    else
        echo -e "${YELLOW}Virtual environment already exists, activating...${NC}"
        source "$venv_name/bin/activate"
    fi
else
    echo -e "${YELLOW}Proceeding without virtual environment${NC}"
fi

# Install dependencies
echo -e "\n${YELLOW}Installing CISSP Analyzer dependencies...${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed from requirements.txt${NC}"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Install package in development mode
echo -e "\n${YELLOW}Installing CISSP Analyzer package...${NC}"
read -p "Install with development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip3 install -e ".[dev]"
    echo -e "${GREEN}✓ Installed with development dependencies${NC}"
else
    pip3 install -e .
    echo -e "${GREEN}✓ Installed CISSP Analyzer${NC}"
fi

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 -c "
import sys
try:
    from cissp_analyzer.dependency_checker import print_dependency_status
    print_dependency_status()
except Exception as e:
    print(f'Error checking dependencies: {e}', file=sys.stderr)
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Installation verification successful${NC}"
else
    echo -e "${RED}✗ Installation verification failed${NC}"
    exit 1
fi

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ INSTALLATION COMPLETE!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "  1. Verify your exam PDF and student Excel files"
echo "  2. Run: python3 setup.py"
echo "  3. Follow the interactive setup wizard"
echo ""
echo -e "${YELLOW}For more information:${NC}"
echo "  Documentation: README.md"
echo "  Examples: examples/"
echo "  Test data: data/"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
