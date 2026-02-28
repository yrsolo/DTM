"""Smoke check for Stage 8 prototype loader + schema gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from web_prototype.loader import PrototypeSchemaError, load_prototype_payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON fixture payload to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    """Verify happy-path load and schema-gate failure path."""
    tmp = Path("artifacts") / "tmp" / "prototype_loader_smoke"
    read_model_file = tmp / "read_model.json"
    schema_file = tmp / "schema_snapshot.json"
    fixture_file = tmp / "fixture_bundle.json"

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
    fixture_bundle = {"bundle_id": "smoke", "sample": {}}

    _write(read_model_file, read_model)
    _write(schema_file, schema_snapshot)
    _write(fixture_file, fixture_bundle)

    load_prototype_payload(
        source_mode="filesystem",
        read_model_path=read_model_file,
        schema_snapshot_path=schema_file,
        fixture_bundle_path=fixture_file,
    )

    broken = dict(read_model)
    broken.pop("quality_summary", None)
    _write(read_model_file, broken)
    try:
        load_prototype_payload(
            source_mode="filesystem",
            read_model_path=read_model_file,
            schema_snapshot_path=schema_file,
            fixture_bundle_path=fixture_file,
        )
    except PrototypeSchemaError:
        print("prototype_loader_smoke_ok")
        return 0

    raise SystemExit("schema gate did not fail")


if __name__ == "__main__":
    raise SystemExit(main())

