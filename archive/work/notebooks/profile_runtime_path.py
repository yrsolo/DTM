# save as: notebooks/profile_runtime_path.py
import asyncio
import json
import os
import time
from statistics import mean

os.environ["ENV"] = "test"
os.environ.setdefault("PROMETHEUS_ENABLED", "0")
os.environ.setdefault("MONITORING_ENABLED", "0")

# import index

from .src.app.bootstrap import build_app_context
from .src.snapshot_engine import build_snapshot_engine
from .tests.api.test_frontend_api_routing import _fixture_event


def ms(start, end):
    return round((end - start) * 1000, 1)


def section(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def time_call(label, fn, *args, **kwargs):
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    t1 = time.perf_counter()
    print(f"{label}: {ms(t0, t1)} ms")
    return result, ms(t0, t1)


async def time_async_call(label, fn, *args, **kwargs):
    t0 = time.perf_counter()
    result = await fn(*args, **kwargs)
    t1 = time.perf_counter()
    print(f"{label}: {ms(t0, t1)} ms")
    return result, ms(t0, t1)


def make_frontend_event():
    event = _fixture_event()
    event["httpMethod"] = "GET"
    event["path"] = "/test/ops/api/v2/frontend"
    event["pathParams"] = {"proxy": "api/v2/frontend"}
    event["params"]["proxy"] = "api/v2/frontend"
    event["url"] = (
        "https://dtm.solofarm.ru/test/ops/api/v2/frontend"
        "?statuses=work,pre_done,done,wait&include_people=true&limit=60"
    )
    event["queryStringParameters"] = {
        "statuses": "work,pre_done,done,wait",
        "include_people": "true",
        "limit": "60",
    }
    event["multiValueQueryStringParameters"] = {
        "statuses": ["work,pre_done,done,wait"],
        "include_people": ["true"],
        "limit": ["60"],
    }
    return event


def make_info_event():
    event = _fixture_event()
    event["httpMethod"] = "GET"
    event["path"] = "/test/ops/info"
    event["pathParams"] = {"proxy": "info"}
    event["params"]["proxy"] = "info"
    event["url"] = "https://dtm.solofarm.ru/test/ops/info?format=json&view=detail"
    event["queryStringParameters"] = {
        "format": "json",
        "view": "detail",
    }
    event["multiValueQueryStringParameters"] = {
        "format": ["json"],
        "view": ["detail"],
    }
    return event


async def main():
    section("BOOTSTRAP")
    ctx, _ = time_call("build_app_context()", build_app_context)
    engine, _ = time_call("build_snapshot_engine(ctx)", build_snapshot_engine, ctx)

    section("SNAPSHOT READS")
    prep, _ = time_call("engine.get_prep_snapshot()", engine.get_prep_snapshot)
    raw, _ = time_call("engine.get_raw_snapshot()", engine.get_raw_snapshot)
    print("prep type:", type(prep).__name__)
    print("raw type :", type(raw).__name__)

    section("RESPONSE CACHE STORE")
    cache_store = getattr(engine, "response_cache_store", None)
    if cache_store is None and hasattr(engine, "get_response_cache_store"):
        cache_store = engine.get_response_cache_store()

    if cache_store is None:
        print("response cache store: not available")
    else:
        print("response cache store:", type(cache_store).__name__)

    section("INDEX HANDLER SINGLE RUN")
    frontend_event = make_frontend_event()
    response, _ = await time_async_call(
        "index.handler(frontend)", index.handler, frontend_event, None
    )
    print("statusCode:", response.get("statusCode"))
    print("Server-Timing:", response.get("headers", {}).get("Server-Timing"))

    body = json.loads(response["body"])
    print("meta.access.mode:", body.get("meta", {}).get("access", {}).get("mode"))
    print("meta.artifact keys:", sorted(body.get("meta", {}).get("artifact", {}).keys()))

    section("RECENT API TRACES VIA /info")
    info_event = make_info_event()
    info_response, _ = await time_async_call("index.handler(info)", index.handler, info_event, None)
    info_body = json.loads(info_response["body"])
    traces = info_body.get("bottlenecks", {}).get("recentApiTraces", [])
    if not traces:
        print("recentApiTraces: empty")
    else:
        trace = traces[0]
        print("traceId:", trace.get("traceId"))
        print("route:", trace.get("route"))
        print("cacheResult:", trace.get("cacheResult"))
        print("frontendHandlerTotalMs:", trace.get("frontendHandlerTotalMs"))
        print("frontendInnerCoreMs:", trace.get("frontendInnerCoreMs"))
        print("unexplainedInsideHandlerMs:", trace.get("unexplainedInsideHandlerMs"))
        print("unexplainedAfterHandlerMs:", trace.get("unexplainedAfterHandlerMs"))
        print("stages:")
        for stage in trace.get("stages", []):
            print(f"  - {stage.get('stage')}: {stage.get('durationMs')} ms")

    section("REPEATED FRONTEND RUNS")
    runs = []
    for i in range(5):
        t0 = time.perf_counter()
        resp = await index.handler(make_frontend_event(), None)
        t1 = time.perf_counter()
        elapsed = ms(t0, t1)
        runs.append(elapsed)
        print(f"run {i + 1}: {elapsed} ms | {resp.get('headers', {}).get('Server-Timing')}")

    print()
    print("avg:", round(mean(runs), 1), "ms")
    print("min:", min(runs), "ms")
    print("max:", max(runs), "ms")


if __name__ == "__main__":
    asyncio.run(main())
