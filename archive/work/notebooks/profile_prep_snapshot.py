import json
import os
import sys
import statistics
import time
from pathlib import Path

import boto3

os.environ["ENV"] = "test"
os.environ.setdefault("PROMETHEUS_ENABLED", "0")
os.environ.setdefault("MONITORING_ENABLED", "0")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app.bootstrap import build_app_context
from src.snapshot_engine import build_snapshot_engine


BUCKET = "dtm"
KEY = "snapshots/test/prep/default.json"
ENDPOINT_URL = "https://storage.yandexcloud.net"
RUNS = 10


def timed(label, fn):
    t0 = time.perf_counter()
    result = fn()
    t1 = time.perf_counter()
    print(f"{label}: {(t1 - t0) * 1000:.1f} ms")
    return result, (t1 - t0) * 1000.0


def main():
    print("ENV:", os.environ.get("ENV"))
    print("PROMETHEUS_ENABLED:", os.environ.get("PROMETHEUS_ENABLED"))
    print("MONITORING_ENABLED:", os.environ.get("MONITORING_ENABLED"))

    s3 = boto3.client("s3", endpoint_url=ENDPOINT_URL)

    ctx, _ = timed("build_app_context()", build_app_context)
    engine, _ = timed("build_snapshot_engine(ctx)", lambda: build_snapshot_engine(ctx))

    prep_cache = getattr(engine, "_prep_cache")
    store = getattr(prep_cache, "_store")
    prep_key = getattr(prep_cache, "_key")

    print("prep_cache:", type(prep_cache).__name__)
    print("store:", type(store).__name__)
    print("prep_key:", prep_key)

    raw_times = []
    store_times = []
    prep_times = []

    for i in range(RUNS):
        _, raw_ms = timed(
            f"run {i + 1} raw boto3",
            lambda: json.loads(
                s3.get_object(Bucket=BUCKET, Key=KEY)["Body"].read().decode("utf-8")
            ),
        )
        raw_times.append(raw_ms)

        _, store_ms = timed(
            f"run {i + 1} _store.get(prep_key)",
            lambda: store.get(prep_key),
        )
        store_times.append(store_ms)

        prep, prep_ms = timed(
            f"run {i + 1} engine.get_prep_snapshot()",
            engine.get_prep_snapshot,
        )
        prep_times.append(prep_ms)
        if i == 0:
            print("prep type:", type(prep).__name__)

    print()
    print("raw boto3 avg:", round(statistics.mean(raw_times), 1), "ms")
    print("raw boto3 min:", round(min(raw_times), 1), "ms")
    print("raw boto3 max:", round(max(raw_times), 1), "ms")
    print("_store.get avg:", round(statistics.mean(store_times), 1), "ms")
    print("_store.get min:", round(min(store_times), 1), "ms")
    print("_store.get max:", round(max(store_times), 1), "ms")
    print("engine.get_prep_snapshot avg:", round(statistics.mean(prep_times), 1), "ms")
    print("engine.get_prep_snapshot min:", round(min(prep_times), 1), "ms")
    print("engine.get_prep_snapshot max:", round(max(prep_times), 1), "ms")


if __name__ == "__main__":
    main()
