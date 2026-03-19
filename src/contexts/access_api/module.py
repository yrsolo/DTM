"""Local builder placeholder for the access API context."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccessApiModule:
    """Context-local module placeholder used during staged migration."""

    name: str = "access_api"


def get_module() -> AccessApiModule:
    """Return a minimal local module instance until real wiring moves here."""

    return AccessApiModule()

