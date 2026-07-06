# Bug Context — Bill Splitter API (set 001)

This document records the **intentional** bugs and security issues seeded into
the sample application (`src/`) so the 4-agent pipeline has concrete defects to
research, verify, fix, security-review, and test.

- **Application**: Bill Splitter REST API (FastAPI)
- **Entry point**: `src/main.py`
- **Core logic**: `src/calculator.py`, `src/storage.py`
- **Run**: `py -m uvicorn src.main:app --reload` → http://127.0.0.1:8000/docs
- **Test**: `py -m pytest`

---

## Seeded defects

| ID | Type | Severity | File | Symbol |
|----|------|----------|------|--------|
| BUG-1 | Logic (rounding) | Medium | `src/calculator.py` | `calculate_split` |
| BUG-2 | Crash / unhandled error | High | `src/main.py`, `src/calculator.py` | `calculate` / `calculate_split` |
| VULN-1 | Hardcoded secret + insecure comparison | High | `src/main.py` | `ADMIN_API_KEY`, `clear_history` |
| VULN-2 | Path traversal | Critical | `src/main.py`, `src/storage.py` | `get_receipt` / `read_receipt` |

---

### BUG-1 — Per-person amount truncated with `int()`

**Location**: `src/calculator.py`, in `calculate_split`:

```python
per_person = int(total / people)
```

**Problem**: `int()` truncates toward zero instead of rounding to 2 decimal
places. Whenever the total does not divide evenly, cents are silently lost and
the per-person figures do not add up to the total.

**Base case (works)**:
- `amount=100, tip_percent=0, people=4` → `per_person = 25.0` ✅

**Trigger case (wrong)**:
- `amount=100, tip_percent=10, people=3` → `total=110`, expected
  `per_person ≈ 36.67`, but returns `36` (≈ $2.01 unaccounted for).

**Expected fix**: `per_person = round(total / people, 2)`.

**Reproduce**:
```bash
curl -s -X POST http://127.0.0.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d "{\"amount\":100,\"tip_percent\":10,\"people\":3}"
```

---

### BUG-2 — `people = 0` raises `ZeroDivisionError` → HTTP 500

**Location**: `src/calculator.py` (`total / people`) reached from
`src/main.py` `calculate` with no validation.

**Problem**: When `people` is `0`, the division raises `ZeroDivisionError`,
which surfaces as an unhandled HTTP 500 instead of a clean `400 Bad Request`.

**Base case (works)**:
- `people >= 1` → normal response.

**Trigger case (crash)**:
- `people=0` → HTTP 500.

**Expected fix**: validate `people >= 1` (e.g. Pydantic `Field(gt=0)` or an
explicit check) and return HTTP 400 with a clear message.

**Reproduce**:
```bash
curl -s -X POST http://127.0.0.1:8000/calculate \
  -H "Content-Type: application/json" \
  -d "{\"amount\":100,\"tip_percent\":10,\"people\":0}"
```

---

### VULN-1 — Hardcoded admin secret + insecure `==` comparison

**Location**: `src/main.py`:

```python
ADMIN_API_KEY = "supersecret-admin-key-123"
...
if api_key == ADMIN_API_KEY:
```

**Problem**: Two issues. (1) The admin key is hardcoded in source and committed
to the repository. (2) The comparison uses `==`, which is not constant-time and
is vulnerable to timing attacks.

**Trigger case**:
- The secret is readable by anyone with repo access; `DELETE /history` is then
  trivially callable.

**Expected fix**: load the key from an environment variable / secret store and
compare with `hmac.compare_digest`.

**Reproduce**:
```bash
curl -s -X DELETE "http://127.0.0.1:8000/history?api_key=supersecret-admin-key-123"
```

---

### VULN-2 — Path traversal in `GET /receipt`

**Location**: `src/storage.py` `read_receipt` (called from `src/main.py`
`get_receipt`):

```python
path = os.path.join(RECEIPTS_DIR, name)
with open(path, "r", encoding="utf-8") as f:
    return f.read()
```

**Problem**: The `name` query parameter is not sanitized, so `../` sequences
let a caller escape the receipts directory and read arbitrary files on disk.

**Base case (works)**:
- `name=1.txt` → returns receipt #1.

**Trigger case (exploit)**:
- `name=../../requirements.txt` (or deeper) → returns files outside the
  receipts folder.

**Expected fix**: reject names containing path separators / `..`, or resolve
the path and verify it stays within `RECEIPTS_DIR`.

**Reproduce**:
```bash
# create a receipt first
curl -s -X POST http://127.0.0.1:8000/calculate -H "Content-Type: application/json" -d "{\"amount\":50,\"tip_percent\":0,\"people\":2}"
# then traverse out of the receipts directory
curl -s "http://127.0.0.1:8000/receipt?name=../../requirements.txt"
```
