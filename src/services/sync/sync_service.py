"""Sync orchestration skeleton for migration stages M2-M3."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.services.sync.hash_gate import evaluate_hash_gate, save_last_hash


@dataclass(slots=True)
class SyncServiceResult:
    """Sync execution summary."""

    sync_skipped: bool
    source_hash: str
    previous_hash: str | None


class SyncService:
    """Incremental sync service skeleton."""

    def __init__(self, state_file: str | Path) -> None:
        self._state_file = state_file

    def run(self, source_payload: Any, source_id: str) -> SyncServiceResult:
        """Run hash-gated sync.

        M2/M3 skeleton:
        - computes source hash
        - decides skip/run
        - stores hash on run path
        """
        decision = evaluate_hash_gate(source_payload=source_payload, state_file=self._state_file)
        if decision.should_sync:
            save_last_hash(state_file=self._state_file, source_id=source_id, source_hash=decision.source_hash)
        return SyncServiceResult(
            sync_skipped=not decision.should_sync,
            source_hash=decision.source_hash,
            previous_hash=decision.previous_hash,
        )

