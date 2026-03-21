"""Tests for YDB exhausted backoff policy."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.platform.infra.ydb.client import YdbClient


class _PoolStub:
    def __init__(self) -> None:
        self.calls = 0

    def retry_operation_sync(self, call, retry_settings=None):  # noqa: ANN001, ARG002
        self.calls += 1
        if self.calls < 3:
            raise RuntimeError("RESOURCE_EXHAUSTED: ResourceExhausted")
        return call(None)


class YdbBackoffTestCase(unittest.TestCase):
    def test_backoff_retries_exhausted_then_succeeds(self) -> None:
        client = YdbClient(endpoint="grpcs://example:2135", database="/db")
        client._session_pool = _PoolStub()  # type: ignore[attr-defined]
        client._retry_settings = object()  # type: ignore[attr-defined]

        with patch("src.platform.infra.ydb.client.time.sleep") as sleep_mock:
            result = client._run(lambda session: "ok")  # noqa: SLF001

        self.assertEqual(result, "ok")
        self.assertEqual(client._session_pool.calls, 3)  # type: ignore[attr-defined]
        self.assertGreaterEqual(sleep_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
