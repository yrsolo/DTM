"""Build Stage 23 operational evidence bundle from cloud smoke outputs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _to_int(value: object, *, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _build_inputs(smoke: dict[str, object]) -> list[dict[str, object]]:
    api = smoke.get("api", {})
    if not isinstance(api, dict):
        api = {}
    v1_status = _to_int(api.get("v1_status_code"), default=0)
    v2_status = _to_int(api.get("v2_status_code"), default=0)
    overlap_count = _to_int(api.get("overlap_count"), default=0)
    v2_contract_version = str(api.get("v2_contract_version", "")).strip()
    v2_readmodel_source = str(api.get("v2_readmodel_source", "")).strip()
    smoke_ok = bool(smoke.get("ok"))
    smoke_sync_status = _to_int((smoke.get("sync_invoke") or {}).get("status_code"), default=0)

    return [
        {"name": "cloud_smoke_ok", "value": smoke_ok, "required": True, "passed": smoke_ok},
        {
            "name": "sync_invoke_status_200",
            "value": smoke_sync_status,
            "required": True,
            "passed": smoke_sync_status == 200,
        },
        {"name": "api_v1_status_200", "value": v1_status, "required": True, "passed": v1_status == 200},
        {"name": "api_v2_status_200", "value": v2_status, "required": True, "passed": v2_status == 200},
        {
            "name": "api_task_overlap_positive",
            "value": overlap_count,
            "required": True,
            "passed": overlap_count > 0,
        },
        {
            "name": "v2_contract_version_present",
            "value": v2_contract_version,
            "required": True,
            "passed": bool(v2_contract_version),
        },
        {
            "name": "v2_readmodel_source_present",
            "value": v2_readmodel_source,
            "required": False,
            "passed": bool(v2_readmodel_source),
        },
    ]


def build_operational_evidence_bundle(smoke: dict[str, object]) -> dict[str, object]:
    checks = _build_inputs(smoke)
    required_failed = [item["name"] for item in checks if item["required"] and not item["passed"]]
    optional_failed = [item["name"] for item in checks if (not item["required"]) and not item["passed"]]
    go_no_go_ready = len(required_failed) == 0
    return {
        "artifact": "stage23_operational_evidence_bundle",
        "generated_at_utc": _utc_iso(),
        "source_artifact": str(smoke.get("artifact", "")),
        "checks": checks,
        "required_failed": required_failed,
        "optional_warnings": optional_failed,
        "go_no_go_input_ready": go_no_go_ready,
        "verdict": "ready" if go_no_go_ready else "not_ready",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Stage 23 operational evidence bundle")
    parser.add_argument(
        "--smoke-file",
        default="work/artifacts/tmp/stage23_canary_precheck.json",
        help="Input cloud smoke JSON file",
    )
    parser.add_argument(
        "--output-file",
        default="work/artifacts/tmp/stage23_operational_evidence_bundle.json",
        help="Output evidence bundle JSON path",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    smoke_path = Path(args.smoke_file)
    if not smoke_path.exists():
        print(f"ERROR: smoke file does not exist: {smoke_path}")
        return 2

    smoke_payload = json.loads(smoke_path.read_text(encoding="utf-8"))
    if not isinstance(smoke_payload, dict):
        print("ERROR: smoke payload must be JSON object")
        return 2

    bundle = build_operational_evidence_bundle(smoke_payload)
    output_path = Path(args.output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"stage23_operational_evidence_bundle_file={output_path}")
    print(f"stage23_operational_evidence_bundle_ready={str(bool(bundle['go_no_go_input_ready'])).lower()}")
    return 0 if bundle["go_no_go_input_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
