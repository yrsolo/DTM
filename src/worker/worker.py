from __future__ import annotations

from typing import Any

from src.commands.serializer import command_from_json
from src.services.errors import PermanentError, TransientError

from .model import JobResult


class Worker:
    def __init__(self, status_store, dispatcher, logger):
        self._status_store = status_store
        self._dispatcher = dispatcher
        self._logger = logger

    async def run_once_from_messages(self, messages: list[Any]) -> dict[str, Any]:
        processed = 0
        succeeded = 0
        failed = 0
        skipped_duplicates = 0
        for message in messages:
            processed += 1
            cmd = command_from_json(message.raw_body)
            existing = self._status_store.get(cmd.job_id)
            if existing is not None and existing.status == "succeeded":
                skipped_duplicates += 1
                self._logger(f"worker_duplicate_succeeded job_id={cmd.job_id}")
                continue
            if existing is not None and existing.status == "running":
                skipped_duplicates += 1
                self._logger(f"worker_duplicate_running job_id={cmd.job_id}")
                continue
            self._status_store.put_running(cmd)
            try:
                result = await self._dispatcher.dispatch(cmd)
            except (TransientError, PermanentError) as error:
                result = JobResult(
                    success=False,
                    details={"errorType": type(error).__name__},
                    warnings=[],
                    error={
                        "code": str(getattr(error, "code", "") or "worker_dispatch_failed"),
                        "message": str(error),
                    },
                )
            except Exception as error:  # pragma: no cover
                result = JobResult(
                    success=False,
                    details={"errorType": type(error).__name__},
                    warnings=[],
                    error={"code": "worker_dispatch_failed", "message": str(error)},
                )
            self._status_store.put_finished(cmd, result)
            if result.success:
                succeeded += 1
            else:
                failed += 1
        return {
            "artifact": "command_worker",
            "status": "ok" if failed == 0 else "partial_failure",
            "processed": processed,
            "succeeded": succeeded,
            "failed": failed,
            "skipped_duplicates": skipped_duplicates,
        }
