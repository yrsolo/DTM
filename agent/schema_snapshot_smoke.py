"""Smoke check for Stage 7 schema snapshot artifact publication."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.schema_snapshot import build_schema_snapshot

SMOKE_BUILD_ID = "schema-smoke"
SCHEMA_FILE = Path("artifacts") / "tmp" / "schema_snapshot_smoke.json"


def _sample_read_model() -> dict[str, object]:
    """Return deterministic read-model payload for schema snapshot smoke."""

    return {
        "schema_version": "1.0.0",
        "source": {"generated_at_utc": "2026-02-27T00:00:00Z", "build_id": "smoke"},
        "board": {"timeline": [], "by_designer": {}},
        "task_details": [],
        "alerts": {},
        "quality_summary": {},
    }


def main() -> int:
    """Build and validate schema snapshot artifact contract."""

    SCHEMA_FILE.parent.mkdir(parents=True, exist_ok=True)
    if SCHEMA_FILE.exists():
        SCHEMA_FILE.unlink()

    payload = build_schema_snapshot(read_model=_sample_read_model(), build_id=SMOKE_BUILD_ID)
    SCHEMA_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    if payload.get("artifact") != "read_model_schema_snapshot":
        raise SystemExit("invalid schema snapshot artifact name")
    if "schema_version" not in payload or "schema" not in payload:
        raise SystemExit("schema snapshot missing required fields")

    print("schema_snapshot_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
