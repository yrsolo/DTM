"""Scoped Mihomo transport for outbound Telegram delivery."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import secrets
import shutil
import socket
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from time import monotonic, sleep, time
from typing import Any
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import yaml

_BUILTIN_PROXIES = {"DIRECT", "REJECT", "REJECT-DROP", "PASS", "COMPATIBLE"}


@dataclass(frozen=True, slots=True)
class TelegramProxySettings:
    env_name: str = "unknown"
    delivery_transport: str = "adaptive_proxy"
    subscription_url: str = ""
    group_name: str = "📢 TELEGA"
    health_url: str = "https://api.telegram.org"
    startup_timeout_seconds: float = 10.0
    subscription_timeout_seconds: float = 20.0
    subscription_retry_attempts: int = 3
    subscription_retry_backoff_seconds: float = 2.0
    health_timeout_seconds: float = 5.0
    cache_ttl_seconds: int = 300
    direct_fallback: bool = True
    binary_path: str = "bin/mihomo"


class MihomoProxySession:
    """Start one loopback-only Mihomo process for a delivery batch."""

    def __init__(
        self,
        settings: TelegramProxySettings,
        *,
        metrics: Any = None,
        logger: Any = None,
    ) -> None:
        self.settings = settings
        self._metrics = metrics
        self._logger = logger
        self._process: subprocess.Popen[bytes] | None = None
        self._work_dir: Path | None = None
        self._config_path: Path | None = None
        self._mixed_port = 0
        self._controller_port = 0
        self._controller_secret = ""
        self._selected = ""

    @property
    def proxy_url(self) -> str | None:
        if self._process is None or self._process.poll() is not None or not self._mixed_port:
            return None
        return f"http://127.0.0.1:{self._mixed_port}"

    @property
    def direct_fallback(self) -> bool:
        return bool(self.settings.direct_fallback)

    async def open(self) -> str | None:
        if str(self.settings.delivery_transport).strip().lower() != "adaptive_proxy":
            return None
        if not self.settings.subscription_url:
            self._counter("dtm.telegram.proxy_refresh_total", result="missing_subscription")
            return None
        binary = self._resolve_binary()
        if not binary.is_file():
            self._warning("telegram_proxy_binary_unavailable")
            self._counter("dtm.telegram.proxy_refresh_total", result="missing_binary")
            return None
        started = monotonic()
        try:
            raw = await asyncio.to_thread(self._load_subscription)
            self._mixed_port = self._free_loopback_port()
            self._controller_port = self._free_loopback_port()
            self._controller_secret = secrets.token_urlsafe(24)
            config = self._build_minimal_config(raw)
            self._write_runtime_config(config)
            self._process = subprocess.Popen(
                [str(binary), "-d", str(self._work_dir), "-f", str(self._config_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            await self._wait_until_ready()
            await self.refresh()
        except Exception as error:
            self._warning("telegram_proxy_start_failed", error_type=type(error).__name__)
            self._counter("dtm.telegram.proxy_refresh_total", result="failed")
            await self.close()
            return None
        self._timing("dtm.telegram.proxy_health_ms", (monotonic() - started) * 1000.0)
        self._counter("dtm.telegram.proxy_refresh_total", result="success")
        return self.proxy_url

    async def refresh(self, *, exclude_current: bool = False) -> bool:
        if self._process is None or self._process.poll() is not None:
            return False
        params = urlencode(
            {
                "url": self.settings.health_url,
                "timeout": max(1, int(self.settings.health_timeout_seconds * 1000)),
            }
        )
        group_path = quote(self.settings.group_name, safe="")
        delays = await asyncio.to_thread(
            self._controller_json,
            f"/group/{group_path}/delay?{params}",
        )
        checked = len(dict(delays or {}))
        healthy = sum(
            1
            for value in dict(delays or {}).values()
            if isinstance(value, (int, float)) and value > 0
        )
        self._gauge("dtm.telegram.proxy_nodes_checked", float(checked))
        self._gauge("dtm.telegram.proxy_nodes_healthy", float(healthy))
        if healthy <= 0:
            raise RuntimeError("telegram_proxy_no_healthy_nodes")
        if exclude_current and self._selected:
            candidates = sorted(
                (float(delay), str(name))
                for name, delay in dict(delays or {}).items()
                if str(name) != self._selected
                and isinstance(delay, (int, float))
                and delay > 0
            )
            if candidates:
                selected = candidates[0][1]
                await asyncio.to_thread(self._controller_select, group_path, selected)
                self._selected = selected
                return True
        group = await asyncio.to_thread(self._controller_json, f"/group/{group_path}")
        selected = str(dict(group or {}).get("now", "")).strip()
        if not selected:
            raise RuntimeError("telegram_proxy_group_has_no_selection")
        self._selected = selected
        return True

    async def close(self) -> None:
        process = self._process
        self._process = None
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                await asyncio.to_thread(process.wait, 2)
            except subprocess.TimeoutExpired:
                process.kill()
                await asyncio.to_thread(process.wait, 2)
        if self._config_path is not None:
            try:
                self._config_path.unlink(missing_ok=True)
            except OSError:
                pass
        if self._work_dir is not None:
            try:
                shutil.rmtree(self._work_dir)
            except OSError:
                pass
        self._config_path = None
        self._work_dir = None
        self._mixed_port = 0
        self._controller_port = 0
        self._controller_secret = ""
        self._selected = ""

    def _resolve_binary(self) -> Path:
        path = Path(self.settings.binary_path)
        if not path.is_absolute():
            package_root = Path(__file__).resolve().parents[4]
            path = package_root / path
        return path.resolve()

    def _cache_path(self) -> Path:
        cache_key = hashlib.sha256(self.settings.subscription_url.encode("utf-8")).hexdigest()[:12]
        return Path(tempfile.gettempdir()) / f"dtm-telegram-proxy-{cache_key}.yaml"

    def _load_subscription(self) -> bytes:
        cache_path = self._cache_path()
        if cache_path.is_file():
            os.chmod(cache_path, 0o600)
        if cache_path.is_file() and time() - cache_path.stat().st_mtime <= max(
            0, self.settings.cache_ttl_seconds
        ):
            self._counter("dtm.telegram.proxy_cache_total", result="fresh_hit")
            return cache_path.read_bytes()
        try:
            raw = self._download_subscription_with_retries()
            temp_path = cache_path.with_suffix(".tmp")
            temp_path.write_bytes(raw)
            os.chmod(temp_path, 0o600)
            temp_path.replace(cache_path)
            self._counter("dtm.telegram.proxy_cache_total", result="refreshed")
            return raw
        except Exception:
            if cache_path.is_file():
                raw = cache_path.read_bytes()
                self._validate_source(raw)
                self._counter("dtm.telegram.proxy_cache_total", result="stale_hit")
                return raw
            self._counter("dtm.telegram.proxy_cache_total", result="miss")
            raise

    def _download_subscription_with_retries(self) -> bytes:
        attempts = max(1, int(self.settings.subscription_retry_attempts))
        for attempt in range(1, attempts + 1):
            try:
                request = Request(
                    self.settings.subscription_url,
                    headers={"User-Agent": "DTM-Telegram-Transport/1.0"},
                )
                with urlopen(request, timeout=self.settings.subscription_timeout_seconds) as response:
                    raw = response.read()
                self._validate_source(raw)
                return raw
            except OSError as error:
                if attempt >= attempts:
                    raise
                fields: dict[str, Any] = {
                    "attempt": attempt,
                    "max_attempts": attempts,
                    "error_type": type(error).__name__,
                }
                status_code = getattr(error, "code", None)
                if isinstance(status_code, int):
                    fields["http_status"] = status_code
                self._warning("telegram_proxy_subscription_attempt_failed", **fields)
                sleep(max(0.0, self.settings.subscription_retry_backoff_seconds) * attempt)
        raise RuntimeError("telegram_proxy_subscription_retry_exhausted")

    def _validate_source(self, raw: bytes) -> dict[str, Any]:
        data = yaml.safe_load(raw.decode("utf-8-sig")) or {}
        if not isinstance(data, dict):
            raise ValueError("telegram_proxy_subscription_must_be_mapping")
        groups = data.get("proxy-groups")
        if not isinstance(groups, list):
            raise ValueError("telegram_proxy_groups_missing")
        group = next(
            (
                item
                for item in groups
                if isinstance(item, dict)
                and str(item.get("name", "")).strip() == self.settings.group_name
            ),
            None,
        )
        if group is None:
            raise ValueError("telegram_proxy_group_missing")
        return data

    def _build_minimal_config(self, raw: bytes) -> dict[str, Any]:
        source = self._validate_source(raw)
        source_groups = [item for item in source.get("proxy-groups", []) if isinstance(item, dict)]
        group = next(
            dict(item)
            for item in source_groups
            if str(item.get("name", "")).strip() == self.settings.group_name
        )
        members = [str(item) for item in list(group.get("proxies", []) or [])]
        uses = [str(item) for item in list(group.get("use", []) or [])]
        source_proxies = [item for item in source.get("proxies", []) if isinstance(item, dict)]
        selected_proxies = [item for item in source_proxies if str(item.get("name", "")) in members]
        resolved = {str(item.get("name", "")) for item in selected_proxies} | _BUILTIN_PROXIES
        unresolved = [name for name in members if name not in resolved]
        if unresolved:
            raise ValueError("telegram_proxy_group_has_unresolved_members")
        source_providers = source.get("proxy-providers", {})
        providers = {}
        if uses:
            if not isinstance(source_providers, dict):
                raise ValueError("telegram_proxy_provider_mapping_missing")
            providers = {name: source_providers[name] for name in uses if name in source_providers}
            if len(providers) != len(set(uses)):
                raise ValueError("telegram_proxy_group_has_unresolved_providers")
        group.update(
            {
                "url": self.settings.health_url,
                "lazy": False,
                "timeout": max(1, int(self.settings.health_timeout_seconds * 1000)),
            }
        )
        config: dict[str, Any] = {
            "mixed-port": self._mixed_port,
            "allow-lan": False,
            "bind-address": "127.0.0.1",
            "mode": "rule",
            "log-level": "warning",
            "external-controller": f"127.0.0.1:{self._controller_port}",
            "secret": self._controller_secret,
            "proxies": selected_proxies,
            "proxy-groups": [group],
            "rules": [f"MATCH,{self.settings.group_name}"],
        }
        if providers:
            config["proxy-providers"] = providers
        return config

    def _write_runtime_config(self, config: dict[str, Any]) -> None:
        self._work_dir = Path(tempfile.mkdtemp(prefix="dtm-telegram-proxy-"))
        self._config_path = self._work_dir / "config.yaml"
        self._config_path.write_text(
            yaml.safe_dump(config, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        os.chmod(self._config_path, 0o600)

    async def _wait_until_ready(self) -> None:
        deadline = monotonic() + max(0.1, self.settings.startup_timeout_seconds)
        while monotonic() < deadline:
            if self._process is None or self._process.poll() is not None:
                raise RuntimeError("telegram_proxy_process_exited")
            try:
                await asyncio.to_thread(self._probe_controller_socket)
                return
            except OSError:
                await asyncio.sleep(0.05)
        raise TimeoutError("telegram_proxy_startup_timeout")

    def _probe_controller_socket(self) -> None:
        with socket.create_connection(("127.0.0.1", self._controller_port), timeout=0.2):
            return None

    def _controller_json(self, path: str) -> dict[str, Any]:
        request = Request(
            f"http://127.0.0.1:{self._controller_port}{path}",
            headers={"Authorization": f"Bearer {self._controller_secret}"},
        )
        with urlopen(request, timeout=self.settings.health_timeout_seconds + 1.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("telegram_proxy_controller_response_invalid")
        return payload

    def _controller_select(self, group_path: str, selected: str) -> None:
        request = Request(
            f"http://127.0.0.1:{self._controller_port}/proxies/{group_path}",
            data=json.dumps({"name": selected}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._controller_secret}",
                "Content-Type": "application/json",
            },
            method="PUT",
        )
        with urlopen(request, timeout=self.settings.health_timeout_seconds + 1.0) as response:
            response.read()

    @staticmethod
    def _free_loopback_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _counter(self, name: str, *, result: str) -> None:
        if self._metrics is not None:
            self._metrics.counter(
                name,
                labels={
                    "env": self.settings.env_name,
                    "module": "telegram",
                    "operation": "proxy",
                    "result": result,
                },
            )

    def _gauge(self, name: str, value: float) -> None:
        if self._metrics is not None:
            self._metrics.gauge(
                name,
                value,
                labels={
                    "env": self.settings.env_name,
                    "module": "telegram",
                    "operation": "proxy",
                    "result": "observed",
                },
            )

    def _timing(self, name: str, value: float) -> None:
        if self._metrics is not None:
            self._metrics.timing(
                name,
                value,
                labels={
                    "env": self.settings.env_name,
                    "module": "telegram",
                    "operation": "proxy",
                    "result": "observed",
                },
            )

    def _warning(self, event: str, **fields: Any) -> None:
        if self._logger is not None:
            self._logger.warning(event, **fields)


__all__ = ["MihomoProxySession", "TelegramProxySettings"]
