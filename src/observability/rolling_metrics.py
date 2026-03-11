from __future__ import annotations

from typing import Iterable

from src.worker.model import JobStatusRecord


def extract_recent_success_values(
    records: Iterable[JobStatusRecord],
    *,
    timing_key: str,
    limit: int = 4,
) -> list[float]:
    values: list[float] = []
    for record in records:
        if str(record.status).strip().lower() != "success":
            continue
        summary = dict(record.summary or {})
        timings = summary.get("timings_ms", {})
        if not isinstance(timings, dict):
            continue
        raw_value = timings.get(timing_key)
        if raw_value is None:
            continue
        try:
            values.append(float(raw_value))
        except (TypeError, ValueError):
            continue
        if len(values) >= max(0, int(limit)):
            break
    return values


def emit_last_and_avg5_gauges(
    metrics,
    *,
    metric_prefix: str,
    logical_name: str,
    current_value_ms: float | int | None,
    previous_values_ms: Iterable[float],
    labels: dict[str, str],
) -> None:
    if metrics is None or current_value_ms is None:
        return
    current_value = float(current_value_ms)
    metric_base = f"{str(metric_prefix).rstrip('.')}.{str(logical_name).strip()}"
    metrics.gauge(f"{metric_base}_last_ms", current_value, labels=labels)
    samples = [current_value]
    for value in previous_values_ms:
        try:
            samples.append(float(value))
        except (TypeError, ValueError):
            continue
        if len(samples) >= 5:
            break
    if samples:
        metrics.gauge(f"{metric_base}_last5_avg_ms", sum(samples) / len(samples), labels=labels)
