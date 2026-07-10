from __future__ import annotations

from agents.fraud_detector import score


def test_fraud_detector_marks_high_risk_for_large_offhour_cross_border_api():
    message = {
        "data": {
            "transaction_id": "TXN004",
            "timestamp": "2026-03-16T02:47:00Z",
            "source_account": "ACC-1004",
            "destination_account": "ACC-5500",
            "amount": "75000.00",
            "currency": "EUR",
            "transaction_type": "wire_transfer",
            "metadata": {"channel": "api", "country": "DE"},
            "status": "validated",
        }
    }
    result = score(message)
    assert result["data"]["status"] == "scored"
    assert result["data"]["risk_level"] == "high"
    assert result["data"]["risk_score"] >= 70


def test_fraud_detector_skips_non_validated_message():
    message = {"data": {"transaction_id": "TXN1", "status": "rejected", "amount": "10.00", "timestamp": "2026-01-01T00:00:00Z"}}
    result = score(message)
    assert result["data"]["status"] == "rejected"
