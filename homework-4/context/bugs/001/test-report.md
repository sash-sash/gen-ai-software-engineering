# Test Report - Bug Set 001

Generated at: 2026-06-29

## Test Files Added/Updated

| File | Action |
|---|---|
| `tests/test_calculator.py` | Updated — added rounding regression test |
| `tests/test_storage.py` | Added — receipt path validation unit tests |
| `tests/test_api.py` | Added — API validation, admin auth, and receipt endpoint tests |

## Mapping: Changed Code → Tests

| Changed code | Test(s) |
|---|---|
| `src/calculator.py` — `round(total / people, 2)` | `test_calculator.py::test_uneven_split_rounds_per_person_to_two_decimals` |
| `src/main.py` — `SplitRequest.people: Field(gt=0)` | `test_api.py::test_calculate_rejects_zero_people`, `test_api.py::test_calculate_rejects_negative_people` |
| `src/main.py` — `ADMIN_API_KEY` env + `hmac.compare_digest` in `clear_history` | `test_api.py::test_clear_history_forbidden_when_admin_key_not_configured`, `test_api.py::test_clear_history_forbidden_with_wrong_key`, `test_api.py::test_clear_history_succeeds_with_correct_key` |
| `src/storage.py` — `read_receipt` path sanitization | `test_storage.py::test_read_receipt_rejects_path_traversal`, `test_storage.py::test_read_receipt_rejects_empty_name`, `test_storage.py::test_read_receipt_rejects_dot_dot`, `test_storage.py::test_read_receipt_rejects_path_separators`, `test_storage.py::test_read_receipt_reads_valid_receipt_file` |
| `src/main.py` — `get_receipt` catches `ValueError` → HTTP 400 | `test_api.py::test_get_receipt_rejects_path_traversal` |

## FIRST Compliance Notes

### Calculator tests (`test_calculator.py`)
- **Fast** — pure function calls, no I/O.
- **Independent** — no shared state between tests.
- **Repeatable** — deterministic numeric inputs and assertions.
- **Self-validating** — explicit assertions on `total` and `per_person`.
- **Timely** — directly targets the rounding regression from bug 001.

### Storage tests (`test_storage.py`)
- **Fast** — local in-memory/disk receipt files only; no network.
- **Independent** — `autouse` fixture clears history before and after each test.
- **Repeatable** — fixed inputs; valid-file test uses `storage.add` for predictable receipt names.
- **Self-validating** — `pytest.raises` for rejection cases; content assertions for happy path.
- **Timely** — covers all new validation branches in `read_receipt`.

### API tests (`test_api.py`)
- **Fast** — `TestClient` in-process; no external HTTP server.
- **Independent** — fixture clears storage per test; admin key patched via `monkeypatch`.
- **Repeatable** — fixed JSON payloads and query params.
- **Self-validating** — status codes and JSON body assertions.
- **Timely** — covers Pydantic validation, secure admin key check, and receipt traversal HTTP mapping.

## Test Command and Results

```text
$ py -m pytest -q
..............                                                           [100%]
14 passed, 33 warnings in 0.31s
```

- **Command:** `py -m pytest -q`
- **Exit code:** 0
- **Result:** 14 passed

(Warnings are third-party deprecation notices from Starlette/FastAPI on Python 3.14; they do not affect pass/fail.)

## Remaining Gaps

- No unit test verifies that `hmac.compare_digest` is used specifically (implementation detail; behavior is covered by wrong-key vs correct-key tests).
- No test for `GET /receipt` returning 404 for a valid name that does not exist (unchanged behavior, out of bug-fix scope).
- No test for `ADMIN_API_KEY` being read from the environment at import time (tests patch the module attribute instead).
- Rounding fix is not exercised end-to-end via `POST /calculate` (covered at calculator unit level only).
