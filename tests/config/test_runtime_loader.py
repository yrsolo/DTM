from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from src.config.loader import _merge_runtime_env_overrides, _runtime_from_dict


class RuntimeLoaderTestCase(unittest.TestCase):
    def test_runtime_loader_reads_bottleneck_metrics_level(self) -> None:
        runtime = _runtime_from_dict({"runtime": {"bottleneck_metrics_level": "debug"}})
        self.assertEqual(runtime.runtime.bottleneck_metrics_level, "debug")

    def test_runtime_loader_supports_dev_mode_backward_compat(self) -> None:
        with patch.dict(os.environ, {"DEV_MODE_METRICS": "1"}, clear=False):
            runtime = _merge_runtime_env_overrides(_runtime_from_dict({}))
        self.assertTrue(runtime.runtime.dev_mode_metrics)

    def test_runtime_loader_env_overrides_bottleneck_metrics_level(self) -> None:
        with patch.dict(os.environ, {"BOTTLENECK_METRICS_LEVEL": "stages"}, clear=False):
            runtime = _merge_runtime_env_overrides(_runtime_from_dict({}))
        self.assertEqual(runtime.runtime.bottleneck_metrics_level, "stages")


if __name__ == "__main__":
    unittest.main()
