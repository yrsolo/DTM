"""Public facade for the access API context."""

from __future__ import annotations

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_browser_read_api(ctx):
    """Return the browser-facing read API owned by access_api."""

    return get_module().browser_read_api(ctx)
