# Homework 6 — AI-Powered Multi-Agent Banking Pipeline

Created by **Oleksandr Kuchuk**

This project implements a file-driven, multi-agent transaction processing pipeline.  
It reads raw transactions from `sample-transactions.json`, validates them, scores fraud risk,
and then settles or holds each transaction. Every transaction gets a terminal JSON result in
`shared/results/`, and the pipeline also writes a run summary.

The design is deterministic and auditable: agents communicate only through JSON messages, and an
audit log captures per-agent outcomes with timestamps. Monetary operations use `Decimal` to avoid
float precision errors.

## Agent Responsibilities

- **Integrator** (`integrator.py`) — initializes directories, wraps input records as messages, runs agent chain, writes summary.
- **Transaction Validator** (`agents/transaction_validator.py`) — checks required fields, amount positivity, and ISO 4217 currency.
- **Fraud Detector** (`agents/fraud_detector.py`) — computes `risk_score` and `risk_level` from amount, timing, geography, and channel.
- **Settlement Processor** (`agents/settlement_processor.py`) — settles low/medium risk transactions or puts high-risk ones on hold.
- **Pipeline Status MCP** (`mcp/server.py`) — exposes tools/resources to query transaction statuses and pipeline summary.

## Architecture (ASCII)

```text
sample-transactions.json
        |
        v
  +--------------+      validated      +---------------+      scored       +---------------------+
  |  Validator   |-------------------->| FraudDetector |------------------>| SettlementProcessor |
  +--------------+                     +---------------+                   +---------------------+
        | rejected                                                              | settled / held
        +-----------------------------------------------------------------------+
                                        writes JSON results + pipeline-summary
                                                    |
                                                    v
                                           shared/results/
```

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11+ |
| Money arithmetic | `decimal.Decimal` |
| Testing | `pytest`, `pytest-cov` |
| MCP server | `fastmcp` |
| Message transport | JSON files (`shared/`) |
| Coverage gate | Cursor hook (`.cursor/hooks.json`) on `git push` |

## Key Commands

- Run pipeline: `cd homework-6 && py integrator.py`
- Dry-run validation only: `cd homework-6 && py agents/transaction_validator.py --dry-run --input sample-transactions.json`
- Run tests with coverage: `cd homework-6 && py -m pytest --cov=. --cov-report=term-missing`

See `HOWTORUN.md` for the full step-by-step workflow.
