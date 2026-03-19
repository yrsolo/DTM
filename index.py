"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.app.bootstrap import build_app_context
from src.entrypoint.handler import handle as handle_entrypoint
from src.entrypoints.index_dispatcher import IndexDispatcher


class _LazyMapping:
    """Lazy mutable mapping used only to preserve test/runtime compatibility."""

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


def _get_app_context():
    global _APP_CONTEXT
    if _APP_CONTEXT is None:
        _APP_CONTEXT = build_app_context()
    return _APP_CONTEXT


def _get_triggers():
    return _get_app_context().cfg.runtime.triggers


def _get_deps():
    return _get_app_context().deps


def _get_dispatcher() -> IndexDispatcher:
    """Build runtime dispatcher lazily inside the explicit entry boundary."""
    global _APP_DISPATCHER
    if _APP_DISPATCHER is None:
        ctx = _get_app_context()
        _APP_DISPATCHER = IndexDispatcher(ctx, triggers=APP_TRIGGERS)
    return _APP_DISPATCHER


APP_DEPS = _LazyMapping(_get_deps)
APP_TRIGGERS = _LazyMapping(_get_triggers)


async def handler(event, _):
    """Yandex Cloud handler."""
    return await handle_entrypoint(
        event,
        _,
        get_dispatcher=_get_dispatcher,
        triggers=APP_TRIGGERS,
        telegram_webhook_path=_get_app_context().cfg.runtime.telegram.webhook_path,
    )
