from __future__ import annotations

import asyncio
import unittest
from unittest.mock import Mock

from src.platform.errors import PermanentError, TransientError
from src.platform.integrations.telegram.notifier import TelegramNotifier


class NetworkError(Exception):
    pass


class BadRequest(Exception):
    pass


class HttpError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


class _FakeProxy:
    def __init__(
        self,
        proxy_url: str | None,
        *,
        direct_fallback: bool = True,
        refresh_error: Exception | None = None,
    ) -> None:
        self.proxy_url = proxy_url
        self.direct_fallback = direct_fallback
        self.refresh_calls = 0
        self.close_calls = 0
        self.exclude_current = False
        self.refresh_error = refresh_error

    async def open(self):  # noqa: ANN201
        return self.proxy_url

    async def refresh(self, *, exclude_current: bool = False) -> bool:
        self.exclude_current = exclude_current
        self.refresh_calls += 1
        if self.refresh_error is not None:
            raise self.refresh_error
        return True

    async def close(self) -> None:
        self.close_calls += 1


class _FakeBot:
    def __init__(self, outcomes) -> None:  # noqa: ANN001
        self.outcomes = list(outcomes)
        self.calls = []

    async def send_message(self, **kwargs):  # noqa: ANN003, ANN201
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    async def shutdown(self) -> None:
        return None


class TelegramNotifierTestCase(unittest.TestCase):
    def test_records_proxy_route_without_endpoint_details(self) -> None:
        logger = Mock()
        notifier = TelegramNotifier("token", logger=logger)

        notifier._route_metric("proxy")

        logger.info.assert_called_once_with("telegram_transport_selected", route="proxy")

    def test_uses_direct_fallback_when_proxy_is_unavailable(self) -> None:
        proxy = _FakeProxy(None)
        notifier = TelegramNotifier("token", proxy_session=proxy)  # type: ignore[arg-type]
        routes = []

        async def replace_bot(proxy_url):  # noqa: ANN001
            routes.append(proxy_url)
            notifier._bot = _FakeBot([{"ok": True}])

        notifier._replace_bot = replace_bot  # type: ignore[method-assign]

        async def scenario():
            async with notifier:
                return await notifier.send_message("1", "hello")

        result = asyncio.run(scenario())
        self.assertEqual(result, {"ok": True})
        self.assertEqual(routes, [None])
        self.assertEqual(proxy.close_calls, 1)

    def test_proxy_transient_failure_refreshes_then_succeeds(self) -> None:
        proxy = _FakeProxy("http://127.0.0.1:7890")
        notifier = TelegramNotifier("token", proxy_session=proxy)  # type: ignore[arg-type]
        bots = [_FakeBot([NetworkError("offline")]), _FakeBot([{"ok": True}])]
        routes = []

        async def replace_bot(proxy_url):  # noqa: ANN001
            routes.append(proxy_url)
            notifier._bot = bots.pop(0)

        notifier._replace_bot = replace_bot  # type: ignore[method-assign]

        async def scenario():
            async with notifier:
                return await notifier.send_message("1", "hello")

        result = asyncio.run(scenario())
        self.assertEqual(result, {"ok": True})
        self.assertEqual(proxy.refresh_calls, 1)
        self.assertTrue(proxy.exclude_current)
        self.assertEqual(routes, ["http://127.0.0.1:7890", "http://127.0.0.1:7890"])

    def test_markup_fallback_only_retries_without_parse_mode(self) -> None:
        notifier = TelegramNotifier("token")
        bot = _FakeBot([BadRequest("Can't parse entities"), {"ok": True}])

        async def replace_bot(_proxy_url):  # noqa: ANN001
            notifier._bot = bot

        notifier._replace_bot = replace_bot  # type: ignore[method-assign]

        async def scenario():
            async with notifier:
                return await notifier.send_message("1", "hello", parse_mode="Markdown")

        result = asyncio.run(scenario())
        self.assertEqual(result, {"ok": True})
        self.assertEqual([call["parse_mode"] for call in bot.calls], ["Markdown", None])

    def test_proxy_controller_failure_still_uses_direct_fallback(self) -> None:
        proxy = _FakeProxy(
            "http://127.0.0.1:7890",
            refresh_error=RuntimeError("controller unavailable"),
        )
        notifier = TelegramNotifier("token", proxy_session=proxy)  # type: ignore[arg-type]
        bots = [_FakeBot([NetworkError("offline")]), _FakeBot([{"ok": True}])]
        routes = []

        async def replace_bot(proxy_url):  # noqa: ANN001
            routes.append(proxy_url)
            notifier._bot = bots.pop(0)

        notifier._replace_bot = replace_bot  # type: ignore[method-assign]

        async def scenario():
            async with notifier:
                return await notifier.send_message("1", "hello")

        result = asyncio.run(scenario())
        self.assertEqual(result, {"ok": True})
        self.assertEqual(routes, ["http://127.0.0.1:7890", None])

    def test_no_proxy_and_disabled_direct_fallback_is_transient(self) -> None:
        proxy = _FakeProxy(None, direct_fallback=False)
        notifier = TelegramNotifier("token", proxy_session=proxy)  # type: ignore[arg-type]

        async def scenario():
            async with notifier:
                return None

        with self.assertRaisesRegex(TransientError, "No healthy"):
            asyncio.run(scenario())

    def test_bad_request_is_permanent(self) -> None:
        classified = TelegramNotifier._classified(BadRequest("chat not found"))
        self.assertIsInstance(classified, PermanentError)

    def test_http_429_is_transient_and_http_401_is_permanent(self) -> None:
        self.assertIsInstance(TelegramNotifier._classified(HttpError(429)), TransientError)
        self.assertIsInstance(TelegramNotifier._classified(HttpError(401)), PermanentError)

    def test_proxy_and_direct_preflight_failure_is_unreachable(self) -> None:
        proxy = _FakeProxy("http://127.0.0.1:7890")
        notifier = TelegramNotifier("token", proxy_session=proxy)  # type: ignore[arg-type]

        async def replace_bot(_proxy_url):  # noqa: ANN001
            raise NetworkError("offline")

        notifier._replace_bot = replace_bot  # type: ignore[method-assign]

        async def scenario():
            async with notifier:
                return None

        with self.assertRaises(TransientError) as raised:
            asyncio.run(scenario())
        self.assertEqual(raised.exception.code, "telegram_unreachable")


if __name__ == "__main__":
    unittest.main()
