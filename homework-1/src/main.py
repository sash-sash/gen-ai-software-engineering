"""Banking Transactions REST API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from . import storage
from .models import AccountBalance, AccountSummary, Transaction, utc_now
from .validators import parse_transaction

app = FastAPI(title="Banking Transactions API", version="1.0.0")


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"service": "Banking Transactions API", "docs": "/docs"}


@app.post("/transactions", status_code=201, response_model=Transaction)
def create_transaction(payload: dict):
    tx_data, errors = parse_transaction(payload)
    if errors:
        return JSONResponse(
            status_code=400,
            content={"error": "Validation failed", "details": errors},
        )
    from .models import build_transaction
    tx = build_transaction(tx_data)
    storage.add(tx)
    return tx


@app.get("/transactions", response_model=list[Transaction])
def list_transactions(
    accountId: Optional[str] = Query(default=None),
    type: Optional[str] = Query(default=None),
    from_: Optional[datetime] = Query(default=None, alias="from"),
    to: Optional[datetime] = Query(default=None),
):
    return storage.list_all(
        account_id=accountId,
        tx_type=type,
        from_date=from_,
        to_date=to,
    )


@app.get("/transactions/{transaction_id}", response_model=Transaction)
def get_transaction(transaction_id: UUID):
    tx = storage.get(transaction_id)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


# ---------------------------------------------------------------------------
# Accounts
# ---------------------------------------------------------------------------

@app.get("/accounts/{accountId}/balance", response_model=AccountBalance)
def get_balance(accountId: str):
    balance = storage.get_balance(accountId)
    return AccountBalance(
        accountId=accountId,
        balance=balance,
        last_updated=utc_now(),
    )


@app.get("/accounts/{accountId}/summary", response_model=AccountSummary)
def get_summary(accountId: str):
    data = storage.get_summary(accountId)
    return AccountSummary(**data)
