"""Local builder placeholder for the rendering context."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RenderingModule:
    """Context-local module placeholder used during staged migration."""

    name: str = "rendering"


def get_module() -> RenderingModule:
    """Return a minimal local module instance until real wiring moves here."""

    return RenderingModule()

