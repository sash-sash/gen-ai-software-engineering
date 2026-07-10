---
description: Generate a full project specification for the multi-agent banking pipeline using the required template.
---

# /write-spec

Produce (or regenerate) `specification.md` for the AI-powered multi-agent banking pipeline.
Follow the template below exactly. Read `sample-transactions.json` and `agents.md` first so
the spec reflects the real input data and project conventions.

## Steps

1. Read `homework-6/sample-transactions.json` to understand the input records and edge cases.
2. Read `homework-6/agents.md` for stack, conventions, and business rules.
3. Write `homework-6/specification.md` with ALL five sections below.
4. Ensure every agent has a Low-Level Task entry in the required format.
5. Keep the "Created by Oleksandr Kuchuk" attribution line at the top.

## Required structure for `specification.md`

**1. High-Level Objective** — one sentence describing what the pipeline does.

**2. Mid-Level Objectives** — 4–5 concrete, testable requirements.

**3. Implementation Notes** — must cover:
- Monetary values via `decimal.Decimal` (never `float`), `ROUND_HALF_UP`, 2 dp.
- Currency codes validated against an ISO 4217 allow-list.
- Logging/audit trail: `timestamp | agent | transaction_id | outcome`.
- PII handling: mask account numbers, never log names.

**4. Context** — beginning state (`sample-transactions.json`), ending state
(`shared/results/`, `pipeline-summary.json`, coverage ≥ 90%), the `shared/` directory
layout, and the standard JSON message format.

**5. Low-Level Tasks** — one entry per agent, each in this exact format:

```
Task: [Agent Name]
Prompt: "[Exact prompt to give the code-generation agent]"
File to CREATE: e.g. agents/[agent_name].py
Function to CREATE: e.g. process_message(message: dict) -> dict
Details: [What the agent checks, transforms, or decides]
```

Cover these agents: Transaction Validator, Fraud Detector, Settlement Processor,
Integrator/Orchestrator, and the custom MCP Server.

## Output

Only the file `homework-6/specification.md`. Do not run the pipeline or create code files.
