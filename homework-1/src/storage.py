"""Thread-safe in-memory storage for transactions."""

from __future__ import annotations

import threading
from datetime import datetime
from typing import Optional
from uuid import UUID

from .models import Transaction


_lock = threading.Lock()
_transactions: dict[UUID, Transaction] = {}


def add(tx: Transaction) -> Transaction:
    with _lock:
        _transactions[tx.id] = tx
    return tx


def get(tx_id: UUID) -> Optional[Transaction]:
    return _transactions.get(tx_id)


def list_all(
    account_id: Optional[str] = None,
    tx_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> list[Transaction]:
    result = list(_transactions.values())

    if account_id:
        result = [
            t for t in result
            if t.fromAccount == account_id or t.toAccount == account_id
        ]
    if tx_type:
        result = [t for t in result if t.type.value == tx_type]
    if from_date:
        result = [t for t in result if t.timestamp >= from_date]
    if to_date:
        result = [t for t in result if t.timestamp <= to_date]

    return sorted(result, key=lambda t: t.timestamp, reverse=True)


def get_balance(account_id: str) -> float:
    """
    Simple balance calculation:
    +amount for deposits (toAccount) and incoming transfers (toAccount)
    -amount for withdrawals (fromAccount) and outgoing transfers (fromAccount)
    """
    balance = 0.0
    for tx in _transactions.values():
        if tx.type.value == "deposit" and tx.toAccount == account_id:
            balance += tx.amount
        elif tx.type.value == "withdrawal" and tx.fromAccount == account_id:
            balance -= tx.amount
        elif tx.type.value == "transfer":
            if tx.toAccount == account_id:
                balance += tx.amount
            if tx.fromAccount == account_id:
                balance -= tx.amount
    return round(balance, 2)


def get_summary(account_id: str) -> dict:
    txs = [
        t for t in _transactions.values()
        if t.fromAccount == account_id or t.toAccount == account_id
    ]
    total_deposits = sum(
        t.amount for t in txs
        if t.type.value == "deposit" and t.toAccount == account_id
    )
    total_withdrawals = sum(
        t.amount for t in txs
        if t.type.value == "withdrawal" and t.fromAccount == account_id
    )
    most_recent = max((t.timestamp for t in txs), default=None)
    return {
        "accountId": account_id,
        "total_deposits": round(total_deposits, 2),
        "total_withdrawals": round(total_withdrawals, 2),
        "transaction_count": len(txs),
        "most_recent_transaction": most_recent,
    }


def clear() -> None:
    with _lock:
        _transactions.clear()
