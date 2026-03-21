from __future__ import annotations

import asyncio
import json
import unittest

from src.entrypoints.http.runtime_execution import RuntimeExecutionRequest, RuntimeExecutor


class _FakeCtx:
    def __init__(self) -> None:
        self.deps = {"tg_bot_token": "", "default_chat_id": None}


class RuntimeExecutionTestCase(unittest.TestCase):
    def test_returns_runtime_result_payload(self) -> None:
        executor = RuntimeExecutor(_FakeCtx())  # type: ignore[arg-type]

        async def _main_func(_request):  # noqa: ANN001
            return {"artifact": "render_v2", "status": "ok", "render_applied": True}

        response = asyncio.run(
            executor.execute(
                RuntimeExecutionRequest(
                    mode="render_v2",
                    planner_event=None,
                    dry_run=False,
                    mock_external=False,
                    force_refresh=True,
                ),
                main_func=_main_func,
                request_factory=lambda **kwargs: kwargs,
                is_http_event=True,
            )
        )

        self.assertEqual(response.status, 200)
        payload = json.loads(response.body)
        self.assertEqual(payload.get("artifact"), "render_v2")
        self.assertTrue(payload.get("render_applied"))

    def test_returns_no_result_fallback_payload(self) -> None:
        executor = RuntimeExecutor(_FakeCtx())  # type: ignore[arg-type]

        async def _main_func(_request):  # noqa: ANN001
            return None

        response = asyncio.run(
            executor.execute(
                RuntimeExecutionRequest(
                    mode="sync-only",
                    planner_event=None,
                    dry_run=False,
                    mock_external=False,
                    force_refresh=False,
                ),
                main_func=_main_func,
                request_factory=lambda **kwargs: kwargs,
                is_http_event=True,
            )
        )

        self.assertEqual(response.status, 200)
        payload = json.loads(response.body)
        self.assertEqual(payload.get("artifact"), "dtm_runtime_ok_no_result")
        self.assertEqual(payload.get("mode"), "sync-only")


if __name__ == "__main__":
    unittest.main()
