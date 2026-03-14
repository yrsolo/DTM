from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.entrypoints.http.dto import HttpRequest
from src.entrypoints.http.task_attachment_read_handler import TaskAttachmentReadHandler


class _FakeAttachmentStore:
    def get_by_attachment_id(self, attachment_id):  # noqa: ANN001
        if attachment_id != "a1":
            return None
        return (
            "task-1",
            SimpleNamespace(
                attachment_id="a1",
                filename_display="spec final.docx",
                status="ready",
                snapshot_visible=True,
                storage_key="attachments/test/task-1/a1-spec-final.docx",
            ),
        )


class _FakeSnapshotEngine:
    def get_attachment_metadata_store(self):
        return _FakeAttachmentStore()


class _FakeStorage:
    def generate_read_url(self, *, key, filename, download, expires_in_seconds=300):  # noqa: ANN001
        action = "download" if download else "view"
        return f"https://example.test/{action}/{key}"


class _FakeCtx:
    def __init__(self) -> None:
        self.deps = {"browser_auth_proxy_secret": "proxy-secret-test"}
        self.cfg = SimpleNamespace(
            runtime=SimpleNamespace(
                runtime=SimpleNamespace(env_default="test"),
                api={"auth_trusted_secret_header": "X-DTM-Proxy-Secret", "auth_trusted_fallback": "masked"}
            )
        )


class TaskAttachmentReadHandlerTestCase(unittest.TestCase):
    def test_view_requires_trusted_full_approved_access(self) -> None:
        import src.entrypoints.http.task_attachment_read_handler as module

        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: _FakeStorage()  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadHandler(_FakeCtx())
            denied = handler.handle(
                HttpRequest(method="GET", path="/test/ops/api/task-attachments/a1/view", is_http_event=True)
            )
            allowed = handler.handle(
                HttpRequest(
                    method="GET",
                    path="/test/ops/api/task-attachments/a1/view",
                    headers={
                        "X-DTM-Proxy-Secret": "proxy-secret-test",
                        "x-dtm-access-mode": "full",
                        "x-dtm-authenticated": "1",
                        "x-dtm-contour": "test",
                        "x-dtm-user-status": "approved",
                    },
                    is_http_event=True,
                )
            )
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]
            module.build_attachment_storage = original_storage  # type: ignore[assignment]

        self.assertIsNotNone(denied)
        self.assertEqual(denied.status, 403)
        self.assertIsNotNone(allowed)
        self.assertEqual(allowed.status, 302)
        self.assertIn("/view/attachments/test/task-1/a1-spec-final.docx", allowed.headers["Location"])

    def test_download_returns_404_for_unknown_attachment(self) -> None:
        import src.entrypoints.http.task_attachment_read_handler as module

        original_engine = module.build_snapshot_engine
        original_storage = module.build_attachment_storage
        module.build_snapshot_engine = lambda _ctx: _FakeSnapshotEngine()  # type: ignore[assignment]
        module.build_attachment_storage = lambda _ctx: _FakeStorage()  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadHandler(_FakeCtx())
            response = handler.handle(
                HttpRequest(
                    method="GET",
                    path="/test/ops/api/task-attachments/missing/download",
                    headers={
                        "X-DTM-Proxy-Secret": "proxy-secret-test",
                        "x-dtm-access-mode": "full",
                        "x-dtm-authenticated": "1",
                        "x-dtm-contour": "test",
                        "x-dtm-user-status": "approved",
                    },
                    is_http_event=True,
                )
            )
        finally:
            module.build_snapshot_engine = original_engine  # type: ignore[assignment]
            module.build_attachment_storage = original_storage  # type: ignore[assignment]

        self.assertIsNotNone(response)
        self.assertEqual(response.status, 404)


if __name__ == "__main__":
    unittest.main()
