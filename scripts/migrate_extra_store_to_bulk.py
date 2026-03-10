from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app.bootstrap import build_app_context
from src.snapshot_engine.model import ExtraSnapshot, TaskExtra
from src.snapshot_engine.serialization import extra_from_dict
from src.snapshot_engine.stores.s3_store import _S3JsonStore


def build_bulk_extra_snapshot_from_legacy(entries: list[tuple[str, TaskExtra]]) -> tuple[ExtraSnapshot, dict[str, Any]]:
    items_by_task_id: dict[str, TaskExtra] = {}
    collisions: list[str] = []
    for key, extra in entries:
        task_id = str(extra.task_id or "").strip()
        if not task_id:
            continue
        if task_id in items_by_task_id:
            collisions.append(task_id)
        items_by_task_id[task_id] = extra
    report = {
        "objects_scanned": len(entries),
        "valid_extras_migrated": len(items_by_task_id),
        "duplicate_task_ids": sorted(set(collisions)),
    }
    return (
        ExtraSnapshot(
            version=2,
            updated_at_utc=datetime.now(timezone.utc),
            items_by_task_id=items_by_task_id,
        ),
        report,
    )


def migrate_extra_store_to_bulk(*, bucket: str, endpoint_url: str | None, access_key: str | None, secret_key: str | None, prefix: str) -> dict[str, Any]:
    store = _S3JsonStore(
        bucket=bucket,
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    clean_prefix = str(prefix).rstrip("/") + "/"
    bulk_key = f"{clean_prefix}default.json"
    entries: list[tuple[str, TaskExtra]] = []
    invalid_payload_count = 0
    for key in store.list_prefix(clean_prefix):
        if key == bulk_key:
            continue
        payload = store.get(key)
        if payload is None:
            continue
        try:
            extra = extra_from_dict(payload)
        except Exception:
            invalid_payload_count += 1
            continue
        entries.append((key, extra))
    snapshot, report = build_bulk_extra_snapshot_from_legacy(entries)
    from src.snapshot_engine.serialization import extra_snapshot_to_dict

    store.put(bulk_key, extra_snapshot_to_dict(snapshot))
    report["invalid_payload_count"] = invalid_payload_count
    report["bulk_key"] = bulk_key
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy per-task snapshot extras into one bulk extra snapshot.")
    parser.add_argument("--env", default="", help="Environment name used to resolve {env} placeholders from runtime config.")
    args = parser.parse_args()

    ctx = build_app_context()
    cfg = ctx.cfg
    deps = ctx.deps
    env_name = str(args.env or cfg.runtime.runtime.env_default).strip().lower() or "dev"
    snap_cfg = cfg.runtime.snapshot_engine
    db_cfg = cfg.db.object_storage
    prefix = str(snap_cfg.prefix_extra).replace("{env}", env_name)
    report = migrate_extra_store_to_bulk(
        bucket=str(snap_cfg.bucket).strip(),
        endpoint_url=str(db_cfg.get("endpoint_url_default", "")).strip() or None,
        access_key=deps.get("aws_access_key_id"),
        secret_key=deps.get("aws_secret_access_key"),
        prefix=prefix,
    )
    for key, value in report.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
