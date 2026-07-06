# Homework 1 — Banking Transactions API

> **Student Name**: Kuchuk Oleksandr  
> **AI Tools Used**: Cursor (Composer / Sonnet 4.5)

---

## Project Overview

A FastAPI REST service for managing banking transactions with:

- CRUD-style API for transactions
- Account balance calculation
- Account transaction summary
- Validation: amount precision, account format `ACC-XXXXX`, ISO 4217 currency codes
- Filtering by `accountId`, `type`, and date range

## Architecture

```
src/
├── main.py          # FastAPI routes & request handling
├── models.py        # Pydantic schemas, enums, validators
├── storage.py       # Thread-safe in-memory store
└── validators.py    # Structured validation error builder
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/transactions` | Create a new transaction |
| `GET` | `/transactions` | List transactions (filterable) |
| `GET` | `/transactions/{id}` | Get transaction by ID |
| `GET` | `/accounts/{accountId}/balance` | Get account balance |
| `GET` | `/accounts/{accountId}/summary` | Get account summary (Task 4A) |

## Transaction Model

```json
{
  "id": "UUID",
  "fromAccount": "ACC-XXXXX",
  "toAccount":   "ACC-XXXXX",
  "amount":      100.50,
  "currency":    "USD",
  "type":        "deposit | withdrawal | transfer",
  "timestamp":   "2024-01-15T10:30:00Z",
  "status":      "pending | completed | failed"
}
```

## Validation Rules

| Field | Rule |
|-------|------|
| `amount` | Positive number, max 2 decimal places |
| `fromAccount` / `toAccount` | Format `ACC-XXXXX` (5 uppercase alphanumeric chars) |
| `currency` | Valid ISO 4217 code (USD, EUR, GBP, …) |

**Validation error format:**
```json
{
  "error": "Validation failed",
  "details": [
    { "field": "amount", "message": "Amount must be a positive number" },
    { "field": "currency", "message": "Invalid currency code 'XYZ'. Use ISO 4217 codes." }
  ]
}
```

## Installation & Run

```powershell
cd homework-1
py -m pip install -r requirements.txt
py -m uvicorn src.main:app --reload --port 8000
```

Swagger UI: http://127.0.0.1:8000/docs

## Project Structure

```
homework-1/
├── src/
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   └── validators.py
├── demo/
│   ├── run.bat
│   ├── sample-requests.http
│   └── sample-data.json
├── docs/screenshots/
├── requirements.txt
├── README.md
└── HOWTORUN.md
```

## AI Model Usage

| Task | Model | Rationale |
|------|-------|-----------|
| API implementation | Cursor / Sonnet 4.5 | Structured code generation |
| Validation logic | Cursor / Sonnet 4.5 | Pydantic v2 field_validator patterns |
| Documentation | Cursor / Sonnet 4.5 | Clear examples for consumers |

---

*Completed as part of the AI-Assisted Development course.*
