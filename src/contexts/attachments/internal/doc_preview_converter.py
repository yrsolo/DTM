from __future__ import annotations

from dataclasses import dataclass

import requests

from src.platform.errors import TransientError


@dataclass(frozen=True, slots=True)
class DocPreviewConversionResult:
    status: str
    attachment_id: str
    preview_mime: str
    preview_size_bytes: int | None
    error_code: str | None
    error_message: str | None


class DocPreviewConverter:
    def __init__(
        self,
        *,
        base_url: str,
        shared_token: str,
        timeout_seconds: float = 30.0,
    ) -> None:
        self._base_url = str(base_url or "").strip().rstrip("/")
        self._shared_token = str(shared_token or "").strip()
        self._timeout_seconds = float(timeout_seconds or 30.0)

    def convert_doc_to_pdf(
        self,
        *,
        attachment_id: str,
        source_url: str,
        target_url: str,
        source_filename: str,
        target_filename: str = "preview.pdf",
        request_id: str | None = None,
    ) -> DocPreviewConversionResult:
        if not self._base_url:
            raise TransientError("Converter base URL is missing.", code="doc_preview_converter_unconfigured")
        headers = {"Content-Type": "application/json"}
        if self._shared_token:
            headers["X-Shared-Token"] = self._shared_token
        payload = {
            "attachment_id": str(attachment_id or "").strip(),
            "source_url": str(source_url or "").strip(),
            "target_url": str(target_url or "").strip(),
            "source_filename": str(source_filename or "").strip(),
            "target_filename": str(target_filename or "preview.pdf").strip(),
            "request_id": str(request_id or "").strip() or None,
        }
        try:
            response = requests.post(
                f"{self._base_url}/convert/doc-to-pdf",
                json=payload,
                headers=headers,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as error:
            raise TransientError(str(error), code="doc_preview_converter_unavailable") from error
        if response.status_code != 200:
            raise TransientError(
                f"Converter returned HTTP {response.status_code}",
                code="doc_preview_converter_failed",
            )
        data = response.json() if response.content else {}
        return DocPreviewConversionResult(
            status=str(data.get("status", "")).strip(),
            attachment_id=str(data.get("attachment_id", "")).strip(),
            preview_mime=str(data.get("preview_mime", "application/pdf")).strip(),
            preview_size_bytes=data.get("preview_size_bytes"),
            error_code=str(data.get("error_code", "")).strip() or None,
            error_message=str(data.get("error_message", "")).strip() or None,
        )
