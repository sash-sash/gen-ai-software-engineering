from __future__ import annotations

from agents.settlement_processor import settle


def test_settlement_holds_high_risk():
    message = {
        "data": {
            "transaction_id": "TXN-H",
            "timestamp": "2026-03-16T10:00:00Z",
            "amount": "60000.00",
            "currency": "USD",
            "transaction_type": "wire_transfer",
            "metadata": {"channel": "branch", "country": "US"},
            "status": "scored",
            "risk_level": "high",
            "risk_score": 95,
        }
    }
    result = settle(message)
    assert result["data"]["status"] == "held"
    assert "manual review" in result["data"]["reason"]


def test_settlement_computes_fee_and_net_amount():
    message = {
        "data": {
            "transaction_id": "TXN-S",
            "timestamp": "2026-03-16T10:00:00Z",
            "amount": "1500.00",
            "currency": "USD",
            "transaction_type": "transfer",
            "metadata": {"channel": "online", "country": "US"},
            "status": "scored",
            "risk_level": "low",
            "risk_score": 12,
        }
    }
    result = settle(message)
    assert result["data"]["status"] == "settled"
    assert result["data"]["fee"] == "7.50"
    assert result["data"]["net_amount"] == "1492.50"
