"""Routing and query parser tests for frontend API handlers."""

from __future__ import annotations

import asyncio
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import index


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "http_event_yc_api_gw.json"


def _fixture_event() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class FrontendApiRoutingTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_readmodel_repo = index.FrontendReadmodelRepo
        index.FrontendReadmodelRepo = lambda *args, **kwargs: SimpleNamespace(  # type: ignore[assignment]
            get_readmodel=lambda readmodel_id: SimpleNamespace(  # noqa: ARG005
                readmodel_id="frontend_v2:default",
                payload_hash="sha256:test",
                built_from_source_hash="source_hash",
                payload=lambda: {
                    "meta": {
                        "artifact": "dtm_frontend_api_v2",
                        "contractVersion": "2.0.1",
                        "generatedAt": "2026-03-02T00:00:00Z",
                        "syncedAt": "2026-03-02T00:00:00Z",
                    },
                    "summary": {"tasksReturned": 1},
                    "filters": {},
                    "entities": {"people": [], "groups": [], "tags": [], "enums": {}},
                    "tasks": [{"id": "101"}],
                },
            )
        )

    def tearDown(self) -> None:
        index.FrontendReadmodelRepo = self._orig_readmodel_repo

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

    def test_root_returns_v2_doc(self) -> None:
        event = _fixture_event()
        event["pathParams"]["proxy"] = ""
        event["params"]["proxy"] = ""
        event["path"] = "/"
        event["url"] = "https://dtm-api-test.solofarm.ru/"
        response = asyncio.run(index.handler(event, None))
        self.assertEqual(response["statusCode"], 200)
        self.assertIn("DTM Frontend API v2", response.get("body", ""))

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

    def test_v2_reads_tasks_from_readmodel_when_source_ydb(self) -> None:
        index.FrontendReadmodelRepo = lambda *args, **kwargs: SimpleNamespace(  # type: ignore[assignment]
            get_readmodel=lambda readmodel_id: SimpleNamespace(  # noqa: ARG005
                readmodel_id="frontend_v2:default",
                payload_hash="sha256:test",
                built_from_source_hash="source_hash",
                payload=lambda: {
                    "meta": {"artifact": "dtm_frontend_api_v2"},
                    "summary": {"tasksReturned": 1},
                    "filters": {},
                    "entities": {"people": [], "groups": [], "tags": [], "enums": {}},
                    "tasks": [{"id": "501"}],
                },
            )
        )
        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend?statuses=work"
        event["queryStringParameters"] = {"statuses": "work"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(payload.get("meta", {}).get("readmodelSource"), "ydb")
        self.assertEqual(payload.get("summary", {}).get("tasksReturned"), 1)

    def test_v2_returns_503_when_readmodel_transport_unavailable(self) -> None:
        class _BrokenReadmodelRepo:
            def __init__(self, *args, **kwargs) -> None:  # noqa: D401, ANN002, ANN003
                pass

            def get_readmodel(self, readmodel_id):  # noqa: ANN001
                _ = readmodel_id
                raise RuntimeError("ydb package is required")

        index.FrontendReadmodelRepo = _BrokenReadmodelRepo  # type: ignore[assignment]

        event = _fixture_event()
        event["pathParams"]["proxy"] = "api/v2/frontend"
        event["params"]["proxy"] = "api/v2/frontend"
        event["url"] = "https://dtm-api-test.solofarm.ru/api/v2/frontend?statuses=work"
        event["queryStringParameters"] = {"statuses": "work"}
        response = asyncio.run(index.handler(event, None))
        payload = json.loads(response.get("body", "{}"))

        self.assertEqual(response["statusCode"], 503)
        self.assertEqual(payload.get("error", {}).get("code"), "frontend_source_unavailable")
        self.assertEqual(payload.get("error", {}).get("details", {}).get("source"), "readmodel")


if __name__ == "__main__":
    unittest.main()
