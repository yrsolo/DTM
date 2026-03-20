"""Compatibility wrapper for the access-api-owned frontend v2 handler."""

from src.contexts.access_api.internal.frontend_v2_handler import (
    FrontendV2Handler,
    build_snapshot_engine,
    get_prep_snapshot,
    get_response_cache_store,
    query_frontend_v2,
)

__all__ = [
    "FrontendV2Handler",
    "build_snapshot_engine",
    "get_prep_snapshot",
    "get_response_cache_store",
    "query_frontend_v2",
]
