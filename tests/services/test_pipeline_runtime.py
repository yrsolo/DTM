"""Smoke tests for snapshot-engine timer pipeline."""

from __future__ import annotations

import importlib
import unittest
from types import SimpleNamespace

from src.app.context import AppContext


def _import_timer_pipeline():
    module = importlib.import_module("src.services.timer_pipeline")
    return importlib.reload(module)


class _FakeEngine:
    def __init__(self, result=None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.calls: list[dict] = []

    def update(self, *, task_source, force: bool):  # noqa: ANN001
        self.calls.append({"task_source": task_source, "force": force})
        if self.error is not None:
            raise self.error
        return self.result


class TimerPipelineSmokeTestCase(unittest.TestCase):
    def _ctx(self) -> AppContext:
        return AppContext(cfg=SimpleNamespace(runtime=SimpleNamespace()), deps={})

    def test_pipeline_returns_early_for_non_timer_mode(self) -> None:
        module = _import_timer_pipeline()
        fake_engine = _FakeEngine(
            result=SimpleNamespace(
                source_id="sheet:test",
                source_hash="hash",
                changed=True,
                raw_written=True,
                prep_written=True,
            )
        )
        module.build_snapshot_engine = lambda _ctx: fake_engine  # type: ignore[assignment]
        task_source = SimpleNamespace(source_id="sheet:test")
        request = module.RunRequest(mode="reminders-only", force_refresh=False, task_source=task_source)

        result = module.TimerPipeline(self._ctx()).run(request)

        self.assertEqual(result, module.PipelineResult(sync_deferred=False, readmodel_deferred=False, ttl_skip=False))
        self.assertEqual(fake_engine.calls, [])

    def test_pipeline_calls_snapshot_update_for_timer_mode(self) -> None:
        module = _import_timer_pipeline()
        fake_engine = _FakeEngine(
            result=SimpleNamespace(
                source_id="sheet:test",
                source_hash="hash",
                changed=True,
                raw_written=True,
                prep_written=True,
            )
        )
        module.build_snapshot_engine = lambda _ctx: fake_engine  # type: ignore[assignment]
        task_source = SimpleNamespace(source_id="sheet:test")
        request = module.RunRequest(mode="timer", force_refresh=False, task_source=task_source)

        result = module.TimerPipeline(self._ctx()).run(request)

        self.assertFalse(result.sync_deferred)
        self.assertFalse(result.readmodel_deferred)
        self.assertFalse(result.ttl_skip)
        self.assertEqual(len(fake_engine.calls), 1)
        self.assertIs(fake_engine.calls[0]["task_source"], task_source)
        self.assertFalse(fake_engine.calls[0]["force"])

    def test_pipeline_sync_only_sets_ttl_skip_when_unchanged(self) -> None:
        module = _import_timer_pipeline()
        fake_engine = _FakeEngine(
            result=SimpleNamespace(
                source_id="sheet:test",
                source_hash="hash",
                changed=False,
                raw_written=False,
                prep_written=False,
            )
        )
        module.build_snapshot_engine = lambda _ctx: fake_engine  # type: ignore[assignment]
        task_source = SimpleNamespace(source_id="sheet:test")
        request = module.RunRequest(mode="sync-only", force_refresh=True, task_source=task_source)

        result = module.TimerPipeline(self._ctx()).run(request)

        self.assertFalse(result.sync_deferred)
        self.assertTrue(result.ttl_skip)
        self.assertEqual(len(fake_engine.calls), 1)
        self.assertTrue(fake_engine.calls[0]["force"])

    def test_pipeline_marks_sync_deferred_on_engine_error(self) -> None:
        module = _import_timer_pipeline()
        fake_engine = _FakeEngine(error=RuntimeError("boom"))
        module.build_snapshot_engine = lambda _ctx: fake_engine  # type: ignore[assignment]
        task_source = SimpleNamespace(source_id="sheet:test")
        request = module.RunRequest(mode="timer", force_refresh=False, task_source=task_source)

        result = module.TimerPipeline(self._ctx()).run(request)

        self.assertTrue(result.sync_deferred)
        self.assertFalse(result.readmodel_deferred)
        self.assertFalse(result.ttl_skip)


if __name__ == "__main__":
    unittest.main()
