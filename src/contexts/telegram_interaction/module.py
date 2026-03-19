"""Local builder placeholder for the telegram interaction context."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelegramInteractionModule:
    """Context-local module placeholder used during staged migration."""

    name: str = "telegram_interaction"


def get_module() -> TelegramInteractionModule:
    """Return a minimal local module instance until real wiring moves here."""

    return TelegramInteractionModule()

