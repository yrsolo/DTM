"""Local builder placeholder for the attachments context."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AttachmentsModule:
    """Context-local module placeholder used during staged migration."""

    name: str = "attachments"


def get_module() -> AttachmentsModule:
    """Return a minimal local module instance until real wiring moves here."""

    return AttachmentsModule()

