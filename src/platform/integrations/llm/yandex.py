"""Yandex LLM adapter boundary."""

from __future__ import annotations

import asyncio
from typing import Any

from core.adapters import LoggerAdapter, NullLogger
from core.reminder_policy import is_transient_llm_error, normalize_chat_messages


class AsyncYandexLLMChatAgent:
    """Async YandexGPT adapter via Foundation Models completion API."""

    def __init__(
        self,
        api_key: str,
        model_uri: str,
        logger: LoggerAdapter | None = None,
        timeout_seconds: float = 25.0,
        retry_attempts: int = 2,
        retry_backoff_seconds: float = 0.8,
    ) -> None:
        self.api_key = str(api_key or "")
        self.model_uri = str(model_uri or "")
        self.logger = logger or NullLogger()
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.retry_attempts = max(1, int(retry_attempts))
        self.retry_backoff_seconds = max(0.0, float(retry_backoff_seconds))
        try:
            import httpx
        except Exception as error:
            raise RuntimeError("Optional dep for Yandex LLM adapter is missing: install `httpx`.") from error
        self.http_client = httpx.AsyncClient(timeout=self.timeout_seconds)

    async def chat(self, messages: Any, model: str | None = None) -> str | None:
        normalized = normalize_chat_messages(messages)
        if not normalized:
            return None
        endpoint = "https://llm.api.cloud.yandex.net/foundationModels/v1/completionAsync"
        resolved_model = str(model or self.model_uri or "")
        if not resolved_model:
            return None
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "modelUri": resolved_model,
            "completionOptions": {
                "stream": False,
                "temperature": 0.2,
                "maxTokens": 2000,
            },
            "messages": normalized,
        }
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = await self.http_client.post(endpoint, headers=headers, json=body)
                response.raise_for_status()
                payload = response.json()
                alternatives = (((payload or {}).get("result") or {}).get("alternatives")) or []
                if not alternatives:
                    return None
                return str((alternatives[0].get("message") or {}).get("text") or "")
            except Exception as error:
                transient = is_transient_llm_error(error)
                can_retry = transient and attempt < self.retry_attempts
                if can_retry:
                    await asyncio.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))
                    continue
                self.logger.log(
                    "Yandex LLM chat error: "
                    f"attempt={attempt}/{self.retry_attempts} transient={transient} error={error}",
                )
                return None
        return None

    async def aclose(self) -> None:
        await self.http_client.aclose()
