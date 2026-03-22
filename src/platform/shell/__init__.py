"""Platform-owned lazy shell and top-entry runtime seams."""

from __future__ import annotations

from src.entrypoints.http.http_shell import HttpShell
from src.entrypoints.queue.worker_shell import WorkerShell
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_shell import TriggerShell
from src.platform.bootstrap import get_app_context

_RUNTIME_SHELL = None
_HTTP_SHELL = None
_WORKER_SHELL = None
_TRIGGER_SHELL = None


def get_trigger_modes():
    """Return the mutable trigger mapping through the runtime shell boundary."""

    return get_app_context().cfg.runtime.triggers


def get_telegram_webhook_path() -> str:
    """Expose the configured Telegram webhook path without widening the top path."""

    return str(get_app_context().cfg.runtime.telegram.webhook_path or "/telegram")


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


async def handle_http_event(event, payload, is_http_event):
    """Handle an HTTP-facing top-path event through the platform shell boundary."""

    return await get_http_shell().handle(event, payload, is_http_event)


async def handle_queue_event(event):
    """Handle a queue event through the platform shell boundary."""

    return await get_worker_shell().handle_queue_event(event)


async def handle_trigger_event(trigger_mode: str, event):
    """Handle a named trigger event through the platform shell boundary."""

    return await get_trigger_shell().handle_trigger(trigger_mode, event)


__all__ = [
    "get_http_shell",
    "get_runtime_shell",
    "get_telegram_webhook_path",
    "get_trigger_modes",
    "get_trigger_shell",
    "get_worker_shell",
    "handle_http_event",
    "handle_queue_event",
    "handle_trigger_event",
]

