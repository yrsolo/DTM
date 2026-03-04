"""Frontend API task-loading helper extracted from index entrypoint."""

from __future__ import annotations

from typing import Any

from src.services.source_policy import build_source_policy_matrix


def load_frontend_tasks(
    dependencies: Any,
    statuses: list[str],
    *,
    app_readmodel_source: str,
    ydb_endpoint: str,
    ydb_database: str,
    ydb_sa_json_credentials: str,
    ydb_sa_key_file: str,
    ydb_operational_task_repo_cls: type,
) -> list[Any]:
    policy = build_source_policy_matrix(
        readmodel_source=app_readmodel_source,
        notify_source="legacy",
        render_source="legacy",
    )
    if not policy.api_reads_ydb():
        return dependencies.task_repository.get_task_by_color_status(statuses)
    task_repo = ydb_operational_task_repo_cls(
        endpoint=ydb_endpoint,
        database=ydb_database,
        sa_json_credentials=ydb_sa_json_credentials,
        sa_key_file=ydb_sa_key_file,
    )
    return task_repo.get_task_by_color_status(statuses)
