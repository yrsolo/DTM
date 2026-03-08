from __future__ import annotations

from typing import Any

from src.services.errors import PermanentError, TransientError

from .model import Command
from .queue import CommandQueueProducer, QueueMessage
from .serializer import command_to_json


def is_message_queue_event(event: Any) -> bool:
    if not isinstance(event, dict) or not isinstance(event.get("messages"), list):
        return False
    for item in list(event.get("messages") or []):
        if not isinstance(item, dict):
            continue
        details = item.get("details", {})
        if not isinstance(details, dict):
            continue
        message = details.get("message", {})
        if not isinstance(message, dict):
            continue
        if str(message.get("body", "")).strip():
            return True
    return False


def queue_messages_from_event(event: Any) -> list[QueueMessage]:
    if not is_message_queue_event(event):
        return []
    result: list[QueueMessage] = []
    for item in list(event.get("messages") or []):
        if not isinstance(item, dict):
            continue
        details = item.get("details", {})
        if not isinstance(details, dict):
            details = {}
        message = details.get("message", {})
        if not isinstance(message, dict):
            message = {}
        raw_body = str(message.get("body", "")).strip()
        if not raw_body:
            continue
        result.append(
            QueueMessage(
                raw_body=raw_body,
                receipt_handle=str(message.get("message_id", "")).strip(),
                attributes={
                    "message_id": str(message.get("message_id", "")).strip(),
                    "queue_name": str(message.get("queue_name", "")).strip(),
                    "created_at": str(message.get("created_at", "")).strip(),
                },
            )
        )
    return result


class YandexMessageQueueProducer(CommandQueueProducer):
    def __init__(
        self,
        *,
        queue_url: str,
        endpoint_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        self._queue_url = str(queue_url).strip()
        if not self._queue_url:
            raise ValueError("queue_url is required")
        try:
            import boto3  # type: ignore
        except Exception as error:  # pragma: no cover
            raise PermanentError("boto3 package is required for Yandex Message Queue", code="mq_sdk_missing") from error
        self._client = boto3.client(
            "sqs",
            endpoint_url=(str(endpoint_url).strip() or None),
            aws_access_key_id=(str(aws_access_key_id).strip() or None),
            aws_secret_access_key=(str(aws_secret_access_key).strip() or None),
        )

    def send(self, cmd: Command) -> None:
        try:
            self._client.send_message(QueueUrl=self._queue_url, MessageBody=command_to_json(cmd))
        except Exception as error:
            raise TransientError(str(error), code="mq_send_failed") from error
