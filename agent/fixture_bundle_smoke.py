"""Smoke check for frontend fixture bundle builder."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.fixture_bundle import build_fixture_bundle

SMOKE_ID = "fixture-smoke"
SMOKE_OUT = Path("artifacts") / "tmp" / "fixture_bundle_smoke.json"
SMOKE_ITEM_LIMIT = 1


def _build_smoke_inputs() -> tuple[dict[str, object], dict[str, object]]:
    """Return deterministic read-model and schema payloads for smoke run."""

    read_model = {
        "schema_version": "1.0.0",
        "source": {"build_id": SMOKE_ID, "generated_at_utc": "2026-02-27T00:00:00Z"},
        "board": {"timeline": [{"id": "1"}, {"id": "2"}], "by_designer": {"ann": [{"id": "1"}]}},
        "task_details": [{"id": "1"}, {"id": "2"}],
        "alerts": {"level": "OK"},
        "quality_summary": {"task_row_issue_count": 0},
    }
    schema_snapshot = {
        "schema_version": "1.0.0",
        "required_top_level_fields": list(read_model.keys()),
        "schema": {"board": {"timeline": {"type": "list"}}},
    }
    return read_model, schema_snapshot


def main() -> int:
    read_model, schema_snapshot = _build_smoke_inputs()
    payload = build_fixture_bundle(
        read_model,
        schema_snapshot,
        bundle_id=SMOKE_ID,
        item_limit=SMOKE_ITEM_LIMIT,
    )
    SMOKE_OUT.parent.mkdir(parents=True, exist_ok=True)
    SMOKE_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    check = json.loads(SMOKE_OUT.read_text(encoding="utf-8"))
    if check.get("artifact") != "frontend_fixture_bundle":
        raise SystemExit("invalid fixture artifact")
    if check.get("counts", {}).get("item_limit") != SMOKE_ITEM_LIMIT:
        raise SystemExit("invalid fixture item_limit")
    print("fixture_bundle_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

