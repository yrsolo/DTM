"""Smoke check for Stage 7 schema snapshot artifact publication."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.schema_snapshot import build_schema_snapshot

def main() -> int:
    out_dir = Path("artifacts") / "tmp"
    out_dir.mkdir(parents=True, exist_ok=True)
    schema_file = out_dir / "schema_snapshot_smoke.json"
    if schema_file.exists():
        schema_file.unlink()

    read_model = {
        "schema_version": "1.0.0",
        "source": {"generated_at_utc": "2026-02-27T00:00:00Z", "build_id": "smoke"},
        "board": {"timeline": [], "by_designer": {}},
        "task_details": [],
        "alerts": {},
        "quality_summary": {},
    }
    payload = build_schema_snapshot(read_model=read_model, build_id="schema-smoke")
    schema_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = json.loads(schema_file.read_text(encoding="utf-8"))
    if payload.get("artifact") != "read_model_schema_snapshot":
        raise SystemExit("invalid schema snapshot artifact name")
    if "schema_version" not in payload or "schema" not in payload:
        raise SystemExit("schema snapshot missing required fields")

    print("schema_snapshot_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
