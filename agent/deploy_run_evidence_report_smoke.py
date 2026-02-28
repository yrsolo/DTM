"""Smoke check for deploy run evidence report builder."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Sequence

PYTHON_EXE = ".venv\\Scripts\\python.exe"
SMOKE_ARTIFACT = Path("artifacts") / "tmp" / "deploy_run_evidence_smoke.json"


def _run_checked(cmd: Sequence[str], error_prefix: str) -> None:
    """Run command and raise with captured output when failed."""

    run = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if run.returncode != 0:
        raise RuntimeError(f"{error_prefix}: {run.stdout}\n{run.stderr}")


def main() -> int:
    """Validate deploy-run evidence report artifact shape."""

    SMOKE_ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        PYTHON_EXE,
        "agent/deploy_run_evidence_report.py",
        "--per-page",
        "1",
        "--output-file",
        str(SMOKE_ARTIFACT),
    ]
    _run_checked(cmd, "deploy_run_evidence_builder_failed")

    payload = json.loads(SMOKE_ARTIFACT.read_text(encoding="utf-8"))
    if payload.get("artifact") != "deploy_run_evidence_report":
        raise RuntimeError("deploy_run_evidence_artifact_mismatch")
    runs = payload.get("runs", [])
    if not runs:
        raise RuntimeError("deploy_run_evidence_no_runs")
    first = runs[0]
    if "run" not in first or "jobs" not in first:
        raise RuntimeError("deploy_run_evidence_missing_sections")
    print("deploy_run_evidence_report_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
