"""Shared utilities for the homework-6 transaction pipeline."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any

TWOPLACES = Decimal("0.01")
ISO4217_ALLOWED = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD"}


def utc_now_z() -> str:
    """Return current UTC timestamp in ISO 8601 format with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_amount(value: Any) -> Decimal:
    """Parse money amount into Decimal, raising ValueError for invalid values."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("amount is not numeric") from exc
    return amount.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def mask_account(account: str) -> str:
    """Mask an account number except last 4 characters."""
    if not account:
        return "UNKNOWN"
    visible = account[-4:]
    return f"ACC-****{visible}"


def append_structured_audit(message: dict[str, Any], agent: str, outcome: str) -> None:
    """Append structured audit row inside message payload."""
    data = message.setdefault("data", {})
    trail = data.setdefault("audit_trail", [])
    trail.append(
        {
            "timestamp": utc_now_z(),
            "agent": agent,
            "transaction_id": data.get("transaction_id", "UNKNOWN"),
            "outcome": outcome,
        }
    )


def append_audit_log_line(log_path: Path, message: dict[str, Any], agent: str, outcome: str) -> None:
    """Append a text audit log line without plaintext PII."""
    data = message.get("data", {})
    timestamp = utc_now_z()
    transaction_id = data.get("transaction_id", "UNKNOWN")
    src = mask_account(str(data.get("source_account", "")))
    dst = mask_account(str(data.get("destination_account", "")))
    line = f"{timestamp} | {agent} | {transaction_id} | {outcome} | src={src} dst={dst}\n"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as file:
        file.write(line)


def update_envelope(message: dict[str, Any], source: str, target: str) -> dict[str, Any]:
    """Return a deep-copied message with updated envelope metadata."""
    new_message = deepcopy(message)
    new_message["source_agent"] = source
    new_message["target_agent"] = target
    new_message["timestamp"] = utc_now_z()
    return new_message


def read_json(path: Path) -> dict[str, Any]:
    """Read JSON object from path."""
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON object to path with deterministic formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
