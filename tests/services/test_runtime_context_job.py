from __future__ import annotations

import unittest

from src.entrypoints.jobs.runtime_context_job import RuntimeContextRequest, resolve_runtime_context


class _TimerShellStub:
    def __init__(self) -> None:
        self.calls = 0

    def run(self, app_context):  # noqa: ANN001, ARG002
        self.calls += 1
        return {"steps": [1, 2]}


class RuntimeContextJobTestCase(unittest.TestCase):
    def test_timer_mode_runs_shell_and_defaults_mock_external(self) -> None:
        shell = _TimerShellStub()
        ctx = resolve_runtime_context(
            RuntimeContextRequest(
                mode="timer",
                event=None,
                dry_run=False,
                mock_external=None,
                force_refresh_raw=None,
                triggers=["timer"],
                force_refresh_default=True,
                resolve_run_mode=lambda **kwargs: kwargs["mode"],
                timer_job_shell=shell,
                app_context=object(),
            )
        )
        self.assertEqual(ctx.mode, "timer")
        self.assertFalse(ctx.mock_external)
        self.assertTrue(ctx.force_refresh)
        self.assertEqual(shell.calls, 1)

    def test_test_mode_defaults_mock_external_true(self) -> None:
        shell = _TimerShellStub()
        ctx = resolve_runtime_context(
            RuntimeContextRequest(
                mode="test",
                event=None,
                dry_run=False,
                mock_external=None,
                force_refresh_raw=False,
                triggers=["timer"],
                force_refresh_default=True,
                resolve_run_mode=lambda **kwargs: kwargs["mode"],
                timer_job_shell=shell,
                app_context=object(),
            )
        )
        self.assertEqual(ctx.mode, "test")
        self.assertTrue(ctx.mock_external)
        self.assertFalse(ctx.force_refresh)
        self.assertEqual(shell.calls, 0)


if __name__ == "__main__":
    unittest.main()
