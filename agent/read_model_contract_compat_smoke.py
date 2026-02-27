"""Compatibility smoke checks for Stage 6 read-model contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.read_model import build_read_model, validate_read_model_contract


def run() -> None:
    payload = build_read_model(
        quality_report={
            "mode": "sync-only",
            "dry_run": True,
            "summary": {"task_row_issue_count": 0},
        },
        alert_evaluation=None,
        build_id="compat-smoke",
    )
    errors = validate_read_model_contract(payload)
    assert not errors, errors

    broken = dict(payload)
    broken.pop("quality_summary", None)
    broken_errors = validate_read_model_contract(broken)
    assert "missing_top_level_field:quality_summary" in broken_errors, broken_errors

    print("read_model_contract_compat_smoke_ok")


if __name__ == "__main__":
    run()
