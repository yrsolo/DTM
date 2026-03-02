"""Unit tests for read-model publication helper."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.services.readmodels.publisher import publish_read_model_to_file


class ReadModelPublisherTestCase(unittest.TestCase):
    def test_publishes_json_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = Path(tmp_dir) / "rm.json"
            payload = {"artifact": "read_models_v1", "summary": {"tasks_total": 1}}
            written = publish_read_model_to_file(payload, target)
            self.assertEqual(written, target)
            loaded = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(loaded["artifact"], "read_models_v1")


if __name__ == "__main__":
    unittest.main()

