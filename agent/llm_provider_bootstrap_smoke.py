"""Smoke-check bootstrap LLM provider selection without external API calls."""

from __future__ import annotations

from core.bootstrap import _build_chat_adapter
import core.bootstrap as bootstrap


def _assert_provider(
    provider: str,
    expected_primary_class_name: str,
    *,
    openai_token: str = "",
    google_key: str = "",
    yandex_key: str = "",
    yandex_model_uri: str = "",
) -> None:
    bootstrap.LLM_PROVIDER = provider
    bootstrap.LLM_FAILOVER_MODE = "draft_only"
    bootstrap.LLM_FAILOVER_PROVIDER = ""
    bootstrap.OPENAI = openai_token
    bootstrap.GOOGLE_LLM_API_KEY = google_key
    bootstrap.YANDEX_LLM_API_KEY = yandex_key
    bootstrap.YANDEX_LLM_MODEL_URI = yandex_model_uri
    adapter = _build_chat_adapter(mock_external=False)
    wrapper_name = type(adapter).__name__
    if wrapper_name != "FallbackChatAdapter":
        raise SystemExit(
            f"provider={provider} expected=FallbackChatAdapter actual={wrapper_name}",
        )
    primary_name = type(adapter.primary).__name__
    if primary_name != expected_primary_class_name:
        raise SystemExit(
            f"provider={provider} expected_primary={expected_primary_class_name} actual_primary={primary_name}",
        )
    print(f"provider={provider} wrapper={wrapper_name} primary={primary_name}")


def main() -> None:
    _assert_provider("openai", "AsyncOpenAIChatAgent", openai_token="smoke")
    _assert_provider("google", "AsyncGoogleLLMChatAgent", google_key="smoke")
    _assert_provider(
        "yandex",
        "AsyncYandexLLMChatAgent",
        yandex_key="smoke",
        yandex_model_uri="gpt://folder-id/yandexgpt/latest",
    )

    bootstrap.LLM_PROVIDER = "openai"
    bootstrap.LLM_FAILOVER_MODE = "provider"
    bootstrap.LLM_FAILOVER_PROVIDER = "google"
    bootstrap.OPENAI = "smoke"
    bootstrap.GOOGLE_LLM_API_KEY = "smoke"
    failover_adapter = _build_chat_adapter(mock_external=False)
    if type(failover_adapter).__name__ != "FallbackChatAdapter":
        raise SystemExit("failover wrapper selection failed")
    if type(failover_adapter.fallback).__name__ != "AsyncGoogleLLMChatAgent":
        raise SystemExit("failover provider selection failed")
    print("failover wrapper=FallbackChatAdapter fallback=AsyncGoogleLLMChatAgent")

    bootstrap.LLM_PROVIDER = "openai"
    bootstrap.LLM_FAILOVER_MODE = "draft_only"
    bootstrap.LLM_FAILOVER_PROVIDER = ""
    mock_adapter = _build_chat_adapter(mock_external=True)
    if type(mock_adapter).__name__ != "MockOpenAIChatAgent":
        raise SystemExit("mock_external selection failed")
    print("mock_external adapter=MockOpenAIChatAgent")
    print("llm_provider_bootstrap_smoke_ok")


if __name__ == "__main__":
    main()
