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
    note: str | None = None
    color: str | None = None
    text_color: str | None = None
    bold: bool | None = None
    italic: bool | None = None
    font_size: int | None = None


@dataclass(frozen=True)
class RenderBorder:
    worksheet_range: str
    side: str = "left"
    width: int = 3
    color: str = "#5FAD56"


@dataclass(frozen=True)
class RenderPlan:
    """Pure plan: values and borders to be written to target sheet."""

    values: list[RenderCell]
    borders: list[RenderBorder]
    warnings: list[str] | None = None


@dataclass(frozen=True)
class RenderApplyResult:
    applied: bool
    rows_written: int
    cells_written: int
    target_spreadsheet: str
    target_worksheet: str
    warnings: list[str]
