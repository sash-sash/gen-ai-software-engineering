"""Local smoke-test client for homework-6 MCP tools (direct function call)."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def load_server_module():
    server_path = Path(__file__).resolve().parent / "server.py"
    spec = importlib.util.spec_from_file_location("homework6_mcp_server", server_path)
    if not spec or not spec.loader:
        raise RuntimeError("Failed to load mcp/server.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test MCP tool outputs")
    parser.add_argument("--transaction-id", default="TXN005")
    args = parser.parse_args()

    server = load_server_module()
    status = server.get_transaction_status(args.transaction_id)
    listing = server.list_pipeline_results()
    summary = server.pipeline_summary()

    print("=== get_transaction_status ===")
    print(json.dumps(status, indent=2, ensure_ascii=True))
    print("\n=== list_pipeline_results (counts) ===")
    print(json.dumps(listing.get("counts", {}), indent=2, ensure_ascii=True))
    print("\n=== pipeline://summary ===")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
