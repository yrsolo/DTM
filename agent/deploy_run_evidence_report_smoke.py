"""Smoke check for deploy run evidence report builder."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


def main() -> int:
    out_file = Path("artifacts") / "tmp" / "deploy_run_evidence_smoke.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ".venv\\Scripts\\python.exe",
        "agent/deploy_run_evidence_report.py",
        "--per-page",
        "1",
        "--output-file",
        str(out_file),
    ]
    run = subprocess.run(cmd, check=False, capture_output=True, text=True, encoding="utf-8")
    if run.returncode != 0:
        raise RuntimeError(f"deploy_run_evidence_builder_failed: {run.stdout}\n{run.stderr}")

    payload = json.loads(out_file.read_text(encoding="utf-8"))
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
