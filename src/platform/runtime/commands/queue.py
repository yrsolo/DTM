from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable

from .model import Command


class CommandQueueProducer(ABC):
    @abstractmethod
    def send(self, cmd: Command) -> None:
        raise NotImplementedError

    def send_many(self, cmds: Iterable[Command]) -> None:
        for cmd in cmds:
            self.send(cmd)


@dataclass(frozen=True, slots=True)
class QueueMessage:
    raw_body: str
    receipt_handle: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)


class CommandQueueConsumer(ABC):
    @abstractmethod
    def receive(self, max_messages: int = 1) -> list[QueueMessage]:
        raise NotImplementedError

    def ack(self, msg: QueueMessage) -> None:  # pragma: no cover
        _ = msg

    def nack(self, msg: QueueMessage) -> None:  # pragma: no cover
        _ = msg
