"""Unit tests for read-model build handler."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.handlers.build_readmodels import handle_build_readmodels


class BuildReadModelsHandlerTestCase(unittest.TestCase):
    def test_handler_builds_and_publishes_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file = str(Path(tmp_dir) / "read_model.json")
            event = {
                "normalized_tasks": [
                    {"task_id": "t1", "title": "Task", "designer_id": "d1", "status": "work", "next_due_at": None}
                ],
                "output_file": output_file,
            }
            result = handle_build_readmodels(event)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["artifact"], "read_models_v1")
            payload = json.loads(Path(output_file).read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["tasks_total"], 1)


if __name__ == "__main__":
    unittest.main()

