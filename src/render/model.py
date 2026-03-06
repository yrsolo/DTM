from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.snapshot_engine.model import Window


@dataclass(frozen=True)
class RenderRequest:
    window: Window | None = None
    statuses: list[str] | None = None


@dataclass(frozen=True)
class RenderCell:
    row: int
    col: int
    value: Any


@dataclass(frozen=True)
class RenderFormat:
    row: int
    col: int
    fmt: dict[str, Any]


@dataclass(frozen=True)
class RenderPlan:
    """Pure plan: values and formats to be written to target sheet."""

    values: list[RenderCell]
    formats: list[RenderFormat]
