"""Build frontend fixture bundle from baseline artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.fixture_bundle import build_fixture_bundle


def _latest_baseline_dir(root: Path) -> Path:
    """Return latest baseline directory under root."""
    candidates = [p for p in root.glob("*") if p.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"no baseline directories found under {root}")
    return sorted(candidates)[-1]


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for fixture bundle builder."""
    parser = argparse.ArgumentParser(description="Build frontend fixture bundle from baseline artifacts")
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        help="Optional explicit baseline artifact directory (contains read_model.json + schema_snapshot.json).",
    )
    parser.add_argument(
        "--baseline-root",
        type=Path,
        default=Path("artifacts") / "baseline",
        help="Baseline root used when --baseline-dir is not provided (default: artifacts/baseline).",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional output file path (default: <baseline-dir>/fixture_bundle.json).",
    )
    parser.add_argument(
        "--bundle-id",
        default="",
        help="Optional fixture bundle id override.",
    )
    parser.add_argument(
        "--item-limit",
        type=int,
        default=20,
        help="Max items sampled per list/map section (default: 20).",
    )
    parser.add_argument(
        "--s3-key",
        default="",
        help="Optional Object Storage key for fixture bundle upload.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    """Load JSON payload from file path."""
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    """Build fixture bundle file and optionally upload to Object Storage."""
    args = parse_args()
    baseline_dir = args.baseline_dir or _latest_baseline_dir(args.baseline_root)
    read_model_file = baseline_dir / "read_model.json"
    schema_snapshot_file = baseline_dir / "schema_snapshot.json"
    output_file = args.output_file or (baseline_dir / "fixture_bundle.json")

    read_model = _load_json(read_model_file)
    schema_snapshot = _load_json(schema_snapshot_file)
    payload = build_fixture_bundle(
        read_model=read_model,
        schema_snapshot=schema_snapshot,
        bundle_id=args.bundle_id,
        item_limit=args.item_limit,
    )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"fixture_bundle_file={output_file}")

    if args.s3_key:
        from utils.storage import S3SnapshotStorage

        storage = S3SnapshotStorage()
        storage.upload_json(args.s3_key, payload)
        print(f"fixture_bundle_s3_key={args.s3_key}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
