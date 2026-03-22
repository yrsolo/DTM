"""Public browser-read entry for the access API context."""

from __future__ import annotations

from .module import get_module


def get_primary_browser_read_api(ctx):
    """Return the primary browser read API owned by access_api."""

    return get_module().primary_browser_read_api(ctx)
