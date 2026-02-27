"""Shared render contracts for sheet cell payloads."""

from dataclasses import dataclass
from typing import Any


@dataclass
class RenderCell:
    """Typed payload used by sheet renderers before calling update_cell."""

    value: Any = None
    note: str | None = None
    color: Any = None
    text_color: Any = None
    col: int | None = None
    row: int | None = None
    bold: bool | None = None
    italic: bool | None = None
    font_size: int | None = None

    def to_cell_data(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.value is not None:
            payload["value"] = self.value
        if self.note is not None:
            payload["note"] = self.note
        if self.color is not None:
            payload["color"] = self.color
        if self.text_color is not None:
            payload["text_color"] = self.text_color
        if self.col is not None:
            payload["col"] = self.col
        if self.row is not None:
            payload["row"] = self.row
        if self.bold is not None:
            payload["bold"] = self.bold
        if self.italic is not None:
            payload["italic"] = self.italic
        if self.font_size is not None:
            payload["font_size"] = self.font_size
        return payload
