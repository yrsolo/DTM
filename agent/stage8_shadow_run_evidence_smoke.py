"""Smoke check for Stage 8 shadow-run evidence builder."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

PYTHON_EXE = ".venv\\Scripts\\python.exe"
BASELINE_ROOT = Path("artifacts") / "tmp" / "stage8_shadow_smoke_baseline"
BASELINE_DIR = BASELINE_ROOT / "20260227_000000Z_smoke_runtime"
EVIDENCE_ROOT = Path("artifacts") / "tmp" / "stage8_shadow_smoke"


def _latest_evidence_dir(root: Path) -> Path:
    """Return the newest evidence directory under the given root."""

    candidates = [p for p in root.glob("*") if p.is_dir()]
    if not candidates:
        raise RuntimeError(f"no evidence dirs under {root}")
    return sorted(candidates)[-1]


def _latest_baseline_dir(root: Path) -> Path | None:
    """Return latest baseline dir with required artifacts or None."""

    required = ("read_model.json", "schema_snapshot.json", "fixture_bundle.json")
    candidates = [
        path
        for path in root.glob("*")
        if path.is_dir() and all((path / file_name).exists() for file_name in required)
    ]
    if not candidates:
        return None
    return sorted(candidates)[-1]


def _run_checked(cmd: Sequence[str], error_prefix: str, env: dict[str, str] | None = None) -> None:
    """Run command and raise with stdout/stderr on non-zero exit."""

    run = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if run.returncode != 0:
        raise RuntimeError(f"{error_prefix}: {run.stdout}\n{run.stderr}")


def _prepare_baseline_artifacts() -> None:
    """Prepare baseline fixture set for smoke run."""

    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    source_baseline = _latest_baseline_dir(Path("artifacts") / "baseline")
    if source_baseline is not None:
        for file_name in ("read_model.json", "schema_snapshot.json", "fixture_bundle.json"):
            shutil.copy2(source_baseline / file_name, BASELINE_DIR / file_name)
        return

    build_baseline_cmd = [
        PYTHON_EXE,
        "local_run.py",
        "--mode",
        "sync-only",
        "--dry-run",
        "--mock-external",
        "--read-model-file",
        str(BASELINE_DIR / "read_model.json"),
        "--schema-snapshot-file",
        str(BASELINE_DIR / "schema_snapshot.json"),
    ]
    _run_checked(build_baseline_cmd, "baseline_builder_failed")

    fixture_cmd = [
        PYTHON_EXE,
        "agent/build_fixture_bundle.py",
        "--baseline-dir",
        str(BASELINE_DIR),
        "--output-file",
        str(BASELINE_DIR / "fixture_bundle.json"),
    ]
    _run_checked(fixture_cmd, "fixture_builder_failed")


def main() -> int:
    """Build baseline and validate shadow-run evidence artifact contract."""

    _prepare_baseline_artifacts()

    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    cmd = [
        PYTHON_EXE,
        "agent/stage8_shadow_run_evidence.py",
        "--baseline-root",
        str(BASELINE_ROOT),
        "--label",
        "smoke",
        "--evidence-root",
        str(EVIDENCE_ROOT),
    ]
    _run_checked(cmd, "shadow_evidence_builder_failed")

    require_cloud_cmd = cmd + ["--require-cloud-keys"]
    env = os.environ.copy()
    env["PROTOTYPE_READ_MODEL_S3_KEY"] = ""
    env["PROTOTYPE_SCHEMA_SNAPSHOT_S3_KEY"] = ""
    env["PROTOTYPE_FIXTURE_BUNDLE_S3_KEY"] = ""
    require_run = subprocess.run(
        require_cloud_cmd,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if require_run.returncode == 0:
        raise RuntimeError("shadow_run_require_cloud_keys_expected_failure_missing")

    evidence_dir = _latest_evidence_dir(EVIDENCE_ROOT)
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
