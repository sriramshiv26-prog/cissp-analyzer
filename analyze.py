#!/usr/bin/env python3
"""
Simple entry point for CISSP Analyzer - Interactive step-by-step setup.

Usage: python3 analyze.py

This script walks you through:
1. Which exam are you analyzing? (Mock 1, Mock 2, etc.)
2. Where is the exam PDF?
3. Do you have an answer key?
4. Add students and their answer files
5. Where to save reports
6. Runs the analysis automatically
"""

from cissp_analyzer.interactive_cli import main

if __name__ == '__main__':
    main()
