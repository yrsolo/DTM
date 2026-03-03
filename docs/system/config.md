# Configuration (Current)

Source of truth: `config/constants.py`.

## Core environment selection
- `ENV` = dev | test | prod
- `STRICT_ENV_GUARD` (0/1)

## Domains
- `WEB_DOMAIN`
- `API_DOMAIN_TEST`
- `API_DOMAIN_PROD`
- `API_DOMAIN` is derived by ENV

## Feature / rollout switches
- `FRONTEND_API_DEFAULT_VERSION` = v1 | v2
- `TIMING_YEAR_MODE` = legacy | anchors | chain

Operational/readmodel sources:
- `STORE_MODE` = legacy | dual_write | ydb_primary | ydb_only
- `READMODEL_SOURCE` = legacy | ydb
- `NOTIFY_SOURCE` = legacy | ydb (defaults to READMODEL_SOURCE)
- `RENDER_SOURCE` = legacy | ydb (defaults to READMODEL_SOURCE)

## YDB
Contour-aware values (prod vs test):
- `YDB_ID`
- `YDB_ENDPOINT`
- `YDB_DATABASE`

Schema/migration:
- `YDB_MIGRATE_ON_START` (0/1)

Legacy compat flags:
- `LEGACY_BLOB_WRITE` (0/1)
- `WRITE_LEGACY_MILESTONES` (0/1)

Quota/backoff tuning:
- `YDB_EXHAUSTED_MAX_ATTEMPTS` (default 6)
- `YDB_EXHAUSTED_BASE_BACKOFF_SECONDS` (default 0.2)
- `YDB_EXHAUSTED_MAX_BACKOFF_SECONDS` (default 4.0)
- `YDB_EXHAUSTED_JITTER_RATIO` (default 0.3)

Pipeline modifiers:
- `FORCE_REFRESH` (0/1)
- `READMODEL_TTL_MINUTES` (default 9)
- `PREFLIGHT_TOP_ROWS` (default 50)
- `FULL_SYNC_INTERVAL_HOURS` (default 24)

## Migration flags (should generally be OFF)
- `MIGRATION_ENABLE_NEW_SYNC_PATH`
- `MIGRATION_ENABLE_NEW_RENDER_PATH`
- `MIGRATION_ENABLE_SOURCE_HASH_GATE`
- `MIGRATION_DUAL_WRITE_STORE`
- `MIGRATION_HASH_GATE_STATE_FILE`
- `MIGRATION_STORE_FILE`

## Telegram
- `TG_TOKEN` (secret)
- `TG_BOT_USERNAME`
- `DEFAULT_CHAT_ID`

## LLM
- `LLM_PROVIDER` = openai | google | yandex
- `OPENAI_TOKEN` (secret)
- `ORG_TOKEN` (optional)
- `OPENAI_MODEL`

Google:
- `GOOGLE_LLM_API_KEY` (secret)
- `GOOGLE_LLM_MODEL` (default gemini-2.0-flash)

Yandex:
- `YANDEX_LLM_API_KEY` (secret)
- `YANDEX_LLM_MODEL_URI` (can be derived from `YC_FOLDER_ID`)

LLM HTTP:
- `LLM_HTTP_TIMEOUT_SECONDS` (default 25)
- `LLM_HTTP_RETRY_ATTEMPTS` (default 2)
- `LLM_HTTP_RETRY_BACKOFF_SECONDS` (default 0.8)

Failover:
- `LLM_FAILOVER_MODE` = draft_only | provider
- `LLM_FAILOVER_PROVIDER` (optional)

## Proxy
- `PROXY_URL`

## Google Sheets
Google key resolution (priority):
- `GOOGLE_KEY_JSON_PATH`
- `GOOGLE_KEY_JSON_B64`
- `GOOGLE_KEY_JSON`
- fallback repo file path

Sheets:
- `SOURCE_SHEET_NAME` (default "Спонсорские ТНТ")
- `TARGET_SHEET_NAME` / `TARGET_SHEET_NAME_PROD` (prod override)

Note: current code also contains large mapping dictionaries (e.g. REPLACE_NAMES) in `constants.py`.
These are non-secret and candidates to move into config files later.
