from __future__ import annotations

import unittest
from types import SimpleNamespace

from src.contexts.access_api.internal import task_attachment_read_api as access_task_attachment_read_module
from src.entrypoints.http.dto import HttpRequest
from src.contexts.access_api.internal.task_attachment_read_api import TaskAttachmentReadApi


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
                kind="docx",
            ),
        )


class _FakeSnapshotEngine:
    def get_attachment_metadata_store(self):
        return _FakeAttachmentStore()


class _FakeDocAttachmentStore:
    def __init__(self, *, preview_state: str, derived_preview_ref: str = "") -> None:
        self._preview_state = preview_state
        self._derived_preview_ref = derived_preview_ref

    def get_by_attachment_id(self, attachment_id):  # noqa: ANN001
        if attachment_id != "doc-1":
            return None
        return (
            "task-1",
            SimpleNamespace(
                attachment_id="doc-1",
                filename_display="legacy.doc",
                status="ready",
                snapshot_visible=True,
                storage_key="attachments/test/task-1/doc-1-legacy.doc",
                kind="doc",
                preview_state=self._preview_state,
                derived_preview_ref=self._derived_preview_ref,
            ),
        )


class _FakeDocEngine:
    def __init__(self, store) -> None:  # noqa: ANN001
        self._store = store

    def get_attachment_metadata_store(self):
        return self._store


class _FakeStorage:
    def generate_read_url(self, *, key, filename, download, expires_in_seconds=300):  # noqa: ANN001
        action = "download" if download else "view"
        return f"https://example.test/{action}/{key}"


class _FakeResolver:
    def __init__(self, *, store) -> None:  # noqa: ANN001
        self._store = store

    def resolve(self, *, attachment_id, access, download):  # noqa: ANN001
        from src.contexts.attachments.internal import AttachmentReadResolver

        return AttachmentReadResolver(
            metadata_store=self._store,
            storage=_FakeStorage(),
        ).resolve(attachment_id=attachment_id, access=access, download=download)


class _FakeCtx:
    def __init__(self) -> None:
        self.deps = {"browser_auth_proxy_secret": "proxy-secret-test"}
        self.cfg = SimpleNamespace(
            runtime=SimpleNamespace(
                runtime=SimpleNamespace(env_default="test"),
                api={"auth_trusted_secret_header": "X-DTM-Proxy-Secret", "auth_trusted_fallback": "masked"}
            )
        )


class TaskAttachmentReadApiTestCase(unittest.TestCase):
    def test_view_requires_trusted_full_approved_access(self) -> None:
        original_resolver = access_task_attachment_read_module.get_attachment_read_capability
        original_access_resolver = access_task_attachment_read_module.get_attachment_read_capability
        access_task_attachment_read_module.get_attachment_read_capability = lambda _ctx: _FakeResolver(store=_FakeAttachmentStore())  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadApi(_FakeCtx())
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
            access_task_attachment_read_module.get_attachment_read_capability = original_access_resolver  # type: ignore[assignment]

        self.assertIsNotNone(denied)
        self.assertEqual(denied.status, 403)
        self.assertIsNotNone(allowed)
        self.assertEqual(allowed.status, 302)
        self.assertIn("/view/attachments/test/task-1/a1-spec-final.docx", allowed.headers["Location"])

    def test_download_returns_404_for_unknown_attachment(self) -> None:
        original_resolver = access_task_attachment_read_module.get_attachment_read_capability
        original_access_resolver = access_task_attachment_read_module.get_attachment_read_capability
        access_task_attachment_read_module.get_attachment_read_capability = lambda _ctx: _FakeResolver(store=_FakeAttachmentStore())  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadApi(_FakeCtx())
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
            access_task_attachment_read_module.get_attachment_read_capability = original_access_resolver  # type: ignore[assignment]

        self.assertIsNotNone(response)
        self.assertEqual(response.status, 404)

    def test_view_doc_preview_redirects_when_ready(self) -> None:
        original_resolver = access_task_attachment_read_module.get_attachment_read_capability
        original_access_resolver = access_task_attachment_read_module.get_attachment_read_capability
        doc_store = _FakeDocAttachmentStore(preview_state="ready", derived_preview_ref="attachments/test/task-1/doc-1/preview.pdf")
        access_task_attachment_read_module.get_attachment_read_capability = lambda _ctx: _FakeResolver(store=doc_store)  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadApi(_FakeCtx())
            allowed = handler.handle(
                HttpRequest(
                    method="GET",
                    path="/test/ops/api/task-attachments/doc-1/view",
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
            access_task_attachment_read_module.get_attachment_read_capability = original_access_resolver  # type: ignore[assignment]

        self.assertIsNotNone(allowed)
        self.assertEqual(allowed.status, 302)
        self.assertIn("/view/attachments/test/task-1/doc-1/preview.pdf", allowed.headers["Location"])

    def test_view_doc_preview_returns_pending_when_not_ready(self) -> None:
        original_resolver = access_task_attachment_read_module.get_attachment_read_capability
        original_access_resolver = access_task_attachment_read_module.get_attachment_read_capability
        doc_store = _FakeDocAttachmentStore(preview_state="pending")
        access_task_attachment_read_module.get_attachment_read_capability = lambda _ctx: _FakeResolver(store=doc_store)  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadApi(_FakeCtx())
            response = handler.handle(
                HttpRequest(
                    method="GET",
                    path="/test/ops/api/task-attachments/doc-1/view",
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
            access_task_attachment_read_module.get_attachment_read_capability = original_access_resolver  # type: ignore[assignment]

        self.assertIsNotNone(response)
        self.assertEqual(response.status, 409)

    def test_view_doc_preview_returns_unavailable_when_failed(self) -> None:
        original_resolver = access_task_attachment_read_module.get_attachment_read_capability
        original_access_resolver = access_task_attachment_read_module.get_attachment_read_capability
        doc_store = _FakeDocAttachmentStore(preview_state="failed")
        access_task_attachment_read_module.get_attachment_read_capability = lambda _ctx: _FakeResolver(store=doc_store)  # type: ignore[assignment]
        try:
            handler = TaskAttachmentReadApi(_FakeCtx())
            response = handler.handle(
                HttpRequest(
                    method="GET",
                    path="/test/ops/api/task-attachments/doc-1/view",
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
            access_task_attachment_read_module.get_attachment_read_capability = original_access_resolver  # type: ignore[assignment]

        self.assertIsNotNone(response)
        self.assertEqual(response.status, 503)


if __name__ == "__main__":
    unittest.main()
