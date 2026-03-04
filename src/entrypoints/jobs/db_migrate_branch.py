"""DB migrate branch helper for main job flow."""

from __future__ import annotations

from typing import Callable


def run_db_migrate_if_requested(
    *,
    mode: str,
    endpoint: str,
    database: str,
    sa_json_credentials: str | None,
    sa_key_file: str | None,
    run_db_migrate: Callable[..., object],
) -> tuple[bool, object | None]:
    if mode != "db_migrate":
        return False, None
    result = run_db_migrate(
        endpoint=endpoint,
        database=database,
        sa_json_credentials=sa_json_credentials,
        sa_key_file=sa_key_file,
    )
    print("db_migrate_done=true")
    return True, result
