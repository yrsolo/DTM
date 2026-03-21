"""Task source contracts owned by the snapshot adapters contour."""

from __future__ import annotations

from typing import Any, Protocol


class TaskSource(Protocol):
    """Source of snapshots and normalized task entities for sync pipelines."""

    @property
    def source_id(self) -> str:
        """Stable source identifier used by sync_state/readmodel."""

    @property
    def source_sheet_name(self) -> str:
        """Human-readable source spreadsheet name."""

    def read_snapshot(self, worksheet_range: str) -> dict[str, object]:
        """Read source snapshot values+colors for the requested range."""

    def build_tasks_from_snapshot(self, full_snapshot: dict[str, object]) -> list[Any]:
        """Build normalized task entities from full snapshot."""
