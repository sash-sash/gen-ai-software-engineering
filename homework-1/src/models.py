"""Pydantic models and enums for Banking Transactions API."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


VALID_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD",
    "CNY", "HKD", "SGD", "NOK", "SEK", "DKK", "PLN", "CZK",
    "HUF", "RON", "BGN", "HRK", "TRY", "RUB", "UAH", "INR",
    "BRL", "MXN", "ZAR", "KRW", "THB", "MYR", "IDR", "PHP",
}

ACCOUNT_PATTERN = r"^ACC-[A-Z0-9]{5}$"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TransactionCreate(BaseModel):
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType
    status: TransactionStatus = TransactionStatus.PENDING

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be a positive number")
        rounded = round(v, 2)
        if rounded != v:
            raise ValueError("Amount must have at most 2 decimal places")
        return rounded

    @field_validator("fromAccount", "toAccount")
    @classmethod
    def validate_account(cls, v: str) -> str:
        import re
        if not re.match(ACCOUNT_PATTERN, v):
            raise ValueError(
                "Account number must follow format ACC-XXXXX "
                "(5 uppercase alphanumeric characters)"
            )
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        code = v.upper()
        if code not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency code '{v}'. Use ISO 4217 codes.")
        return code


class Transaction(BaseModel):
    id: UUID
    fromAccount: str
    toAccount: str
    amount: float
    currency: str
    type: TransactionType
    timestamp: datetime
    status: TransactionStatus


class AccountBalance(BaseModel):
    accountId: str
    balance: float
    currency: str = "USD"
    last_updated: datetime


class AccountSummary(BaseModel):
    accountId: str
    total_deposits: float
    total_withdrawals: float
    transaction_count: int
    most_recent_transaction: Optional[datetime]


def build_transaction(data: TransactionCreate) -> Transaction:
    return Transaction(
        id=uuid4(),
        fromAccount=data.fromAccount,
        toAccount=data.toAccount,
        amount=data.amount,
        currency=data.currency,
        type=data.type,
        timestamp=utc_now(),
        status=data.status,
    )
