"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.app.bootstrap import build_app_context
from src.entrypoints.index_dispatcher import IndexDispatcher

APP_CONTEXT = build_app_context()
APP_CFG = APP_CONTEXT.cfg
APP_DEPS = APP_CONTEXT.deps
APP_TRIGGERS = dict(APP_CFG.runtime.triggers)
APP_DISPATCHER = IndexDispatcher(APP_CONTEXT, triggers=APP_TRIGGERS)

async def handler(event, _):
    """Yandex Cloud handler."""
    return await APP_DISPATCHER.handle(event, _)
