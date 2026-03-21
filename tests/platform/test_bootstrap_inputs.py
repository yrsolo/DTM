from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import src.platform.bootstrap as bootstrap_module


class BootstrapInputsTestCase(unittest.TestCase):
    def test_build_base_bootstrap_deps_uses_cfg_defaults_and_env_overrides(self) -> None:
        cfg = bootstrap_module.load_config()
        with patch.dict(
            os.environ,
            {
                "SOURCE_SHEET_NAME": "Source Book",
                "TARGET_SHEET_NAME": "Target Book",
                "TG_TOKEN": "tg-token",
                "TG_BOT_USERNAME": "@dtm_bot",
                "DEFAULT_CHAT_ID": "-1001",
                "YC_SA_JSON_CREDENTIALS": "{json}",
                "YC_SA_KEY_FILE": "/tmp/key.json",
                "MIGRATION_STORE_FILE": "work/artifacts/custom/store.json",
            },
            clear=False,
        ):
            deps = bootstrap_module._build_base_bootstrap_deps(cfg, structured_logger=object())

        self.assertEqual(deps["sheet_info"]["spreadsheet_name"], "Target Book")
        self.assertEqual(cfg.tables.google_sheets["source_sheet_name_default"], "Source Book")
        self.assertEqual(deps["tg_bot_token"], "tg-token")
        self.assertEqual(deps["tg_bot_username"], "@dtm_bot")
        self.assertEqual(deps["default_chat_id"], "-1001")
        self.assertEqual(deps["yc_sa_json_credentials"], "{json}")
        self.assertEqual(deps["yc_sa_key_file"], "/tmp/key.json")
        self.assertEqual(deps["migration_store_file"], "work/artifacts/custom/store.json")

    def test_resolve_google_key_json_path_supports_raw_json_env(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            temp_root = Path(tmp_dir)
            fake_temp_file = temp_root / "dtm_google_key.json"
            with patch.object(bootstrap_module.tempfile, "gettempdir", return_value=str(temp_root)), patch.dict(
                os.environ,
                {"GOOGLE_KEY_JSON": '{"type":"service_account"}', "GOOGLE_KEY_JSON_PATH": "", "GOOGLE_KEY_JSON_B64": ""},
                clear=False,
            ):
                resolved = bootstrap_module._resolve_google_key_json_path()
                self.assertEqual(resolved, str(fake_temp_file))
                self.assertTrue(Path(resolved).exists())
                self.assertEqual(Path(resolved).read_text(encoding="utf-8"), '{"type":"service_account"}')


if __name__ == "__main__":
    unittest.main()
