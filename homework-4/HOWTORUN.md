# HOWTORUN - Homework 4

## 1) Install dependencies
```powershell
cd homework-4
py -m pip install -r requirements.txt
```

## 2) Run the API
```powershell
py -m uvicorn src.main:app --reload
```

Open:
- API root: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

## 3) Run baseline tests
```powershell
py -m pytest -q
```

## 3.1) Run full 4-agent pipeline (single command)

Prerequisites (one-time):
```powershell
irm 'https://cursor.com/install?win32=true' | iex
agent login
```

Run the real agent pipeline:
```powershell
./run-pipeline.ps1
```

This resets the app to its buggy seed, then runs all 4 agents (Research
Verifier, Bug Fixer, Security Verifier, Unit Test Generator) via `cursor-agent`.
Raw agent logs are written to `context/bugs/001/logs/`.

## 4) Quick functional checks

Working request:
```powershell
curl.exe -X POST "http://127.0.0.1:8000/calculate" -H "Content-Type: application/json" -d "{\"amount\":100,\"tip_percent\":0,\"people\":4}"
```

Bug trigger examples:
```powershell
curl.exe -X POST "http://127.0.0.1:8000/calculate" -H "Content-Type: application/json" -d "{\"amount\":100,\"tip_percent\":10,\"people\":3}"
curl.exe -i -X POST "http://127.0.0.1:8000/calculate" -H "Content-Type: application/json" -d "{\"amount\":100,\"tip_percent\":10,\"people\":0}"
```

## 5) Pipeline inputs/outputs
Input context:
- `context/bugs/001/bug-context.md`
- `context/bugs/001/research/codebase-research.md`
- `context/bugs/001/implementation-plan.md`

Outputs expected from agents:
- `context/bugs/001/research/verified-research.md`
- `context/bugs/001/fix-summary.md`
- `context/bugs/001/security-report.md`
- `context/bugs/001/test-report.md`
