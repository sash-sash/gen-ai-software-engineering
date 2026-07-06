# HOWTORUN — Homework 2

## 1) Install dependencies

```powershell
cd homework-2
py -m pip install -r requirements.txt
```

## 2) Start the API

```powershell
py -m uvicorn src.main:app --reload --port 8000
```

## 3) Create a ticket

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/tickets" -ContentType "application/json" -Body '{"customer_id":"c1","customer_email":"user@example.com","customer_name":"Test User","subject":"Login issue","description":"I cannot login because my password reset fails.","auto_classify":true}'
```

## 4) Import sample CSV

```powershell
curl.exe -X POST "http://127.0.0.1:8000/tickets/import" -F "format=csv" -F "file=@sample_tickets.csv"
```

## 5) Auto-classify a ticket

Replace `{id}` with a ticket UUID from step 3:

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/tickets/{id}/auto-classify"
```

## 6) Run tests with coverage

```powershell
py -m pytest -q
```

Expected: all tests pass, coverage **>85%**.

## 7) Regenerate sample data (optional)

```powershell
py scripts\generate_samples.py
```
