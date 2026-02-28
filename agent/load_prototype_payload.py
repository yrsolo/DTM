"""Load Stage 8 prototype payload from local or Object Storage artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from web_prototype.loader import PrototypeSchemaError, load_prototype_payload


def parse_args() -> argparse.Namespace:
    """Parse CLI options for prototype payload loading."""
    parser = argparse.ArgumentParser(description="Load Stage 8 prototype payload from artifacts")
    parser.add_argument(
        "--source-mode",
        choices=("filesystem", "object_storage"),
        default="filesystem",
        help="Artifact source mode (default: filesystem).",
    )
    parser.add_argument("--read-model-file", type=Path, help="Filesystem path for read_model.json")
    parser.add_argument("--schema-snapshot-file", type=Path, help="Filesystem path for schema_snapshot.json")
    parser.add_argument("--fixture-bundle-file", type=Path, help="Filesystem path for fixture_bundle.json")
    parser.add_argument("--read-model-s3-key", default="", help="Object Storage key for read_model artifact")
    parser.add_argument("--schema-snapshot-s3-key", default="", help="Object Storage key for schema snapshot artifact")
    parser.add_argument("--fixture-bundle-s3-key", default="", help="Object Storage key for fixture bundle artifact")
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional output file for merged payload summary.",
    )
    return parser.parse_args()


def _build_summary(payload: object) -> dict[str, object]:
    """Build compact summary for loaded prototype payload."""
    read_model = payload.read_model
    board = dict(read_model.get("board", {}))
    return {
        "schema_version": read_model.get("schema_version"),
        "timeline_count": len(board.get("timeline", [])),
        "designer_count": len(board.get("by_designer", [])),
        "task_details_count": len(read_model.get("task_details", [])),
        "fixture_bundle_id": payload.fixture_bundle.get("bundle_id"),
    }


def main() -> int:
    """Load payload from selected source mode and optionally save summary JSON."""
    args = parse_args()
    payload = load_prototype_payload(
        source_mode=args.source_mode,
        read_model_path=args.read_model_file,
        schema_snapshot_path=args.schema_snapshot_file,
        fixture_bundle_path=args.fixture_bundle_file,
        read_model_s3_key=args.read_model_s3_key,
        schema_snapshot_s3_key=args.schema_snapshot_s3_key,
        fixture_bundle_s3_key=args.fixture_bundle_s3_key,
    )
    summary = _build_summary(payload)
    if args.output_file:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"prototype_payload_summary={args.output_file}")
    print("prototype_payload_load_ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PrototypeSchemaError as exc:
        print(f"prototype_payload_schema_error={exc}")
        raise SystemExit(2)
