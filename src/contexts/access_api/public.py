"""Public primary read-model entry for the access API context."""

from __future__ import annotations

from .module import get_module


def get_primary_browser_read_model(ctx):
    """Return the primary browser read model owned by access_api."""

    return get_module().primary_browser_read_model(ctx)
