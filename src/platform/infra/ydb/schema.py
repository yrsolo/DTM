"""YDB schema management for DTM operational/readmodel tables."""

from __future__ import annotations

from src.platform.infra.ydb.client import YdbClient


def _ddl_tasks(table_name: str) -> str:
    return f"""
    CREATE TABLE `{table_name}` (
        task_id Utf8,
        title Utf8,
        brand Utf8,
        format_ Utf8,
        customer Utf8,
        raw_timing Utf8,
        owner_id Utf8,
        group_id Utf8,
        status Utf8,
        start_date Date,
        end_date Date,
        next_due_date Date,
        tags_json Utf8,
        links_json Utf8,
        task_hash Utf8,
        task_revision Uint64,
        history Utf8,
        raw_payload Utf8,
        updated_at_utc Timestamp,
        PRIMARY KEY (task_id)
    );
    """


def _ddl_milestones(table_name: str) -> str:
    return f"""
    CREATE TABLE `{table_name}` (
        task_id Utf8,
        idx Uint32,
        type Utf8,
        planned_date Date,
        actual_date Date,
        status Utf8,
        raw_text Utf8,
        confidence Double,
        inference_rule Utf8,
        PRIMARY KEY (task_id, idx)
    );
    """


def _ddl_milestones_versioned(table_name: str) -> str:
    return f"""
    CREATE TABLE `{table_name}` (
        task_id Utf8,
        version Uint64,
        idx Uint32,
        type Utf8,
        planned_date Date,
        actual_date Date,
        status Utf8,
        raw_text Utf8,
        confidence Double,
        inference_rule Utf8,
        PRIMARY KEY (task_id, version, idx)
    );
    """


def _ddl_sync_state(table_name: str) -> str:
    return f"""
    CREATE TABLE `{table_name}` (
        source_id Utf8,
        preflight_hash_50 Utf8,
        source_hash_full Utf8,
        synced_at_utc Timestamp,
        last_full_sync_at Timestamp,
        last_success_at_utc Timestamp,
        last_error Utf8,
        last_error_code Utf8,
        last_error_at_utc Timestamp,
        PRIMARY KEY (source_id)
    );
    """


def _ddl_task_versions(table_name: str) -> str:
    return f"""
    CREATE TABLE `{table_name}` (
        task_id Utf8,
        version Uint64,
        status Utf8,
        content_hash Utf8,
        payload_json Utf8,
        created_at_utc Timestamp,
        PRIMARY KEY (task_id, version)
    );
    """


def _ddl_readmodel(table_name: str) -> str:
    return f"""
    CREATE TABLE `{table_name}` (
        readmodel_id Utf8,
        contract_version Utf8,
        payload_json Utf8,
        payload_hash Utf8,
        built_from_source_hash Utf8,
        generated_at_utc Timestamp,
        PRIMARY KEY (readmodel_id)
    );
    """


def ensure_tables(
    client: YdbClient,
    *,
    tasks_table: str = "dtm_tasks",
    milestones_table: str = "dtm_task_milestones",
    milestones_versioned_table: str = "dtm_task_milestones_v",
    versions_table: str = "dtm_task_versions",
    sync_state_table: str = "dtm_sync_state",
    readmodel_table: str = "dtm_readmodel_frontend_v2",
) -> None:
    """Create required tables (idempotent)."""

    for ddl in (
        _ddl_tasks(tasks_table),
        _ddl_milestones(milestones_table),
        _ddl_milestones_versioned(milestones_versioned_table),
        _ddl_task_versions(versions_table),
        _ddl_sync_state(sync_state_table),
        _ddl_readmodel(readmodel_table),
    ):
        try:
            client.execute_scheme(ddl)
        except Exception as exc:
            text = str(exc).lower()
            if "exists" in text or "already" in text:
                continue
            raise

    ensure_tasks_history_column(client, tasks_table=tasks_table)


def ensure_tasks_history_column(client: YdbClient, *, tasks_table: str = "dtm_tasks") -> None:
    """Ensure dtm_tasks has first-class `history` column for task raw status text."""
    alter = f"ALTER TABLE `{tasks_table}` ADD COLUMN history Utf8;"
    try:
        client.execute_scheme(alter)
    except Exception as exc:
        text = str(exc).lower()
        if (
            "exists" in text
            or "already" in text
            or "duplicate" in text
            or "cannot add column" in text
        ):
            return
        raise
