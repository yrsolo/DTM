"""S3 storage helpers for JSON snapshots."""

from __future__ import annotations

import json
import os

import boto3


class S3SnapshotStorage:
    """Save and load JSON snapshots in S3-compatible storage."""

    def __init__(
        self,
        bucket=None,
        endpoint_url=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
    ):
        self.bucket = bucket or os.environ.get("S3_BUCKET", "")
        if not self.bucket:
            raise ValueError("S3_BUCKET is required for Object Storage artifact upload")
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url or os.environ.get("S3_ENDPOINT_URL", ""),
            aws_access_key_id=aws_access_key_id or os.environ.get("AWS_ACCESS_KEY_ID", ""),
            aws_secret_access_key=aws_secret_access_key or os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        )

    def upload_json(self, key, payload):
        """Upload JSON payload to bucket by object key."""
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType="application/json; charset=utf-8",
        )

    def download_json(self, key):
        """Download JSON payload from bucket by object key."""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return json.loads(response["Body"].read().decode("utf-8"))
