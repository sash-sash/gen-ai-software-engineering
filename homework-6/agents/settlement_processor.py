"""Settlement processor agent for terminal transaction outcomes."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline_utils import (
    TWOPLACES,
    append_audit_log_line,
    append_structured_audit,
    parse_amount,
    update_envelope,
)

AGENT_NAME = "settlement_processor"
TERMINAL_TARGET = "results"


def _to_iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_iso(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def settle(message: dict[str, Any], audit_log_path: Path | None = None) -> dict[str, Any]:
    """Settle transactions or put high-risk ones on hold."""
    settled = update_envelope(message, source=AGENT_NAME, target=TERMINAL_TARGET)
    data = settled.setdefault("data", {})

    if data.get("status") != "scored":
        append_structured_audit(settled, AGENT_NAME, "skipped_non_scored")
        if audit_log_path:
            append_audit_log_line(audit_log_path, settled, AGENT_NAME, "skipped_non_scored")
        return settled

    if data.get("risk_level") == "high":
        data["status"] = "held"
        data["reason"] = "high fraud risk requires manual review"
        append_structured_audit(settled, AGENT_NAME, "held")
        if audit_log_path:
            append_audit_log_line(audit_log_path, settled, AGENT_NAME, "held")
        return settled

    amount = parse_amount(data.get("amount"))
    fee = (amount * Decimal("0.005")).quantize(TWOPLACES, rounding=ROUND_HALF_UP)
    fee = max(Decimal("1.00"), min(Decimal("25.00"), fee))
    net = (amount - fee).quantize(TWOPLACES, rounding=ROUND_HALF_UP)

    is_cross_border = str(data.get("metadata", {}).get("country", "US")).upper() != "US"
    is_wire = str(data.get("transaction_type", "")).lower() == "wire_transfer"
    plus_days = 2 if is_cross_border or is_wire else 1
    settlement_date = _parse_iso(str(data.get("timestamp"))) + timedelta(days=plus_days)

    data["fee"] = format(fee, ".2f")
    data["net_amount"] = format(net, ".2f")
    data["settlement_date"] = _to_iso_z(settlement_date)
    data["status"] = "settled"
    data.pop("reason", None)

    append_structured_audit(settled, AGENT_NAME, "settled")
    if audit_log_path:
        append_audit_log_line(audit_log_path, settled, AGENT_NAME, "settled")
    return settled
