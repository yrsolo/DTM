"""Yandex Cloud entrypoint with thin top-level dispatch."""

from src.entrypoints.root.handler import handle as handle_entrypoint
from src.platform.shell import (
    handle_http_event,
    handle_queue_event,
    handle_trigger_event,
    get_telegram_webhook_path,
    get_trigger_modes,
)


async def handler(event, _):
    """Yandex Cloud handler."""
    return await handle_entrypoint(
        event,
        _,
        handle_http_event=handle_http_event,
        handle_queue_event=handle_queue_event,
        handle_trigger_event=handle_trigger_event,
        get_telegram_webhook_path=get_telegram_webhook_path,
        get_trigger_modes=get_trigger_modes,
    )
