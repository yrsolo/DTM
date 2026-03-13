import importlib
import os
import sys
import unittest
from unittest.mock import patch


class ImportSafetyTestCase(unittest.TestCase):
    def _assert_safe_import(self, module_name: str, export_name: str) -> None:
        bootstrap = importlib.import_module("src.app.bootstrap")
        sys.modules.pop(module_name, None)

        with patch.dict(os.environ, {}, clear=True):
            with patch.object(
                bootstrap,
                "build_app_context",
                side_effect=AssertionError(f"build_app_context called during import: {module_name}"),
            ):
                module = importlib.import_module(module_name)

        self.assertTrue(hasattr(module, export_name))

    def test_index_import_is_safe_without_runtime_env(self) -> None:
        self._assert_safe_import("index", "handler")

    def test_planner_runtime_entry_import_is_safe_without_runtime_env(self) -> None:
        self._assert_safe_import(
            "src.entrypoints.runtime.planner_runtime_entry",
            "run_planner_runtime",
        )


if __name__ == "__main__":
    unittest.main()
