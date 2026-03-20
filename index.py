"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.entrypoint.handler import handle as handle_entrypoint
from src.platform.bootstrap import (
    APP_DEPS,
    APP_TRIGGERS,
    get_app_context,
    get_http_shell,
    get_telegram_webhook_path,
    get_trigger_shell,
    get_worker_shell,
)


def _get_app_context():
    return get_app_context()


async def handler(event, _):
    """Yandex Cloud handler."""
    return await handle_entrypoint(
        event,
        _,
        get_http_shell=get_http_shell,
        get_worker_shell=get_worker_shell,
        get_trigger_shell=get_trigger_shell,
        get_telegram_webhook_path=get_telegram_webhook_path,
        triggers=APP_TRIGGERS,
    )
