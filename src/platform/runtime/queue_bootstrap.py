"""Platform-owned helpers for queue runtime bootstrap."""

from __future__ import annotations

from src.commands.yandex_mq import YandexMessageQueueProducer
from src.jobs.attach_task_file_job import AttachTaskFileJob
from src.jobs.cleanup_task_attachments_job import CleanupTaskAttachmentsJob
from src.jobs.delete_task_attachment_job import DeleteTaskAttachmentJob
from src.jobs.generate_attachment_preview_job import GenerateAttachmentPreviewJob
from src.jobs.group_query_reply_job import GroupQueryReplyJob
from src.jobs.render_designers_job import RenderDesignersJob
from src.jobs.render_timeline_job import RenderTimelineJob
from src.jobs.send_reminders_job import SendRemindersJob
from src.jobs.update_snapshot_job import UpdateSnapshotJob
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
        update_snapshot_job=UpdateSnapshotJob(ctx),
        send_reminders_job=SendRemindersJob(ctx),
        render_timeline_job=RenderTimelineJob(ctx),
        render_designers_job=RenderDesignersJob(ctx),
        group_query_reply_job=GroupQueryReplyJob(ctx),
        attach_task_file_job=AttachTaskFileJob(ctx),
        delete_task_attachment_job=DeleteTaskAttachmentJob(ctx),
        cleanup_task_attachments_job=CleanupTaskAttachmentsJob(ctx),
        generate_attachment_preview_job=GenerateAttachmentPreviewJob(ctx),
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
