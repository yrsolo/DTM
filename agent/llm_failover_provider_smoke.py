"""Smoke check for provider failover adapter behavior."""

import asyncio
from typing import Any

from core.reminder import FallbackChatAdapter


class EmptyAdapter:
    async def chat(self, messages: Any, model: str | None = None) -> None:
        _ = messages
        _ = model
        return None


class StaticAdapter:
    def __init__(self, text: str) -> None:
        self.text = text

    async def chat(self, messages: Any, model: str | None = None) -> str:
        _ = messages
        _ = model
        return self.text


async def run() -> None:
    adapter = FallbackChatAdapter(
        primary=EmptyAdapter(),
        primary_provider="openai",
        mode="provider",
        fallback=StaticAdapter("fallback-ok"),
        fallback_provider="google",
    )
    result = await adapter.chat([{"role": "user", "content": "hello"}])
    assert result == "fallback-ok"
    counters = adapter.get_failover_counters()
    assert counters["fallback_calls"] == 1, counters
    assert counters["fallback_success"] == 1, counters
    assert counters["mode"] == "provider", counters
    print("llm_failover_provider_smoke_ok")


if __name__ == "__main__":
    asyncio.run(run())
