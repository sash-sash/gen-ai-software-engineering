from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.transaction_validator import validate


def test_validator_rejects_invalid_currency():
    message = {
        "message_id": "m1",
        "timestamp": "2026-01-01T00:00:00Z",
        "source_agent": "integrator",
        "target_agent": "transaction_validator",
        "message_type": "transaction",
        "data": {
            "transaction_id": "TXN-X",
            "timestamp": "2026-03-16T10:05:00Z",
            "source_account": "ACC-1006",
            "destination_account": "ACC-7700",
            "amount": "200.00",
            "currency": "XYZ",
            "transaction_type": "transfer",
            "metadata": {"channel": "online", "country": "US"},
        },
    }
    result = validate(message)
    assert result["data"]["status"] == "rejected"
    assert "invalid ISO 4217 currency" in result["data"]["reason"]
    assert result["target_agent"] == "results"


def test_validator_rejects_negative_amount():
    message = {
        "data": {
            "transaction_id": "TXN-Y",
            "timestamp": "2026-03-16T10:10:00Z",
            "source_account": "ACC-1007",
            "destination_account": "ACC-8800",
            "amount": "-100.00",
            "currency": "GBP",
            "transaction_type": "refund",
            "metadata": {"channel": "online", "country": "GB"},
        }
    }
    result = validate(message)
    assert result["data"]["status"] == "rejected"
    assert result["data"]["reason"] == "amount must be greater than 0"


def test_validator_rejects_missing_fields():
    message = {"data": {"transaction_id": "TXN-Z", "amount": "10.00"}}
    result = validate(message)
    assert result["data"]["status"] == "rejected"
    assert "missing required field(s)" in result["data"]["reason"]


def test_validator_accepts_valid_transaction():
    message = {
        "data": {
            "transaction_id": "TXN-OK",
            "timestamp": "2026-03-16T10:10:00Z",
            "source_account": "ACC-1001",
            "destination_account": "ACC-2001",
            "amount": "123.45",
            "currency": "usd",
            "transaction_type": "transfer",
            "metadata": {"channel": "online", "country": "US"},
        }
    }
    result = validate(message)
    assert result["data"]["status"] == "validated"
    assert result["data"]["currency"] == "USD"
    assert result["target_agent"] == "fraud_detector"


def test_validator_rejects_non_numeric_amount():
    message = {
        "data": {
            "transaction_id": "TXN-BAD-AMOUNT",
            "timestamp": "2026-03-16T10:10:00Z",
            "source_account": "ACC-1001",
            "destination_account": "ACC-2001",
            "amount": "abc",
            "currency": "USD",
            "transaction_type": "transfer",
        }
    }
    result = validate(message)
    assert result["data"]["status"] == "rejected"
    assert result["data"]["reason"] == "amount must be numeric"


def test_validator_dry_run_report(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    from agents.transaction_validator import _dry_run_report

    payload = [
        {
            "transaction_id": "TXN1",
            "timestamp": "2026-03-16T10:10:00Z",
            "source_account": "ACC-1001",
            "destination_account": "ACC-2001",
            "amount": "10.00",
            "currency": "USD",
            "transaction_type": "transfer",
        },
        {
            "transaction_id": "TXN2",
            "timestamp": "2026-03-16T10:10:00Z",
            "source_account": "ACC-1001",
            "destination_account": "ACC-2001",
            "amount": "-1.00",
            "currency": "USD",
            "transaction_type": "transfer",
        },
    ]
    input_file = tmp_path / "transactions.json"
    input_file.write_text(json.dumps(payload), encoding="utf-8")

    rc = _dry_run_report(input_file)
    out = capsys.readouterr().out
    assert rc == 0
    assert "total=2 valid=1 invalid=1" in out


def test_validator_main_without_dry_run(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    from agents import transaction_validator as module

    monkeypatch.setattr("sys.argv", ["transaction_validator.py"])
    rc = module.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "Use --dry-run for standalone validation report." in out
