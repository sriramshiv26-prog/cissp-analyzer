#!/bin/bash
# Quick start script for exam analysis

echo "=========================================="
echo "CISSP Exam Analysis System"
echo "=========================================="
echo ""
echo "Starting interactive analysis workflow..."
echo ""

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run analysis
python3 run_exam_analysis.py
