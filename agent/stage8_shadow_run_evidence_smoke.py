"""Smoke check for Stage 8 shadow-run evidence builder."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


def _latest_evidence_dir(root: Path) -> Path:
    candidates = [p for p in root.glob("*") if p.is_dir()]
    if not candidates:
        raise RuntimeError(f"no evidence dirs under {root}")
    return sorted(candidates)[-1]


def main() -> int:
    baseline_root = Path("artifacts") / "tmp" / "stage8_shadow_smoke_baseline"
    baseline_dir = baseline_root / "20260227_000000Z_smoke_runtime"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    build_baseline_cmd = [
        ".venv\\Scripts\\python.exe",
        "local_run.py",
        "--mode",
        "sync-only",
        "--dry-run",
        "--read-model-file",
        str(baseline_dir / "read_model.json"),
        "--schema-snapshot-file",
        str(baseline_dir / "schema_snapshot.json"),
    ]
    run = subprocess.run(build_baseline_cmd, check=False, capture_output=True, text=True, encoding="utf-8")
    if run.returncode != 0:
        raise RuntimeError(f"baseline_builder_failed: {run.stdout}\n{run.stderr}")
    fixture_cmd = [
        ".venv\\Scripts\\python.exe",
        "agent/build_fixture_bundle.py",
        "--baseline-dir",
        str(baseline_dir),
        "--output-file",
        str(baseline_dir / "fixture_bundle.json"),
    ]
    run = subprocess.run(fixture_cmd, check=False, capture_output=True, text=True, encoding="utf-8")
    if run.returncode != 0:
        raise RuntimeError(f"fixture_builder_failed: {run.stdout}\n{run.stderr}")

    out_root = Path("artifacts") / "tmp" / "stage8_shadow_smoke"
    out_root.mkdir(parents=True, exist_ok=True)
    cmd = [
        ".venv\\Scripts\\python.exe",
        "agent/stage8_shadow_run_evidence.py",
        "--baseline-root",
        str(baseline_root),
        "--label",
        "smoke",
        "--evidence-root",
        str(out_root),
    ]
    run = subprocess.run(cmd, check=False, capture_output=True, text=True, encoding="utf-8")
    if run.returncode != 0:
        raise RuntimeError(f"shadow_evidence_builder_failed: {run.stdout}\n{run.stderr}")

    evidence_dir = _latest_evidence_dir(out_root)
    summary_file = evidence_dir / "shadow_run_evidence.json"
    if not summary_file.exists():
        raise RuntimeError("shadow_run_evidence_json_missing")
    payload = json.loads(summary_file.read_text(encoding="utf-8"))
    if payload.get("artifact") != "stage8_shadow_run_evidence":
        raise RuntimeError("shadow_run_evidence_artifact_mismatch")
    if "checklist" not in payload:
        raise RuntimeError("shadow_run_checklist_missing")
    if payload["checklist"].get("consumer_reads_artifacts_read_only") is not True:
        raise RuntimeError("shadow_run_read_only_check_failed")
    print("stage8_shadow_run_evidence_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
