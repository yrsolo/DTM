"""S3 storage helpers for JSON snapshots."""

from __future__ import annotations

import json
import os
from typing import Any

import boto3


def _env(name: str) -> str:
    """Read trimmed environment value for storage settings."""
    return os.environ.get(name, "").strip()


class S3SnapshotStorage:
    """Save and load JSON snapshots in S3-compatible storage."""

    def __init__(
        self,
        bucket: str | None = None,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        self.bucket = (bucket or _env("S3_BUCKET")).strip()
        if not self.bucket:
            raise ValueError("S3_BUCKET is required for Object Storage artifact upload")
        self.client = boto3.client(
            "s3",
            endpoint_url=(endpoint_url or _env("S3_ENDPOINT_URL")) or None,
            aws_access_key_id=(aws_access_key_id or _env("AWS_ACCESS_KEY_ID")) or None,
            aws_secret_access_key=(aws_secret_access_key or _env("AWS_SECRET_ACCESS_KEY")) or None,
        )

    def upload_json(self, key: str, payload: Any) -> None:
        """Upload JSON payload to bucket by object key."""
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType="application/json; charset=utf-8",
        )

    def download_json(self, key: str) -> dict[str, Any]:
        """Download JSON payload from bucket by object key."""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response["Body"].read().decode("utf-8"))
