"""DB migrate job entrypoint."""

from __future__ import annotations

from typing import Any

from src.adapters.ydb.client import YdbClient
from src.adapters.ydb.schema import ensure_tables


def run_db_migrate(
    *,
    endpoint: str,
    database: str,
    sa_json_credentials: str | None = None,
    sa_key_file: str | None = None,
) -> dict[str, Any]:
    """Ensure YDB schema and return migration summary."""

    client = YdbClient(
        endpoint=endpoint,
        database=database,
        sa_json_credentials=sa_json_credentials,
        sa_key_file=sa_key_file,
    )
    ensure_tables(client)
    return {
        "mode": "db_migrate",
        "summary": {
            "db_migrate_done": True,
            "ydb_queries_count": client.stats.ydb_queries_count,
            "ydb_duration_ms": client.stats.duration_ms,
            "ydb_error_code": client.stats.error_code,
        },
    }
