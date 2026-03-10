from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.infra.grafana_api import (  # noqa: E402
    ensure_folder,
    grafana_dashboard_url,
    grafana_embed_url,
    upsert_dashboard,
)
from src.infra.grafana_specs import build_test_grafana_dashboard  # noqa: E402


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
    parser = argparse.ArgumentParser(description="Create/update the Grafana dashboard from repo spec.")
    parser.add_argument("--base-url", default="http://style-app.solofarm.ru:3000")
    parser.add_argument("--env", default="test")
    parser.add_argument("--folder-title", default="DTM Test")
    parser.add_argument("--token-env", default="GRAFANA_TOKEN")
    args = parser.parse_args()

    token = _load_env_value(str(args.token_env)) or _load_env_value("GRAFANA_API_TOKEN")
    if not token:
        raise SystemExit("Missing Grafana token in .env or environment.")

    folder = ensure_folder(
        base_url=str(args.base_url),
        api_token=token,
        title=str(args.folder_title),
    )
    dashboard = build_test_grafana_dashboard(env_name=str(args.env))
    result = upsert_dashboard(
        base_url=str(args.base_url),
        api_token=token,
        dashboard=dashboard,
        folder_uid=str(folder.get("uid", "")).strip() or None,
        overwrite=True,
    )
    uid = str(result.get("uid", "")).strip() or str(dashboard.get("uid", "")).strip()
    print(f"folder_uid={folder.get('uid','')}")
    print(f"dashboard_uid={uid}")
    print(f"dashboard_url={grafana_dashboard_url(str(args.base_url), uid)}")
    print(f"embed_url={grafana_embed_url(str(args.base_url), uid)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
