# Code Review Issues - Quick Reference

## Priority 0: FIX IMMEDIATELY

### Issue #1: Path Traversal Vulnerability
- **File**: `cissp_analyzer/history_loader.py`
- **Severity**: CRITICAL
- **Lines**: 16-18, 71-72
- **Problem**: Student names like `../../../etc` escape the base directory
- **Fix**: Add `path.resolve().relative_to(base.resolve())` validation
- **Test**: `path_traversal_protection()`
- **Time**: 2 hours

### Issue #2: Filename Case Sensitivity
- **File**: `cissp_analyzer/filename_parser.py`
- **Severity**: CRITICAL
- **Line**: 16
- **Problem**: Only matches `Mock1`, not `MOCK1` or `mock1`
- **Fix**: Add `re.IGNORECASE` flag or `(?i)` in regex
- **Test**: Files with different casing should all parse correctly
- **Time**: 1 hour

## Priority 1: FIX BEFORE PRODUCTION

### Issue #3: Sheet Index Documentation
- **File**: `cissp_analyzer/individual_report_gen.py`
- **Lines**: 339, 469, 530
- **Problem**: Comments say "Sheet 7" but actual index is 7
- **Fix**: Update docstrings with correct index numbers
- **Time**: 0.5 hours

### Issue #4: Trend Threshold Hardcoded
- **File**: `cissp_analyzer/trend_calculator.py`
- **Lines**: 73-98
- **Problem**: Uses `> 0.05` with no way to configure
- **Fix**: Make threshold configurable constant
- **Test**: Test with different thresholds
- **Time**: 1 hour

## Priority 2: FIX THIS MONTH

### Issue #5: Missing Index Validation
- **File**: `cissp_analyzer/pattern_detector.py`
- **Lines**: 16-93
- **Problem**: Wrong indices in `wrong_question_ids` are silently ignored
- **Fix**: Validate all indices before processing
- **Test**: Raise ValueError for out-of-bounds indices
- **Time**: 1.5 hours

### Issue #6: Use Logging Not Print
- **File**: `cissp_analyzer/history_loader.py`
- **Lines**: 77-81
- **Problem**: Uses `print()` instead of `logging`
- **Fix**: Replace with `logging.warning()`
- **Time**: 0.5 hours

## Priority 3: NICE TO HAVE

### Issue #7: Floating Point Precision
- **File**: `cissp_analyzer/trend_calculator.py`
- **Problem**: Floating point rounding issues
- **Fix**: Document precision expectations or round results
- **Time**: 0.5 hours

### Issue #8: Excel Error Handling
- **File**: `cissp_analyzer/excel_parser.py`
- **Problem**: Low coverage (54%), missing edge cases
- **Fix**: Add validation, better error messages
- **Time**: 1 hour

---

## Test Results Summary

```
67 tests PASSED ✓
3 tests SKIPPED (need test files)
0 tests FAILED ✓

Coverage:
- FilenameParser: 100%
- ProgressSheetGenerator: 100%
- TrendCalculator: 98%
- PatternDetector: 90%
- HistoryLoader: 90%
- AdaptivePlanGenerator: 80%
Overall: 84%
```

---

## Files to Review/Fix

1. **cissp_analyzer/history_loader.py** - Path validation needed
2. **cissp_analyzer/filename_parser.py** - Case sensitivity fix
3. **cissp_analyzer/individual_report_gen.py** - Documentation cleanup
4. **cissp_analyzer/trend_calculator.py** - Threshold configurability + precision
5. **cissp_analyzer/pattern_detector.py** - Input validation

---

## Testing Checklist

Before deployment:
- [ ] Run `pytest tests/ -v --cov` (expect 67 passed)
- [ ] Test path traversal: `HistoryLoader("../../../etc")`
- [ ] Test filename parsing: Both "MOCK1" and "mock1"
- [ ] Test trend boundaries: Exactly 0.05 improvement
- [ ] Test out-of-bounds indices in PatternDetector
- [ ] Verify all sheets appear in correct order in generated Excel

---

## Code Quality Checklist

- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] No hardcoded magic numbers (use constants)
- [ ] Use logging module, not print()
- [ ] Validate all user inputs
- [ ] Handle edge cases explicitly
- [ ] Error messages are descriptive

