"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.entrypoint.handler import handle as handle_entrypoint
from src.platform.bootstrap import (
    APP_DEPS,
    APP_TRIGGERS,
    get_app_context,
    get_http_shell,
    get_trigger_shell,
    get_worker_shell,
)


def _get_app_context():
    return get_app_context()


def _get_http_shell():
    return get_http_shell()


def _get_worker_shell():
    return get_worker_shell()


def _get_trigger_shell():
    return get_trigger_shell()


async def handler(event, _):
    """Yandex Cloud handler."""
    return await handle_entrypoint(
        event,
        _,
        get_http_shell=_get_http_shell,
        get_worker_shell=_get_worker_shell,
        get_trigger_shell=_get_trigger_shell,
        triggers=APP_TRIGGERS,
        telegram_webhook_path=_get_app_context().cfg.runtime.telegram.webhook_path,
    )
