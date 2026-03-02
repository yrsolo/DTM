"""Unit tests for migration sync handler."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.handlers.sync import handle_sync


class SyncHandlerTestCase(unittest.TestCase):
    def test_hash_gate_skips_second_unchanged_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_file = str(Path(tmp_dir) / "state.json")
            event = {
                "source_id": "google-sheet:test",
                "state_file": state_file,
                "source_payload": {"rows": [{"id": "1", "title": "Task"}]},
            }
            first = handle_sync(event)
            second = handle_sync(event)

            self.assertFalse(first["sync_skipped"])
            self.assertTrue(second["sync_skipped"])
            self.assertEqual(first["source_hash"], second["source_hash"])


if __name__ == "__main__":
    unittest.main()

