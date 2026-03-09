from __future__ import annotations

from time import perf_counter

from src.commands.serializer import command_from_json
from src.services.errors import PermanentError, TransientError, UserError

from .model import JobResult


class Worker:
    def __init__(self, status_store, dispatcher, logger, metrics=None, structured_logger=None, env_name: str = ""):
        self._status_store = status_store
        self._dispatcher = dispatcher
        self._logger = logger
        self._metrics = metrics
        self._structured_logger = structured_logger
        self._env_name = str(env_name or "").strip() or "unknown"

    async def run_once_from_messages(self, messages: list[Any]) -> dict[str, Any]:
        processed = 0
        succeeded = 0
        retryable_failed = 0
        terminal_failed = 0
        skipped_duplicates = 0
        for message in messages:
            processed += 1
            try:
                cmd = command_from_json(message.raw_body)
            except Exception as error:
                terminal_failed += 1
                if self._metrics is not None:
                    self._metrics.counter(
                        "dtm.worker.command_failures_total",
                        labels={"env": self._env_name, "module": "worker", "operation": "deserialize", "result": "failed_terminal"},
                    )
                if self._structured_logger is not None:
                    self._structured_logger.error(
                        "worker_command_finished",
                        job_id="",
                        command_type="",
                        status="failed_terminal",
                        error_code="malformed_command_payload",
                        error_type=type(error).__name__,
                    )
                self._logger(f"worker_malformed_payload error_type={type(error).__name__}")
                continue
            existing = self._status_store.get(cmd.job_id)
            if existing is not None and existing.status == "success":
                skipped_duplicates += 1
                self._logger(f"worker_duplicate_succeeded job_id={cmd.job_id}")
                if self._structured_logger is not None:
                    self._structured_logger.info(
                        "worker_command_finished",
                        job_id=cmd.job_id,
                        command_type=cmd.type,
                        status="duplicate_success",
                    )
                continue
            if existing is not None and existing.status == "running":
                skipped_duplicates += 1
                self._logger(f"worker_duplicate_running job_id={cmd.job_id}")
                if self._structured_logger is not None:
                    self._structured_logger.warning(
                        "worker_command_finished",
                        job_id=cmd.job_id,
                        command_type=cmd.type,
                        status="duplicate_running",
                    )
                continue
            self._status_store.put_running(cmd)
            started_at = perf_counter()
            try:
                result = await self._dispatcher.dispatch(cmd)
            except TransientError as error:
                result = JobResult(
                    success=False,
                    retryable=True,
                    failure_kind="retryable",
                    error_code=str(getattr(error, "code", "") or "worker_dispatch_transient"),
                    details={"errorType": type(error).__name__},
                    warnings=[],
                    error={
                        "code": str(getattr(error, "code", "") or "worker_dispatch_transient"),
                        "message": str(error),
                    },
                )
            except (PermanentError, UserError, ValueError) as error:
                result = JobResult(
                    success=False,
                    retryable=False,
                    failure_kind="terminal",
                    error_code=str(getattr(error, "code", "") or "worker_dispatch_terminal"),
                    details={"errorType": type(error).__name__},
                    warnings=[],
                    error={
                        "code": str(getattr(error, "code", "") or "worker_dispatch_terminal"),
                        "message": str(error),
                    },
                )
            except Exception as error:  # pragma: no cover
                result = JobResult(
                    success=False,
                    retryable=False,
                    failure_kind="terminal",
                    error_code="worker_dispatch_failed",
                    details={"errorType": type(error).__name__},
                    warnings=[],
                    error={"code": "worker_dispatch_failed", "message": str(error)},
                )
            duration_ms = (perf_counter() - started_at) * 1000.0
            self._status_store.put_finished(cmd, result)
            if result.success:
                succeeded += 1
                if self._metrics is not None:
                    self._metrics.counter(
                        "dtm.worker.commands_total",
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "success"},
                    )
                    self._metrics.timing(
                        "dtm.worker.command_duration_ms",
                        duration_ms,
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "success"},
                    )
                if self._structured_logger is not None:
                    self._structured_logger.info(
                        "worker_command_finished",
                        job_id=cmd.job_id,
                        command_type=cmd.type,
                        status="success",
                        duration_ms=round(duration_ms, 2),
                    )
            elif result.retryable:
                retryable_failed += 1
                if self._metrics is not None:
                    self._metrics.counter(
                        "dtm.worker.command_failures_total",
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "failed_retryable"},
                    )
                    self._metrics.counter(
                        "dtm.worker.command_retries_total",
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "retry_requested"},
                    )
                    self._metrics.timing(
                        "dtm.worker.command_duration_ms",
                        duration_ms,
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "failed_retryable"},
                    )
                if self._structured_logger is not None:
                    self._structured_logger.warning(
                        "worker_command_finished",
                        job_id=cmd.job_id,
                        command_type=cmd.type,
                        status="failed_retryable",
                        error_code=result.error_code or str((result.error or {}).get("code", "")),
                        duration_ms=round(duration_ms, 2),
                    )
            else:
                terminal_failed += 1
                if self._metrics is not None:
                    self._metrics.counter(
                        "dtm.worker.command_failures_total",
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "failed_terminal"},
                    )
                    self._metrics.timing(
                        "dtm.worker.command_duration_ms",
                        duration_ms,
                        labels={"env": self._env_name, "module": "worker", "operation": cmd.type, "result": "failed_terminal"},
                    )
                if self._structured_logger is not None:
                    self._structured_logger.error(
                        "worker_command_finished",
                        job_id=cmd.job_id,
                        command_type=cmd.type,
                        status="failed_terminal",
                        error_code=result.error_code or str((result.error or {}).get("code", "")),
                        duration_ms=round(duration_ms, 2),
                    )
        return {
            "artifact": "command_worker",
            "status": "retryable_failure"
            if retryable_failed > 0
            else ("partial_failure" if terminal_failed > 0 else "ok"),
            "processed": processed,
            "succeeded": succeeded,
            "failed": retryable_failed + terminal_failed,
            "retryable_failed": retryable_failed,
            "terminal_failed": terminal_failed,
            "skipped_duplicates": skipped_duplicates,
            "retry_requested": retryable_failed > 0,
        }
