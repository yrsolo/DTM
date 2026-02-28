"""Build Stage 8 shadow-run evidence package for web prototype consumer."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv


def _utc_stamp() -> str:
    """Return compact UTC timestamp for artifact folder names."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest_baseline_dir(root: Path) -> Path:
    """Return latest baseline directory containing required artifact files."""
    required = ("read_model.json", "schema_snapshot.json", "fixture_bundle.json")
    candidates = [
        p
        for p in root.glob("*")
        if p.is_dir() and all((p / file_name).exists() for file_name in required)
    ]
    if not candidates:
        raise FileNotFoundError(f"no baseline directories with required artifacts under {root}")
    return sorted(candidates)[-1]


def parse_args() -> argparse.Namespace:
    """Parse CLI args for Stage 8 shadow-run evidence builder."""
    parser = argparse.ArgumentParser(description="Build Stage 8 shadow-run evidence package")
    parser.add_argument(
        "--baseline-root",
        type=Path,
        default=Path("artifacts") / "baseline",
        help="Baseline root with timestamped capture dirs (default: artifacts/baseline).",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        default=Path("artifacts") / "shadow_run_stage8",
        help="Output root for evidence package (default: artifacts/shadow_run_stage8).",
    )
    parser.add_argument(
        "--label",
        default="stage8_shadow_run",
        help="Label suffix for evidence directory (default: stage8_shadow_run).",
    )
    parser.add_argument(
        "--require-cloud-keys",
        action="store_true",
        help="Fail run when cloud profile S3 keys are not provided.",
    )
    return parser.parse_args()


def _default_python() -> str:
    """Pick project virtualenv python when available."""
    venv_python = Path(".venv") / "Scripts" / "python.exe"
    return str(venv_python) if venv_python.exists() else os.environ.get("PYTHON", "python")


def _run(cmd: Sequence[str], cwd: Path | None = None) -> dict[str, Any]:
    """Run command and return normalized process evidence payload."""
    started = time.perf_counter()
    proc = subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        check=False,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "elapsed_ms": elapsed_ms,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _has_cloud_keys() -> bool:
    """Check whether all required Object Storage keys are present."""
    return all(
        (
            os.environ.get("PROTOTYPE_READ_MODEL_S3_KEY", "").strip(),
            os.environ.get("PROTOTYPE_SCHEMA_SNAPSHOT_S3_KEY", "").strip(),
            os.environ.get("PROTOTYPE_FIXTURE_BUNDLE_S3_KEY", "").strip(),
        )
    )


def main() -> int:
    """Build Stage 8 shadow-run evidence artifacts and evaluate pass/fail checks."""
    load_dotenv(".env")
    args = parse_args()
    run_id = f"{_utc_stamp()}_{args.label}"
    out_dir = args.evidence_root / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline_dir = _latest_baseline_dir(args.baseline_root)
    py = _default_python()

    commands: dict[str, dict[str, object]] = {}

    commands["load_filesystem"] = _run(
        [
            py,
            "agent/load_prototype_payload.py",
            "--source-mode",
            "filesystem",
            "--read-model-file",
            str(baseline_dir / "read_model.json"),
            "--schema-snapshot-file",
            str(baseline_dir / "schema_snapshot.json"),
            "--fixture-bundle-file",
            str(baseline_dir / "fixture_bundle.json"),
            "--output-file",
            str(out_dir / "filesystem_payload_summary.json"),
        ]
    )
    commands["prepare_filesystem"] = _run(
        [
            py,
            "agent/prepare_web_prototype_payload.py",
            "--source-mode",
            "filesystem",
            "--baseline-root",
            str(args.baseline_root),
            "--output-file",
            str(out_dir / "prototype_payload_filesystem.json"),
        ]
    )
    commands["loader_schema_smoke"] = _run([py, "agent/prototype_loader_smoke.py"])
    commands["assets_smoke"] = _run([py, "agent/web_prototype_assets_smoke.py"])

    cloud_result: dict[str, object]
    cloud_keys_present = _has_cloud_keys()
    if cloud_keys_present:
        cloud_result = _run(
            [
                py,
                "agent/load_prototype_payload.py",
                "--source-mode",
                "object_storage",
                "--read-model-s3-key",
                os.environ["PROTOTYPE_READ_MODEL_S3_KEY"],
                "--schema-snapshot-s3-key",
                os.environ["PROTOTYPE_SCHEMA_SNAPSHOT_S3_KEY"],
                "--fixture-bundle-s3-key",
                os.environ["PROTOTYPE_FIXTURE_BUNDLE_S3_KEY"],
                "--output-file",
                str(out_dir / "object_storage_payload_summary.json"),
            ]
        )
    else:
        cloud_result = {
            "cmd": [],
            "returncode": None,
            "elapsed_ms": 0,
            "stdout": "",
            "stderr": "",
            "status": "skipped_missing_s3_keys",
        }
    commands["load_object_storage"] = cloud_result

    for name, result in commands.items():
        (out_dir / f"{name}.log").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    checklist = {
        "consumer_reads_artifacts_read_only": commands["load_filesystem"]["returncode"] == 0,
        "schema_gate_passes_or_reports_error": commands["loader_schema_smoke"]["returncode"] == 0,
        "empty_state_render_contract_present": commands["assets_smoke"]["returncode"] == 0,
        "cloud_profile_fetch_validated": (
            commands["load_object_storage"].get("returncode") == 0
            if cloud_keys_present
            else "skipped_missing_s3_keys"
        ),
        "cloud_keys_required_mode": bool(args.require_cloud_keys),
        "cloud_keys_present": bool(cloud_keys_present),
    }
    evidence = {
        "artifact": "stage8_shadow_run_evidence",
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "baseline_dir": str(baseline_dir),
        "evidence_dir": str(out_dir),
        "commands": commands,
        "checklist": checklist,
    }
    summary_file = out_dir / "shadow_run_evidence.json"
    summary_file.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")

    failed = [
        name
        for name in ("load_filesystem", "prepare_filesystem", "loader_schema_smoke", "assets_smoke")
        if commands[name]["returncode"] != 0
    ]
    if cloud_keys_present and commands["load_object_storage"].get("returncode") != 0:
        failed.append("load_object_storage")
    if args.require_cloud_keys and not cloud_keys_present:
        failed.append("missing_required_cloud_keys")

    print(f"shadow_run_evidence_file={summary_file}")
    print(f"shadow_run_baseline_dir={baseline_dir}")
    print(f"shadow_run_cloud_check={'enabled' if cloud_keys_present else 'skipped_missing_s3_keys'}")
    print(f"shadow_run_require_cloud_keys={args.require_cloud_keys}")
    if failed:
        print(f"shadow_run_failed_checks={','.join(failed)}")
        return 2
    print("stage8_shadow_run_evidence_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
