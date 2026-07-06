# How to Run — Banking Transactions API

## Prerequisites

- Python 3.11+
- PowerShell (Windows) or bash (Linux/macOS)

## Step 1 — Install dependencies

```powershell
cd homework-1
py -m pip install -r requirements.txt
```

## Step 2 — Start the server

```powershell
py -m uvicorn src.main:app --reload --port 8000
```

The API is now running at **http://localhost:8000**.

## Step 3 — Explore

| URL | Description |
|-----|-------------|
| http://localhost:8000/docs | Interactive Swagger UI |
| http://localhost:8000/redoc | ReDoc API reference |

## Quick test (PowerShell)

```powershell
# Create a deposit
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/transactions" `
  -ContentType "application/json" `
  -Body '{"fromAccount":"ACC-00000","toAccount":"ACC-12345","amount":1000.00,"currency":"USD","type":"deposit"}'

# List all transactions
Invoke-RestMethod -Uri "http://localhost:8000/transactions"

# Get balance for ACC-12345
Invoke-RestMethod -Uri "http://localhost:8000/accounts/ACC-12345/balance"

# Get summary for ACC-12345
Invoke-RestMethod -Uri "http://localhost:8000/accounts/ACC-12345/summary"
```

## Run via demo script

```powershell
cd homework-1
.\demo\run.bat
```

## VS Code REST Client

Open `demo/sample-requests.http` in VS Code with the **REST Client** extension installed to run all sample requests interactively.

## Filtering examples

```powershell
# By account
Invoke-RestMethod "http://localhost:8000/transactions?accountId=ACC-12345"

# By type
Invoke-RestMethod "http://localhost:8000/transactions?type=transfer"

# By date range
Invoke-RestMethod "http://localhost:8000/transactions?from=2024-01-01T00:00:00Z&to=2030-12-31T00:00:00Z"

# Combined
Invoke-RestMethod "http://localhost:8000/transactions?accountId=ACC-12345&type=transfer"
```
