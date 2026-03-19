"""Target runtime classification helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeClassification:
    """Minimal transport-level classification result."""

    source: str
    details: dict[str, Any] = field(default_factory=dict)


def classify_event(_event: Any) -> RuntimeClassification:
    """Import-safe placeholder until current event classification moves here."""

    return RuntimeClassification(source="unknown")

