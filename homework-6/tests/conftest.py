from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import integrator


@pytest.fixture
def isolated_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    base_dir = tmp_path / "hw6"
    base_dir.mkdir(parents=True, exist_ok=True)
    sample_src = Path(__file__).resolve().parents[1] / "sample-transactions.json"
    shutil.copy(sample_src, base_dir / "sample-transactions.json")

    shared_dir = base_dir / "shared"
    input_dir = shared_dir / "input"
    processing_dir = shared_dir / "processing"
    output_dir = shared_dir / "output"
    results_dir = shared_dir / "results"

    monkeypatch.setattr(integrator, "BASE_DIR", base_dir)
    monkeypatch.setattr(integrator, "SHARED_DIR", shared_dir)
    monkeypatch.setattr(integrator, "INPUT_DIR", input_dir)
    monkeypatch.setattr(integrator, "PROCESSING_DIR", processing_dir)
    monkeypatch.setattr(integrator, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(integrator, "RESULTS_DIR", results_dir)
    monkeypatch.setattr(integrator, "AUDIT_LOG_PATH", results_dir / "audit.log")

    return base_dir
