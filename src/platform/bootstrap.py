"""Lazy runtime bootstrap helpers for the target platform layer."""

from __future__ import annotations

from src.app.bootstrap import build_app_context
from src.entrypoints.http.http_shell import HttpShell
from src.entrypoints.index_dispatcher import IndexDispatcher
from src.entrypoints.queue.worker_shell import WorkerShell
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_shell import TriggerShell


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
_RUNTIME_SHELL = None
_HTTP_SHELL = None
_WORKER_SHELL = None
_TRIGGER_SHELL = None


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


def get_runtime_shell() -> RuntimeShell:
    """Build the shared runtime shell lazily for the top entry path."""

    global _RUNTIME_SHELL
    if _RUNTIME_SHELL is None:
        _RUNTIME_SHELL = RuntimeShell(get_app_context())
    return _RUNTIME_SHELL


def get_http_shell() -> HttpShell:
    """Build the shared HTTP shell lazily for the top entry path."""

    global _HTTP_SHELL
    if _HTTP_SHELL is None:
        _HTTP_SHELL = HttpShell(get_app_context(), runtime_shell=get_runtime_shell())
    return _HTTP_SHELL


def get_worker_shell() -> WorkerShell:
    """Build the shared worker shell lazily for the top entry path."""

    global _WORKER_SHELL
    if _WORKER_SHELL is None:
        _WORKER_SHELL = WorkerShell(get_app_context())
    return _WORKER_SHELL


def get_trigger_shell() -> TriggerShell:
    """Build the shared trigger shell lazily for the top entry path."""

    global _TRIGGER_SHELL
    if _TRIGGER_SHELL is None:
        _TRIGGER_SHELL = TriggerShell(get_app_context(), runtime_shell=get_runtime_shell())
    return _TRIGGER_SHELL


APP_DEPS = LazyMapping(get_deps)
APP_TRIGGERS = LazyMapping(get_triggers)
