from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.commands.model import Command
from src.platform.errors import PermanentError, TransientError

from .model import JobResult, JobStatusRecord


def _to_iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def _from_iso(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class S3JobStatusStore:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None,
        aws_access_key_id: str | None,
        aws_secret_access_key: str | None,
        status_prefix: str,
        latest_prefix: str,
    ) -> None:
        self._bucket = str(bucket).strip()
        self._status_prefix = str(status_prefix).strip().rstrip("/") + "/"
        self._latest_prefix = str(latest_prefix).strip().rstrip("/") + "/"
        self._history_prefix = self._derive_history_prefix(self._status_prefix)
        self._endpoint_url = str(endpoint_url).strip() or None
        self._aws_access_key_id = str(aws_access_key_id).strip() or None
        self._aws_secret_access_key = str(aws_secret_access_key).strip() or None
        self._client = None
        self._history_limit = 50
        self._history_per_command_limit = 20
        if not self._bucket:
            raise ValueError("bucket is required")

    @staticmethod
    def _derive_history_prefix(status_prefix: str) -> str:
        cleaned = str(status_prefix).strip().rstrip("/") + "/"
        if cleaned.endswith("status/"):
            return cleaned[: -len("status/")] + "history/"
        parts = [part for part in cleaned.split("/") if part]
        if not parts:
            return "history/"
        parts[-1] = "history"
        return "/".join(parts) + "/"

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import boto3  # type: ignore
        except Exception as error:  # pragma: no cover
            raise PermanentError("boto3 package is required for S3 job status store", code="s3_sdk_missing") from error
        self._client = boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
        )
        return self._client

    def _status_key(self, job_id: str) -> str:
        return f"{self._status_prefix}{job_id}.json"

    def _latest_key(self, command_type: str) -> str:
        return f"{self._latest_prefix}{command_type}.json"

    def _history_index_key(self) -> str:
        return f"{self._history_prefix}index.json"

    def _history_by_command_key(self, command_type: str) -> str:
        return f"{self._history_prefix}by-command/{str(command_type).strip()}.json"

    def _put_json(self, key: str, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        try:
            self._get_client().put_object(
                Bucket=self._bucket,
                Key=key,
                Body=body,
                ContentType="application/json; charset=utf-8",
            )
        except Exception as error:
            raise TransientError(str(error), code="job_status_put_failed") from error

    def _get_json(self, key: str) -> dict[str, Any] | None:
        try:
            response = self._get_client().get_object(Bucket=self._bucket, Key=key)
        except Exception as error:
            response_dict = getattr(error, "response", {})
            code = str(response_dict.get("Error", {}).get("Code", "")).strip() if isinstance(response_dict, dict) else ""
            if code in {"NoSuchKey", "NoSuchBucket", "404"}:
                return None
            raise TransientError(str(error), code="job_status_get_failed") from error
        payload = json.loads(response["Body"].read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise PermanentError("Job status payload must be an object", code="job_status_invalid")
        return payload

    def _get_json_list(self, key: str) -> list[dict[str, Any]]:
        payload = self._get_json(key)
        if payload is None:
            return []
        items = payload.get("items", [])
        if not isinstance(items, list):
            raise PermanentError("Job history payload must contain object items list", code="job_history_invalid")
        return [dict(item) for item in items if isinstance(item, dict)]

    def _put_json_list(self, key: str, items: list[dict[str, Any]]) -> None:
        self._put_json(key, {"items": items})

    @staticmethod
    def _record_to_dict(record: JobStatusRecord) -> dict[str, Any]:
        return {
            "job_id": record.job_id,
            "command_type": record.command_type,
            "status": record.status,
            "requested_at_utc": _to_iso(record.requested_at_utc),
            "started_at_utc": _to_iso(record.started_at_utc),
            "finished_at_utc": _to_iso(record.finished_at_utc),
            "requested_by": dict(record.requested_by),
            "summary": dict(record.summary),
            "warnings": list(record.warnings),
            "retryable": bool(record.retryable),
            "error": dict(record.error or {}) if record.error else None,
        }

    @staticmethod
    def _record_from_dict(payload: dict[str, Any]) -> JobStatusRecord:
        return JobStatusRecord(
            job_id=str(payload.get("job_id", "")).strip(),
            command_type=str(payload.get("command_type", "")).strip(),
            status=str(payload.get("status", "")).strip(),
            requested_at_utc=_from_iso(payload.get("requested_at_utc")) or datetime.now(timezone.utc),
            started_at_utc=_from_iso(payload.get("started_at_utc")),
            finished_at_utc=_from_iso(payload.get("finished_at_utc")),
            requested_by=dict(payload.get("requested_by", {}) or {}),
            summary=dict(payload.get("summary", {}) or {}),
            warnings=[str(item) for item in list(payload.get("warnings", []) or [])],
            retryable=bool(payload.get("retryable", False)),
            error=dict(payload.get("error", {}) or {}) or None,
        )

    def put_queued(self, cmd: Command) -> JobStatusRecord:
        record = JobStatusRecord(
            job_id=cmd.job_id,
            command_type=cmd.type,
            status="accepted",
            requested_at_utc=cmd.created_at_utc,
            requested_by={
                "source": cmd.requested_by.source,
                "user_id": cmd.requested_by.user_id,
                "chat_id": cmd.requested_by.chat_id,
            },
        )
        payload = self._record_to_dict(record)
        self._put_json(self._status_key(cmd.job_id), payload)
        self._put_json(self._latest_key(cmd.type), payload)
        return record

    def append_history(self, record: JobStatusRecord) -> None:
        item = self._record_to_dict(record)
        recent = [item]
        for existing in self._get_json_list(self._history_index_key()):
            if str(existing.get("job_id", "")).strip() == record.job_id:
                continue
            recent.append(existing)
        self._put_json_list(self._history_index_key(), recent[: self._history_limit])

        by_command = [item]
        for existing in self._get_json_list(self._history_by_command_key(record.command_type)):
            if str(existing.get("job_id", "")).strip() == record.job_id:
                continue
            by_command.append(existing)
        self._put_json_list(
            self._history_by_command_key(record.command_type),
            by_command[: self._history_per_command_limit],
        )

    def put_running(self, cmd: Command) -> JobStatusRecord:
        existing = self.get(cmd.job_id)
        requested_at = existing.requested_at_utc if existing is not None else cmd.created_at_utc
        record = JobStatusRecord(
            job_id=cmd.job_id,
            command_type=cmd.type,
            status="running",
            requested_at_utc=requested_at,
            started_at_utc=datetime.now(timezone.utc),
            requested_by={
                "source": cmd.requested_by.source,
                "user_id": cmd.requested_by.user_id,
                "chat_id": cmd.requested_by.chat_id,
            },
            summary=dict(existing.summary) if existing is not None else {},
            warnings=list(existing.warnings) if existing is not None else [],
            retryable=False,
        )
        payload = self._record_to_dict(record)
        self._put_json(self._status_key(cmd.job_id), payload)
        self._put_json(self._latest_key(cmd.type), payload)
        return record

    def put_finished(self, cmd: Command, result: JobResult) -> JobStatusRecord:
        existing = self.get(cmd.job_id)
        record = JobStatusRecord(
            job_id=cmd.job_id,
            command_type=cmd.type,
            status=(
                "success"
                if result.success
                else ("failed_retryable" if result.retryable else "failed_terminal")
            ),
            requested_at_utc=(existing.requested_at_utc if existing is not None else cmd.created_at_utc),
            started_at_utc=(existing.started_at_utc if existing is not None else None),
            finished_at_utc=datetime.now(timezone.utc),
            requested_by={
                "source": cmd.requested_by.source,
                "user_id": cmd.requested_by.user_id,
                "chat_id": cmd.requested_by.chat_id,
            },
            summary=dict(result.details),
            warnings=list(result.warnings),
            retryable=bool(result.retryable),
            error=dict(result.error or {}) if result.error else None,
        )
        payload = self._record_to_dict(record)
        self._put_json(self._status_key(cmd.job_id), payload)
        self._put_json(self._latest_key(cmd.type), payload)
        self.append_history(record)
        return record

    def get(self, job_id: str) -> JobStatusRecord | None:
        payload = self._get_json(self._status_key(str(job_id).strip()))
        if payload is None:
            return None
        return self._record_from_dict(payload)

    def get_latest(self, command_type: str) -> JobStatusRecord | None:
        payload = self._get_json(self._latest_key(str(command_type).strip()))
        if payload is None:
            return None
        return self._record_from_dict(payload)

    def get_recent(self, limit: int = 20) -> list[JobStatusRecord]:
        items = self._get_json_list(self._history_index_key())
        return [self._record_from_dict(item) for item in items[: max(0, int(limit))]]

    def get_recent_by_command(self, command_type: str, limit: int = 10) -> list[JobStatusRecord]:
        items = self._get_json_list(self._history_by_command_key(str(command_type).strip()))
        return [self._record_from_dict(item) for item in items[: max(0, int(limit))]]
