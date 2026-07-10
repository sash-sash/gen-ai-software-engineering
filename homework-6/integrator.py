"""Integrator/orchestrator for the homework-6 multi-agent banking pipeline."""

from __future__ import annotations

import json
import shutil
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

from agents.fraud_detector import score
from agents.settlement_processor import settle
from agents.transaction_validator import validate
from pipeline_utils import TWOPLACES, utc_now_z, write_json

BASE_DIR = Path(__file__).resolve().parent
SHARED_DIR = BASE_DIR / "shared"
INPUT_DIR = SHARED_DIR / "input"
PROCESSING_DIR = SHARED_DIR / "processing"
OUTPUT_DIR = SHARED_DIR / "output"
RESULTS_DIR = SHARED_DIR / "results"
AUDIT_LOG_PATH = RESULTS_DIR / "audit.log"


def _ensure_shared_dirs(clear_existing: bool = True) -> None:
    for directory in (INPUT_DIR, PROCESSING_DIR, OUTPUT_DIR, RESULTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
        if clear_existing:
            for child in directory.iterdir():
                if child.is_file() and child.name != ".gitkeep":
                    child.unlink()


def _create_message(record: dict[str, Any]) -> dict[str, Any]:
    tx_id = str(record.get("transaction_id", "UNKNOWN"))
    message_id = str(uuid.uuid5(uuid.NAMESPACE_URL, tx_id))
    return {
        "message_id": message_id,
        "timestamp": utc_now_z(),
        "source_agent": "integrator",
        "target_agent": "transaction_validator",
        "message_type": "transaction",
        "data": record,
    }


def _write_initial_messages(records: list[dict[str, Any]]) -> list[Path]:
    paths: list[Path] = []
    for record in sorted(records, key=lambda item: str(item.get("transaction_id", ""))):
        message = _create_message(record)
        tx_id = str(record.get("transaction_id", "UNKNOWN"))
        path = INPUT_DIR / f"{tx_id}.json"
        write_json(path, message)
        paths.append(path)
    return paths


def _build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    settled_totals: dict[str, Decimal] = {}
    summary = {
        "run_timestamp": utc_now_z(),
        "processed": len(results),
        "validated": 0,
        "rejected": 0,
        "scored": 0,
        "held": 0,
        "settled": 0,
        "settled_totals_by_currency": {},
    }
    for message in results:
        data = message.get("data", {})
        status = data.get("status")
        if status in ("validated", "scored", "held", "settled"):
            summary["validated"] += 1
        if status == "rejected":
            summary["rejected"] += 1
        if data.get("risk_score") is not None:
            summary["scored"] += 1
        if status == "held":
            summary["held"] += 1
        if status == "settled":
            summary["settled"] += 1
            currency = str(data.get("currency", "UNKNOWN"))
            net = Decimal(str(data.get("net_amount", "0.00"))).quantize(TWOPLACES)
            settled_totals[currency] = settled_totals.get(currency, Decimal("0.00")) + net
    summary["settled_totals_by_currency"] = {
        key: format(value.quantize(TWOPLACES), ".2f")
        for key, value in sorted(settled_totals.items())
    }
    return summary


def run_pipeline(input_path: str = "sample-transactions.json") -> dict[str, Any]:
    """Run the full transaction pipeline and return summary stats."""
    _ensure_shared_dirs(clear_existing=True)
    records = json.loads((BASE_DIR / input_path).read_text(encoding="utf-8"))
    input_files = _write_initial_messages(records)

    final_messages: list[dict[str, Any]] = []
    for raw_file in input_files:
        processing_file = PROCESSING_DIR / raw_file.name
        shutil.move(str(raw_file), str(processing_file))
        raw_message = json.loads(processing_file.read_text(encoding="utf-8"))

        validated = validate(raw_message, audit_log_path=AUDIT_LOG_PATH)
        write_json(OUTPUT_DIR / f"{raw_file.stem}-validated.json", validated)

        if validated["data"].get("status") == "rejected":
            final = validated
        else:
            scored = score(validated, audit_log_path=AUDIT_LOG_PATH)
            write_json(OUTPUT_DIR / f"{raw_file.stem}-scored.json", scored)
            final = settle(scored, audit_log_path=AUDIT_LOG_PATH)

        write_json(RESULTS_DIR / f"{raw_file.stem}.json", final)
        final_messages.append(final)
        processing_file.unlink(missing_ok=True)

    summary = _build_summary(final_messages)
    write_json(RESULTS_DIR / "pipeline-summary.json", summary)
    _print_summary(summary)
    return summary


def _print_summary(summary: dict[str, Any]) -> None:
    print("Pipeline finished")
    print(
        "processed={processed} validated={validated} rejected={rejected} "
        "scored={scored} held={held} settled={settled}".format(**summary)
    )
    print("settled_totals_by_currency:", summary["settled_totals_by_currency"])


if __name__ == "__main__":
    run_pipeline()
