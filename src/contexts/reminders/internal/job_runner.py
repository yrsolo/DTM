from __future__ import annotations

from src.platform.context import AppContext
from src.contexts.reminders.public import get_delivery_api
from src.platform.observability import timed


class SendRemindersJob:
    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    async def run(self, cmd):
        metrics = self._ctx.deps.get("metrics_client")
        logger = self._ctx.deps.get("structured_logger")
        delivery_api = get_delivery_api(self._ctx)
        snapshot_read = delivery_api.snapshot_read_api()
        usecase = delivery_api.usecase(snapshot_read)
        formatter = delivery_api.formatter()
        sender = delivery_api.sender()
        notify_cfg = self._ctx.cfg.runtime.notify
        mode = str(cmd.payload.get("mode", "morning")).strip().lower() or "morning"
        today = delivery_api.today_in_runtime_timezone()
        if mode == "morning" and today.weekday() >= 5:
            return {
                "artifact": "reminder_v2",
                "status": "ok",
                "mode": mode,
                "today": today.isoformat(),
                "next_workday": "",
                "groups": 0,
                "delivery_counters": {"candidates_total": 0, "sent": 0},
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
        with timed(
            metrics,
            "dtm.notify.duration_ms",
            {
                "env": str(self._ctx.cfg.runtime.runtime.env_default),
                "module": "notify",
                "operation": mode,
                "result": "finished",
            },
        ):
            result = await delivery_api.job_runner(
                usecase=usecase,
                formatter=formatter,
                sender=sender,
                helper_character=str(self._ctx.cfg.llm.assistant.get("helper_character", "")),
                enhancer=delivery_api.enhancer(mock_external=mock_llm),
                people_lookup=snapshot_read,
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
                delivery_api.request(
                    mode=mode,
                    statuses=list(cmd.payload.get("statuses", ["work", "pre_done"])),
                    include_today=bool(cmd.payload.get("include_today", True)),
                    include_next_workday=bool(cmd.payload.get("include_next_workday", True)),
                    today_override=today if mode == "morning" else None,
                    force_test_chat=bool(cmd.payload.get("force_test_chat", False))
                    or mode == "test"
                    or str(self._ctx.cfg.runtime.runtime.env_default).strip().lower() == "test",
                    test_chat_id_override=str(
                        cmd.payload.get("test_chat_id_override", notify_cfg.test_chat_id_override or "")
                    ),
                )
            )
        if metrics is not None:
            metrics.counter(
                "dtm.notify.total",
                labels={
                    "env": str(self._ctx.cfg.runtime.runtime.env_default),
                    "module": "notify",
                    "operation": mode,
                    "result": "success",
                },
            )
            metrics.gauge(
                "dtm.notify.messages_sent",
                float(result.delivery_counters.get("sent", 0)),
                labels={
                    "env": str(self._ctx.cfg.runtime.runtime.env_default),
                    "module": "notify",
                    "operation": mode,
                    "result": "success",
                },
            )
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


__all__ = ["SendRemindersJob"]
