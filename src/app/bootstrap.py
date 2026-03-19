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
)
from src.app.context import AppContext
from src.config.loader import load_config
from src.infra.doc_preview_converter import DocPreviewConverter
from src.observability import (
    NoopMetricsClient,
    StdoutJsonLogger,
)
from src.platform.infra.monitoring_bootstrap import build_metrics_dependencies
from src.platform.runtime.queue_bootstrap import build_queue_runtime
from src.services.mappers.task_payload_mapper import TaskPayloadMapper


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
        "yc_sa_json_credentials": YC_SA_JSON_CREDENTIALS,
        "yc_sa_key_file": YC_SA_KEY_FILE,
        "legacy_blob_write": LEGACY_BLOB_WRITE,
        "migration_store_file": MIGRATION_STORE_FILE,
        "write_legacy_milestones": WRITE_LEGACY_MILESTONES,
        "task_payload_mapper": TaskPayloadMapper(),
        "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID", "").strip(),
        "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY", "").strip(),
        "openai_token": os.getenv("OPENAI_TOKEN", "").strip(),
        "org_token": os.getenv("ORG_TOKEN", "").strip(),
        "proxy_url": os.getenv("PROXY_URL", "").strip(),
        "google_llm_api_key": os.getenv("GOOGLE_LLM_API_KEY", "").strip(),
        "yandex_llm_api_key": os.getenv("YANDEX_LLM_API_KEY", "").strip(),
        "tg_webhook_secret_token": os.getenv("TG_WEBHOOK_SECRET_TOKEN", "").strip(),
        "browser_auth_proxy_secret": os.getenv("BROWSER_AUTH_PROXY_SECRET", "").strip(),
        "grafana_api_token": os.getenv("GRAFANA_API_TOKEN", "").strip() or os.getenv("GRAFANA_TOKEN", "").strip(),
        "yandex_prometheus_api_key": os.getenv("YANDEX_PROMETHEUS_API_KEY", "").strip()
        or os.getenv("YMP_API_KEY", "").strip(),
        "metrics_client": NoopMetricsClient(),
        "metrics_sink": NoopMetricsClient(),
        "structured_logger": structured_logger,
    }
    doc_preview_converter_url = os.getenv("DOC_PREVIEW_CONVERTER_URL", "").strip()
    doc_preview_converter_token = os.getenv("DOC_PREVIEW_CONVERTER_SHARED_TOKEN", "").strip()
    if doc_preview_converter_url:
        deps["doc_preview_converter"] = DocPreviewConverter(
            base_url=doc_preview_converter_url,
            shared_token=doc_preview_converter_token,
        )
    ctx = AppContext(cfg=cfg, deps=deps)
    deps.update(build_metrics_dependencies(ctx, deps, structured_logger=structured_logger))
    deps.update(build_queue_runtime(ctx, deps))
    return ctx
