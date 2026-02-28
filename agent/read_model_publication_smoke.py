"""Smoke for Stage 6 read-model publication path in local launcher."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Sequence

SMOKE_BUILD_ID = "read-model-smoke"
SMOKE_OUT_FILE = Path("artifacts") / "tmp" / "read_model_publication_smoke.json"


def _run_checked(cmd: Sequence[str], error_prefix: str) -> None:
    """Run command and raise with captured output when failed."""

    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"{error_prefix} rc={proc.returncode} stdout={proc.stdout} stderr={proc.stderr}"
        )


def run() -> None:
    """Validate read-model publication via local launcher in mock mode."""

    SMOKE_OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SMOKE_OUT_FILE.exists():
        SMOKE_OUT_FILE.unlink()

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
        str(SMOKE_OUT_FILE),
        "--read-model-build-id",
        SMOKE_BUILD_ID,
    ]
    _run_checked(cmd, "local_run_failed")
    if not SMOKE_OUT_FILE.exists():
        raise RuntimeError("read_model_file_not_created")

    payload = json.loads(SMOKE_OUT_FILE.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0.0", payload
    assert payload["source"]["build_id"] == SMOKE_BUILD_ID, payload
    assert "quality_summary" in payload and isinstance(payload["quality_summary"], dict), payload
    assert "alerts" in payload and isinstance(payload["alerts"], list), payload
    print("read_model_publication_smoke_ok")


if __name__ == "__main__":
    run()
