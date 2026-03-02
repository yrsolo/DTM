"""Domain data contracts for migration stages M1-M3."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(slots=True)
class TaskRaw:
    """Raw task row from source sheet before normalization."""

    source_file_id: str
    source_sheet_name: str
    source_row_id: str
    title_raw: str
    designer_raw: str = ""
    timings_raw: str = ""
    stages_raw: str = ""
    status_raw: str = ""
    updated_at_source: str | None = None
    raw_hash_basis: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class StageNormalized:
    """Normalized stage entity parsed from raw stage/timing text."""

    task_id: str
    idx: int
    type: str
    planned_at: date | None
    fact_at: date | None
    status: str
    raw_text: str
    inference_rule: str = ""
    confidence: float = 1.0


@dataclass(slots=True)
class TaskNormalized:
    """Normalized task with parsed stages and derived fields."""

    task_id: str
    title: str
    project: str | None
    designer_id: str | None
    status: str
    stages: list[StageNormalized]
    next_due_at: date | None
    raw_fields: dict[str, str] = field(default_factory=dict)
    inference: dict[str, Any] = field(default_factory=dict)

