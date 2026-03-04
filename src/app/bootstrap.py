"""Application bootstrap for config-first runtime wiring."""

from __future__ import annotations

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


def build_app_context() -> AppContext:
    """Load YAML config and return bootstrap context.

    Dependency wiring is intentionally lightweight in CAM-CONFIG-REFORM-V0.
    Full service/repository composition is planned for subsequent campaigns.
    """

    cfg = load_config()
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
    }
    return AppContext(cfg=cfg, deps=deps)
