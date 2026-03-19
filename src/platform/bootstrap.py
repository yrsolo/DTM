"""Lazy runtime bootstrap helpers for the target platform layer."""

from __future__ import annotations

from src.app.bootstrap import build_app_context
from src.entrypoints.index_dispatcher import IndexDispatcher


class LazyMapping:
    """Lazy mutable mapping kept for runtime/test compatibility."""

    def __init__(self, getter):
        self._getter = getter

    def _mapping(self):
        return self._getter()

    def __getitem__(self, key):
        return self._mapping()[key]

    def __setitem__(self, key, value) -> None:
        self._mapping()[key] = value

    def __delitem__(self, key) -> None:
        del self._mapping()[key]

    def __iter__(self):
        return iter(self._mapping())

    def __len__(self) -> int:
        return len(self._mapping())

    def get(self, key, default=None):
        return self._mapping().get(key, default)

    def keys(self):
        return self._mapping().keys()

    def items(self):
        return self._mapping().items()

    def values(self):
        return self._mapping().values()

    def clear(self) -> None:
        self._mapping().clear()

    def update(self, *args, **kwargs) -> None:
        self._mapping().update(*args, **kwargs)


_APP_CONTEXT = None
_APP_DISPATCHER = None


def get_app_context():
    """Build the shared runtime context lazily inside the entry boundary."""

    global _APP_CONTEXT
    if _APP_CONTEXT is None:
        _APP_CONTEXT = build_app_context()
    return _APP_CONTEXT


def get_triggers():
    """Expose the mutable trigger mapping through the lazy app context."""

    return get_app_context().cfg.runtime.triggers


def get_deps():
    """Expose mutable deps through the lazy app context."""

    return get_app_context().deps


def get_dispatcher() -> IndexDispatcher:
    """Build the transitional dispatcher lazily inside the entry boundary."""

    global _APP_DISPATCHER
    if _APP_DISPATCHER is None:
        ctx = get_app_context()
        _APP_DISPATCHER = IndexDispatcher(ctx, triggers=APP_TRIGGERS)
    return _APP_DISPATCHER


APP_DEPS = LazyMapping(get_deps)
APP_TRIGGERS = LazyMapping(get_triggers)

