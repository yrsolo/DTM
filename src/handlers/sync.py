"""Sync handler for migration path (M2/M3)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.services.sync.sync_service import SyncService


def _event_payload(event: dict[str, Any]) -> Any:
    payload = event.get("source_payload")
    if payload is not None:
        return payload
    return event


def handle_sync(event: dict[str, Any]) -> dict[str, Any]:
    """Execute hash-gated sync cycle from handler event payload.

    Event fields:
    - `source_payload` (optional): hash basis payload
    - `source_id` (optional): source identifier for state record
    - `state_file` (optional): custom state file path
    """
    source_id = str(event.get("source_id", "google-sheet:unknown")).strip()
    state_file = Path(str(event.get("state_file", "artifacts/tmp/hash_gate_state.json")))
    service = SyncService(state_file=state_file)
    result = service.run(source_payload=_event_payload(event), source_id=source_id)

    return {
        "status": "ok",
        "handler": "sync",
        "source_id": source_id,
        "sync_skipped": result.sync_skipped,
        "source_hash": result.source_hash,
        "previous_hash": result.previous_hash,
    }
