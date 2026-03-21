"""OpenAI adapter boundary."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

from src.platform.contracts.adapters import LoggerAdapter, NullLogger
from src.platform.policies.reminder_policy import is_transient_llm_error, sanitize_proxy_url


def _safe_print(text: Any) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


class AsyncOpenAIChatAgent:
    """Async OpenAI chat adapter used by reminder pipeline."""

    def __init__(
        self,
        api_key: str,
        proxies: Mapping[str, str] | None = None,
        model: str | None = None,
        organization: str | None = None,
        logger: LoggerAdapter | None = None,
        timeout_seconds: float = 25.0,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.8,
    ) -> None:
        self.api_key = api_key
        self.organization = organization
        self.proxies = dict(proxies or {})
        self.endpoint = "https://api.openai.com/v1/chat/completions"
        self.model = model
        self.logger = logger or NullLogger()
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.retry_attempts = max(1, int(retry_attempts))
        self.retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        proxy_url = sanitize_proxy_url(self.proxies.get("https://") or self.proxies.get("http://"))
        client_kwargs = {"timeout": self.timeout_seconds}
        if proxy_url:
            client_kwargs["proxy"] = proxy_url
        try:
            import httpx
            from openai import AsyncOpenAI
        except Exception as error:
            raise RuntimeError("Optional deps for OpenAI adapter are missing: install `httpx` and `openai`.") from error
        self.http_client = httpx.AsyncClient(**client_kwargs)
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            http_client=self.http_client,
        )

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        """Call OpenAI chat completion with transient retry guard."""
        _safe_print(f"openai_proxies={self.proxies}")

        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        if not model:
            model = self.model
        if not model:
            model = "gpt-3.5-turbo"

        _safe_print(f"openai_messages={messages}")

        completion = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                completion = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                break
            except Exception as error:
                transient = is_transient_llm_error(error)
                can_retry = transient and attempt < self.retry_attempts
                if can_retry:
                    await asyncio.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))
                    continue
                self.logger.log(
                    "OpenAI chat error: "
                    f"attempt={attempt}/{self.retry_attempts} transient={transient} error={error}",
                )
                return None

        if completion is None:
            return None
        return completion.choices[0].message.content

    async def aclose(self) -> None:
        await self.http_client.aclose()


