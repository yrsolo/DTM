"""Compatibility smoke checks for Stage 6 read-model contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.read_model import build_read_model, validate_read_model_contract

SMOKE_BUILD_ID = "compat-smoke"
MISSING_FIELD_ERROR = "missing_top_level_field:quality_summary"


def _build_payload() -> dict[str, object]:
    """Return deterministic payload for contract compatibility checks."""

    return build_read_model(
        quality_report={
            "mode": "sync-only",
            "dry_run": True,
            "summary": {"task_row_issue_count": 0},
        },
        alert_evaluation=None,
        build_id=SMOKE_BUILD_ID,
    )


def run() -> None:
    """Execute compatibility assertions for read-model contract validator."""

    payload = _build_payload()
    errors = validate_read_model_contract(payload)
    assert not errors, errors

    broken = dict(payload)
    broken.pop("quality_summary", None)
    broken_errors = validate_read_model_contract(broken)
    assert MISSING_FIELD_ERROR in broken_errors, broken_errors

    print("read_model_contract_compat_smoke_ok")


if __name__ == "__main__":
    run()
