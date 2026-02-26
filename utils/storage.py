"""S3 storage helpers for JSON snapshots."""

import json

import boto3

from config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET,
    S3_ENDPOINT_URL,
)


class S3SnapshotStorage:
    """Save and load JSON snapshots in S3-compatible storage."""

    def __init__(
        self,
        bucket=S3_BUCKET,
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    ):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
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
