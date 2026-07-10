"""Transaction validator agent for the banking pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pipeline_utils import (
    ISO4217_ALLOWED,
    append_audit_log_line,
    append_structured_audit,
    parse_amount,
    update_envelope,
)

AGENT_NAME = "transaction_validator"
NEXT_AGENT = "fraud_detector"
REQUIRED_FIELDS = (
    "transaction_id",
    "timestamp",
    "source_account",
    "destination_account",
    "amount",
    "currency",
    "transaction_type",
)


def validate(message: dict[str, Any], audit_log_path: Path | None = None) -> dict[str, Any]:
    """Validate incoming transaction message and route it downstream."""
    validated = update_envelope(message, source=AGENT_NAME, target=NEXT_AGENT)
    data = validated.setdefault("data", {})
    missing_fields = [field for field in REQUIRED_FIELDS if not data.get(field)]
    if missing_fields:
        data["status"] = "rejected"
        data["reason"] = f"missing required field(s): {', '.join(missing_fields)}"
        validated["target_agent"] = "results"
        append_structured_audit(validated, AGENT_NAME, "rejected")
        if audit_log_path:
            append_audit_log_line(audit_log_path, validated, AGENT_NAME, "rejected")
        return validated

    currency = str(data.get("currency", "")).upper()
    if currency not in ISO4217_ALLOWED:
        data["status"] = "rejected"
        data["reason"] = f"invalid ISO 4217 currency: {currency}"
        validated["target_agent"] = "results"
        append_structured_audit(validated, AGENT_NAME, "rejected")
        if audit_log_path:
            append_audit_log_line(audit_log_path, validated, AGENT_NAME, "rejected")
        return validated
    data["currency"] = currency

    try:
        amount = parse_amount(data.get("amount"))
    except ValueError:
        data["status"] = "rejected"
        data["reason"] = "amount must be numeric"
        validated["target_agent"] = "results"
        append_structured_audit(validated, AGENT_NAME, "rejected")
        if audit_log_path:
            append_audit_log_line(audit_log_path, validated, AGENT_NAME, "rejected")
        return validated

    if amount <= 0:
        data["status"] = "rejected"
        data["reason"] = "amount must be greater than 0"
        validated["target_agent"] = "results"
        append_structured_audit(validated, AGENT_NAME, "rejected")
        if audit_log_path:
            append_audit_log_line(audit_log_path, validated, AGENT_NAME, "rejected")
        return validated

    data["amount"] = format(amount, ".2f")
    data["status"] = "validated"
    data.pop("reason", None)
    append_structured_audit(validated, AGENT_NAME, "validated")
    if audit_log_path:
        append_audit_log_line(audit_log_path, validated, AGENT_NAME, "validated")
    return validated


def _dry_run_report(input_path: Path) -> int:
    """Run validator over sample transactions and print compact report."""
    records = json.loads(input_path.read_text(encoding="utf-8"))
    valid = 0
    invalid = 0
    reasons: dict[str, int] = {}
    for record in records:
        message = {"data": record}
        result = validate(message)
        status = result["data"]["status"]
        if status == "validated":
            valid += 1
        else:
            invalid += 1
            reason = result["data"].get("reason", "unknown")
            reasons[reason] = reasons.get(reason, 0) + 1

    print("Validator dry-run summary")
    print(f"total={len(records)} valid={valid} invalid={invalid}")
    if reasons:
        print("reasons:")
        for reason, count in sorted(reasons.items()):
            print(f"- {reason}: {count}")
    return 0


def main() -> int:
    """CLI entry point for validator dry-run mode."""
    parser = argparse.ArgumentParser(description="Transaction validator")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate sample-transactions.json and print summary",
    )
    parser.add_argument(
        "--input",
        default="sample-transactions.json",
        help="Input JSON file for dry-run",
    )
    args = parser.parse_args()
    if args.dry_run:
        return _dry_run_report(Path(args.input))
    print("Use --dry-run for standalone validation report.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
