# HOWTORUN — Homework 6

## 1) Install dependencies

```powershell
cd homework-6
py -m pip install -r requirements.txt
```

## 2) Run the full pipeline

```powershell
py integrator.py
```

Expected output includes a final summary line:

- `processed=8`
- `rejected=2` (TXN006, TXN007)
- at least one `held` transaction (for high risk)

Results appear in:

- `shared/results/TXN001.json` ... `shared/results/TXN008.json`
- `shared/results/pipeline-summary.json`
- `shared/results/audit.log`

## 3) Validate only (dry-run)

```powershell
py agents/transaction_validator.py --dry-run --input sample-transactions.json
```

## 4) Run test suite with coverage

```powershell
py -m pytest --cov=. --cov-report=term-missing
```

Coverage gate target:
- hard block under **80%** (hook)
- project target **90%+**

## 5) Start custom MCP server locally

Open a new terminal and run:

```powershell
cd homework-6
py mcp/server.py
```

This starts MCP stdio server `pipeline-status` (used via `mcp.json`).

## 6) Send a local "request" to MCP tools (quick smoke test)

```powershell
cd homework-6
py mcp/smoke_test.py --transaction-id TXN005
```

This command prints:
- `get_transaction_status` result
- `list_pipeline_results` counters
- `pipeline://summary` text

## 7) Verify MCP tools in Cursor

1. Ensure `homework-6/mcp.json` is loaded by Cursor.
2. Run pipeline once (`py integrator.py`).
3. In chat, call:
   - `get_transaction_status` with `transaction_id: "TXN005"`
   - `list_pipeline_results`
4. Read resource: `pipeline://summary`

## 8) Coverage gate hook behavior

Hook file:
- `.cursor/hooks.json`
- `.cursor/hooks/check-homework6-coverage.py`

Behavior:
- On `git push`, hook runs `pytest --cov-fail-under=80` in `homework-6`.
- Push is denied if tests fail or coverage is below 80%.
