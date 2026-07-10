# Specification — AI-Powered Multi-Agent Banking Pipeline

> Created by **Oleksandr Kuchuk** — Homework 6 (Final Capstone)

---

## 1. High-Level Objective

Build a file-driven, multi-agent banking pipeline that validates raw transactions, scores them for fraud risk, settles the safe ones (and holds the risky ones), and writes an auditable outcome for every transaction to `shared/results/`.

---

## 2. Mid-Level Objectives

1. **Validation** — Every transaction is checked for required fields, a strictly positive monetary amount, and an ISO 4217 currency code; invalid ones are rejected with a machine-readable reason.
2. **Fraud scoring** — Each validated transaction receives an integer risk score (0–100) and a risk level (`low` / `medium` / `high`) based on high value, unusual timing, cross-border movement, and channel.
3. **Settlement** — Low/medium-risk transactions are settled with a computed fee, net amount, and settlement date; high-risk transactions are placed on `hold` for manual review instead of being settled.
4. **Auditable results** — Every transaction (approved, held, or rejected) lands in `shared/results/` as a JSON file, and the run produces a `pipeline-summary.json` with counts and totals.
5. **Observability & safety** — All agent operations are logged with ISO 8601 timestamps, agent name, transaction ID, and outcome; account numbers and customer names are masked in logs (no plaintext PII).

---

## 3. Implementation Notes

- **Monetary values:** parse and compute all amounts with `decimal.Decimal` — never `float`. Use `ROUND_HALF_UP` and quantize to 2 decimal places for money.
- **Currency codes:** validate against an ISO 4217 allow-list (at minimum USD, EUR, GBP, JPY, CHF, CAD, AUD). `XYZ` must be rejected.
- **Amounts:** amount must be present, numeric, and strictly greater than `0`. Negative amounts (e.g. refunds encoded as `-100.00`) are rejected by the validator; refunds should be modeled as positive amounts with `transaction_type = "refund"` if supported later.
- **Logging / audit trail:** each agent appends a structured line — `timestamp | agent | transaction_id | outcome`. Account numbers → mask to last 4 chars (`ACC-****1001`); names are not logged.
- **PII:** `source_account`, `destination_account`, and any names are sensitive; never write them to logs in plaintext.
- **Message passing:** agents communicate only through JSON files moving `input → processing → output → results`. No shared in-memory state between agents.
- **Determinism:** given the same input, the pipeline must produce the same results (fixed rules, no wall-clock dependence in scoring except the transaction's own timestamp).

---

## 4. Context

### Beginning state
- `sample-transactions.json` — 8 raw transaction records (includes deliberate edge cases: `TXN005` $75k high value, `TXN006` invalid currency `XYZ`, `TXN007` negative amount, `TXN004` 02:47 off-hours cross-border).
- Empty (or absent) `shared/` directory tree.

### Ending state
- `shared/results/<TXN_ID>.json` — one result file per transaction with final status and full audit trail.
- `shared/results/pipeline-summary.json` — totals: processed, validated, rejected, settled, held, and summed settled amount per currency.
- Test coverage ≥ 90% (gate blocks push below 80%).

### Directory layout
```
shared/
├── input/       ← integrator drops initial messages here
├── processing/  ← agent moves message here while working
├── output/      ← agent writes result here for the next agent
└── results/     ← final outcomes + pipeline-summary.json
```

### Standard message format
```json
{
  "message_id": "uuid4-string",
  "timestamp": "2026-03-16T10:00:00Z",
  "source_agent": "transaction_validator",
  "target_agent": "fraud_detector",
  "message_type": "transaction",
  "data": {
    "transaction_id": "TXN001",
    "amount": "1500.00",
    "currency": "USD",
    "status": "validated"
  }
}
```

---

## 5. Low-Level Tasks

### Task: Transaction Validator
```
Prompt: "Create agents/transaction_validator.py. Implement validate(message: dict) -> dict
         that checks required fields (transaction_id, timestamp, source_account,
         destination_account, amount, currency, transaction_type), parses amount as
         decimal.Decimal (must be > 0), and validates currency against an ISO 4217
         allow-list. Return a message with data.status='validated' and target_agent
         ='fraud_detector', or data.status='rejected' with data.reason on failure.
         Support a --dry-run CLI mode that reads sample-transactions.json and prints a
         table of total/valid/invalid with rejection reasons."
File to CREATE: agents/transaction_validator.py
Function to CREATE: validate(message: dict) -> dict
Details: Rejects TXN006 (currency XYZ) and TXN007 (amount -100.00). Never uses float.
         Masks account numbers in logs.
```

### Task: Fraud Detector
```
Prompt: "Create agents/fraud_detector.py. Implement score(message: dict) -> dict that
         computes an integer risk_score (0-100) and risk_level from rules: high value
         (>10k adds points, >50k adds more), off-hours timestamp (00:00-05:59),
         cross-border (metadata.country != home country 'US'), and channel risk
         (api/online higher than branch). Attach data.risk_score and data.risk_level,
         set target_agent='settlement_processor'."
File to CREATE: agents/fraud_detector.py
Function to CREATE: score(message: dict) -> dict
Details: TXN005 ($75k) -> high; TXN002 ($25k) -> medium/high; TXN004 (02:47, DE) ->
         elevated. Only processes messages with status='validated'.
```

### Task: Settlement Processor
```
Prompt: "Create agents/settlement_processor.py. Implement settle(message: dict) -> dict.
         If risk_level == 'high', set status='held' with reason (no settlement). Otherwise
         compute fee (0.5% of amount, min 1.00, max 25.00, ROUND_HALF_UP), net_amount =
         amount - fee, and settlement_date = timestamp + T+1 (T+2 for wire_transfer or
         cross-border). Set status='settled'. Write final message to shared/results/."
File to CREATE: agents/settlement_processor.py
Function to CREATE: settle(message: dict) -> dict
Details: All money via Decimal quantized to 2dp. Produces the terminal result written to
         shared/results/<TXN_ID>.json.
```

### Task: Integrator / Orchestrator
```
Prompt: "Create integrator.py. Set up shared/ directories, load sample-transactions.json,
         wrap each record in the standard message format into shared/input/, then run
         validator -> fraud_detector -> settlement_processor, moving files through
         processing/ and output/. Rejected messages skip downstream agents and go straight
         to results/. Finally write shared/results/pipeline-summary.json and print a
         summary table."
File to CREATE: integrator.py
Function to CREATE: run_pipeline(input_path: str = "sample-transactions.json") -> dict
Details: Deterministic ordering by transaction_id. Returns summary dict for tests.
```

### Task: Custom MCP Server
```
Prompt: "Create mcp/server.py with FastMCP exposing get_transaction_status(transaction_id)
         and list_pipeline_results() tools plus a pipeline://summary resource, all reading
         from shared/results/."
File to CREATE: mcp/server.py
Function to CREATE: get_transaction_status(transaction_id: str) -> dict
Details: Reads terminal results written by the settlement processor. Read-only.
```
