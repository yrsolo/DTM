"""Public facade for the reminders context."""

from __future__ import annotations

from .module import get_module


def get_public_api():
    """Return the local module without leaking internal package layout."""

    return get_module()


def get_snapshot_engine(ctx):
    return get_module().build_snapshot_engine(ctx)


def get_usecase(snapshot_engine):
    return get_module().build_usecase(snapshot_engine)


def get_formatter(ctx):
    return get_module().build_formatter(ctx)


def get_sender(ctx):
    return get_module().build_sender(ctx)


def get_enhancer(ctx, *, mock_external: bool):
    return get_module().build_enhancer(ctx, mock_external=mock_external)


def get_today_in_runtime_timezone(ctx):
    return get_module().today_in_runtime_timezone(ctx)


def get_job_runner(**kwargs):
    return get_module().build_job_runner(**kwargs)


def get_send_reminders_job(ctx):
    """Return the owning reminder job runner."""

    from src.jobs.send_reminders_job import SendRemindersJob

    return SendRemindersJob(ctx)
