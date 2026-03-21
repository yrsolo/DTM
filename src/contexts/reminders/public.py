"""Public facade for the reminders context."""

from __future__ import annotations

from src.platform.runtime.commands.types import SEND_REMINDERS

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_read_api(ctx):
    return get_module().snapshot_read_api(ctx)


def get_usecase(snapshot_read):
    return get_module().usecase(snapshot_read)


def get_formatter(ctx):
    return get_module().formatter(ctx)


def get_sender(ctx):
    return get_module().sender(ctx)


def get_enhancer(ctx, *, mock_external: bool):
    return get_module().enhancer(ctx, mock_external=mock_external)


def get_today_in_runtime_timezone(ctx):
    return get_module().today_in_runtime_timezone(ctx)


def get_job_runner(**kwargs):
    return get_module().job_runner(**kwargs)


def make_reminder_request(**kwargs):
    return get_module().request(**kwargs)


def get_send_reminders_job(ctx):
    """Return the owning reminder job runner."""

    from .internal.job_runner import SendRemindersJob

    return SendRemindersJob(ctx)


def get_command_handlers(ctx) -> dict[str, object]:
    """Return the reminders-owned queue command handlers."""

    return {SEND_REMINDERS: get_send_reminders_job(ctx)}

