from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import requests


@dataclass(frozen=True, slots=True)
class PrometheusMetricSample:
    name: str
    value: float
    labels: dict[str, str]
    ts_ms: int


def _now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def normalize_prometheus_metric_name(name: str) -> str:
    cleaned = str(name or "").strip().lower()
    if not cleaned:
        return ""
    normalized: list[str] = []
    for char in cleaned:
        if char.isalnum() or char == "_":
            normalized.append(char)
        else:
            normalized.append("_")
    collapsed = "".join(normalized)
    while "__" in collapsed:
        collapsed = collapsed.replace("__", "_")
    return collapsed.strip("_")


def normalize_prometheus_labels(labels: dict[str, str] | None) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in dict(labels or {}).items():
        key_clean = str(key or "").strip()
        value_clean = str(value or "").strip()
        if not key_clean or not value_clean:
            continue
        label_key = normalize_prometheus_metric_name(key_clean)
        if not label_key:
            continue
        normalized[label_key] = value_clean
    return normalized


def build_prometheus_metric_sample(
    *,
    name: str,
    value: float,
    labels: dict[str, str] | None = None,
    service_label: str,
    namespace: str,
    ts_ms: int | None = None,
) -> PrometheusMetricSample:
    merged_labels = normalize_prometheus_labels(labels)
    merged_labels.setdefault("service", str(service_label or "").strip() or "dtm")
    merged_labels.setdefault("namespace", str(namespace or "").strip() or "dtm")
    return PrometheusMetricSample(
        name=normalize_prometheus_metric_name(name),
        value=float(value),
        labels=merged_labels,
        ts_ms=int(ts_ms if ts_ms is not None else _now_ms()),
    )


@lru_cache(maxsize=1)
def _remote_write_message_classes():
    try:
        from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError("protobuf_dependency_missing") from exc

    file_descriptor = descriptor_pb2.FileDescriptorProto()
    file_descriptor.name = "dtm_prometheus_remote_write.proto"
    file_descriptor.package = "dtm.prometheus"
    file_descriptor.syntax = "proto3"

    label_msg = file_descriptor.message_type.add()
    label_msg.name = "Label"
    label_name = label_msg.field.add()
    label_name.name = "name"
    label_name.number = 1
    label_name.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    label_name.type = descriptor_pb2.FieldDescriptorProto.TYPE_STRING
    label_value = label_msg.field.add()
    label_value.name = "value"
    label_value.number = 2
    label_value.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    label_value.type = descriptor_pb2.FieldDescriptorProto.TYPE_STRING

    sample_msg = file_descriptor.message_type.add()
    sample_msg.name = "Sample"
    sample_value = sample_msg.field.add()
    sample_value.name = "value"
    sample_value.number = 1
    sample_value.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    sample_value.type = descriptor_pb2.FieldDescriptorProto.TYPE_DOUBLE
    sample_timestamp = sample_msg.field.add()
    sample_timestamp.name = "timestamp"
    sample_timestamp.number = 2
    sample_timestamp.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    sample_timestamp.type = descriptor_pb2.FieldDescriptorProto.TYPE_INT64

    timeseries_msg = file_descriptor.message_type.add()
    timeseries_msg.name = "TimeSeries"
    ts_labels = timeseries_msg.field.add()
    ts_labels.name = "labels"
    ts_labels.number = 1
    ts_labels.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    ts_labels.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    ts_labels.type_name = ".dtm.prometheus.Label"
    ts_samples = timeseries_msg.field.add()
    ts_samples.name = "samples"
    ts_samples.number = 2
    ts_samples.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    ts_samples.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    ts_samples.type_name = ".dtm.prometheus.Sample"

    write_request_msg = file_descriptor.message_type.add()
    write_request_msg.name = "WriteRequest"
    wr_timeseries = write_request_msg.field.add()
    wr_timeseries.name = "timeseries"
    wr_timeseries.number = 1
    wr_timeseries.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED
    wr_timeseries.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    wr_timeseries.type_name = ".dtm.prometheus.TimeSeries"

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_descriptor)

    get_message_class = getattr(message_factory, "GetMessageClass", None)
    if get_message_class is not None:
        label_cls = get_message_class(pool.FindMessageTypeByName("dtm.prometheus.Label"))
        sample_cls = get_message_class(pool.FindMessageTypeByName("dtm.prometheus.Sample"))
        timeseries_cls = get_message_class(pool.FindMessageTypeByName("dtm.prometheus.TimeSeries"))
        write_request_cls = get_message_class(pool.FindMessageTypeByName("dtm.prometheus.WriteRequest"))
        return label_cls, sample_cls, timeseries_cls, write_request_cls

    factory = message_factory.MessageFactory(pool)
    label_cls = factory.GetPrototype(pool.FindMessageTypeByName("dtm.prometheus.Label"))
    sample_cls = factory.GetPrototype(pool.FindMessageTypeByName("dtm.prometheus.Sample"))
    timeseries_cls = factory.GetPrototype(pool.FindMessageTypeByName("dtm.prometheus.TimeSeries"))
    write_request_cls = factory.GetPrototype(pool.FindMessageTypeByName("dtm.prometheus.WriteRequest"))
    return label_cls, sample_cls, timeseries_cls, write_request_cls


def build_remote_write_payload(metrics: list[PrometheusMetricSample]) -> bytes:
    _, _, _, write_request_cls = _remote_write_message_classes()
    write_request = write_request_cls()
    for item in metrics:
        series = write_request.timeseries.add()
        metric_label = series.labels.add()
        metric_label.name = "__name__"
        metric_label.value = item.name
        for key, value in sorted(item.labels.items()):
            label = series.labels.add()
            label.name = key
            label.value = value
        sample = series.samples.add()
        sample.value = float(item.value)
        sample.timestamp = int(item.ts_ms)
    return write_request.SerializeToString()


def compress_remote_write_payload(payload: bytes) -> bytes:
    try:
        import snappy
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError("snappy_dependency_missing") from exc
    return snappy.compress(payload)


def workspace_remote_write_endpoint(workspace_id: str) -> str:
    workspace = str(workspace_id or "").strip()
    if not workspace:
        return ""
    return f"https://monitoring.api.cloud.yandex.net/prometheus/workspaces/{workspace}/api/v1/write"


def workspace_query_endpoint(workspace_id: str) -> str:
    workspace = str(workspace_id or "").strip()
    if not workspace:
        return ""
    return f"https://monitoring.api.cloud.yandex.net/prometheus/workspaces/{workspace}/api/v1/query"


def write_prometheus_remote_write(
    *,
    endpoint_write: str,
    metrics: list[PrometheusMetricSample],
    bearer_token: str,
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    if not str(bearer_token or "").strip():
        raise RuntimeError("prometheus_api_key_missing")
    protobuf_payload = build_remote_write_payload(metrics)
    compressed_payload = compress_remote_write_payload(protobuf_payload)
    headers = {
        "Authorization": f"Bearer {str(bearer_token).strip()}",
        "Content-Type": "application/x-protobuf",
        "Content-Encoding": "snappy",
        "X-Prometheus-Remote-Write-Version": "0.1.0",
    }
    response = requests.post(
        str(endpoint_write).strip(),
        headers=headers,
        data=compressed_payload,
        timeout=max(0.1, float(timeout_seconds)),
    )
    response.raise_for_status()
    if not response.content:
        return {"status_code": response.status_code, "body": ""}
    try:
        return dict(response.json() or {})
    except Exception:
        return {"status_code": response.status_code, "body": response.text}
