"""Shared render contracts for sheet cell payloads."""

from dataclasses import dataclass
from typing import Any

OPTIONAL_FIELDS = (
    "note",
    "color",
    "text_color",
    "col",
    "row",
    "bold",
    "italic",
    "font_size",
)


@dataclass(slots=True)
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
        """Convert dataclass payload to sparse renderer cell dict."""

        payload: dict[str, Any] = {}
        if self.value is not None:
            payload["value"] = self.value
        for field_name in OPTIONAL_FIELDS:
            field_value = getattr(self, field_name)
            if field_value is not None:
                payload[field_name] = field_value
        return payload
