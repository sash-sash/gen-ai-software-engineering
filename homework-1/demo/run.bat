@echo off
echo Installing dependencies...
py -m pip install -r requirements.txt

echo.
echo Starting Banking Transactions API on http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo.
py -m uvicorn src.main:app --reload --port 8000
