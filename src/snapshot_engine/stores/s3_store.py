"""S3-backed stores for snapshot engine."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.services.errors import PermanentError, TransientError
from src.snapshot_engine.model import PeopleSnapshot, PrepSnapshot, RawSnapshot, TaskExtra
from src.snapshot_engine.serialization import (
    dumps_json,
    extra_from_dict,
    extra_to_dict,
    loads_json,
    people_from_dict,
    people_to_dict,
    prep_from_dict,
    prep_to_dict,
    raw_from_dict,
    raw_to_dict,
)


def _is_missing_key(error: Exception) -> bool:
    response = getattr(error, "response", {})
    if not isinstance(response, dict):
        response = {}
    code = str(response.get("Error", {}).get("Code", "")).strip()
    return code in {"NoSuchKey", "NoSuchBucket", "404"}


class _S3JsonStore:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        self.bucket = str(bucket).strip()
        if not self.bucket:
            raise ValueError("S3 bucket is required")
        try:
            import boto3  # type: ignore
        except Exception as error:  # pragma: no cover - dependency bootstrap guard
            raise PermanentError("boto3 package is required for snapshot_engine S3 storage", code="s3_sdk_missing") from error
        self.client = boto3.client(
            "s3",
            endpoint_url=(str(endpoint_url).strip() or None),
            aws_access_key_id=(str(aws_access_key_id).strip() or None),
            aws_secret_access_key=(str(aws_secret_access_key).strip() or None),
        )

    def get(self, key: str) -> dict[str, Any] | None:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            raw = response["Body"].read().decode("utf-8")
            return loads_json(raw)
        except Exception as error:
            if _is_missing_key(error):
                return None
            raise TransientError(str(error), code="s3_get_failed") from error
        except ValueError as error:
            raise PermanentError(str(error), code="snapshot_payload_invalid") from error

    def put(self, key: str, payload: dict[str, Any]) -> None:
        temp_key = f"{key}.tmp.{int(datetime.now(timezone.utc).timestamp())}"
        body = dumps_json(payload).encode("utf-8")
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=temp_key,
                Body=body,
                ContentType="application/json; charset=utf-8",
            )
            self.client.copy_object(
                Bucket=self.bucket,
                CopySource={"Bucket": self.bucket, "Key": temp_key},
                Key=key,
            )
            self.client.delete_object(Bucket=self.bucket, Key=temp_key)
        except Exception as error:
            raise TransientError(str(error), code="s3_put_failed") from error


class S3RawCache:
    def __init__(self, store: _S3JsonStore, key: str) -> None:
        self._store = store
        self._key = key

    def get(self) -> RawSnapshot | None:
        payload = self._store.get(self._key)
        if payload is None:
            return None
        return raw_from_dict(payload)

    def put(self, raw: RawSnapshot) -> None:
        self._store.put(self._key, raw_to_dict(raw))


class S3PrepCache:
    def __init__(self, store: _S3JsonStore, key: str) -> None:
        self._store = store
        self._key = key

    def get(self) -> PrepSnapshot | None:
        payload = self._store.get(self._key)
        if payload is None:
            return None
        return prep_from_dict(payload)

    def put(self, prep: PrepSnapshot) -> None:
        self._store.put(self._key, prep_to_dict(prep))


class S3ExtraStore:
    def __init__(self, store: _S3JsonStore, prefix: str) -> None:
        self._store = store
        self._prefix = str(prefix).rstrip("/") + "/"

    def _key(self, task_id: str) -> str:
        return f"{self._prefix}{task_id}.json"

    def get_many(self, task_ids: list[str]) -> dict[str, TaskExtra]:
        result: dict[str, TaskExtra] = {}
        for task_id in task_ids:
            key = self._key(task_id)
            payload = self._store.get(key)
            if payload is None:
                continue
            result[task_id] = extra_from_dict(payload)
        return result

    def upsert(self, extra: TaskExtra) -> None:
        self._store.put(self._key(extra.task_id), extra_to_dict(extra))

    def mark_orphaned(self, task_id: str, orphaned: bool = True) -> None:
        payload = self._store.get(self._key(task_id)) or {"task_id": task_id}
        payload["orphaned"] = bool(orphaned)
        payload["updated_at_utc"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self._store.put(self._key(task_id), payload)


class S3PeopleStore:
    def __init__(self, store: _S3JsonStore, key: str) -> None:
        self._store = store
        self._key = str(key).strip()

    def get(self) -> PeopleSnapshot | None:
        payload = self._store.get(self._key)
        if payload is None:
            return None
        return people_from_dict(payload)

    def put(self, snapshot: PeopleSnapshot) -> None:
        self._store.put(self._key, people_to_dict(snapshot))


def build_s3_stores(
    *,
    bucket: str,
    endpoint_url: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
    raw_key: str,
    prep_key: str,
    extra_prefix: str,
    people_key: str,
) -> tuple[S3RawCache, S3PrepCache, S3ExtraStore, S3PeopleStore]:
    store = _S3JsonStore(
        bucket=bucket,
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return (
        S3RawCache(store, raw_key),
        S3PrepCache(store, prep_key),
        S3ExtraStore(store, extra_prefix),
        S3PeopleStore(store, people_key),
    )
