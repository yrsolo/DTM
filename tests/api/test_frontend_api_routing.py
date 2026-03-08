"""Routing and query parser tests for frontend API handlers."""

from __future__ import annotations

import asyncio
import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import index
from src.entrypoints.http import frontend_v2_handler as frontend_v2_module


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


class FrontendApiRoutingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_build_snapshot_engine = frontend_v2_module.build_snapshot_engine
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

    def tearDown(self) -> None:
        frontend_v2_module.build_snapshot_engine = self._orig_build_snapshot_engine  # type: ignore[assignment]

    def test_http_path_from_proxy_template(self) -> None:
        event = _fixture_event()
        self.assertEqual(index._http_path(event), "/api/v1/frontend")

    def test_query_params_from_multivalue(self) -> None:
        event = _fixture_event()
        params = index._query_params(event)
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
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend?statuses=work"
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
        event["url"] = "https://dtm-api-test.solofarm.ru/"
        response = asyncio.run(index.handler(event, None))
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("DTM Frontend API v2", response.get("body", ""))

    def test_info_page_returns_dashboard_html(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "info"
        event["params"]["proxy"] = "info"
        event["url"] = "https://dtm-api-test.solofarm.ru/info"
        response = asyncio.run(index.handler(event, None))
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("DTM Info Dashboard", response.get("body", ""))
        self.assertIn("/admin/commands/render-timeline", response.get("body", ""))
        self.assertIn("/admin/jobs/", response.get("body", ""))

    def test_v2_doc_contains_endpoints_query_and_response_fields(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend/doc"
        event["params"]["proxy"] = "api/v2/frontend/doc"
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend/doc"
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
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend/doc?format=json"
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
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend?window_start=2026-03-01"
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
            "https://dtm-api-test.solofarm.ru/api/v2/frontend?"
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
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend?statuses=work&limit=1"
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
        request_payload, is_http_event = index._extract_payload(event)
        run_mode = index._extract_run_mode(
            event,
            request_payload,
            is_http_event,
            allowed_run_modes=index.ALLOWED_RUN_MODES,
            query_params=index._query_params,
        )
        force_refresh = index._extract_force_refresh(
            event,
            request_payload,
            is_http_event,
            query_params=index._query_params,
            parse_bool=index._parse_bool,
        )
        self.assertEqual(run_mode, "sync-only")
        self.assertTrue(force_refresh)

    def test_runtime_mode_parses_render_v2(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["queryStringParameters"] = {"mode": "render_v2"}
        request_payload, is_http_event = index._extract_payload(event)
        run_mode = index._extract_run_mode(
            event,
            request_payload,
            is_http_event,
            allowed_run_modes=index.ALLOWED_RUN_MODES,
            query_params=index._query_params,
        )
        self.assertEqual(run_mode, "render_v2")

    def test_v2_returns_503_when_snapshot_source_unavailable(self) -> None:
        frontend_v2_module.build_snapshot_engine = lambda _ctx: (_ for _ in ()).throw(RuntimeError("s3 down"))  # type: ignore[assignment]
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend?statuses=work"
        event["queryStringParameters"] = {"statuses": "work"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))

        self.assertEqual(response["statusCode"], 503)
        self.assertEqual(payload.get("error", {}).get("code"), "frontend_source_unavailable")
        self.assertEqual(payload.get("error", {}).get("details", {}).get("source"), "snapshot")


if __name__ == "__main__":
    unittest.main()
