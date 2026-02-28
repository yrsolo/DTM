"""Smoke check for Stage 8 prototype source switch payload preparation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _write(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON payload fixture to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    """Run filesystem-mode payload preparation smoke scenario."""
    root = Path("artifacts") / "tmp" / "prepare_web_payload_smoke"
    baseline_root = root / "baseline"
    run_dir = baseline_root / "20260227_000000Z_smoke"

    read_model = {
        "schema_version": "1.0.0",
        "generated_at_utc": "2026-02-27T00:00:00Z",
        "source": {"mode": "sync-only", "dry_run": True, "build_id": "smoke"},
        "board": {"timeline": [], "by_designer": []},
        "task_details": [],
        "alerts": [],
        "quality_summary": {},
    }
    schema_snapshot = {
        "schema_version": "1.0.0",
        "required_top_level_fields": sorted(read_model.keys()),
        "schema": {},
    }
    fixture_bundle = {
        "bundle_id": "smoke",
        "sample": {"timeline": [], "task_details": [], "by_designer": {}},
    }

    _write(run_dir / "read_model.json", read_model)
    _write(run_dir / "schema_snapshot.json", schema_snapshot)
    _write(run_dir / "fixture_bundle.json", fixture_bundle)

    out_file = root / "prototype_payload.json"
    cmd = [
        sys.executable,
        "agent/prepare_web_prototype_payload.py",
        "--source-mode",
        "filesystem",
        "--baseline-root",
        str(baseline_root),
        "--output-file",
        str(out_file),
    ]
    run = subprocess.run(cmd, text=True, capture_output=True, check=False)
    if run.returncode != 0:
        print(run.stdout)
        print(run.stderr)
        raise SystemExit(run.returncode)

    payload = json.loads(out_file.read_text(encoding="utf-8"))
    if payload.get("source_mode") != "filesystem":
        raise SystemExit("invalid source_mode")
    if "fixture_bundle" not in payload:
        raise SystemExit("missing fixture_bundle")
    print("prepare_web_prototype_payload_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

