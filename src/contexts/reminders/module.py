"""Local builder placeholder for the reminders context."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RemindersModule:
    """Context-local module placeholder used during staged migration."""

    name: str = "reminders"


def get_module() -> RemindersModule:
    """Return a minimal local module instance until real wiring moves here."""

    return RemindersModule()

