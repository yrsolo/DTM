"""Legacy blob store-write helper for main job flow."""

from __future__ import annotations

from typing import Any, Callable


def run_legacy_store_write(
    *,
    legacy_blob_write: bool,
    store_mode: str,
    mode: str,
    allow_sync: bool,
    tasks: list[Any],
    task_to_store_record: Callable[[Any], dict[str, object]],
    runtime_env: str,
    ydb_endpoint: str,
    ydb_database: str,
    migration_store_file: str,
    sa_json_credentials: str | None,
    sa_key_file: str | None,
    build_store: Callable[..., Any],
    safe_print: Callable[[str], None],
) -> None:
    if not (store_mode in {"dual_write", "ydb_primary", "ydb_only"} and mode in {"timer", "test", "sync-only"}):
        return

    if legacy_blob_write and allow_sync:
        records = [task_to_store_record(task) for task in tasks]
        store = build_store(
            store_mode,
            env_name=runtime_env,
            ydb_endpoint=ydb_endpoint,
            ydb_database=ydb_database,
            json_file_path=migration_store_file,
            sa_json_credentials=sa_json_credentials,
            sa_key_file=sa_key_file,
        )
        store_result = store.upsert_tasks(records)
        safe_print(
            "migration_store_write="
            f"store_mode={store_mode} "
            "write_path=dual_write_legacy "
            f"store_file={migration_store_file} "
            f"records={len(records)} "
            f"result={store_result}"
        )
        return

    safe_print("migration_store_write=skipped write_path=normalized_only reason=LEGACY_BLOB_WRITE_disabled")
