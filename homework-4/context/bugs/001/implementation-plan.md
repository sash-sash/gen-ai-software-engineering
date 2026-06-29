# Implementation Plan - Bug Set 001

## Goal
Fix functional and security issues documented in:
- `context/bugs/001/bug-context.md`
- `context/bugs/001/research/codebase-research.md`

## Planned changes

### 1) Fix split rounding bug
- File: `src/calculator.py`
- Change:
  - Before: `per_person = int(total / people)`
  - After: `per_person = round(total / people, 2)`
- Reason: preserve cents and avoid money loss in uneven splits.

### 2) Validate `people` to prevent divide-by-zero
- File: `src/main.py`
- Change:
  - Add Pydantic constraint for `people` (`gt=0`) in `SplitRequest`.
- Reason: return validation error instead of runtime 500.

### 3) Remove hardcoded secret and use secure compare
- File: `src/main.py`
- Change:
  - Replace hardcoded `ADMIN_API_KEY` with env-based config.
  - Use `hmac.compare_digest` for API key comparison.
- Reason: eliminate credential leak and timing-attack prone comparison.

### 4) Prevent path traversal in receipt endpoint
- File: `src/storage.py` and `src/main.py`
- Change:
  - Validate requested receipt name (reject path separators and parent traversal).
  - Ensure normalized path remains under `RECEIPTS_DIR`.
- Reason: prevent arbitrary file read.

### 5) Add/extend tests for changed code
- File: `tests/test_calculator.py` and new API-level tests if needed.
- Coverage targets:
  - Rounding behavior for uneven split.
  - Validation error for `people=0`.
  - Receipt traversal blocked.
  - Clear-history auth check.

## Test command
```powershell
py -m pytest -q
```

## Expected outcome
- Functional bug cases fixed.
- Security vulnerabilities mitigated.
- Tests pass.
