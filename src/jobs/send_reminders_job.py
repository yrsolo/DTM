from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from src.adapters.llm_google import AsyncGoogleLLMChatAgent
from src.adapters.llm_openai import AsyncOpenAIChatAgent
from src.adapters.llm_yandex import AsyncYandexLLMChatAgent
from src.adapters.telegram import TelegramNotifier
from src.app.context import AppContext
from src.observability import timed
from src.notify import ReminderFormatter, ReminderJob, ReminderRequest, ReminderUseCase
from src.snapshot_engine import build_snapshot_engine


def _build_notify_enhancer(ctx: AppContext, *, mock_external: bool):
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


def _today_in_runtime_timezone(ctx: AppContext):
    timezone_name = str(ctx.cfg.runtime.runtime.timezone or "Europe/Moscow").strip() or "Europe/Moscow"
    try:
        return datetime.now(ZoneInfo(timezone_name)).date()
    except Exception:
        return datetime.now().date()


class SendRemindersJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    async def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        snapshot_engine = build_snapshot_engine(self._ctx)
        usecase = ReminderUseCase(snapshot_engine)
        formatter = ReminderFormatter(
            timezone_name=str(self._ctx.cfg.runtime.runtime.timezone or "Europe/Moscow"),
            hidden_stage_names=tuple(self._ctx.cfg.mapping.hidden_stage_names or ()),
        )
        sender = TelegramNotifier(
            bot_token=str(self._ctx.deps.get("tg_bot_token", "")),
            default_chat_id=self._ctx.deps.get("default_chat_id"),
        )
        notify_cfg = self._ctx.cfg.runtime.notify
        mode = str(cmd.payload.get("mode", "morning")).strip().lower() or "morning"
        today = _today_in_runtime_timezone(self._ctx)
        if mode == "morning" and today.weekday() >= 5:
            return {
                "artifact": "reminder_v2",
                "status": "ok",
                "mode": mode,
                "today": today.isoformat(),
                "next_workday": "",
                "groups": 0,
                "delivery_counters": {
                    "candidates_total": 0,
                    "sent": 0,
                },
                "enhancement_counters": {},
                "warnings": ["morning_weekend_skipped"],
            }
        llm_mode = str(notify_cfg.llm_mode_default or "provider")
        mock_external = bool(cmd.payload.get("mock_external", False))
        mock_llm = bool(
            mock_external
            or llm_mode == "draft_only"
            or str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() == "test"
        )
        with timed(metrics, "dtm.notify.duration_ms", {"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "notify", "operation": mode, "result": "finished"}):
            result = await ReminderJob(
                usecase=usecase,
                formatter=formatter,
                sender=sender,
                helper_character=str(self._ctx.cfg.llm.assistant.get("helper_character", "")),
                enhancer=_build_notify_enhancer(self._ctx, mock_external=mock_llm),
                people_lookup=snapshot_engine,
                default_chat_id=str(self._ctx.deps.get("default_chat_id", "")).strip(),
                enhance_concurrency=int(notify_cfg.enhance_concurrency),
                send_retry_attempts=int(notify_cfg.send_retry_attempts),
                send_retry_backoff_seconds=float(notify_cfg.send_retry_backoff_seconds),
                send_retry_backoff_multiplier=float(notify_cfg.send_retry_backoff_multiplier),
                llm_mode=llm_mode,
                llm_model=str(self._ctx.cfg.llm.models.get("openai_default", "")),
                runtime_env=str(self._ctx.cfg.runtime.runtime.env_default),
                mock_llm=mock_llm,
            ).run(
                ReminderRequest(
                    mode=mode,
                    statuses=list(cmd.payload.get("statuses", ["work", "pre_done"])),
                    include_today=bool(cmd.payload.get("include_today", True)),
                    include_next_workday=bool(cmd.payload.get("include_next_workday", True)),
                    today_override=today if mode == "morning" else None,
                    force_test_chat=bool(cmd.payload.get("force_test_chat", False))
                    or mode == "test"
                    or str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() == "test",
                    test_chat_id_override=str(cmd.payload.get("test_chat_id_override", notify_cfg.test_chat_id_override or "")),
                )
            )
        if metrics is not None:
            metrics.counter("dtm.notify.total", labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "notify", "operation": mode, "result": "success"})
            metrics.gauge("dtm.notify.messages_sent", float(result.delivery_counters.get("sent", 0)), labels={"env": str(self._ctx.cfg.runtime.runtime.env_default), "module": "notify", "operation": mode, "result": "success"})
        if logger is not None:
            logger.info(
                "reminder_finished",
                mode=mode,
                groups=len(result.groups),
                sent=int(result.delivery_counters.get("sent", 0)),
                warnings=len(result.warnings),
            )
        return {
            "artifact": result.artifact,
            "status": result.status,
            "mode": result.mode,
            "today": result.today,
            "next_workday": result.next_workday,
            "groups": len(result.groups),
            "delivery_counters": dict(result.delivery_counters),
            "enhancement_counters": dict(result.enhancement_counters),
            "warnings": list(result.warnings),
        }
