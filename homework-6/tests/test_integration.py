from __future__ import annotations

import json
from pathlib import Path

from integrator import run_pipeline


def test_pipeline_end_to_end_creates_results_and_summary(isolated_workspace: Path):
    summary = run_pipeline("sample-transactions.json")
    results_dir = isolated_workspace / "shared" / "results"

    assert summary["processed"] == 8
    assert summary["rejected"] == 2
    assert summary["held"] >= 1
    assert summary["settled"] >= 1

    tx_files = sorted(path.name for path in results_dir.glob("TXN*.json"))
    assert len(tx_files) == 8
    assert (results_dir / "pipeline-summary.json").exists()
    assert (results_dir / "audit.log").exists()

    tx006 = json.loads((results_dir / "TXN006.json").read_text(encoding="utf-8"))
    tx007 = json.loads((results_dir / "TXN007.json").read_text(encoding="utf-8"))
    tx005 = json.loads((results_dir / "TXN005.json").read_text(encoding="utf-8"))

    assert tx006["data"]["status"] == "rejected"
    assert "currency" in tx006["data"]["reason"]
    assert tx007["data"]["status"] == "rejected"
    assert tx005["data"]["status"] in {"held", "settled"}
