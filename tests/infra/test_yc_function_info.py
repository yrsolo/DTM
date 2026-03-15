from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.infra.yc_function_info import get_function_build_info


class YcFunctionInfoTestCase(unittest.TestCase):
    @patch("src.infra.yc_function_info.get_iam_token", return_value="iam-token")
    @patch("src.infra.yc_function_info.requests.get")
    def test_get_function_build_info_uses_versions_by_tag_endpoint(self, get_mock: Mock, _token_mock: Mock) -> None:
        list_response = Mock()
        list_response.raise_for_status.return_value = None
        list_response.json.return_value = {
            "functions": [
                {"id": "function-1", "name": "dtm"},
            ]
        }
        version_response = Mock()
        version_response.raise_for_status.return_value = None
        version_response.json.return_value = {
            "id": "version-1",
            "createdAt": "2026-03-15T10:00:00+00:00",
            "runtime": "python311",
            "resources": {"memory": "512MB"},
            "executionTimeout": "240s",
            "entrypoint": "index.handler",
            "serviceAccountId": "aje-test",
        }
        get_mock.side_effect = [list_response, version_response]

        result = get_function_build_info(
            folder_id="folder-1",
            function_name="dtm",
            sa_json_credentials="{}",
            sa_key_file="",
        )

        self.assertEqual(result.active_version_id, "version-1")
        self.assertEqual(get_mock.call_args_list[1].kwargs["params"], {"functionId": "function-1", "tag": "$latest"})
        self.assertIn("/versions:byTag", get_mock.call_args_list[1].args[0])


if __name__ == "__main__":
    unittest.main()
