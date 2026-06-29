# Security Report - Bug Set 001

Generated at: 2026-06-29

## Scope

- Reviewed `context/bugs/001/fix-summary.md`.
- Reviewed current source files: `src/main.py`, `src/storage.py`, and `src/calculator.py`.
- Review areas: injection, hardcoded secrets, insecure comparisons, missing validation/error handling, unsafe dependencies, path traversal, and XSS/CSRF where relevant.

## Risk Summary

The original hardcoded admin secret, insecure string comparison, divide-by-zero validation issue, and direct path traversal issue are addressed in the current code. Residual risk is concentrated around API boundary hardening: the admin API key is still accepted in the query string, and calculation inputs still permit invalid financial values. No evidence of code execution injection, hardcoded secrets, insecure secret comparison, exploitable path traversal, XSS sinks, CSRF-prone cookie authentication, or unsafe dependency usage was found in the reviewed source.

- CRITICAL: 0
- HIGH: 0
- MEDIUM: 1
- LOW: 1
- INFO: 1

## Findings

### Finding 1

- Severity: MEDIUM
- File:line: `src/main.py:51`
- Impact: `clear_history` accepts the administrative API key as a query parameter. Query-string secrets are commonly captured in server access logs, reverse proxy logs, browser history, monitoring tools, and referrer metadata, increasing the chance that the admin credential is exposed.
- Remediation: Move the admin credential to an HTTP header such as `Authorization: Bearer <token>` or `X-Admin-API-Key`, avoid logging the header value, and keep the existing `hmac.compare_digest` comparison.

### Finding 2

- Severity: LOW
- File:line: `src/main.py:21`
- Impact: `SplitRequest` constrains `people` but does not constrain `amount` or `tip_percent`. Negative amounts or negative tips can be submitted and persisted, which can corrupt calculation history and receipts with invalid financial values.
- Remediation: Add Pydantic constraints such as `amount: float = Field(gt=0)` and an explicit non-negative or bounded range for `tip_percent`, depending on accepted business rules.

### Finding 3

- Severity: INFO
- File:line: `requirements.txt:1`
- Impact: Dependencies are pinned to explicit versions, and no unsafe dependency usage was observed in the reviewed source. This lowers supply-chain drift risk, but pinned versions still require routine vulnerability checks.
- Remediation: Run dependency scanning in CI, for example with `pip-audit` or an equivalent scanner, and update pinned packages when vulnerabilities are reported.
