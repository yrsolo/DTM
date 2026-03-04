from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from src.entrypoints.jobs.hash_gate_job import resolve_allow_sync_by_hash_gate


@dataclass
class _TaskStub:
    id: str
    brand: str
    format_: str
    project_name: str
    customer: str
    designer: str
    raw_timing: str
    status: str


class _RepoStub:
    def __init__(self) -> None:
        self.source_sheet_info = type("SheetInfo", (), {"spreadsheet_name": "sheet-test"})()
        self._tasks = [
            _TaskStub(
                id="1",
                brand="Brand",
                format_="Format",
                project_name="Project",
                customer="Customer",
                designer="Designer",
                raw_timing="raw",
                status="work",
            )
        ]

    def get_all_tasks(self):
        return list(self._tasks)


class HashGateJobTestCase(unittest.TestCase):
    def test_returns_true_when_gate_disabled(self) -> None:
        allow_sync = resolve_allow_sync_by_hash_gate(
            enabled=False,
            mode="timer",
            source_task_repository=_RepoStub(),
            state_file_path=str(Path(tempfile.gettempdir()) / "dtm_hash_gate_disabled.json"),
            safe_print=lambda _: None,
        )
        self.assertTrue(allow_sync)

    def test_detects_no_changes_after_first_state_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            state_file = str(Path(temp_dir) / "gate.json")
            repo = _RepoStub()
            first = resolve_allow_sync_by_hash_gate(
                enabled=True,
                mode="timer",
                source_task_repository=repo,
                state_file_path=state_file,
                safe_print=lambda _: None,
            )
            second = resolve_allow_sync_by_hash_gate(
                enabled=True,
                mode="timer",
                source_task_repository=repo,
                state_file_path=state_file,
                safe_print=lambda _: None,
            )
            self.assertTrue(first)
            self.assertFalse(second)


if __name__ == "__main__":
    unittest.main()
