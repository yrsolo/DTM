"""Routing and query parser tests for frontend API handlers."""

from __future__ import annotations

import asyncio
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import index
from src.entrypoints.http import frontend_v2_handler as frontend_v2_module
from src.entrypoints.http import info_handler as info_handler_module
from src.entrypoints.http.event_parser import extract_payload, http_path, query_params
from src.entrypoints.http.frontend_query_params import parse_bool
from src.entrypoints.http.runtime_mode import extract_force_refresh, extract_run_mode
from src.entrypoints.runtime.runtime_contract import STANDARD_RUN_MODES
from src.worker.model import JobStatusRecord


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "http_event_yc_api_gw.json"


def _fixture_event() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class _FakeSnapshotEngine:
    def __init__(self, payload: dict):
        self.payload = payload
        self.queries = []

    def frontend_v2(self, query):  # noqa: ANN001
        self.queries.append(query)
        return dict(self.payload)


class _FakeInfoSnapshotEngine:
    def __init__(self) -> None:
        now = "2026-03-09T12:00:00Z"
        self._prep_cache = type(
            "PrepCache",
            (),
            {
                "get": staticmethod(
                    lambda: type(
                        "Prep",
                        (),
                        {
                            "tasks_by_id": {"task-1": type("TaskView", (), {"sheet": type("Sheet", (), {"status": "work"})()})()},
                            "source_id": "sheet:test",
                            "raw_source_hash": "sha256:test",
                            "built_at_utc": datetime.fromisoformat(now.replace("Z", "+00:00")),
                        },
                    )()
                )
            },
        )()
        self._raw_cache = type(
            "RawCache",
            (),
            {"get": staticmethod(lambda: type("Raw", (), {"fetched_at_utc": datetime.fromisoformat(now.replace("Z", "+00:00"))})())},
        )()


class _FakeInfoStatusStore:
    def __init__(self) -> None:
        self.render = JobStatusRecord(
            job_id="job-render-1",
            command_type="render_timeline_sheet",
            status="success",
            requested_at_utc=datetime(2026, 3, 9, 12, 0, tzinfo=timezone.utc),
            finished_at_utc=datetime(2026, 3, 9, 12, 0, 5, tzinfo=timezone.utc),
            requested_by={"source": "admin"},
            summary={"render_applied": False, "target_worksheet": "Задачи"},
            warnings=["no_matching_tasks"],
        )

    def get_recent(self, limit: int = 20):
        return [self.render][:limit]

    def get_latest(self, command_type: str):
        if command_type == "render_timeline_sheet":
            return self.render
        return None


class FrontendApiRoutingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_build_snapshot_engine = frontend_v2_module.build_snapshot_engine
        self._orig_info_build_snapshot_engine = info_handler_module.build_snapshot_engine
        self._orig_info_get_queue_live_stats = info_handler_module.get_queue_live_stats
        self._orig_info_get_function_build_info = info_handler_module.get_function_build_info
        self._orig_info_storage_stats = info_handler_module.InfoHandler._storage_stats
        self._orig_job_status_store = index.APP_DEPS.get("job_status_store")
        self._engine = _FakeSnapshotEngine(
            payload={
                "meta": {
                    "artifact": "dtm_frontend_api_v2",
                    "contractVersion": "2.0.1",
                    "generatedAt": "2026-03-02T00:00:00Z",
                    "syncedAt": "2026-03-02T00:00:00Z",
                    "readmodelSource": "s3_snapshot",
                },
                "summary": {"tasksReturned": 1},
                "filters": {},
                "entities": {"people": [], "groups": [], "tags": [], "enums": {}},
                "tasks": [{"id": "101", "history": "raw"}],
            }
        )
        frontend_v2_module.build_snapshot_engine = lambda _ctx: self._engine  # type: ignore[assignment]
        info_handler_module.build_snapshot_engine = lambda _ctx: _FakeInfoSnapshotEngine()  # type: ignore[assignment]
        info_handler_module.get_queue_live_stats = lambda **_kwargs: type(  # type: ignore[assignment]
            "QueueStats",
            (),
            {"to_dict": staticmethod(lambda: {"queue_name": "dtm-test-commands", "messages_visible": 1, "messages_in_flight": 0, "messages_delayed": 0, "dlq_configured": True})},
        )()
        info_handler_module.get_function_build_info = lambda **_kwargs: type(  # type: ignore[assignment]
            "BuildInfo",
            (),
            {
                "function_name": "dtm",
                "active_version_id": "d4etest",
                "deployed_at": "2026-03-09T09:00:00Z",
                "runtime": "python311",
                "memory": "512MB",
                "timeout_seconds": 240,
                "entrypoint": "index.handler",
                "service_account_id": "aje-test",
            },
        )()
        info_handler_module.InfoHandler._storage_stats = lambda _self, _bucket, _prefix: {  # type: ignore[assignment]
            "objectsTotal": 4,
            "bytesTotal": 1024,
            "bytesHuman": "1.00 KB",
            "byPrefix": {"raw": 100, "prep": 200, "extra": 300, "attachments": 400, "jobs": 24},
        }
        index.APP_DEPS["job_status_store"] = _FakeInfoStatusStore()

    def tearDown(self) -> None:
        frontend_v2_module.build_snapshot_engine = self._orig_build_snapshot_engine  # type: ignore[assignment]
        info_handler_module.build_snapshot_engine = self._orig_info_build_snapshot_engine  # type: ignore[assignment]
        info_handler_module.get_queue_live_stats = self._orig_info_get_queue_live_stats  # type: ignore[assignment]
        info_handler_module.get_function_build_info = self._orig_info_get_function_build_info  # type: ignore[assignment]
        info_handler_module.InfoHandler._storage_stats = self._orig_info_storage_stats  # type: ignore[assignment]
        index.APP_DEPS["job_status_store"] = self._orig_job_status_store

    def test_http_path_from_proxy_template(self) -> None:
        event = _fixture_event()
        self.assertEqual(http_path(event), "/api/v1/frontend")

    def test_query_params_from_multivalue(self) -> None:
        event = _fixture_event()
        params = query_params(event)
        self.assertEqual(params.get("statuses"), "work,pre_done")
        self.assertEqual(params.get("limit"), "100")
        self.assertEqual(params.get("include_people"), "true")

    def test_v1_endpoint_aliases_to_v2_payload(self) -> None:
        event = _fixture_event()
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(payload.get("meta", {}).get("artifact"), "dtm_frontend_api_v2")
        self.assertIn("history", payload.get("tasks", [{}])[0])

    def test_v2_endpoint_returns_v2_payload(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm.solofarm.ru/test/api/v2/frontend?statuses=work"
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response["body"])
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(payload.get("meta", {}).get("artifact"), "dtm_frontend_api_v2")
        self.assertEqual(payload.get("meta", {}).get("readmodelSource"), "s3_snapshot")

    def test_root_returns_v2_doc(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = ""
        event["params"]["proxy"] = ""
        event["path"] = "/"
        event["url"] = "https://dtm.solofarm.ru/"
        response = asyncio.run(index.handler(event, None))
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("DTM Frontend API v2", response.get("body", ""))

    def test_info_page_returns_dashboard_html(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "info"
        event["params"]["proxy"] = "info"
        event["url"] = "https://dtm.solofarm.ru/info"
        response = asyncio.run(index.handler(event, None))
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("DTM Info Dashboard", response.get("body", ""))
        self.assertIn("Function Build", response.get("body", ""))
        self.assertIn("Queue State", response.get("body", ""))
        self.assertIn("Recent Jobs", response.get("body", ""))
        self.assertIn("Last Render Job", response.get("body", ""))

    def test_info_json_contains_telegram_block(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "info"
        event["params"]["proxy"] = "info"
        event["url"] = "https://dtm.solofarm.ru/info?format=json"
        event["queryStringParameters"] = {"format": "json"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("telegram", payload)
        self.assertIn("webhookPath", payload["telegram"])
        self.assertIn("build", payload)
        self.assertIn("jobs", payload)
        self.assertIn("renderDebug", payload)
        self.assertEqual(payload.get("build", {}).get("activeVersionId"), "d4etest")

    def test_v2_doc_contains_endpoints_query_and_response_fields(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend/doc"
        event["params"]["proxy"] = "api/v2/frontend/doc"
        event["url"] = "https://dtm.solofarm.ru/test/api/v2/frontend/doc"
        response = asyncio.run(index.handler(event, None))
        body = response.get("body", "")
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("Endpoints", body)
        self.assertIn("Query Examples", body)
        self.assertIn("tasks[].revision", body)
        self.assertIn("brand", body)
        self.assertIn("format_", body)
        self.assertIn("customer", body)
        self.assertIn("history", body)
        self.assertIn("reserved", body)
        self.assertIn("implemented", body)

    def test_v2_doc_json_contains_field_status(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend/doc"
        event["params"]["proxy"] = "api/v2/frontend/doc"
        event["url"] = "https://dtm.solofarm.ru/test/api/v2/frontend/doc?format=json"
        event["queryStringParameters"] = {"format": "json"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))
        field_status = payload.get("field_status", {})
        statuses_query = payload.get("query", {}).get("statuses", {})
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(field_status.get("tasks[].hash"), "reserved")
        self.assertEqual(field_status.get("summary"), "implemented")
        self.assertEqual(
            statuses_query.get("allowed_values"),
            ["work", "pre_done", "wait", "done"],
        )

    def test_v2_window_validation_requires_both_bounds(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm.solofarm.ru/test/api/v2/frontend?window_start=2026-03-01"
        event["queryStringParameters"] = {"window_start": "2026-03-01"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(payload.get("error", {}).get("code"), "invalid_window")

    def test_v2_window_validation_rejects_invalid_range(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = (
            "https://dtm.solofarm.ru/test/api/v2/frontend?"
            "window_start=2026-04-01&window_end=2026-03-01"
        )
        event["queryStringParameters"] = {
            "window_start": "2026-04-01",
            "window_end": "2026-03-01",
        }
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(payload.get("error", {}).get("code"), "invalid_window")

    def test_v2_limit_and_status_filters_are_forwarded_to_query_engine(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm.solofarm.ru/test/api/v2/frontend?statuses=work&limit=1"
        event["queryStringParameters"] = {"statuses": "work", "limit": "1"}
        response = asyncio.run(index.handler(event, None))

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(len(self._engine.queries), 1)
        self.assertEqual(self._engine.queries[0].statuses, ["work"])
        self.assertEqual(self._engine.queries[0].limit, 1)

    def test_runtime_mode_parses_sync_only_and_force_refresh(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["queryStringParameters"] = {
            "mode": "sync-only",
            "force_refresh": "1",
        }
        request_payload, is_http_event = extract_payload(event)
        run_mode = extract_run_mode(
            event,
            request_payload,
            is_http_event,
            allowed_run_modes=STANDARD_RUN_MODES,
            query_params=query_params,
        )
        force_refresh = extract_force_refresh(
            event,
            request_payload,
            is_http_event,
            query_params=query_params,
            parse_bool=parse_bool,
        )
        self.assertEqual(run_mode, "sync-only")
        self.assertTrue(force_refresh)

    def test_runtime_mode_parses_render_v2(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["queryStringParameters"] = {"mode": "render_v2"}
        request_payload, is_http_event = extract_payload(event)
        run_mode = extract_run_mode(
            event,
            request_payload,
            is_http_event,
            allowed_run_modes=STANDARD_RUN_MODES,
            query_params=query_params,
        )
        self.assertEqual(run_mode, "render_v2")

    def test_legacy_runtime_mode_is_rejected_explicitly(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["queryStringParameters"] = {"mode": "legacy_planner_timer"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(payload.get("error", {}).get("code"), "unsupported_mode")

    def test_v2_returns_503_when_snapshot_source_unavailable(self) -> None:
        frontend_v2_module.build_snapshot_engine = lambda _ctx: (_ for _ in ()).throw(RuntimeError("s3 down"))  # type: ignore[assignment]
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm.solofarm.ru/test/api/v2/frontend?statuses=work"
        event["queryStringParameters"] = {"statuses": "work"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))

        self.assertEqual(response["statusCode"], 503)
        self.assertEqual(payload.get("error", {}).get("code"), "frontend_source_unavailable")
        self.assertEqual(payload.get("error", {}).get("details", {}).get("source"), "snapshot")


if __name__ == "__main__":
    unittest.main()
