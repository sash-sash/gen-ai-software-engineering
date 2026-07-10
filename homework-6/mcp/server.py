"""Custom FastMCP server exposing pipeline status tools/resources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

BASE_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = BASE_DIR / "shared" / "results"
SUMMARY_PATH = RESULTS_DIR / "pipeline-summary.json"

mcp = FastMCP(
    name="Pipeline Status MCP",
    instructions=(
        "Use this server to inspect homework-6 pipeline results. "
        "Call get_transaction_status for a specific transaction, "
        "list_pipeline_results for aggregate status, and read pipeline://summary "
        "for a human-readable summary."
    ),
)


def _load_result_files() -> list[Path]:
    if not RESULTS_DIR.exists():
        return []
    return sorted(
        [
            file
            for file in RESULTS_DIR.glob("*.json")
            if file.name not in {"pipeline-summary.json"}
        ]
    )


def _load_message(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@mcp.tool()
def get_transaction_status(transaction_id: str) -> dict[str, Any]:
    """Return status details for a single transaction id."""
    target = (RESULTS_DIR / f"{transaction_id}.json")
    if not target.exists():
        return {
            "found": False,
            "transaction_id": transaction_id,
            "status": "not_found",
            "message": "No transaction result file exists for this id.",
        }

    message = _load_message(target)
    data = message.get("data", {})
    return {
        "found": True,
        "transaction_id": data.get("transaction_id", transaction_id),
        "status": data.get("status"),
        "risk_level": data.get("risk_level"),
        "risk_score": data.get("risk_score"),
        "reason": data.get("reason"),
        "fee": data.get("fee"),
        "net_amount": data.get("net_amount"),
        "settlement_date": data.get("settlement_date"),
    }


@mcp.tool()
def list_pipeline_results() -> dict[str, Any]:
    """Return aggregate status and per-transaction rows."""
    rows: list[dict[str, Any]] = []
    counters = {"rejected": 0, "held": 0, "settled": 0}
    for result_file in _load_result_files():
        message = _load_message(result_file)
        data = message.get("data", {})
        status = str(data.get("status", "unknown"))
        if status in counters:
            counters[status] += 1
        rows.append(
            {
                "transaction_id": data.get("transaction_id"),
                "status": status,
                "risk_level": data.get("risk_level"),
                "currency": data.get("currency"),
                "amount": data.get("amount"),
                "net_amount": data.get("net_amount"),
            }
        )
    return {
        "total_results": len(rows),
        "counts": counters,
        "results": rows,
    }


@mcp.resource("pipeline://summary")
def pipeline_summary() -> str:
    """Return latest pipeline run summary text."""
    if SUMMARY_PATH.exists():
        payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
        lines = [
            "Pipeline Summary",
            f"Run timestamp: {payload.get('run_timestamp')}",
            f"Processed: {payload.get('processed')}",
            f"Validated: {payload.get('validated')}",
            f"Rejected: {payload.get('rejected')}",
            f"Scored: {payload.get('scored')}",
            f"Held: {payload.get('held')}",
            f"Settled: {payload.get('settled')}",
            f"Settled totals: {payload.get('settled_totals_by_currency')}",
        ]
        return "\n".join(lines)
    return "No pipeline-summary.json found. Run the pipeline first."


if __name__ == "__main__":
    mcp.run()
