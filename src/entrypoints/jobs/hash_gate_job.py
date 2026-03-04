"""Source hash-gate helper for main job flow."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from src.services.sync.hash_basis import build_hash_basis
from src.services.sync.hash_gate import evaluate_hash_gate, save_last_hash


def resolve_allow_sync_by_hash_gate(
    *,
    enabled: bool,
    mode: str,
    source_task_repository: Any,
    state_file_path: str,
    safe_print: Callable[[str], None],
) -> bool:
    if not (enabled and mode in {"timer", "test", "sync-only"}):
        return True

    rows = []
    for task in source_task_repository.get_all_tasks():
        rows.append(
            {
                "id": task.id,
                "brand": task.brand,
                "format_": task.format_,
                "project_name": task.project_name,
                "customer": task.customer,
                "designer": task.designer,
                "raw_timing": task.raw_timing,
                "status": task.status,
            }
        )
    basis = build_hash_basis(rows)
    state_file = Path(state_file_path)
    decision = evaluate_hash_gate(source_payload=basis, state_file=state_file)
    safe_print(
        "source_hash_gate="
        f"source_hash={decision.source_hash} "
        f"previous_hash={decision.previous_hash} "
        f"should_sync={decision.should_sync}"
    )
    if decision.should_sync:
        save_last_hash(
            state_file=state_file,
            source_id=source_task_repository.source_sheet_info.spreadsheet_name,
            source_hash=decision.source_hash,
        )
    return decision.should_sync
