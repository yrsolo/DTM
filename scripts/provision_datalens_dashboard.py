from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.config.loader import load_config
from src.platform.integrations.datalens.api import (
    create_dashboard,
    create_ql_chart,
    datalens_dashboard_url,
    find_or_create_monitoring_connection,
    find_or_create_workbook,
)
from src.platform.integrations.datalens.specs import build_test_ops_dashboard_spec
from src.platform.integrations.yandex_cloud.iam import get_iam_token


def _extract_workbook_id(payload: dict[str, object]) -> str:
    for key in ("workbookId", "workbook_id", "id"):
        value = str(payload.get(key, "")).strip()
        if value:
            return value
    return ""


def _yc_cli_value(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True).strip()
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Provision the test-first DataLens ops dashboard from repo specs."
    )
    parser.add_argument("--env", default="", choices=("test", "prod", ""))
    parser.add_argument("--cloud-id", default="")
    args = parser.parse_args()

    cfg = load_config(Path("config"))
    env_name = str(args.env or cfg.runtime.runtime.env_default or "").strip().lower() or "dev"
    if env_name == "prod":
        raise RuntimeError("This provisioning script is test-first only. Switch config/env to test.")
    if not bool(cfg.runtime.datalens.enabled):
        raise RuntimeError("datalens.enabled=false in runtime config.")

    iam_token = _yc_cli_value(["yc", "iam", "create-token"]) or get_iam_token("", "", timeout_seconds=4.0)
    cloud_id = str(args.cloud_id or "").strip() or _yc_cli_value(["yc", "config", "get", "cloud-id"]) or "b1g6d49mf4scmtn4kjki"
    workbook_result = find_or_create_workbook(
        iam_token=iam_token,
        org_id=cfg.runtime.datalens.org_id,
        title=cfg.runtime.datalens.workbook_name,
        description="Ops workbook for DTM observability",
    )
    workbook_id = _extract_workbook_id(workbook_result)
    if not workbook_id:
        raise RuntimeError(f"Workbook id missing in response: {workbook_result}")

    connection_id = str(cfg.runtime.datalens.connection_id_test or "").strip()
    connection_result: dict[str, object] = {"status": "configured", "id": connection_id} if connection_id else {}
    if not connection_id:
        connection_result = find_or_create_monitoring_connection(
            iam_token=iam_token,
            org_id=cfg.runtime.datalens.org_id,
            workbook_id=workbook_id,
            name=cfg.runtime.datalens.connection_name_test,
            cloud_id=cloud_id,
            folder_id=str(cfg.deploy.yandex_cloud.folder_id).strip(),
            service_account_id=str(cfg.deploy.yandex_cloud.service_account_id).strip(),
            description="Monitoring connection for DTM test ops",
        )
        connection_id = str(connection_result.get("id") or connection_result.get("entryId") or "").strip()
    if not connection_id:
        raise RuntimeError(f"Connection id missing in response: {connection_result}")

    spec = build_test_ops_dashboard_spec(env_name="test")
    chart_ids_by_key: dict[str, str] = {}
    for chart_spec in spec.charts:
        chart_result = create_ql_chart(
            iam_token=iam_token,
            org_id=cfg.runtime.datalens.org_id,
            workbook_id=workbook_id,
            connection_entry_id=connection_id,
            spec=chart_spec,
        )
        if not chart_result.entry_id:
            raise RuntimeError(f"Chart id missing for {chart_spec.key}: {chart_result.raw}")
        chart_ids_by_key[chart_spec.key] = chart_result.entry_id

    dashboard_result = create_dashboard(
        iam_token=iam_token,
        org_id=cfg.runtime.datalens.org_id,
        spec=spec,
        chart_ids_by_key=chart_ids_by_key,
    )
    dashboard_id = str(dashboard_result.get("id") or dashboard_result.get("entryId") or "").strip()
    print(
        json.dumps(
            {
                "workbook_id": workbook_id,
                "connection_id": connection_id,
                "chart_ids": chart_ids_by_key,
                "dashboard_id": dashboard_id,
                "dashboard_url": datalens_dashboard_url(cfg.runtime.datalens.org_id, dashboard_id),
                "raw": dashboard_result,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
