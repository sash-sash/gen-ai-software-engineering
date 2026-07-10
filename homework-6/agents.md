# agents.md — Project Context for AI Agents

> Created by **Oleksandr Kuchuk** — Homework 6 (Final Capstone)

This file gives AI coding agents (and human contributors) the shared context needed to work on the multi-agent banking pipeline. Read it before generating or editing code.

---

## Project summary

A file-driven, multi-agent pipeline that processes raw banking transactions end-to-end:
**validate → score for fraud → settle or hold → record result.** Agents never share memory; they communicate exclusively through JSON files that move across `shared/` subdirectories.

## Tech stack & conventions

- **Language:** Python 3.11+
- **Money:** `decimal.Decimal` only. Never `float`. Quantize to 2 dp with `ROUND_HALF_UP`.
- **Currency:** ISO 4217 allow-list (USD, EUR, GBP, JPY, CHF, CAD, AUD).
- **Time:** ISO 8601 UTC strings (`2026-03-16T10:00:00Z`).
- **Tests:** `pytest` + `pytest-cov`; isolate filesystem via `tmp_path`. Target ≥ 90%, hard gate 80%.
- **MCP:** `fastmcp` for the custom pipeline-status server; `context7` for library lookups.
- **Style:** small pure functions, type hints, docstrings; no narration comments.

## Repository layout

```
homework-6/
├── sample-transactions.json   # input data (do not edit)
├── integrator.py              # orchestrator / entry point
├── agents/                    # one module per agent
│   ├── transaction_validator.py
│   ├── fraud_detector.py
│   └── settlement_processor.py
├── shared/{input,processing,output,results}/
├── mcp/server.py              # FastMCP server
├── mcp.json                   # context7 + pipeline-status
├── tests/
├── .cursor/commands/          # skills: write-spec, run-pipeline, validate-transactions
└── docs/screenshots/
```

## The agents

| Agent | Module | Entry function | Input status | Output |
|-------|--------|----------------|--------------|--------|
| Transaction Validator | `agents/transaction_validator.py` | `validate(message)` | raw | `validated` or `rejected` |
| Fraud Detector | `agents/fraud_detector.py` | `score(message)` | `validated` | adds `risk_score`, `risk_level` |
| Settlement Processor | `agents/settlement_processor.py` | `settle(message)` | scored | `settled` or `held` (terminal) |

## Message contract

Agents pass the standard message envelope (see `specification.md` §4). Rules:
- Preserve `message_id`; update `source_agent`, `target_agent`, `timestamp` on hand-off.
- Put agent output under `data`; never mutate original transaction fields — add new ones.
- A `rejected` message skips all downstream agents and goes straight to `shared/results/`.

## Pipeline flow

```
sample-transactions.json
        │  (integrator wraps each record)
        ▼
   shared/input/
        ▼
 Transaction Validator ──rejected──▶ shared/results/
        │ validated
        ▼
   Fraud Detector
        │ scored
        ▼
 Settlement Processor ──▶ shared/results/  +  pipeline-summary.json
```

## Business rules cheat-sheet

- **Reject** when: missing required field, amount ≤ 0 or non-numeric, currency not in ISO allow-list.
- **Fraud score** rises with: amount > $10k and > $50k, off-hours (00:00–05:59), cross-border (`metadata.country != "US"`), risky channel (`api`/`online`).
- **Settlement:** `high` risk → `held`. Else fee = 0.5% (min 1.00, max 25.00), `net = amount - fee`, settlement date T+1 (T+2 for `wire_transfer` or cross-border).

## Known edge cases in sample data

| TXN | Trigger | Expected |
|-----|---------|----------|
| TXN005 | $75,000 | high risk → held |
| TXN002 | $25,000 wire | elevated risk |
| TXN006 | currency `XYZ` | rejected (invalid currency) |
| TXN007 | amount `-100.00` | rejected (non-positive amount) |
| TXN004 | 02:47, country DE | off-hours + cross-border risk |

## Safety / PII

- Mask account numbers in logs to last 4 chars (`ACC-****1001`).
- Never log customer names or full account numbers.
- Audit line format: `timestamp | agent | transaction_id | outcome`.
