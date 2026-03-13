from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src.config.loader import _merge_runtime_env_overrides, _runtime_from_dict, load_config


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

    def test_runtime_loader_reads_metrics_delivery_mode(self) -> None:
        runtime = _runtime_from_dict({"runtime": {"metrics_delivery_mode": "off"}})
        self.assertEqual(runtime.runtime.metrics_delivery_mode, "off")

    def test_runtime_loader_env_overrides_metrics_delivery_mode(self) -> None:
        with patch.dict(os.environ, {"METRICS_DELIVERY_MODE": "buffered"}, clear=False):
            runtime = _merge_runtime_env_overrides(_runtime_from_dict({"runtime": {"metrics_delivery_mode": "off"}}))
        self.assertEqual(runtime.runtime.metrics_delivery_mode, "buffered")

    def test_load_config_allows_same_prod_spreadsheet_when_only_tasks_sheet_is_forbidden(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            config_dir = Path(tmp_dir)
            (config_dir / "runtime.yaml").write_text("runtime:\n  env_default: prod\n", encoding="utf-8")
            (config_dir / "tables.yaml").write_text(
                "\n".join(
                    [
                        "google_sheets:",
                        "  source_sheet_name_default: Спонсорские ТНТ",
                        "  target_sheet_name_default: Спонсорские ТНТ ТЕСТ",
                        "  target_sheet_name_prod_default: Спонсорские ТНТ",
                        "sheet_names:",
                        "  tasks: ТАБЛИЧКА",
                        "  task_calendar: Задачи",
                        "  designers: Дизайнеры",
                    ]
                ),
                encoding="utf-8",
            )
            for name in ("db.yaml", "llm.yaml", "mapping.yaml", "deploy.yaml"):
                (config_dir / name).write_text("{}\n", encoding="utf-8")

            cfg = load_config(config_dir)

        self.assertEqual(cfg.runtime.runtime.env_default, "prod")
        self.assertEqual(cfg.tables.google_sheets["source_sheet_name_default"], "Спонсорские ТНТ")
        self.assertEqual(cfg.tables.google_sheets["target_sheet_name_prod_default"], "Спонсорские ТНТ")


if __name__ == "__main__":
    unittest.main()
