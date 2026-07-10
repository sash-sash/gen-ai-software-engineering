"""Fraud detector agent for risk scoring."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline_utils import (
    append_audit_log_line,
    append_structured_audit,
    parse_amount,
    update_envelope,
)

AGENT_NAME = "fraud_detector"
NEXT_AGENT = "settlement_processor"


def _parse_hour(timestamp: str) -> int:
    normalized = timestamp.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized).hour


def _risk_level(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def score(message: dict[str, Any], audit_log_path: Path | None = None) -> dict[str, Any]:
    """Score validated transactions and route for settlement."""
    scored = update_envelope(message, source=AGENT_NAME, target=NEXT_AGENT)
    data = scored.setdefault("data", {})

    if data.get("status") != "validated":
        append_structured_audit(scored, AGENT_NAME, "skipped_non_validated")
        if audit_log_path:
            append_audit_log_line(audit_log_path, scored, AGENT_NAME, "skipped_non_validated")
        return scored

    amount = parse_amount(data.get("amount"))
    risk_score = 0
    if amount > 10000:
        risk_score += 35
    if amount > 50000:
        risk_score += 35

    hour = _parse_hour(str(data.get("timestamp")))
    if 0 <= hour <= 5:
        risk_score += 20

    country = str(data.get("metadata", {}).get("country", "US")).upper()
    if country != "US":
        risk_score += 15

    channel = str(data.get("metadata", {}).get("channel", "")).lower()
    channel_weights = {"api": 15, "online": 10, "mobile": 6, "branch": 2}
    risk_score += channel_weights.get(channel, 3)

    risk_score = min(100, int(risk_score))
    data["risk_score"] = risk_score
    data["risk_level"] = _risk_level(risk_score)
    data["status"] = "scored"

    append_structured_audit(scored, AGENT_NAME, f"scored_{data['risk_level']}")
    if audit_log_path:
        append_audit_log_line(audit_log_path, scored, AGENT_NAME, f"scored_{data['risk_level']}")
    return scored
