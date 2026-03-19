"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.entrypoint.handler import handle as handle_entrypoint
from src.platform.bootstrap import APP_TRIGGERS, get_app_context, get_dispatcher


def _get_app_context():
    return get_app_context()


def _get_dispatcher():
    return get_dispatcher()


async def handler(event, _):
    """Yandex Cloud handler."""
    return await handle_entrypoint(
        event,
        _,
        get_dispatcher=_get_dispatcher,
        triggers=APP_TRIGGERS,
        telegram_webhook_path=_get_app_context().cfg.runtime.telegram.webhook_path,
    )
