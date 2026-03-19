"""DEPRECATED: compatibility wrapper over archived legacy planner bootstrap wiring."""

from __future__ import annotations

from typing import Any

from src.archive.legacy_runtime import planner_bootstrap as _impl

PlannerDependencies = _impl.PlannerDependencies
LLM_PROVIDER = _impl.LLM_PROVIDER
LLM_FAILOVER_MODE = _impl.LLM_FAILOVER_MODE
LLM_FAILOVER_PROVIDER = _impl.LLM_FAILOVER_PROVIDER
OPENAI = _impl.OPENAI
GOOGLE_LLM_API_KEY = _impl.GOOGLE_LLM_API_KEY
YANDEX_LLM_API_KEY = _impl.YANDEX_LLM_API_KEY
YANDEX_LLM_MODEL_URI = _impl.YANDEX_LLM_MODEL_URI


def _sync_mutable_knobs() -> None:
    _impl.LLM_PROVIDER = LLM_PROVIDER
    _impl.LLM_FAILOVER_MODE = LLM_FAILOVER_MODE
    _impl.LLM_FAILOVER_PROVIDER = LLM_FAILOVER_PROVIDER
    _impl.OPENAI = OPENAI
    _impl.GOOGLE_LLM_API_KEY = GOOGLE_LLM_API_KEY
    _impl.YANDEX_LLM_API_KEY = YANDEX_LLM_API_KEY
    _impl.YANDEX_LLM_MODEL_URI = YANDEX_LLM_MODEL_URI


def _build_chat_adapter(mock_external: bool, **kwargs: Any):
    _sync_mutable_knobs()
    return _impl._build_chat_adapter(mock_external, **kwargs)


def build_planner_dependencies(*args: Any, **kwargs: Any):
    _sync_mutable_knobs()
    return _impl.build_planner_dependencies(*args, **kwargs)
