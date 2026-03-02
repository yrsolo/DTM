"""Source hash gate for incremental sync runs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class HashGateDecision:
    """Hash gate output for sync orchestration."""

    source_hash: str
    previous_hash: str | None
    should_sync: bool


def compute_source_hash(payload: Any) -> str:
    """Compute deterministic hash from source-range payload only."""
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def load_last_hash(state_file: str | Path) -> str | None:
    """Load previously stored source hash."""
    path = Path(state_file)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return str(data.get("source_hash", "")).strip() or None


def save_last_hash(state_file: str | Path, source_id: str, source_hash: str) -> None:
    """Persist source hash decision state."""
    path = Path(state_file)
    payload = {
        "source_id": source_id,
        "source_hash": source_hash,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def evaluate_hash_gate(source_payload: Any, state_file: str | Path) -> HashGateDecision:
    """Decide whether sync should execute."""
    source_hash = compute_source_hash(source_payload)
    previous_hash = load_last_hash(state_file)
    return HashGateDecision(
        source_hash=source_hash,
        previous_hash=previous_hash,
        should_sync=(source_hash != previous_hash),
    )

