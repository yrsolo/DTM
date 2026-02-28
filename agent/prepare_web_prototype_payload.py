"""Prepare Stage 8 web prototype payload from filesystem or Object Storage."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from web_prototype.loader import PrototypeSchemaError, load_prototype_payload

OBJECT_STORAGE_ENV_KEYS = (
    "PROTOTYPE_READ_MODEL_S3_KEY",
    "PROTOTYPE_SCHEMA_SNAPSHOT_S3_KEY",
    "PROTOTYPE_FIXTURE_BUNDLE_S3_KEY",
)


def _latest_baseline_dir(root: Path) -> Path:
    """Return latest baseline folder under root."""
    candidates = [p for p in root.glob("*") if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"no baseline directories under {root}")
    return sorted(candidates)[-1]


def parse_args() -> argparse.Namespace:
    """Parse CLI args for prototype payload preparation."""
    parser = argparse.ArgumentParser(description="Prepare web prototype payload for Stage 8")
    parser.add_argument(
        "--source-mode",
        choices=("auto", "filesystem", "object_storage"),
        default="auto",
        help="Payload source mode (default: auto).",
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        default=Path("artifacts") / "baseline",
        help="Baseline root for filesystem mode (default: artifacts/baseline).",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=Path("web_prototype") / "static" / "prototype_payload.json",
        help="Output payload file (default: web_prototype/static/prototype_payload.json).",
    )
    return parser.parse_args()


def _resolve_mode(mode: str) -> str:
    """Resolve source mode using explicit arg first, then environment fallback."""
    if mode != "auto":
        return mode
    env_mode = os.environ.get("PROTOTYPE_SOURCE_MODE", "").strip().lower()
    if env_mode in {"filesystem", "object_storage"}:
        return env_mode
    return "filesystem"


def _s3_keys_from_env() -> tuple[str, str, str]:
    """Read required Object Storage keys from environment."""
    values = tuple(os.environ.get(key, "") for key in OBJECT_STORAGE_ENV_KEYS)
    return values[0], values[1], values[2]


def main() -> int:
    """Build canonical prototype payload JSON from selected source mode."""
    args = parse_args()
    mode = _resolve_mode(args.source_mode)

    if mode == "filesystem":
        baseline_dir = _latest_baseline_dir(args.baseline_root)
        payload = load_prototype_payload(
            source_mode="filesystem",
            read_model_path=baseline_dir / "read_model.json",
            schema_snapshot_path=baseline_dir / "schema_snapshot.json",
            fixture_bundle_path=baseline_dir / "fixture_bundle.json",
        )
    else:
        read_model_s3_key, schema_snapshot_s3_key, fixture_bundle_s3_key = _s3_keys_from_env()
        payload = load_prototype_payload(
            source_mode="object_storage",
            read_model_s3_key=read_model_s3_key,
            schema_snapshot_s3_key=schema_snapshot_s3_key,
            fixture_bundle_s3_key=fixture_bundle_s3_key,
        )

    output = {
        "source_mode": mode,
        "read_model": payload.read_model,
        "schema_snapshot": payload.schema_snapshot,
        "fixture_bundle": payload.fixture_bundle,
    }
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"prototype_payload_file={args.output_file}")
    print(f"prototype_payload_source_mode={mode}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PrototypeSchemaError as exc:
        print(f"prototype_payload_schema_error={exc}")
        raise SystemExit(2)
