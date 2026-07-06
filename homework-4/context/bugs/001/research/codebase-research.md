# Codebase Research - Bug Set 001

## Scope
Analyzed files:
- `src/calculator.py`
- `src/main.py`
- `src/storage.py`

## Claim 1 - Per-person amount is truncated
- Reference: `src/calculator.py` (`calculate_split`)
- Evidence: `per_person = int(total / people)`
- Impact: Loses cents when split is not an integer.
- Repro:
  - `amount=100, tip_percent=10, people=3`
  - Expected around `36.67`, actual `36`.

## Claim 2 - Missing validation for `people > 0`
- Reference: `src/main.py` (`calculate`) and `src/calculator.py` (`total / people`)
- Evidence: No guard against `people=0` before division.
- Impact: `ZeroDivisionError`, API returns HTTP 500.
- Repro:
  - `POST /calculate` with `people=0`.

## Claim 3 - Hardcoded admin secret and insecure comparison
- Reference: `src/main.py` (`ADMIN_API_KEY`, `clear_history`)
- Evidence:
  - Hardcoded key in code.
  - Comparison uses `==` (`if api_key == ADMIN_API_KEY:`).
- Impact:
  - Secret leakage risk.
  - Timing side-channel risk.

## Claim 4 - Path traversal in receipt reader
- Reference: `src/storage.py` (`read_receipt`) and `src/main.py` (`get_receipt`)
- Evidence:
  - `os.path.join(RECEIPTS_DIR, name)` with user-controlled `name`.
  - No validation of `..` or absolute paths.
- Impact: Arbitrary file read outside receipts directory.
- Repro:
  - `GET /receipt?name=../../requirements.txt`

## Suggested fix direction
1. Replace truncation with two-decimal rounding.
2. Validate request input to ensure `people >= 1`.
3. Move admin secret to environment variable and use constant-time comparison.
4. Sanitize/normalize receipt path and enforce directory boundary.
