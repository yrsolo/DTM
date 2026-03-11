from __future__ import annotations

from dataclasses import asdict, dataclass
from urllib.parse import urlparse


@dataclass(frozen=True, slots=True)
class QueueLiveStats:
    queue_name: str
    messages_visible: int
    messages_in_flight: int
    messages_delayed: int
    dlq_configured: bool
    raw_attributes: dict[str, str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _queue_name_from_url(queue_url: str) -> str:
    parsed = urlparse(str(queue_url or "").strip())
    path = parsed.path.strip("/")
    if not path:
        return ""
    return path.rsplit("/", 1)[-1]


def get_queue_live_stats(
    *,
    queue_url: str,
    endpoint_url: str | None,
    aws_access_key_id: str | None,
    aws_secret_access_key: str | None,
) -> QueueLiveStats:
    import boto3  # type: ignore

    client = boto3.client(
        "sqs",
        region_name="ru-central1",
        endpoint_url=str(endpoint_url).strip() or None,
        aws_access_key_id=str(aws_access_key_id or "").strip() or None,
        aws_secret_access_key=str(aws_secret_access_key or "").strip() or None,
    )
    response = client.get_queue_attributes(
        QueueUrl=str(queue_url).strip(),
        AttributeNames=[
            "ApproximateNumberOfMessages",
            "ApproximateNumberOfMessagesNotVisible",
            "ApproximateNumberOfMessagesDelayed",
            "RedrivePolicy",
        ],
    )
    attrs = dict(response.get("Attributes", {}) or {})
    return QueueLiveStats(
        queue_name=_queue_name_from_url(queue_url),
        messages_visible=int(attrs.get("ApproximateNumberOfMessages", "0") or "0"),
        messages_in_flight=int(attrs.get("ApproximateNumberOfMessagesNotVisible", "0") or "0"),
        messages_delayed=int(attrs.get("ApproximateNumberOfMessagesDelayed", "0") or "0"),
        dlq_configured=bool(str(attrs.get("RedrivePolicy", "")).strip()),
        raw_attributes={str(k): str(v) for k, v in attrs.items()},
    )
