from __future__ import annotations

import asyncio
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import yaml

from src.platform.integrations.telegram.proxy import MihomoProxySession, TelegramProxySettings


def _subscription(*, group_name: str = "📢 TELEGA", unresolved: bool = False) -> bytes:
    members = ["Авто", "Fast"]
    proxies = [
        {
            "name": "Авто",
            "type": "vless",
            "server": "auto.example",
            "port": 443,
            "uuid": "00000000-0000-0000-0000-000000000001",
        },
        {
            "name": "Fast",
            "type": "vless",
            "server": "fast.example",
            "port": 443,
            "uuid": "00000000-0000-0000-0000-000000000002",
        },
        {
            "name": "Unused",
            "type": "vless",
            "server": "unused.example",
            "port": 443,
            "uuid": "00000000-0000-0000-0000-000000000003",
        },
    ]
    if unresolved:
        members.append("Missing")
    payload = {
        "proxies": proxies,
        "proxy-groups": [
            {
                "name": group_name,
                "type": "url-test",
                "proxies": members,
                "url": "https://telegram.org",
                "tolerance": 600,
            }
        ],
        "rules": ["MATCH,DIRECT"],
    }
    return yaml.safe_dump(payload, allow_unicode=True).encode("utf-8")


class MihomoProxySessionTestCase(unittest.TestCase):
    def _session(self) -> MihomoProxySession:
        return MihomoProxySession(
            TelegramProxySettings(
                subscription_url="https://secret.invalid/config?token=redacted",
                group_name="📢 TELEGA",
                health_url="https://api.telegram.org",
            )
        )

    def test_builds_minimal_loopback_config_and_preserves_member_order(self) -> None:
        session = self._session()
        session._mixed_port = 17890
        session._controller_port = 19090
        session._controller_secret = "controller-secret"

        config = session._build_minimal_config(_subscription())

        self.assertFalse(config["allow-lan"])
        self.assertEqual(config["bind-address"], "127.0.0.1")
        self.assertEqual(config["rules"], ["MATCH,📢 TELEGA"])
        self.assertEqual([item["name"] for item in config["proxies"]], ["Авто", "Fast"])
        group = config["proxy-groups"][0]
        self.assertEqual(group["proxies"], ["Авто", "Fast"])
        self.assertEqual(group["tolerance"], 600)
        self.assertEqual(group["url"], "https://api.telegram.org")
        self.assertFalse(group["lazy"])

    def test_rejects_missing_group(self) -> None:
        session = self._session()
        with self.assertRaisesRegex(ValueError, "telegram_proxy_group_missing"):
            session._build_minimal_config(_subscription(group_name="Other"))

    def test_rejects_unresolved_group_member(self) -> None:
        session = self._session()
        with self.assertRaisesRegex(ValueError, "unresolved_members"):
            session._build_minimal_config(_subscription(unresolved=True))

    def test_rejects_corrupted_yaml(self) -> None:
        session = self._session()
        with self.assertRaises(yaml.YAMLError):
            session._build_minimal_config(b"proxy-groups: [unterminated")

    def test_binary_path_is_resolved_from_deployment_root(self) -> None:
        session = self._session()
        expected_root = Path(__file__).resolve().parents[4]
        self.assertEqual(session._resolve_binary(), (expected_root / "bin/mihomo").resolve())

    def test_uses_stale_last_known_good_config_when_refresh_fails(self) -> None:
        session = self._session()
        with TemporaryDirectory() as tmp_dir:
            cache_path = Path(tmp_dir) / "subscription.yaml"
            cache_path.write_bytes(_subscription())
            os.utime(cache_path, (1, 1))
            with patch.object(session, "_cache_path", return_value=cache_path), patch(
                "src.platform.integrations.telegram.proxy.urlopen",
                side_effect=OSError("offline"),
            ) as mocked_urlopen:
                raw = session._load_subscription()
                mocked_urlopen.assert_called_once()
        self.assertEqual(session._validate_source(raw)["proxy-groups"][0]["name"], "📢 TELEGA")

    def test_refresh_excludes_failed_selected_node_and_pins_next_best(self) -> None:
        session = self._session()
        session._process = type("Process", (), {"poll": lambda self: None})()  # type: ignore[assignment]
        session._controller_port = 9090
        session._controller_secret = "secret"
        session._selected = "Авто"
        with patch.object(
            session,
            "_controller_json",
            return_value={"Авто": 100, "Fast": 150},
        ) as controller_json, patch.object(session, "_controller_select") as controller_select:
            refreshed = asyncio.run(session.refresh(exclude_current=True))

        self.assertTrue(refreshed)
        self.assertEqual(session._selected, "Fast")
        controller_json.assert_called_once_with(ANY)
        controller_select.assert_called_once_with(ANY, "Fast")

    def test_open_and_close_manage_one_scoped_process(self) -> None:
        session = self._session()
        process = MagicMock()
        process.poll.return_value = None
        process.wait.return_value = 0
        with TemporaryDirectory() as tmp_dir:
            binary = Path(tmp_dir) / "mihomo"
            binary.touch()
            with patch.object(session, "_resolve_binary", return_value=binary), patch.object(
                session,
                "_load_subscription",
                return_value=_subscription(),
            ), patch.object(
                session,
                "_free_loopback_port",
                side_effect=[17890, 19090],
            ), patch.object(
                session,
                "_wait_until_ready",
                new=AsyncMock(),
            ), patch.object(
                session,
                "refresh",
                new=AsyncMock(return_value=True),
            ), patch(
                "src.platform.integrations.telegram.proxy.subprocess.Popen",
                return_value=process,
            ) as popen:
                proxy_url = asyncio.run(session.open())
                runtime_dir = session._work_dir
                self.assertEqual(proxy_url, "http://127.0.0.1:17890")
                self.assertIsNotNone(runtime_dir)
                self.assertTrue(runtime_dir.is_dir())
                popen.assert_called_once()
                asyncio.run(session.close())

        process.terminate.assert_called_once()
        self.assertFalse(runtime_dir.exists())


if __name__ == "__main__":
    unittest.main()
