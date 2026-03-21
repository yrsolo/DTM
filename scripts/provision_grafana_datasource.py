from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.config.loader import load_config  # noqa: E402
from src.platform.integrations.grafana.api import upsert_prometheus_datasource  # noqa: E402
from src.platform.integrations.yandex_cloud.prometheus import workspace_query_endpoint  # noqa: E402


def _load_env_value(name: str) -> str:
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == name:
                return value.strip().strip('"').strip("'")
    return str(os.getenv(name, "")).strip()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or update the Grafana Prometheus datasource for DTM."
    )
    parser.add_argument("--env", default="test", choices=("test", "prod"))
    parser.add_argument("--base-url", default="")
    parser.add_argument("--name", default="")
    parser.add_argument("--workspace-id", default="")
    parser.add_argument("--query-url", default="")
    parser.add_argument("--grafana-token-env", default="GRAFANA_TOKEN")
    parser.add_argument("--prometheus-token-env", default="YANDEX_PROMETHEUS_API_KEY")
    args = parser.parse_args()

    cfg = load_config()
    env_name = str(args.env or "test").strip().lower()
    grafana_cfg = cfg.runtime.grafana
    prometheus_cfg = cfg.runtime.prometheus

    base_url = str(args.base_url or grafana_cfg.public_base_url or "").strip()
    if not base_url:
        raise SystemExit("Missing Grafana base URL. Set grafana.public_base_url or pass --base-url.")

    datasource_name = str(args.name or "").strip() or (
        "DTM YMP Prod" if env_name == "prod" else "DTM YMP Test"
    )
    workspace_id = str(args.workspace_id or "").strip()
    if not workspace_id:
        if env_name == "prod":
            workspace_id = str(prometheus_cfg.workspace_id_prod or "").strip() or str(
                prometheus_cfg.workspace_id_test or ""
            ).strip()
        else:
            workspace_id = str(prometheus_cfg.workspace_id_test or "").strip() or str(
                prometheus_cfg.workspace_id_prod or ""
            ).strip()
    query_url = str(args.query_url or "").strip() or workspace_query_endpoint(workspace_id)
    if not query_url:
        raise SystemExit(
            "Missing YMP query endpoint. Set prometheus.workspace_id_* in config or pass --workspace-id/--query-url."
        )

    grafana_token = (
        _load_env_value(str(args.grafana_token_env))
        or _load_env_value("GRAFANA_API_TOKEN")
    )
    if not grafana_token:
        raise SystemExit("Missing Grafana API token in .env or environment.")

    prometheus_token = (
        _load_env_value(str(args.prometheus_token_env))
        or _load_env_value("YMP_API_KEY")
    )
    if not prometheus_token:
        raise SystemExit("Missing Yandex Prometheus API key in .env or environment.")

    result = upsert_prometheus_datasource(
        base_url=base_url,
        api_token=grafana_token,
        name=datasource_name,
        datasource_url=query_url,
        bearer_token=prometheus_token,
    )
    print(f"name={datasource_name}")
    print(f"url={query_url}")
    print(f"id={result.get('id', '')}")
    print(f"uid={result.get('datasource', {}).get('uid', '') or result.get('uid', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
