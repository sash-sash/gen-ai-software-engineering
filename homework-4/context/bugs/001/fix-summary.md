# Fix Summary - Bug Set 001

Generated at: 2026-06-29

## Changes Made

### 1) Split rounding bug — `src/calculator.py`

| | |
|---|---|
| **Location** | `calculate_split`, line assigning `per_person` |
| **Before** | `per_person = int(total / people)` — truncated cents (e.g. 110/3 → 36) |
| **After** | `per_person = round(total / people, 2)` — preserves two decimal places (e.g. 110/3 → 36.67) |
| **Test result** | `py -m pytest -q` → 2 passed (existing happy-path tests still pass) |

### 2) Divide-by-zero validation — `src/main.py`

| | |
|---|---|
| **Location** | `SplitRequest` model |
| **Before** | `people: int` — no lower bound; `people=0` caused `ZeroDivisionError` → HTTP 500 |
| **After** | `people: int = Field(gt=0)` — Pydantic returns HTTP 422 for zero/negative values |
| **Test result** | `py -m pytest -q` → 2 passed (no API-level validation tests in suite yet) |

### 3) Hardcoded secret + insecure compare — `src/main.py`

| | |
|---|---|
| **Location** | Module-level `ADMIN_API_KEY` and `clear_history` endpoint |
| **Before** | `ADMIN_API_KEY = "supersecret-admin-key-123"` hardcoded; compared with `==` |
| **After** | `ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")`; comparison via `hmac.compare_digest`; returns 403 when key is unset or wrong |
| **Test result** | `py -m pytest -q` → 2 passed (no admin-auth API tests in suite yet) |

### 4) Receipt path traversal — `src/storage.py` and `src/main.py`

| | |
|---|---|
| **Location** | `storage.read_receipt` and `get_receipt` route |
| **Before** | `os.path.join(RECEIPTS_DIR, name)` with no validation; `../` sequences could escape the receipts directory |
| **After** | Reject empty names, `..`, and path separators; resolve with `os.path.realpath` and verify resolved path stays under `RECEIPTS_DIR` via `os.path.commonpath`. `get_receipt` maps `ValueError` to HTTP 400 |
| **Test result** | `py -m pytest -q` → 2 passed (no storage/API traversal tests in suite yet) |

## Overall Status

**PASS** — All four planned fixes applied to `src/`. Test command `py -m pytest -q` completed with exit code 0 (2 passed).

Note: Extended regression tests described in `context/bugs/001/test-report.md` (rounding, validation, auth, traversal) are not yet present under `tests/`; only baseline calculator tests exist. Source fixes align with the implementation plan and verified research.

## Manual Verification

1. **Rounding**: `POST /calculate` with `{"amount":100,"tip_percent":10,"people":3}` → `per_person` should be `36.67`.
2. **Zero people**: `POST /calculate` with `"people":0` → HTTP 422 validation error (not 500).
3. **Admin key**: Set `ADMIN_API_KEY` env var, then `DELETE /history?api_key=<key>` → `{"status":"cleared"}`; wrong or missing key → HTTP 403.
4. **Path traversal**: `GET /receipt?name=../../requirements.txt` → HTTP 400; `GET /receipt?name=1.txt` (after a calculation) → receipt content.

## References

- `context/bugs/001/implementation-plan.md`
- `context/bugs/001/research/verified-research.md`
- `context/bugs/001/bug-context.md`
- `agents/bug-fixer.agent.md`
