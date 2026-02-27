"""Smoke for Stage 6 read-model publication path in local launcher."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run() -> None:
    out_file = Path("artifacts") / "tmp" / "read_model_publication_smoke.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if out_file.exists():
        out_file.unlink()

    cmd = [
        sys.executable,
        "local_run.py",
        "--mode",
        "reminders-only",
        "--dry-run",
        "--mock-external",
        "--evaluate-alerts",
        "--alert-fail-on",
        "none",
        "--read-model-file",
        str(out_file),
        "--read-model-build-id",
        "read-model-smoke",
    ]
    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"local_run_failed rc={proc.returncode} stdout={proc.stdout} stderr={proc.stderr}")
    if not out_file.exists():
        raise RuntimeError("read_model_file_not_created")

    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0.0", payload
    assert payload["source"]["build_id"] == "read-model-smoke", payload
    assert "quality_summary" in payload and isinstance(payload["quality_summary"], dict), payload
    assert "alerts" in payload and isinstance(payload["alerts"], list), payload
    print("read_model_publication_smoke_ok")


if __name__ == "__main__":
    run()
