"""Platform-owned maintenance job for job-status retention cleanup."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.platform.errors import UserError


class CleanupJobStatusesJob:
    """Delete old terminal job-status records from the status store."""

    def __init__(self, ctx) -> None:
        self._ctx = ctx

    def _status_store(self):
        store = self._ctx.deps.get("job_status_store")
        if store is None:
            raise UserError("Job status store is not configured for current environment.", code="job_status_store_unavailable")
        return store

    @staticmethod
    def _resolve_cutoff(payload: dict) -> datetime:
        raw_delete_before = str(payload.get("delete_before_utc", "")).strip()
        raw_older_than = payload.get("older_than_hours")
        if raw_delete_before and raw_older_than not in {None, ""}:
            raise UserError(
                "Specify either delete_before_utc or older_than_hours, not both.",
                code="cleanup_job_statuses_payload_conflict",
            )
        if not raw_delete_before and raw_older_than in {None, ""}:
            raise UserError(
                "cleanup_job_statuses requires delete_before_utc or older_than_hours.",
                code="cleanup_job_statuses_cutoff_required",
            )
        if raw_delete_before:
            text = raw_delete_before
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            try:
                cutoff = datetime.fromisoformat(text)
            except ValueError as error:
                raise UserError(
                    "delete_before_utc must be a valid ISO-8601 timestamp.",
                    code="cleanup_job_statuses_delete_before_invalid",
                ) from error
            if cutoff.tzinfo is None:
                cutoff = cutoff.replace(tzinfo=timezone.utc)
            return cutoff.astimezone(timezone.utc)
        try:
            hours = int(raw_older_than)
        except (TypeError, ValueError) as error:
            raise UserError(
                "older_than_hours must be a positive integer.",
                code="cleanup_job_statuses_older_than_invalid",
            ) from error
        if hours <= 0:
            raise UserError(
                "older_than_hours must be a positive integer.",
                code="cleanup_job_statuses_older_than_invalid",
            )
        return datetime.now(timezone.utc) - timedelta(hours=hours)

    @staticmethod
    def _resolve_limit(payload: dict) -> int | None:
        raw_limit = payload.get("limit")
        if raw_limit in {None, ""}:
            return None
        try:
            limit = int(raw_limit)
        except (TypeError, ValueError) as error:
            raise UserError(
                "limit must be a non-negative integer.",
                code="cleanup_job_statuses_limit_invalid",
            ) from error
        if limit < 0:
            raise UserError(
                "limit must be a non-negative integer.",
                code="cleanup_job_statuses_limit_invalid",
            )
        return limit

    def run(self, command) -> dict:
        payload = dict(command.payload or {})
        cutoff = self._resolve_cutoff(payload)
        limit = self._resolve_limit(payload)
        summary = self._status_store().prune_terminal_statuses_before(
            cutoff,
            dry_run=bool(payload.get("dry_run", False)),
            limit=limit,
        )
        return {
            "artifact": "cleanup_job_statuses",
            "status": "ok",
            "summary": summary,
            "delete_before_utc": summary.get("delete_before_utc"),
            "dry_run": bool(summary.get("dry_run", False)),
        }
