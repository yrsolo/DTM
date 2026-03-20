"""Platform-owned helpers for queue runtime bootstrap."""

from __future__ import annotations

from src.commands.yandex_mq import YandexMessageQueueProducer
from src.contexts.attachments.public import (
    get_attach_task_file_job,
    get_cleanup_task_attachments_job,
    get_delete_task_attachment_job,
    get_generate_attachment_preview_job,
)
from src.contexts.reminders.public import get_send_reminders_job
from src.contexts.rendering.public import (
    get_render_designers_job,
    get_render_timeline_job,
)
from src.contexts.snapshot.public import get_update_snapshot_job
from src.contexts.telegram_interaction.public import get_group_query_reply_job
from src.worker.dispatcher import CommandDispatcher
from src.worker.status_store import S3JobStatusStore
from src.worker.worker import Worker


def _resolve_env_prefix(value: str, env_name: str) -> str:
    token = "{env}"
    cleaned = str(value or "").strip()
    if token in cleaned:
        return cleaned.replace(token, str(env_name or "").strip().lower() or "dev")
    return cleaned


def _resolve_queue_url(cfg) -> str:
    env_name = str(cfg.runtime.runtime.env_default or "").strip().lower()
    if env_name == "prod":
        return str(cfg.runtime.queue.prod_queue_url or "").strip()
    return str(cfg.runtime.queue.test_queue_url or "").strip()


def build_queue_runtime(ctx, deps: dict) -> dict:
    """Build queue producer/dispatcher/worker wiring for runtime mode."""

    cfg = ctx.cfg
    queue_cfg = cfg.runtime.queue
    if not bool(queue_cfg.enabled):
        return {}

    bucket = str(cfg.runtime.snapshot_engine.bucket).strip()
    endpoint_url = str(cfg.db.object_storage.get("endpoint_url_default", "")).strip() or None
    env_name = str(cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
    status_store = S3JobStatusStore(
        bucket=bucket,
        endpoint_url=endpoint_url,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
        status_prefix=_resolve_env_prefix(str(queue_cfg.status_prefix), env_name),
        latest_prefix=_resolve_env_prefix(str(queue_cfg.latest_prefix), env_name),
    )
    producer = YandexMessageQueueProducer(
        queue_url=_resolve_queue_url(cfg),
        endpoint_url=str(queue_cfg.endpoint_url or "").strip() or None,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
    )
    dispatcher = CommandDispatcher(
        update_snapshot_job=get_update_snapshot_job(ctx),
        send_reminders_job=get_send_reminders_job(ctx),
        render_timeline_job=get_render_timeline_job(ctx),
        render_designers_job=get_render_designers_job(ctx),
        group_query_reply_job=get_group_query_reply_job(ctx),
        attach_task_file_job=get_attach_task_file_job(ctx),
        delete_task_attachment_job=get_delete_task_attachment_job(ctx),
        cleanup_task_attachments_job=get_cleanup_task_attachments_job(ctx),
        generate_attachment_preview_job=get_generate_attachment_preview_job(ctx),
    )
    worker = Worker(
        status_store=status_store,
        dispatcher=dispatcher,
        logger=ctx.log,
        metrics=deps.get("metrics_client"),
        structured_logger=deps.get("structured_logger"),
        env_name=str(cfg.runtime.runtime.env_default),
    )
    return {
        "job_status_store": status_store,
        "command_queue_producer": producer,
        "command_dispatcher": dispatcher,
        "command_worker": worker,
    }
