"""Application bootstrap for config-first runtime wiring."""

from __future__ import annotations

import os

from config import (
    DEFAULT_CHAT_ID,
    KEY_JSON,
    LEGACY_BLOB_WRITE,
    MIGRATION_STORE_FILE,
    SHEET_INFO,
    TG,
    TG_BOT_USERNAME,
    WRITE_LEGACY_MILESTONES,
    YC_SA_JSON_CREDENTIALS,
    YC_SA_KEY_FILE,
    YDB_DATABASE,
    YDB_ENDPOINT,
    YDB_MIGRATE_ON_START,
)
from src.app.context import AppContext
from src.config.loader import load_config
from src.infra.yc_iam import get_iam_token
from src.observability import NoopMetricsClient, StdoutJsonLogger, YandexMonitoringMetricsClient
from src.services.mappers.task_payload_mapper import TaskPayloadMapper


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


def build_app_context() -> AppContext:
    """Load YAML config and return bootstrap context.

    Dependency wiring is intentionally lightweight in CAM-CONFIG-REFORM-V0.
    Full service/repository composition is planned for subsequent campaigns.
    """

    cfg = load_config()
    structured_logger = StdoutJsonLogger()
    deps = {
        "key_json": KEY_JSON,
        "sheet_info": SHEET_INFO,
        "tg_bot_token": TG,
        "tg_bot_username": TG_BOT_USERNAME,
        "default_chat_id": DEFAULT_CHAT_ID,
        "ydb_endpoint": YDB_ENDPOINT,
        "ydb_database": YDB_DATABASE,
        "ydb_sa_json_credentials": YC_SA_JSON_CREDENTIALS,
        "ydb_sa_key_file": YC_SA_KEY_FILE,
        "legacy_blob_write": LEGACY_BLOB_WRITE,
        "migration_store_file": MIGRATION_STORE_FILE,
        "write_legacy_milestones": WRITE_LEGACY_MILESTONES,
        "ydb_migrate_on_start": YDB_MIGRATE_ON_START,
        "task_payload_mapper": TaskPayloadMapper(),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "").strip(),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "").strip(),
        "openai_token": os.getenv("OPENAI_TOKEN", "").strip(),
        "org_token": os.getenv("ORG_TOKEN", "").strip(),
        "proxy_url": os.getenv("PROXY_URL", "").strip(),
        "google_llm_api_key": os.getenv("GOOGLE_LLM_API_KEY", "").strip(),
        "yandex_llm_api_key": os.getenv("YANDEX_LLM_API_KEY", "").strip(),
        "tg_webhook_secret_token": os.getenv("TG_WEBHOOK_SECRET_TOKEN", "").strip(),
        "metrics_client": NoopMetricsClient(),
        "structured_logger": structured_logger,
    }
    ctx = AppContext(cfg=cfg, deps=deps)
    monitoring_cfg = cfg.runtime.monitoring
    if bool(monitoring_cfg.enabled) and str(monitoring_cfg.backend).strip().lower() == "yandex_monitoring":
        folder_id = str(monitoring_cfg.folder_id).strip() or str(cfg.deploy.yandex_cloud.folder_id).strip()

        def _iam_token_provider() -> str:
            return get_iam_token(
                deps.get("ydb_sa_json_credentials"),
                deps.get("ydb_sa_key_file"),
                timeout_seconds=4.0,
            )

        deps["metrics_client"] = YandexMonitoringMetricsClient(
            folder_id=folder_id,
            iam_token_provider=_iam_token_provider,
            logger=structured_logger,
            endpoint_write=str(monitoring_cfg.endpoint_write).strip(),
            service_label=str(monitoring_cfg.service).strip() or "dtm",
            namespace=str(monitoring_cfg.namespace).strip() or "dtm",
        )
    queue_cfg = cfg.runtime.queue
    if bool(queue_cfg.enabled):
        from src.commands.yandex_mq import YandexMessageQueueProducer
        from src.jobs.render_designers_job import RenderDesignersJob
        from src.jobs.render_timeline_job import RenderTimelineJob
        from src.jobs.send_reminders_job import SendRemindersJob
        from src.jobs.update_snapshot_job import UpdateSnapshotJob
        from src.jobs.group_query_reply_job import GroupQueryReplyJob
        from src.jobs.attach_task_file_job import AttachTaskFileJob
        from src.worker.dispatcher import CommandDispatcher
        from src.worker.status_store import S3JobStatusStore
        from src.worker.worker import Worker

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
        )
        deps["job_status_store"] = status_store
        deps["command_queue_producer"] = producer
        deps["command_dispatcher"] = dispatcher
        deps["command_worker"] = Worker(
            status_store=status_store,
            dispatcher=dispatcher,
            logger=ctx.log,
            metrics=deps.get("metrics_client"),
            structured_logger=deps.get("structured_logger"),
            env_name=str(cfg.runtime.runtime.env_default),
        )
    return ctx
