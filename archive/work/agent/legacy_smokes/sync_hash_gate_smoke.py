"""Smoke check for M3 source hash gate behavior.

Expected:
- first run: sync_skipped=False
- second run with same payload: sync_skipped=True
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.services.sync.sync_service import SyncService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run hash-gate smoke check")
    parser.add_argument(
        "--state-file",
        default="artifacts/tmp/hash_gate_state_smoke.json",
        help="State file path for hash-gate smoke.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    state_file = Path(args.state_file)
    state_file.parent.mkdir(parents=True, exist_ok=True)
    if state_file.exists():
        state_file.unlink()

    source_id = "google-sheet:smoke:ТАБЛИЧКА"
    payload = {
        "rows": [
            {"id": "row-1", "title": "Task A", "status": "work"},
            {"id": "row-2", "title": "Task B", "status": "pre_done"},
        ]
    }

    service = SyncService(state_file=state_file)
    first = service.run(source_payload=payload, source_id=source_id)
    second = service.run(source_payload=payload, source_id=source_id)

    result = {
        "first_run": {
            "sync_skipped": first.sync_skipped,
            "source_hash": first.source_hash,
            "previous_hash": first.previous_hash,
        },
        "second_run": {
            "sync_skipped": second.sync_skipped,
            "source_hash": second.source_hash,
            "previous_hash": second.previous_hash,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if first.sync_skipped:
        print("hash_gate_smoke_failed:first_run_should_not_be_skipped")
        return 1
    if not second.sync_skipped:
        print("hash_gate_smoke_failed:second_run_should_be_skipped")
        return 1
    print("hash_gate_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
