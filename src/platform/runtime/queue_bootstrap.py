"""Platform-owned helpers for queue runtime bootstrap."""

from __future__ import annotations

from src.platform.runtime.commands.yandex_mq import YandexMessageQueueProducer
from src.contexts.attachments.public import get_command_handlers as get_attachment_command_handlers
from src.contexts.reminders.public import get_command_handlers as get_reminder_command_handlers
from src.contexts.rendering.public import get_command_handlers as get_rendering_command_handlers
from src.contexts.snapshot.public import get_command_handlers as get_snapshot_command_handlers
from src.contexts.telegram_interaction.public import get_command_handlers as get_telegram_command_handlers
from src.platform.runtime.command_runtime import CommandRuntime
from src.platform.runtime.worker.dispatcher import CommandDispatcher
from src.platform.runtime.worker.status_store import S3JobStatusStore
from src.platform.runtime.worker.worker import Worker


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


def _build_command_handlers(ctx) -> dict[str, object]:
    handlers: dict[str, object] = {}
    handlers.update(get_snapshot_command_handlers(ctx))
    handlers.update(get_reminder_command_handlers(ctx))
    handlers.update(get_rendering_command_handlers(ctx))
    handlers.update(get_telegram_command_handlers(ctx))
    handlers.update(get_attachment_command_handlers(ctx))
    return handlers


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
    dispatcher = CommandDispatcher(_build_command_handlers(ctx))
    worker = Worker(
        status_store=status_store,
        dispatcher=dispatcher,
        logger=ctx.log,
        metrics=deps.get("metrics_client"),
        structured_logger=deps.get("structured_logger"),
        env_name=str(cfg.runtime.runtime.env_default),
    )
    command_runtime = CommandRuntime(
        producer=producer,
        status_store=status_store,
        worker=worker,
    )
    return {
        "command_runtime": command_runtime,
        "job_status_store": status_store,
        "command_queue_producer": producer,
        "command_dispatcher": dispatcher,
        "command_worker": worker,
    }

