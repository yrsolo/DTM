"""Module surface for the access API context."""

from __future__ import annotations

from dataclasses import dataclass

from .application.primary_browser_read_model import PrimaryBrowserReadModel


@dataclass(frozen=True, slots=True)
class AccessApiModule:
    """Own the primary browser read-model surface for the active runtime."""

    name: str = "access_api"

    def primary_browser_read_model(self, ctx):
        return PrimaryBrowserReadModel(ctx)


def get_module() -> AccessApiModule:
    """Return the canonical module surface for the access API context."""

    return AccessApiModule()
