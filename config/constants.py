"""Constants for the project."""

import base64
import os
import tempfile
from pathlib import Path
from types import MappingProxyType as MapProxy
from typing import Mapping

from dotenv import load_dotenv
from src.config.loader import load_config

ALLOWED_ENVS = frozenset({"dev", "test", "prod"})
ALLOWED_LLM_PROVIDERS = frozenset({"openai", "google", "yandex"})
ALLOWED_LLM_FAILOVER_MODES = frozenset({"draft_only", "provider"})
ALLOWED_STORE_MODES = frozenset({"legacy", "dual_write", "ydb_primary", "ydb_only"})
ALLOWED_READ_SOURCES = frozenset({"legacy", "ydb"})
ALLOWED_TIMING_YEAR_MODES = frozenset({"legacy", "anchors", "chain"})


def _env(name: str, default: str = "") -> str:
    """Return stripped environment value."""

    return os.environ.get(name, default).strip()


def _env_flag(name: str, default: str = "0") -> bool:
    """Parse bool-like flag from environment."""

    return _env(name, default).lower() in {"1", "true", "yes"}


def _contour_env(name: str, default: str = "") -> str:
    """Return contour-specific value with legacy fallback.

    Priority:
    - ENV=prod -> <NAME>_PROD
    - ENV=dev/test -> <NAME>_TEST
    - fallback -> <NAME>
    """

    suffix = "PROD" if RUNTIME_ENV == "prod" else "TEST"
    scoped_value = _env(f"{name}_{suffix}")
    if scoped_value:
        return scoped_value
    return _env(name, default)


def _load_runtime_env() -> str:
    """Load base .env and optional profile-specific file.

    Profile file naming: .env.<env>, for example .env.dev or .env.prod.
    """
    load_dotenv()
    runtime_env = _env("ENV", "dev").lower() or "dev"
    profile_path = Path(f".env.{runtime_env}")
    if profile_path.exists():
        load_dotenv(dotenv_path=profile_path, override=True)
    if runtime_env not in ALLOWED_ENVS:
        raise ValueError(f"Unsupported ENV={runtime_env!r}. Allowed values: dev, test, prod.")
    return runtime_env


RUNTIME_ENV = _load_runtime_env()
_APP_CFG = load_config()
_RUNTIME_CFG = _APP_CFG.runtime
_TABLES_CFG = _APP_CFG.tables
_DB_CFG = _APP_CFG.db
_LLM_CFG = _APP_CFG.llm
_MAPPING_CFG = _APP_CFG.mapping

ALLOWED_LLM_PROVIDERS = frozenset(
    str(item).lower() for item in _LLM_CFG.llm.get("allowed_providers", ALLOWED_LLM_PROVIDERS)
)
ALLOWED_LLM_FAILOVER_MODES = frozenset(
    str(item).lower() for item in _LLM_CFG.failover.get("allowed_modes", ALLOWED_LLM_FAILOVER_MODES)
)
ALLOWED_TIMING_YEAR_MODES = frozenset(
    str(item).lower() for item in _RUNTIME_CFG.timing.allowed_year_modes
)

STRICT_ENV_GUARD = _env_flag(
    "STRICT_ENV_GUARD", "1" if _RUNTIME_CFG.runtime.strict_env_guard_default else "0"
)
WEB_DOMAIN = _env("WEB_DOMAIN")
if not WEB_DOMAIN:
    WEB_DOMAIN = str(_RUNTIME_CFG.web.get("domain", ""))
API_DOMAIN_TEST = _env("API_DOMAIN_TEST")
if not API_DOMAIN_TEST:
    API_DOMAIN_TEST = str(_RUNTIME_CFG.web.get("api_domain_test", ""))
API_DOMAIN_PROD = _env("API_DOMAIN_PROD")
if not API_DOMAIN_PROD:
    API_DOMAIN_PROD = str(_RUNTIME_CFG.web.get("api_domain_prod", ""))
API_DOMAIN = API_DOMAIN_PROD if RUNTIME_ENV == "prod" else API_DOMAIN_TEST
DEBUG_HTTP_EVENT = _env_flag(
    "DEBUG_HTTP_EVENT", "1" if _RUNTIME_CFG.api.get("debug_http_event_default", False) else "0"
)
TIMING_YEAR_MODE = _env("TIMING_YEAR_MODE", _RUNTIME_CFG.timing.year_mode_default).lower()
if TIMING_YEAR_MODE not in ALLOWED_TIMING_YEAR_MODES:
    raise ValueError(
        f"Unsupported TIMING_YEAR_MODE={TIMING_YEAR_MODE!r}. "
        "Allowed values: legacy, anchors, chain."
    )

# Operational store / readmodel rollout switches.
STORE_MODE = _env("STORE_MODE", _RUNTIME_CFG.sources.store_mode_default).lower()
if STORE_MODE not in ALLOWED_STORE_MODES:
    raise ValueError(
        f"Unsupported STORE_MODE={STORE_MODE!r}. "
        "Allowed values: legacy, dual_write, ydb_primary, ydb_only."
    )
READMODEL_SOURCE = _env("READMODEL_SOURCE", _RUNTIME_CFG.sources.readmodel_source_default).lower()
if READMODEL_SOURCE not in ALLOWED_READ_SOURCES:
    raise ValueError(
        f"Unsupported READMODEL_SOURCE={READMODEL_SOURCE!r}. Allowed values: legacy, ydb."
    )
_notify_default = _RUNTIME_CFG.sources.notify_source_default
if _notify_default == "readmodel_source":
    _notify_default = READMODEL_SOURCE
NOTIFY_SOURCE = _env("NOTIFY_SOURCE", _notify_default).lower()
if NOTIFY_SOURCE not in ALLOWED_READ_SOURCES:
    raise ValueError(f"Unsupported NOTIFY_SOURCE={NOTIFY_SOURCE!r}. Allowed values: legacy, ydb.")
_render_default = _RUNTIME_CFG.sources.render_source_default
if _render_default == "readmodel_source":
    _render_default = READMODEL_SOURCE
RENDER_SOURCE = _env("RENDER_SOURCE", _render_default).lower()
if RENDER_SOURCE not in ALLOWED_READ_SOURCES:
    raise ValueError(f"Unsupported RENDER_SOURCE={RENDER_SOURCE!r}. Allowed values: legacy, ydb.")

YDB_ID = _contour_env("YDB_ID")
YDB_ENDPOINT = _contour_env("YDB_ENDPOINT")
YDB_DATABASE = _contour_env("YDB_DATABASE")
YC_SA_JSON_CREDENTIALS = _env("YC_SA_JSON_CREDENTIALS")
YC_SA_KEY_FILE = _env("YC_SA_KEY_FILE")
YDB_MIGRATE_ON_START = _env_flag(
    "YDB_MIGRATE_ON_START", "1" if _DB_CFG.ydb.get("migrate_on_start_default", False) else "0"
)
LEGACY_BLOB_WRITE = _env_flag(
    "LEGACY_BLOB_WRITE", "1" if _DB_CFG.compat.get("legacy_blob_write_default", False) else "0"
)
WRITE_LEGACY_MILESTONES = _env_flag(
    "WRITE_LEGACY_MILESTONES",
    "1" if _DB_CFG.compat.get("write_legacy_milestones_default", False) else "0",
)
YDB_EXHAUSTED_MAX_ATTEMPTS = max(
    1, int(_env("YDB_EXHAUSTED_MAX_ATTEMPTS", str(_DB_CFG.retry.get("exhausted_max_attempts", 6))))
)
YDB_EXHAUSTED_BASE_BACKOFF_SECONDS = max(
    0.05,
    float(
        _env(
            "YDB_EXHAUSTED_BASE_BACKOFF_SECONDS",
            str(_DB_CFG.retry.get("exhausted_base_backoff_seconds", 0.2)),
        )
    ),
)
YDB_EXHAUSTED_MAX_BACKOFF_SECONDS = max(
    YDB_EXHAUSTED_BASE_BACKOFF_SECONDS,
    float(
        _env(
            "YDB_EXHAUSTED_MAX_BACKOFF_SECONDS",
            str(_DB_CFG.retry.get("exhausted_max_backoff_seconds", 4.0)),
        )
    ),
)
YDB_EXHAUSTED_JITTER_RATIO = min(
    1.0,
    max(
        0.0,
        float(_env("YDB_EXHAUSTED_JITTER_RATIO", str(_DB_CFG.retry.get("exhausted_jitter_ratio", 0.3)))),
    ),
)
FORCE_REFRESH = _env_flag(
    "FORCE_REFRESH", "1" if _RUNTIME_CFG.pipeline.force_refresh_default else "0"
)
READMODEL_TTL_MINUTES = max(
    1, int(_env("READMODEL_TTL_MINUTES", str(_RUNTIME_CFG.pipeline.readmodel_ttl_minutes)))
)
PREFLIGHT_TOP_ROWS = max(1, int(_env("PREFLIGHT_TOP_ROWS", str(_RUNTIME_CFG.pipeline.preflight_top_rows))))
FULL_SYNC_INTERVAL_HOURS = max(
    1, int(_env("FULL_SYNC_INTERVAL_HOURS", str(_RUNTIME_CFG.pipeline.full_sync_interval_hours)))
)

# Migration feature flags (safe defaults: disabled)
MIGRATION_ENABLE_NEW_SYNC_PATH = _env_flag("MIGRATION_ENABLE_NEW_SYNC_PATH")
MIGRATION_ENABLE_NEW_RENDER_PATH = _env_flag("MIGRATION_ENABLE_NEW_RENDER_PATH")
MIGRATION_ENABLE_SOURCE_HASH_GATE = _env_flag("MIGRATION_ENABLE_SOURCE_HASH_GATE")
MIGRATION_DUAL_WRITE_STORE = _env_flag("MIGRATION_DUAL_WRITE_STORE")
MIGRATION_HASH_GATE_STATE_FILE = _env(
    "MIGRATION_HASH_GATE_STATE_FILE", "artifacts/tmp/source_hash_gate_state.json"
)
MIGRATION_STORE_FILE = _env("MIGRATION_STORE_FILE", "artifacts/tmp/normalized_store.json")

TG = os.environ.get("TG_TOKEN")
TG_BOT_USERNAME = _env("TG_BOT_USERNAME")
OPENAI = os.environ.get("OPENAI_TOKEN")
ORG = os.environ.get("ORG_TOKEN")
LLM_PROVIDER = _env("LLM_PROVIDER", str(_LLM_CFG.llm.get("provider_default", "openai"))).lower()
if LLM_PROVIDER not in ALLOWED_LLM_PROVIDERS:
    raise ValueError(
        f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. Allowed values: openai, google, yandex."
    )
OPENAI_MODEL = _env("OPENAI_MODEL", "")
GOOGLE_LLM_API_KEY = _env("GOOGLE_LLM_API_KEY")
GOOGLE_LLM_MODEL = _env("GOOGLE_LLM_MODEL", str(_LLM_CFG.models.get("google_default", "gemini-2.0-flash")))
YANDEX_LLM_API_KEY = _env("YANDEX_LLM_API_KEY")
YANDEX_LLM_MODEL_URI = _env("YANDEX_LLM_MODEL_URI")
LLM_HTTP_TIMEOUT_SECONDS = float(
    _env("LLM_HTTP_TIMEOUT_SECONDS", str(_LLM_CFG.http.get("timeout_seconds", 25)))
)
LLM_HTTP_RETRY_ATTEMPTS = max(
    1, int(_env("LLM_HTTP_RETRY_ATTEMPTS", str(_LLM_CFG.http.get("retry_attempts", 2))))
)
LLM_HTTP_RETRY_BACKOFF_SECONDS = max(
    0.0, float(_env("LLM_HTTP_RETRY_BACKOFF_SECONDS", str(_LLM_CFG.http.get("retry_backoff_seconds", 0.8))))
)
LLM_FAILOVER_MODE = _env(
    "LLM_FAILOVER_MODE", str(_LLM_CFG.failover.get("mode_default", "draft_only"))
).lower()
if LLM_FAILOVER_MODE not in ALLOWED_LLM_FAILOVER_MODES:
    raise ValueError(
        f"Unsupported LLM_FAILOVER_MODE={LLM_FAILOVER_MODE!r}. "
        "Allowed values: draft_only, provider."
    )
LLM_FAILOVER_PROVIDER = _env(
    "LLM_FAILOVER_PROVIDER", str(_LLM_CFG.failover.get("provider_default", ""))
).lower()
if LLM_FAILOVER_PROVIDER and LLM_FAILOVER_PROVIDER not in ALLOWED_LLM_PROVIDERS:
    raise ValueError(
        f"Unsupported LLM_FAILOVER_PROVIDER={LLM_FAILOVER_PROVIDER!r}. "
        "Allowed values: openai, google, yandex."
    )
if not YANDEX_LLM_MODEL_URI:
    yc_folder_id = _env("YC_FOLDER_ID")
    if yc_folder_id:
        YANDEX_LLM_MODEL_URI = f"gpt://{yc_folder_id}/yandexgpt/latest"
PROXY = _env("PROXY_URL")
PROXIES: Mapping[str, str] = MapProxy({"https://": PROXY}) if PROXY else MapProxy({})


def _resolve_google_key_json_path() -> str:
    """Resolve Google service-account key path.

    Priority:
    1) GOOGLE_KEY_JSON_PATH (already materialized file path)
    2) GOOGLE_KEY_JSON_B64 (base64-encoded JSON payload)
    3) GOOGLE_KEY_JSON (raw JSON payload text)
    4) local development fallback file path in repository
    """
    key_path = _env("GOOGLE_KEY_JSON_PATH")
    if key_path:
        return key_path

    key_b64 = _env("GOOGLE_KEY_JSON_B64")
    key_text = _env("GOOGLE_KEY_JSON")
    if key_b64:
        key_text = base64.b64decode(key_b64).decode("utf-8")

    if key_text:
        tmp_file = Path(tempfile.gettempdir()) / "dtm_google_key.json"
        tmp_file.write_text(key_text, encoding="utf-8")
        return str(tmp_file)

    return "key/google_key_poised-backbone-191400-4e9fc454915f.json"


KEY_JSON = _resolve_google_key_json_path()

DEFAULT_CHAT_ID = os.environ.get(
    "DEFAULT_CHAT_ID", str(_LLM_CFG.assistant.get("default_chat_id_default", "-4083724311"))
)

_GOOGLE_SHEETS_CFG = _TABLES_CFG.google_sheets
SOURCE_SHEET_NAME = os.environ.get(
    "SOURCE_SHEET_NAME",
    str(_GOOGLE_SHEETS_CFG.get("source_sheet_name_default", "")),
)
TARGET_SHEET_NAME = os.environ.get("TARGET_SHEET_NAME", "").strip()
if not TARGET_SHEET_NAME:
    default_key = (
        "target_sheet_name_prod_default" if RUNTIME_ENV == "prod" else "target_sheet_name_default"
    )
    TARGET_SHEET_NAME = str(_GOOGLE_SHEETS_CFG.get(default_key, _GOOGLE_SHEETS_CFG.get("target_sheet_name_default", "")))
if STRICT_ENV_GUARD and RUNTIME_ENV in {"dev", "test"} and SOURCE_SHEET_NAME == TARGET_SHEET_NAME:
    raise ValueError(
        "Unsafe env contour: for ENV=dev/test SOURCE_SHEET_NAME and "
        "TARGET_SHEET_NAME must be different when STRICT_ENV_GUARD=1."
    )

REPLACE_NAMES = MapProxy(dict(_MAPPING_CFG.project_aliases))

SHEET_NAMES = MapProxy(dict(_TABLES_CFG.sheet_names))

SHEET_INFO = MapProxy(
    {
        "spreadsheet_name": TARGET_SHEET_NAME,
        "sheet_names": SHEET_NAMES,
    }
)

SOURCE_SHEET_INFO = MapProxy(
    {
        "spreadsheet_name": SOURCE_SHEET_NAME,
        "sheet_names": SHEET_NAMES,
    }
)

TASK_FIELD_MAP = MapProxy(dict(_TABLES_CFG.field_maps.get("tasks", {})))

# Legacy sheet columns for people map are configured via YAML field_maps.people.
# id, name, email, telegram_id, chat_id, info, position
PEOPLE_FIELD_MAP = MapProxy(dict(_TABLES_CFG.field_maps.get("people", {})))

COLOR_STATUS = MapProxy(dict(_MAPPING_CFG.status_by_color))

_palette = dict(_MAPPING_CFG.palette)
if "deep_purple" in _palette and "deep purple" not in _palette:
    _palette["deep purple"] = _palette["deep_purple"]
COLORS = MapProxy(_palette)

# MODEL is kept for backward compatibility with older code paths.
# MODEL = 'o1-preview'
# MODEL = 'gpt-4o'
MODEL = OPENAI_MODEL or str(_LLM_CFG.models.get("openai_default", "gpt-5"))
# MODEL = 'o1-mini'

HELPER_CHARACTER = str(_LLM_CFG.assistant.get("helper_character", ""))

TRIGGERS = MapProxy(dict(_RUNTIME_CFG.triggers))
NO_VISIBLE_STAGES = tuple(str(item) for item in _MAPPING_CFG.hidden_stage_names)
