"""Store builders for the snapshot context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.contexts.snapshot.internal.engine.stores.s3_store import build_s3_stores
from src.platform.context import AppContext


@dataclass(frozen=True, slots=True)
class SnapshotStores:
    """Concrete store bundle shared by snapshot services."""

    attachment_bucket: str
    raw_cache: Any
    prep_cache: Any
    extra_store: Any
    people_store: Any
    response_cache_store: Any


def _resolve_env_prefix(value: str, env_name: str) -> str:
    token = "{env}"
    cleaned = str(value or "").strip()
    if token in cleaned:
        return cleaned.replace(token, str(env_name or "").strip().lower() or "dev")
    return cleaned


def build_snapshot_stores(ctx: AppContext) -> SnapshotStores:
    """Build the concrete store bundle shared by snapshot APIs."""

    cfg = ctx.cfg
    deps = ctx.deps
    snap_cfg = cfg.runtime.snapshot_engine
    db_cfg = cfg.db.object_storage
    endpoint_url = str(db_cfg.get("endpoint_url_default", "")).strip()
    env_name = str(cfg.runtime.runtime.env_default).strip().lower() or "dev"
    raw_cache, prep_cache, extra_store, people_store, response_cache_store = build_s3_stores(
        bucket=str(snap_cfg.bucket).strip(),
        endpoint_url=endpoint_url,
        aws_access_key_id=deps.get("aws_access_key_id"),
        aws_secret_access_key=deps.get("aws_secret_access_key"),
        raw_key=_resolve_env_prefix(str(snap_cfg.prefix_raw), env_name),
        prep_key=_resolve_env_prefix(str(snap_cfg.prefix_prep), env_name),
        extra_prefix=_resolve_env_prefix(str(snap_cfg.prefix_extra), env_name),
        people_key=_resolve_env_prefix(str(snap_cfg.prefix_people), env_name),
        response_prefix=_resolve_env_prefix(str(snap_cfg.prefix_responses), env_name),
    )
    return SnapshotStores(
        attachment_bucket=str(snap_cfg.bucket).strip(),
        raw_cache=raw_cache,
        prep_cache=prep_cache,
        extra_store=extra_store,
        people_store=people_store,
        response_cache_store=response_cache_store,
    )
