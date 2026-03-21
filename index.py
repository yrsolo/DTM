"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.entrypoints.root.handler import handle as handle_entrypoint
from src.platform.bootstrap import (
    get_http_shell,
    get_telegram_webhook_path,
    get_trigger_modes,
    get_trigger_shell,
    get_worker_shell,
)


async def handler(event, _):
    """Yandex Cloud handler."""
    return await handle_entrypoint(
        event,
        _,
        get_http_shell=get_http_shell,
        get_worker_shell=get_worker_shell,
        get_trigger_shell=get_trigger_shell,
        get_telegram_webhook_path=get_telegram_webhook_path,
        get_trigger_modes=get_trigger_modes,
    )
