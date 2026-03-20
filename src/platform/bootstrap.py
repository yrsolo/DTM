"""Lazy runtime bootstrap helpers for the target platform layer."""

from __future__ import annotations

from src.app.bootstrap import build_app_context
from src.entrypoints.http.http_shell import HttpShell
from src.entrypoints.queue.worker_shell import WorkerShell
from src.entrypoints.runtime.runtime_shell import RuntimeShell
from src.entrypoints.triggers.trigger_shell import TriggerShell


_APP_CONTEXT = None
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


def get_trigger_modes():
    """Return the mutable trigger mapping through the runtime boundary."""

    return get_app_context().cfg.runtime.triggers


def get_runtime_deps():
    """Return the mutable runtime dependency bag through the platform boundary."""

    return get_app_context().deps


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
