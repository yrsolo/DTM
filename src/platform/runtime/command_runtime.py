"""Platform-owned command runtime capability for queue/status/worker access."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CommandRuntime:
    producer: object | None = None
    status_store: object | None = None
    worker: object | None = None

    def can_enqueue(self) -> bool:
        return self.producer is not None and self.status_store is not None

    def enqueue(self, cmd):
        if not self.can_enqueue():
            return None
        self.producer.send(cmd)
        return self.status_store.put_queued(cmd)

    def get(self, job_id: str):
        if self.status_store is None:
            return None
        return self.status_store.get(job_id)

    def get_worker(self):
        return self.worker


def get_command_runtime(ctx) -> CommandRuntime:
    runtime = ctx.deps.get("command_runtime")
    if not isinstance(runtime, CommandRuntime):
        runtime = CommandRuntime()
    runtime.producer = ctx.deps.get("command_queue_producer", runtime.producer)
    runtime.status_store = ctx.deps.get("job_status_store", runtime.status_store)
    runtime.worker = ctx.deps.get("command_worker", runtime.worker)
    ctx.deps["command_runtime"] = runtime
    return runtime
