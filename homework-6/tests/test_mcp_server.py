from __future__ import annotations

import importlib.util
from pathlib import Path

from integrator import run_pipeline


def test_mcp_tools_return_status_and_summary(isolated_workspace: Path, monkeypatch):
    server_path = Path(__file__).resolve().parents[1] / "mcp" / "server.py"
    spec = importlib.util.spec_from_file_location("homework6_mcp_server", server_path)
    assert spec and spec.loader
    server = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server)

    run_pipeline("sample-transactions.json")
    results_dir = isolated_workspace / "shared" / "results"

    monkeypatch.setattr(server, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(server, "SUMMARY_PATH", results_dir / "pipeline-summary.json")

    row = server.get_transaction_status("TXN001")
    assert row["found"] is True
    assert row["transaction_id"] == "TXN001"

    listing = server.list_pipeline_results()
    assert listing["total_results"] == 8

    summary_text = server.pipeline_summary()
    assert "Pipeline Summary" in summary_text
    assert "Processed: 8" in summary_text
