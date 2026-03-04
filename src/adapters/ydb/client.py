"""Shared YDB client helpers."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.parse import urlsplit

def normalize_endpoint(endpoint: str) -> str:
    """Strip DSN query tail and keep plain endpoint for SDK."""
    raw = str(endpoint or "").strip()
    if not raw:
        return raw
    if "://" in raw:
        parsed = urlsplit(raw)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    return raw.split("?", 1)[0]


def build_credentials(
    ydb_module: Any,
    *,
    sa_json_credentials: str | None = None,
    sa_key_file: str | None = None,
) -> Any:
    """Resolve YDB credentials with explicit SA-json priority for local/dev."""
    sa_json = str(sa_json_credentials or "").strip()
    if sa_json:
        return ydb_module.iam.ServiceAccountCredentials.from_content(sa_json)
    sa_key_file = str(sa_key_file or "").strip()
    if sa_key_file:
        return ydb_module.iam.ServiceAccountCredentials.from_file(sa_key_file)
    return ydb_module.credentials_from_env_variables()


@dataclass(slots=True)
class YdbExecutionStats:
    ydb_queries_count: int = 0
    duration_ms: int = 0
    error_code: str = ""


class YdbClient:
    """Thin helper over YDB session pool with bounded retries/backoff."""

    def __init__(
        self,
        endpoint: str,
        database: str,
        *,
        sa_json_credentials: str | None = None,
        sa_key_file: str | None = None,
        exhausted_max_attempts: int = 6,
        exhausted_base_backoff_seconds: float = 0.2,
        exhausted_max_backoff_seconds: float = 4.0,
        exhausted_jitter_ratio: float = 0.3,
    ) -> None:
        if not endpoint.strip() or not database.strip():
            raise ValueError("YDB endpoint/database are required")
        self.endpoint = normalize_endpoint(endpoint)
        self.database = database
        self.sa_json_credentials = str(sa_json_credentials or "")
        self.sa_key_file = str(sa_key_file or "")
        self.exhausted_max_attempts = max(1, int(exhausted_max_attempts))
        self.exhausted_base_backoff_seconds = max(0.05, float(exhausted_base_backoff_seconds))
        self.exhausted_max_backoff_seconds = max(
            self.exhausted_base_backoff_seconds,
            float(exhausted_max_backoff_seconds),
        )
        self.exhausted_jitter_ratio = min(1.0, max(0.0, float(exhausted_jitter_ratio)))
        self._driver = None
        self._session_pool = None
        self._retry_settings = None
        self.stats = YdbExecutionStats()

    def _ensure(self) -> None:
        if self._session_pool is not None:
            return
        try:
            import ydb
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("ydb package is required") from exc
        driver = ydb.Driver(
            endpoint=self.endpoint,
            database=self.database,
            credentials=build_credentials(
                ydb,
                sa_json_credentials=self.sa_json_credentials,
                sa_key_file=self.sa_key_file,
            ),
        )
        driver.wait(fail_fast=True, timeout=7)
        self._driver = driver
        self._session_pool = ydb.SessionPool(driver)
        self._retry_settings = ydb.RetrySettings(
            max_retries=2,
            max_session_acquire_timeout=7,
            get_session_client_timeout=7,
            idempotent=True,
        )

    def execute_scheme(self, query: str) -> None:
        self._ensure()

        def _call(session) -> None:
            session.execute_scheme(query)

        self._run(_call)

    def execute(self, query: str, params: dict[str, Any] | None = None) -> Any:
        self._ensure()
        payload = params or {}

        def _call(session) -> Any:
            prepared = session.prepare(query)
            return session.transaction().execute(prepared, payload, commit_tx=True)

        return self._run(_call)

    def query(self, query: str) -> Any:
        self._ensure()

        def _call(session) -> Any:
            return session.transaction().execute(query, commit_tx=True)

        return self._run(_call)

    def _run(self, call: Callable[[Any], Any]) -> Any:
        self.stats.ydb_queries_count += 1
        started = time.perf_counter()
        self.stats.error_code = ""
        for attempt in range(1, self.exhausted_max_attempts + 1):
            try:
                result = self._session_pool.retry_operation_sync(call, retry_settings=self._retry_settings)
                self.stats.duration_ms += int((time.perf_counter() - started) * 1000)
                return result
            except Exception as exc:
                text = str(exc).lower()
                is_exhausted = "resourceexhausted" in text or "resource_exhausted" in text
                self.stats.error_code = "ydb_resource_exhausted" if is_exhausted else "ydb_error"
                if not is_exhausted or attempt >= self.exhausted_max_attempts:
                    self.stats.duration_ms += int((time.perf_counter() - started) * 1000)
                    raise
                base_backoff = min(
                    self.exhausted_max_backoff_seconds,
                    self.exhausted_base_backoff_seconds * (2 ** (attempt - 1)),
                )
                jitter = base_backoff * self.exhausted_jitter_ratio * random.random()
                sleep_seconds = base_backoff + jitter
                print(
                    "ydb_backoff "
                    f"attempt={attempt} "
                    f"sleep_seconds={sleep_seconds:.3f} "
                    f"error_code={self.stats.error_code}"
                )
                time.sleep(sleep_seconds)
        self.stats.duration_ms += int((time.perf_counter() - started) * 1000)
        raise RuntimeError("YDB execution failed after retry loop")
