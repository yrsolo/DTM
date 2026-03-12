"""Yandex Cloud entrypoint with thin top-level dispatch."""

from collections.abc import MutableMapping
from functools import lru_cache
from typing import Iterator

from src.app.bootstrap import build_app_context
from src.entrypoints.index_dispatcher import IndexDispatcher


class _LazyMappingProxy(MutableMapping[str, object]):
    def __init__(self, getter) -> None:
        self._getter = getter

    def _mapping(self) -> MutableMapping[str, object]:
        return self._getter()

    def __getitem__(self, key: str) -> object:
        return self._mapping()[key]

    def __setitem__(self, key: str, value: object) -> None:
        self._mapping()[key] = value

    def __delitem__(self, key: str) -> None:
        del self._mapping()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._mapping())

    def __len__(self) -> int:
        return len(self._mapping())


@lru_cache(maxsize=1)
def _get_app_context():
    return build_app_context()


@lru_cache(maxsize=1)
def _get_dispatcher() -> IndexDispatcher:
    """Build runtime dispatcher lazily inside the explicit entry boundary."""
    ctx = _get_app_context()
    return IndexDispatcher(ctx, triggers=APP_TRIGGERS)


APP_DEPS = _LazyMappingProxy(lambda: _get_app_context().deps)
APP_TRIGGERS = _LazyMappingProxy(lambda: _get_app_context().cfg.runtime.triggers)


async def handler(event, _):
    """Yandex Cloud handler."""
    return await _get_dispatcher().handle(event, _)
