"""Legacy blob store-write helper for main job flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class LegacyStoreWriteRequest:
    legacy_blob_write: bool
    store_mode: str
    mode: str
    allow_sync: bool
    tasks: list[Any]
    task_to_store_record: Callable[[Any], dict[str, object]]
    runtime_env: str
    ydb_endpoint: str
    ydb_database: str
    migration_store_file: str
    sa_json_credentials: str | None
    sa_key_file: str | None
    build_store: Callable[..., Any]
    safe_print: Callable[[str], None]


def run_legacy_store_write(request: LegacyStoreWriteRequest) -> None:
    if not (
        request.store_mode in {"dual_write", "ydb_primary", "ydb_only"}
        and request.mode in {"timer", "test", "sync-only"}
    ):
        return

    if request.legacy_blob_write and request.allow_sync:
        records = [request.task_to_store_record(task) for task in request.tasks]
        store = request.build_store(
            request.store_mode,
            env_name=request.runtime_env,
            ydb_endpoint=request.ydb_endpoint,
            ydb_database=request.ydb_database,
            json_file_path=request.migration_store_file,
            sa_json_credentials=request.sa_json_credentials,
            sa_key_file=request.sa_key_file,
        )
        store_result = store.upsert_tasks(records)
        request.safe_print(
            "migration_store_write="
            f"store_mode={request.store_mode} "
            "write_path=dual_write_legacy "
            f"store_file={request.migration_store_file} "
            f"records={len(records)} "
            f"result={store_result}"
        )
        return

    request.safe_print("migration_store_write=skipped write_path=normalized_only reason=LEGACY_BLOB_WRITE_disabled")
