"""Module surface for the access API context."""

from __future__ import annotations

from dataclasses import dataclass

from .application.browser_read_api import PrimaryBrowserReadApi


@dataclass(frozen=True, slots=True)
class AccessApiModule:
    """Own the primary browser read surface for the active runtime."""

    name: str = "access_api"

    def primary_browser_read_api(self, ctx):
        return PrimaryBrowserReadApi(ctx)


def get_module() -> AccessApiModule:
    """Return the canonical module surface for the access API context."""

    return AccessApiModule()
