# Verified Research - Bug Set 001

## Verification Summary
- Result: **PASS**
- Research Quality: **Q3 - Good**

## Verified Claims
- Claim 1 is verified. `src/calculator.py` defines `calculate_split`, computes `tip` and `total`, then sets `per_person = int(total / people)`. For `amount=100`, `tip_percent=10`, and `people=3`, the total is `110`, `110 / 3` is approximately `36.67`, and `int(...)` truncates the value to `36`.
- Claim 2 is verified. `src/main.py` accepts `people` through `SplitRequest` without a lower-bound constraint, and `calculate` passes `req.people` directly to `calculator.calculate_split`. `src/calculator.py` divides by `people`, so `people=0` can raise `ZeroDivisionError`; the route does not handle that exception.
- Claim 3 is verified. `src/main.py` declares `ADMIN_API_KEY = "supersecret-admin-key-123"` in source code, and `clear_history` authorizes the request with `if api_key == ADMIN_API_KEY:`.
- Claim 4 is verified. `src/storage.py` implements `read_receipt` by joining `RECEIPTS_DIR` with user-controlled `name` and opening the resulting path. There is no rejection of `..`, no absolute-path handling, no normalization check, and no enforcement that the resolved path remains inside the receipts directory. `src/main.py` passes the query parameter `name` directly to `storage.read_receipt`.
- The suggested fix directions are consistent with observed code behavior: preserve cents when splitting, validate `people >= 1`, externalize the admin secret and compare it safely, and constrain receipt reads to the receipts directory.

## Discrepancies Found
- No factual discrepancies were found in the bug claims or referenced files.
- The research gives file/function references instead of precise `file:line` references. The referenced files and functions are real and relevant, but the lack of line-specific citations prevents a Q4 score.
- Claim 2's reproduction identifies the failing route and input value, but does not provide a complete JSON request body.
- Claim 3 describes a valid security issue, but does not include a concrete reproduction step.

## Research Quality Assessment
- Level: **Q3 - Good**
- Reasoning: The referenced source files exist, the cited functions exist, the quoted snippets match the current source semantically, and the root causes are supported by direct code evidence. The reproduction examples are mostly clear and the fix directions align with the implementation. The research is not Q4 because references are not line-specific and some reproduction details are incomplete.

## References
- `context/bugs/001/research/codebase-research.md`
- `skills/research-quality-measurement.md`
- `agents/research-verifier.agent.md`
- `src/calculator.py`: `calculate_split`, especially `per_person = int(total / people)`
- `src/main.py`: `SplitRequest`, `calculate`, `ADMIN_API_KEY`, `clear_history`, `get_receipt`
- `src/storage.py`: `read_receipt`

