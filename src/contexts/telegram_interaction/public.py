"""Public facade for the telegram interaction context."""

from __future__ import annotations

from .module import get_module


def get_public_api():
    """Return the local module placeholder without leaking internals."""

    return get_module()

