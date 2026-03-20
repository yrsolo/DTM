"""Application bootstrap for config-first runtime wiring."""

from __future__ import annotations

import base64
import os
from pathlib import Path
import tempfile

from dotenv import load_dotenv

from src.app.context import AppContext
from src.config.loader import load_config
from src.observability import (
    NoopMetricsClient,
    StdoutJsonLogger,
)
from src.platform.infra.monitoring_bootstrap import build_metrics_dependencies
from src.platform.runtime.queue_bootstrap import build_queue_runtime


def _load_runtime_env_files() -> str:
    """Load base .env and optional profile-specific file for bootstrap/runtime."""

    load_dotenv()
    runtime_env = str(os.getenv("ENV", "dev")).strip().lower() or "dev"
    profile_path = Path(f".env.{runtime_env}")
    if profile_path.exists():
        load_dotenv(dotenv_path=profile_path, override=True)
    return runtime_env


def _resolve_google_key_json_path() -> str:
    """Resolve Google service-account key path for active bootstrap."""

    key_path = str(os.getenv("GOOGLE_KEY_JSON_PATH", "")).strip()
    if key_path:
        return key_path

    key_b64 = str(os.getenv("GOOGLE_KEY_JSON_B64", "")).strip()
    key_text = str(os.getenv("GOOGLE_KEY_JSON", "")).strip()
    if key_b64:
        key_text = base64.b64decode(key_b64).decode("utf-8")

    if key_text:
        tmp_file = Path(tempfile.gettempdir()) / "dtm_google_key.json"
        tmp_file.write_text(key_text, encoding="utf-8")
        return str(tmp_file)

    return "key/google_key_poised-backbone-191400-4e9fc454915f.json"


def _resolve_target_sheet_name(cfg) -> str:
    """Resolve target spreadsheet name with ENV-sensitive fallback."""

    target_sheet_name = str(os.getenv("TARGET_SHEET_NAME", "")).strip()
    if target_sheet_name:
        return target_sheet_name
    env_name = str(cfg.runtime.runtime.env_default or "").strip().lower()
    default_key = "target_sheet_name_prod_default" if env_name == "prod" else "target_sheet_name_default"
    tables_cfg = getattr(cfg, "tables", None)
    google_sheets_cfg = dict(getattr(tables_cfg, "google_sheets", {}) or {})
    return str(
        google_sheets_cfg.get(default_key, google_sheets_cfg.get("target_sheet_name_default", ""))
    ).strip()


def _build_base_bootstrap_deps(cfg, structured_logger) -> dict[str, object]:
    """Build the base app deps without relying on legacy config.constants."""

    tables_cfg = getattr(cfg, "tables", None)
    llm_cfg = getattr(cfg, "llm", None)
    google_sheets_cfg = dict(getattr(tables_cfg, "google_sheets", {}) or {})
    sheet_names = dict(getattr(tables_cfg, "sheet_names", {}) or {})
    assistant_cfg = dict(getattr(llm_cfg, "assistant", {}) or {})
    source_sheet_name = str(
        os.getenv("SOURCE_SHEET_NAME", str(google_sheets_cfg.get("source_sheet_name_default", "")))
    ).strip()
    if source_sheet_name and tables_cfg is not None:
        google_sheets_cfg["source_sheet_name_default"] = source_sheet_name
        tables_cfg.google_sheets = google_sheets_cfg

    return {
        "key_json": _resolve_google_key_json_path(),
        "sheet_info": {
            "spreadsheet_name": _resolve_target_sheet_name(cfg),
            "sheet_names": sheet_names,
        },
        "tg_bot_token": str(os.getenv("TG_TOKEN", "")).strip(),
        "tg_bot_username": str(os.getenv("TG_BOT_USERNAME", "")).strip(),
        "default_chat_id": str(
            os.getenv("DEFAULT_CHAT_ID", str(assistant_cfg.get("default_chat_id_default", "-4083724311")))
        ).strip(),
        "yc_sa_json_credentials": str(os.getenv("YC_SA_JSON_CREDENTIALS", "")).strip(),
        "yc_sa_key_file": str(os.getenv("YC_SA_KEY_FILE", "")).strip(),
        "legacy_blob_write": str(os.getenv("LEGACY_BLOB_WRITE", "")).strip().lower()
        in {"1", "true", "yes"},
        "migration_store_file": str(os.getenv("MIGRATION_STORE_FILE", "artifacts/tmp/normalized_store.json")).strip(),
        "write_legacy_milestones": str(os.getenv("WRITE_LEGACY_MILESTONES", "")).strip().lower()
        in {"1", "true", "yes"},
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
        "doc_preview_converter_url": os.getenv("DOC_PREVIEW_CONVERTER_URL", "").strip(),
        "doc_preview_converter_shared_token": os.getenv("DOC_PREVIEW_CONVERTER_SHARED_TOKEN", "").strip(),
        "metrics_client": NoopMetricsClient(),
        "metrics_sink": NoopMetricsClient(),
        "structured_logger": structured_logger,
    }


def build_app_context() -> AppContext:
    """Load YAML config and return bootstrap context.

    Dependency wiring is intentionally lightweight in CAM-CONFIG-REFORM-V0.
    Full service/repository composition is planned for subsequent campaigns.
    """

    _load_runtime_env_files()
    cfg = load_config()
    structured_logger = StdoutJsonLogger()
    deps = _build_base_bootstrap_deps(cfg, structured_logger)
    ctx = AppContext(cfg=cfg, deps=deps)
    deps.update(build_metrics_dependencies(ctx, deps, structured_logger=structured_logger))
    deps.update(build_queue_runtime(ctx, deps))
    return ctx
