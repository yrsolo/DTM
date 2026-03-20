from __future__ import annotations

import unittest

from src.archive.legacy_runtime.entrypoints.jobs.readmodel_probe_job import (
    ReadmodelProbeRequest,
    run_readmodel_freshness_probe,
)


class _RepoStub:
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        self.kwargs = kwargs

    def get_readmodel(self, readmodel_id: str):  # noqa: ARG002
        return object()


class _FailRepoStub:
    def __init__(self, **kwargs) -> None:  # noqa: ANN003
        raise RuntimeError("repo unavailable")


class ReadmodelProbeJobTestCase(unittest.TestCase):
    def test_logs_freshness_when_enabled(self) -> None:
        logs = []
        run_readmodel_freshness_probe(
            ReadmodelProbeRequest(
                mode="test",
                render_source="ydb",
                notify_source="legacy",
                ydb_endpoint="ep",
                ydb_database="db",
                ydb_sa_json_credentials=None,
                ydb_sa_key_file=None,
                marker_builder=lambda _: {"available": True},
                safe_print=logs.append,
                repo_cls=_RepoStub,  # type: ignore[arg-type]
            )
        )
        self.assertTrue(any("readmodel_freshness=" in line for line in logs))

    def test_logs_error_when_probe_fails(self) -> None:
        logs = []
        run_readmodel_freshness_probe(
            ReadmodelProbeRequest(
                mode="test",
                render_source="ydb",
                notify_source="legacy",
                ydb_endpoint="ep",
                ydb_database="db",
                ydb_sa_json_credentials=None,
                ydb_sa_key_file=None,
                marker_builder=lambda _: {"available": True},
                safe_print=logs.append,
                repo_cls=_FailRepoStub,  # type: ignore[arg-type]
            )
        )
        self.assertTrue(any("readmodel_freshness_error=repo unavailable" in line for line in logs))

    def test_skips_when_sources_do_not_require_probe(self) -> None:
        logs = []
        run_readmodel_freshness_probe(
            ReadmodelProbeRequest(
                mode="timer",
                render_source="legacy",
                notify_source="legacy",
                ydb_endpoint="ep",
                ydb_database="db",
                ydb_sa_json_credentials=None,
                ydb_sa_key_file=None,
                marker_builder=lambda _: {"available": True},
                safe_print=logs.append,
                repo_cls=_RepoStub,  # type: ignore[arg-type]
            )
        )
        self.assertEqual(logs, [])


if __name__ == "__main__":
    unittest.main()
