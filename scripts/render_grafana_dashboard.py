from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.platform.integrations.grafana.specs import build_test_grafana_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Grafana dashboard JSON from repo spec.")
    parser.add_argument("--env", default="test", help="Environment label to bake into the dashboard queries.")
    parser.add_argument("--output", default="", help="Optional file path to write the dashboard JSON.")
    parser.add_argument("--datasource-uid", default="", help="Optional Grafana datasource UID to bind panels to.")
    parser.add_argument("--datasource-name", default="", help="Optional Grafana datasource name to bind panels to.")
    args = parser.parse_args()

    dashboard = build_test_grafana_dashboard(
        env_name=str(args.env or "test"),
        datasource_uid=str(args.datasource_uid or ""),
        datasource_name=str(args.datasource_name or ""),
    )
    payload = json.dumps(dashboard, ensure_ascii=False, indent=2)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
