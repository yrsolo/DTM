"""Smoke-check bootstrap LLM provider selection without external API calls."""

from __future__ import annotations

from core.bootstrap import _build_chat_adapter
import core.bootstrap as bootstrap


def _assert_provider(
    provider: str,
    expected_class_name: str,
    *,
    openai_token: str = "",
    google_key: str = "",
    yandex_key: str = "",
    yandex_model_uri: str = "",
) -> None:
    bootstrap.LLM_PROVIDER = provider
    bootstrap.OPENAI = openai_token
    bootstrap.GOOGLE_LLM_API_KEY = google_key
    bootstrap.YANDEX_LLM_API_KEY = yandex_key
    bootstrap.YANDEX_LLM_MODEL_URI = yandex_model_uri
    adapter = _build_chat_adapter(mock_external=False)
    actual_name = type(adapter).__name__
    if actual_name != expected_class_name:
        raise SystemExit(
            f"provider={provider} expected={expected_class_name} actual={actual_name}",
        )
    print(f"provider={provider} adapter={actual_name}")


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
    mock_adapter = _build_chat_adapter(mock_external=True)
    if type(mock_adapter).__name__ != "MockOpenAIChatAgent":
        raise SystemExit("mock_external selection failed")
    print("mock_external adapter=MockOpenAIChatAgent")
    print("llm_provider_bootstrap_smoke_ok")


if __name__ == "__main__":
    main()
