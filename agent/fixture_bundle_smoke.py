"""Smoke check for frontend fixture bundle builder."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.fixture_bundle import build_fixture_bundle


def main() -> int:
    read_model = {
        "schema_version": "1.0.0",
        "source": {"build_id": "fixture-smoke", "generated_at_utc": "2026-02-27T00:00:00Z"},
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

    payload = build_fixture_bundle(read_model, schema_snapshot, bundle_id="fixture-smoke", item_limit=1)
    out_file = Path("artifacts") / "tmp" / "fixture_bundle_smoke.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    check = json.loads(out_file.read_text(encoding="utf-8"))
    if check.get("artifact") != "frontend_fixture_bundle":
        raise SystemExit("invalid fixture artifact")
    if check.get("counts", {}).get("item_limit") != 1:
        raise SystemExit("invalid fixture item_limit")
    print("fixture_bundle_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

