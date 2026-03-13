# CAM-2026-03-12-DOC-CODE-REALIGN-V1

Status: planned
Priority: P1
Owner intent: eliminate architecture-document drift so agents stop following stale system stories.

## Problem statement

Current docs appear to describe multiple project eras at once:
- README still presents YDB/readmodel-first architecture
- newer system docs describe snapshot-first read side
- module map still treats planner-centric orchestration as canonical
- some skeleton docs describe already-implemented paths as future work

This confuses execution and causes architectural backsliding.

## Scope

Required docs to update:
- `README.md`
- `docs/system/architecture.md`
- `docs/system/module_map.md`
- `docs/system/command_runtime_architecture.md`
- `docs/system/metrics_schema.md`
- `docs/system/job_status_schema.md`
- `docs/system/prometheus_integration.md`
- `docs/system/yc_monitoring_integration.md`

Potential archive/update targets:
- telegram skeleton docs
- file attachment skeleton doc
- command queue skeleton doc

## Required editorial rules

1. Active docs must describe current runtime, not historical intent.
2. Transitional modules must be labeled explicitly as transitional.
3. Frozen modules must be labeled frozen.
4. Browser auth namespace and access mode contract must be documented.
5. Docs must mention that Telegram/reminder is frozen for now.

## Concrete tasks

1. Rewrite public architecture summary in `README.md`.
2. Update `architecture.md` to snapshot/query/auth-proxy aware picture.
3. Rewrite `module_map.md` with statuses:
   - canonical
   - transitional
   - frozen
   - legacy
4. Update runtime docs to reflect explicit queue/read split and browser-facing `/ops/*` routes.
5. Update metrics docs to describe real hot-path strategy and stage timings.
6. Archive or relabel stale skeleton docs that are no longer future-only.

## Acceptance criteria

- docs no longer present YDB-first story as canonical read path
- planner runtime is labeled transitional, not ideal canonical center
- browser auth/masked/full contract is documented
- frozen Telegram/reminder status is documented
- doc set has coherent one-story narrative
