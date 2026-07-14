# Trap Analysis Engine - Quick Reference

## Import

```python
from cissp_analyzer.trap_analysis_engine import (
    TrapAnalysisEngine,
    AnswerAnalysisResult,
    TrapExplanation,
    TrapVulnerability,
)
```

## 3-Line Example

```python
engine = TrapAnalysisEngine()
results = engine.analyze_all_answers({1: "B", 2: "A"}, {1: "A", 2: "A"})
recommendations = engine.generate_recommendations(
    engine.summarize_vulnerabilities(results)
)
```

## Common Tasks

### Get Trap Info for a Question

```python
info = engine.get_question_trap_info(5)
print(info["trap_name"])      # "Wrong Technology"
print(info["prevention_strategy"])  # "Create threat-to-tool mapping chart"
```

### Find Student's Weakest Traps

```python
results = engine.analyze_all_answers(answers, answer_key)
vulnerabilities = engine.summarize_vulnerabilities(results)

top_5_traps = vulnerabilities[:5]
for vuln in top_5_traps:
    print(f"{vuln.trap_name}: {vuln.frequency_count} mistakes")
```

### Get Detailed Explanation for Wrong Answer

```python
result = engine.analyze_answer(42, "C", "A")

if not result.is_correct and result.trap_explanation:
    exp = result.trap_explanation
    print(f"Trap: {exp.trap_name}")
    print(f"Severity: {exp.severity}")
    print(f"Why: {exp.why_student_fell}")
    print(f"Fix: {exp.isc2_fix}")
    print(f"Confidence: {exp.confidence_score:.1%}")
```

### Generate Study Plan

```python
vulnerabilities = engine.summarize_vulnerabilities(results)
plan = engine.generate_recommendations(vulnerabilities)

print(plan["primary_recommendation"])
for item in plan["study_plan"][:3]:
    print(f"  {item}")
```

### Export Results

```python
# JSON format
json_report = engine.export_analysis_results(results, "json")

# CSV format (for spreadsheets)
csv_report = engine.export_analysis_results(results, "csv")

# Markdown (for docs)
md_report = engine.export_analysis_results(results, "markdown")
```

## The 21 Traps (Cheat Sheet)

| Trap | When | How to Avoid |
|------|------|------------|
| **NEG** | Question has LEAST/EXCEPT/NOT | Flip the stem, re-read |
| **ORDER** | Process sequence (BCP, IR) | Write out lifecycle before choosing |
| **ROLE** | Different job titles | Match role to authority level |
| **TOOL** | Security control selection | Know what each tool solves |
| **DEFINITION** | Auth vs Authz, Risk vs Threat | Use concept flashcards |
| **LIFECYCLE** | Process stage (Design/Deploy) | Memorize sequences |
| **COMPLIANCE** | GDPR/CCPA/HIPAA/PCI-DSS | Create regulatory matrix |
| **HIERARCHY** | CEO vs CISO vs Data Owner | Understand org structure |
| **ABS** | Always/Never/All/Completely | Eliminate absolute answers |
| **ALL** | Strategic vs Tactical | Pick broadest answer |
| **GOLD** | Shiny technical terms | Match domain to question |
| **SCOPE** | Cloud shared responsibility | Know IaaS/PaaS/SaaS boundaries |
| **VERSUS** | Two correct but one better | Check ISC2 best practices |
| **CONTEXT** | Internal/External/Cloud/On-prem | Highlight scenario clues |
| **ASSUMPTION** | Single-layer answer | Add defense-in-depth layer |
| **ETHIC** | Hacking back, vigilante | Follow ISC2 Canon |
| **EASY** | Too simple/obvious | Trust obvious answers |
| **TIME** | Spending 4+ min per question | 90-sec timer, eliminate & guess |
| **REPEAT** | Seen this topic before | Treat as new question |
| **METRIC** | RTO/RPO/SLA/MTBF | Create metrics reference card |
| **TIMING** | When vs What | Create timeline diagrams |

## Data Returned

### AnswerAnalysisResult

```python
result.question_num          # int: 1-161
result.student_answer        # str: "A", "B", "C", "D"
result.correct_answer        # str: "A", "B", "C", "D"
result.is_correct            # bool: True/False
result.trap_category         # str: "NEG", "TOOL", etc. (None if correct)
result.trap_explanation      # TrapExplanation object (if wrong)
result.domain                # int: 1-8
result.difficulty            # str: "Easy", "Medium", "Hard"
```

### TrapExplanation

```python
exp.question_num             # int
exp.trap_category            # str: "NEG", "TOOL", etc.
exp.trap_name                # str: "Negative Modifiers"
exp.severity                 # str: "Critical", "High", "Medium", "Low"
exp.why_student_fell         # str: Detailed explanation
exp.isc2_fix                 # str: Learning point
exp.prevention_tip           # str: How to avoid
exp.example                  # str: Example of correct answer
exp.affected_domain          # int: 1-8
exp.confidence_score         # float: 0.0-1.0
```

### TrapVulnerability

```python
vuln.trap_category           # str: "NEG", "TOOL", etc.
vuln.trap_name               # str: "Negative Modifiers"
vuln.frequency_count         # int: How many times
vuln.affected_questions      # list: [1, 5, 23, ...]
vuln.success_rate            # float: % correct
vuln.severity                # str: "Critical", "High", "Medium", "Low"
vuln.is_high_priority        # bool: True for priority traps
vuln.recommendation          # str: What to study
```

### Recommendations Dict

```python
recommendations["study_plan"]           # List[str]: Ordered items
recommendations["high_priority_traps"]  # List[Dict]: Top traps
recommendations["medium_priority_traps"]  # List[Dict]: Next tier
recommendations["total_vulnerabilities"]  # int: Count
recommendations["primary_recommendation"]  # str: Main focus
```

## Method Reference

```python
# Initialize
engine = TrapAnalysisEngine()
engine = TrapAnalysisEngine(
    trap_categories_path="path/to/trap_categories_reference.json",
    question_mapping_path="path/to/question_domain_mapping.json"
)

# Single answer
result = engine.analyze_answer(question_num, student_ans, correct_ans)

# Batch analysis
results = engine.analyze_all_answers(answers_dict, answer_key_dict)

# Summarization
vulnerabilities = engine.summarize_vulnerabilities(results)

# Recommendations
plan = engine.generate_recommendations(vulnerabilities)

# Lookup
trap_info = engine.get_trap_details("NEG")
question_info = engine.get_question_trap_info(5)

# Export
json_str = engine.export_analysis_results(results, "json")
csv_str = engine.export_analysis_results(results, "csv")
md_str = engine.export_analysis_results(results, "markdown")

# Check mappings
all_traps = engine.load_trap_mappings()
```

## Integration Checklist

- [ ] Import TrapAnalysisEngine in your module
- [ ] Initialize engine (typically in __init__ or setup)
- [ ] Call analyze_all_answers() with student answers and key
- [ ] Call summarize_vulnerabilities() on results
- [ ] Call generate_recommendations() for study plan
- [ ] Add trap data to student/class reports
- [ ] Display top 3-5 vulnerabilities to student
- [ ] Include prevention tips and ISC2 fixes in feedback

## Files

```
cissp_analyzer/
├── trap_analysis_engine.py          # Main module (this one)
├── models.py                        # Data structures
└── (other modules)

docs/
├── trap_categories_reference.json   # Trap definitions (21 categories)
├── TRAP_ANALYSIS_INTEGRATION_GUIDE.md
└── TRAP_ANALYSIS_QUICK_REFERENCE.md (this file)

data/
└── question_domain_mapping.json     # Question -> trap mapping
```

## Common Patterns

### Find all questions with specific trap

```python
q_nums = engine.question_mappings.values()
trap_q_nums = [q for q in q_nums if q.get("exam_trick") == "NEG"]
```

### Filter high-confidence trap identifications

```python
high_conf = [
    r for r in results 
    if r.trap_explanation and r.trap_explanation.confidence_score > 0.8
]
```

### Get vulnerability distribution across domains

```python
by_domain = defaultdict(list)
for vuln in vulnerabilities:
    domain = engine.get_trap_details(vuln.trap_category)
    for domain_id in domain.get("affected_domains", []):
        by_domain[domain_id].append(vuln)
```

### Create custom study schedule

```python
plan = engine.generate_recommendations(vulnerabilities)
daily_items = [plan["study_plan"][i] for i in range(0, len(plan["study_plan"]), 2)]
```

## Troubleshooting

### Module not found
```python
# Make sure you're in the project root or cissp-analyzer is in PYTHONPATH
import sys
sys.path.insert(0, "/Users/sriram/cissp-analyzer")
from cissp_analyzer.trap_analysis_engine import TrapAnalysisEngine
```

### JSONDecodeError on load
```python
# Verify JSON files exist and are valid
import json
with open("docs/trap_categories_reference.json") as f:
    json.load(f)  # Will raise JSONDecodeError if invalid
```

### Empty vulnerabilities list
```python
# This is OK - means student didn't fall for any identified traps
# All answers were either correct, or errors weren't mapped to categories
if not vulnerabilities:
    print("Excellent! No major trap vulnerabilities.")
else:
    print(f"Found {len(vulnerabilities)} trap patterns")
```

## Performance Notes

- `analyze_answer()` - O(1), <1ms per answer
- `analyze_all_answers()` - O(n), ~1ms per answer, ~160ms for full exam
- `summarize_vulnerabilities()` - O(n), linear in results
- `generate_recommendations()` - O(m log m) where m = vulnerabilities

For 160 questions: ~200ms total analysis time.

## Version

- Module: `trap_analysis_engine.py` v1.0.0
- Trap Categories: 21 total, all 161 CISSP questions mapped
- Last Updated: 2026-07-14
