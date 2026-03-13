# CAM-2026-03-12-RUNTIME-DEPLANNERIZE-AND-BOOTSTRAP-HARDENING-V1

Status: planned
Priority: P0
Owner intent: remove planner-centric top runtime, eliminate import-time bootstrap side effects, make app importable/testable without production env.

## Why this campaign exists

Current code has good new subsystems, but top runtime still behaves like a hybrid planner-era orchestrator. Import-time bootstrap currently leaks production config requirements into test/import paths and makes reasoning, testing, and further refactoring harder.

This campaign is the first execution priority.

## Scope

In scope:
- `index.py`
- `src/app/bootstrap.py`
- `src/entrypoints/index_dispatcher.py`
- `src/entrypoints/runtime/planner_runtime_entry.py`
- direct callers of planner runtime helpers
- testability of imports for active runtime modules

Out of scope:
- Telegram/reminder redesign
- auth/masking implementation
- major query-engine redesign

## Desired end-state

- no global `APP_CONTEXT = build_app_context()` in runtime modules
- planner runtime reduced to transition adapter or deleted from active paths
- each active top-level action has explicit callable boundary
- app modules import cleanly without prod-only env
- bootstrap becomes composition root only

## Required design rules

1. `build_app_context()` is called only from explicit runtime boundaries.
2. Runtime modules accept `AppContext` as an argument instead of constructing it globally.
3. Business execution functions are split by use-case, not by planner mode matrix.
4. Old planner runtime may remain as compatibility shim but must stop being conceptual center.

## Recommended target structure

### New/updated public runtime seams

```python
# src/entrypoints/runtime/runtime_actions.py
from src.app.context import AppContext


def run_update_snapshot(ctx: AppContext) -> dict: ...

def run_send_reminders(ctx: AppContext) -> dict: ...

def run_render_timeline(ctx: AppContext) -> dict: ...

def run_render_designers(ctx: AppContext) -> dict: ...
```

```python
# src/entrypoints/runtime/planner_runtime_entry.py
from src.app.context import AppContext


def run_planner_runtime(ctx: AppContext, mode: str, **kwargs) -> dict: ...
```

Planner runtime should delegate to explicit runtime actions and contain no global context.

### Bootstrap seam

```python
# src/app/bootstrap.py
from src.app.context import AppContext
from src.config.types import AppConfig


def load_app_config() -> AppConfig: ...

def build_app_context(cfg: AppConfig | None = None) -> AppContext: ...
```

No module-level production bootstrapping.

## Concrete tasks

1. Remove module-level bootstrap side effects from active runtime modules.
2. Introduce `runtime_actions.py` with explicit action functions.
3. Make `IndexDispatcher` call explicit action functions or HTTP router/worker handlers.
4. Reduce `planner_runtime_entry.py` to a thin compatibility adapter.
5. Audit tests/imports that currently fail due to env-dependent imports.
6. Add/import-safe smoke tests.
7. Record remaining transitional imports from old `core/*` and planner-era helpers.

## Suggested smoke tests

- import `index.py` without production secrets in env
- import `src/entrypoints/runtime/planner_runtime_entry.py`
- invoke non-cloud local smoke for read path dispatch
- run targeted tests for bootstrap and dispatcher modules

## Acceptance criteria

- no import-time call chain requires `YANDEX_PROMETHEUS_API_KEY`
- runtime modules are importable in a stripped env
- planner runtime no longer creates global app context
- active top-level actions are explicit functions
- evidence file includes before/after import behavior
