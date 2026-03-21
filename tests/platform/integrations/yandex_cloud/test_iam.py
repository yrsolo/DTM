from __future__ import annotations

import base64
import json
import tempfile
import unittest
from unittest.mock import patch

from src.platform.integrations.yandex_cloud.iam import get_iam_token, load_service_account_key


class YcIamHelpersTestCase(unittest.TestCase):
    def test_load_service_account_key_from_raw_json(self) -> None:
        payload = {"service_account_id": "aje-test", "id": "kid", "private_key": "pem"}
        loaded = load_service_account_key(json.dumps(payload), "")
        self.assertEqual(loaded["service_account_id"], "aje-test")

    def test_load_service_account_key_from_base64_json(self) -> None:
        payload = {"service_account_id": "aje-test-b64", "id": "kid", "private_key": "pem"}
        raw = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
        loaded = load_service_account_key(raw, "")
        self.assertEqual(loaded["service_account_id"], "aje-test-b64")

    def test_load_service_account_key_from_file(self) -> None:
        payload = {"service_account_id": "aje-test-file", "id": "kid", "private_key": "pem"}
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json", delete=False) as fh:
            fh.write(json.dumps(payload))
            fh.flush()
            loaded = load_service_account_key("", fh.name)
        self.assertEqual(loaded["service_account_id"], "aje-test-file")

    @patch("src.platform.integrations.yandex_cloud.iam.requests.get")
    def test_get_iam_token_falls_back_to_metadata(self, mock_get) -> None:
        mock_get.return_value.json.return_value = {"access_token": "metadata-token"}
        mock_get.return_value.raise_for_status.return_value = None

        token = get_iam_token("", "")

        self.assertEqual(token, "metadata-token")


if __name__ == "__main__":
    unittest.main()
