from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from src.app.context import AppContext
from src.services.errors import PermanentError, TransientError, UserError


def _safe_filename(name: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(name or "").strip())
    return text.strip("-") or "file.bin"


def _content_disposition_filename(name: str) -> str:
    text = str(name or "").replace('"', "").replace("\r", "").replace("\n", "").strip()
    return text or "file.bin"


@dataclass(frozen=True, slots=True)
class AttachmentStorage:
    bucket: str
    endpoint_url: str | None
    aws_access_key_id: str | None
    aws_secret_access_key: str | None

    def _client(self):
        try:
            import boto3  # type: ignore
        except Exception as error:
            raise PermanentError("Attachment storage client is unavailable.", code="s3_sdk_missing") from error
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    def build_object_key(self, *, env_name: str, task_id: str, attachment_id: str, filename: str) -> str:
        safe_name = _safe_filename(filename)
        return f"attachments/{str(env_name or '').strip().lower() or 'dev'}/{str(task_id or '').strip()}/{str(attachment_id or '').strip()}-{safe_name}"

    def generate_upload_contract(
        self,
        *,
        key: str,
        mime_type: str,
        expires_in_seconds: int = 900,
    ) -> dict[str, Any]:
        client = self._client()
        try:
            upload_url = client.generate_presigned_url(
                "put_object",
                Params={"Bucket": self.bucket, "Key": key, "ContentType": mime_type},
                ExpiresIn=int(expires_in_seconds),
                HttpMethod="PUT",
            )
        except Exception as error:
            raise TransientError(str(error), code="attachment_upload_contract_failed") from error
        return {
            "method": "PUT",
            "uploadUrl": upload_url,
            "headers": {"Content-Type": mime_type},
            "expiresIn": int(expires_in_seconds),
        }

    def head_object(self, *, key: str) -> dict[str, Any]:
        client = self._client()
        try:
            return dict(client.head_object(Bucket=self.bucket, Key=key) or {})
        except Exception as error:
            raise UserError("Uploaded object was not found.", code="attachment_object_missing") from error

    def delete_object(self, *, key: str) -> None:
        client = self._client()
        try:
            client.delete_object(Bucket=self.bucket, Key=key)
        except Exception as error:
            raise TransientError(str(error), code="attachment_delete_failed") from error

    def generate_read_url(
        self,
        *,
        key: str,
        filename: str,
        download: bool,
        expires_in_seconds: int = 300,
    ) -> str:
        client = self._client()
        disposition = "attachment" if download else "inline"
        safe_name = _content_disposition_filename(filename)
        try:
            return str(
                client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket,
                        "Key": key,
                        "ResponseContentDisposition": f'{disposition}; filename="{safe_name}"',
                    },
                    ExpiresIn=int(expires_in_seconds),
                    HttpMethod="GET",
                )
            )
        except Exception as error:
            raise TransientError(str(error), code="attachment_read_url_failed") from error


def build_attachment_storage(ctx: AppContext) -> AttachmentStorage:
    return AttachmentStorage(
        bucket=str(ctx.cfg.runtime.snapshot_engine.bucket or "").strip(),
        endpoint_url=str(ctx.cfg.db.object_storage.get("endpoint_url_default", "")).strip() or None,
        aws_access_key_id=ctx.deps.get("aws_access_key_id"),
        aws_secret_access_key=ctx.deps.get("aws_secret_access_key"),
    )
