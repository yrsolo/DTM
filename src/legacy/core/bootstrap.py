"""DEPRECATED: reference-only legacy bootstrap compatibility shim."""

from __future__ import annotations

from src.legacy.app import planner_bootstrap as _impl

PlannerDependencies = _impl.PlannerDependencies
build_planner_dependencies = _impl.build_planner_dependencies

# Backward-compatible mutable knobs used by legacy smoke scripts.
LLM_PROVIDER = _impl.LLM_PROVIDER
LLM_FAILOVER_MODE = _impl.LLM_FAILOVER_MODE
LLM_FAILOVER_PROVIDER = _impl.LLM_FAILOVER_PROVIDER
OPENAI = _impl.OPENAI
GOOGLE_LLM_API_KEY = _impl.GOOGLE_LLM_API_KEY
YANDEX_LLM_API_KEY = _impl.YANDEX_LLM_API_KEY
YANDEX_LLM_MODEL_URI = _impl.YANDEX_LLM_MODEL_URI


def _build_chat_adapter(mock_external: bool):
    _impl.LLM_PROVIDER = LLM_PROVIDER
    _impl.LLM_FAILOVER_MODE = LLM_FAILOVER_MODE
    _impl.LLM_FAILOVER_PROVIDER = LLM_FAILOVER_PROVIDER
    _impl.OPENAI = OPENAI
    _impl.GOOGLE_LLM_API_KEY = GOOGLE_LLM_API_KEY
    _impl.YANDEX_LLM_API_KEY = YANDEX_LLM_API_KEY
    _impl.YANDEX_LLM_MODEL_URI = YANDEX_LLM_MODEL_URI
    return _impl._build_chat_adapter(mock_external)
