"""Runtime-owned helpers for default frontend cache invalidation."""

from __future__ import annotations

from typing import Any


def default_frontend_cache_key(*, route_class: str, access_mode: str) -> str:
    return f"frontend_v2/default/{route_class}/{access_mode}"


def default_frontend_cache_keys() -> list[str]:
    keys: list[str] = []
    for route_class in ("api", "bff"):
        for access_mode in ("masked", "full"):
            keys.append(default_frontend_cache_key(route_class=route_class, access_mode=access_mode))
    return keys


def invalidate_default_frontend_cache_store(cache_store: Any) -> None:
    if cache_store is None:
        return
    for cache_key in default_frontend_cache_keys():
        cache_store.delete(cache_key)
