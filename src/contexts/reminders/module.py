"""Local builder for the reminders context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from src.adapters.llm_google import AsyncGoogleLLMChatAgent
from src.adapters.llm_openai import AsyncOpenAIChatAgent
from src.adapters.llm_yandex import AsyncYandexLLMChatAgent
from src.adapters.telegram import TelegramNotifier
from src.notify import ReminderFormatter, ReminderJob, ReminderUseCase
from src.contexts.snapshot.public import get_snapshot_engine


@dataclass(frozen=True, slots=True)
class RemindersModule:
    """Context-local builder bundle used during staged migration."""

    name: str = "reminders"

    def build_snapshot_engine(self, ctx):
        return get_snapshot_engine(ctx)

    def build_usecase(self, snapshot_engine):
        return ReminderUseCase(snapshot_engine)

    def build_formatter(self, ctx):
        return ReminderFormatter(
            timezone_name=str(ctx.cfg.runtime.runtime.timezone or "Europe/Moscow"),
            hidden_stage_names=tuple(ctx.cfg.mapping.hidden_stage_names or ()),
        )

    def build_sender(self, ctx):
        return TelegramNotifier(
            bot_token=str(ctx.deps.get("tg_bot_token", "")),
            default_chat_id=ctx.deps.get("default_chat_id"),
        )

    def build_enhancer(self, ctx, *, mock_external: bool):
        if bool(mock_external):
            return None
        cfg = ctx.cfg
        deps = ctx.deps
        provider = str(cfg.llm.llm.get("provider_default", "openai")).strip().lower()
        timeout = float(cfg.llm.http.get("timeout_seconds_default", 25))
        retry_attempts = int(cfg.llm.http.get("retry_attempts_default", 2))
        retry_backoff = float(cfg.llm.http.get("retry_backoff_seconds_default", 0.8))
        proxy_url = str(deps.get("proxy_url", "")).strip()
        proxy_map = {"https://": proxy_url, "http://": proxy_url} if proxy_url else {}
        if provider == "google":
            api_key = str(deps.get("google_llm_api_key", "")).strip()
            model = str(cfg.llm.models.get("google_default", "")).strip()
            if not api_key:
                return None
            return AsyncGoogleLLMChatAgent(
                api_key=api_key,
                model=model,
                timeout_seconds=timeout,
                retry_attempts=retry_attempts,
                retry_backoff_seconds=retry_backoff,
            )
        if provider == "yandex":
            api_key = str(deps.get("yandex_llm_api_key", "")).strip()
            model_uri = str(cfg.llm.models.get("yandex_default_uri", "")).strip()
            if not api_key or not model_uri:
                return None
            return AsyncYandexLLMChatAgent(
                api_key=api_key,
                model_uri=model_uri,
                timeout_seconds=timeout,
                retry_attempts=retry_attempts,
                retry_backoff_seconds=retry_backoff,
            )
        api_key = str(deps.get("openai_token", "")).strip()
        model = str(cfg.llm.models.get("openai_default", "")).strip()
        if not api_key:
            return None
        return AsyncOpenAIChatAgent(
            api_key=api_key,
            proxies=proxy_map,
            model=model,
            organization=str(deps.get("org_token", "")).strip() or None,
            timeout_seconds=timeout,
            retry_attempts=retry_attempts,
            retry_backoff_seconds=retry_backoff,
        )

    def today_in_runtime_timezone(self, ctx):
        timezone_name = str(ctx.cfg.runtime.runtime.timezone or "Europe/Moscow").strip() or "Europe/Moscow"
        try:
            return datetime.now(ZoneInfo(timezone_name)).date()
        except Exception:
            return datetime.now().date()

    def build_job_runner(self, **kwargs):
        return ReminderJob(**kwargs)


def get_module() -> RemindersModule:
    """Return the local module instance for the reminders context."""

    return RemindersModule()
