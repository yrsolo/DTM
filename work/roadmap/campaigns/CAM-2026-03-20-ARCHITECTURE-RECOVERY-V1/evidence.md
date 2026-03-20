# CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1 Evidence

## Trust gate
- source: active runtime docs, modularity audit, current context/module code, owner-provided recovery plan
- last_verified_at: 2026-03-20
- verified_by: Codex
- evidence:
  - `docs/architecture/runtime/modular-monolith-v2.md`
  - `docs/architecture/runtime/modularity-audit-2026-03-19.md`
  - `src/contexts/*/module.py`
  - `src/contexts/*/public.py`
  - `agent/intructions/new_plan.md`
- trust_level: high
- notes:
  - recovery canon replaces the previous normative source because the audit shows the existing modular-monolith wave stopped at phase-one modularity
  - current runtime docs such as `module-map.md` remain descriptive evidence, not the new normative source

## Completed Tasks
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T002`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T003`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P01-T004`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P02-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P03-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P04-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P05-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P06-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P07-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P08-T001`
- [x] `CAM-2026-03-20-ARCHITECTURE-RECOVERY-V1-P09-T001`

## Verification
- Command:
  - `Get-Content docs/architecture/runtime/modular-monolith-v2.md`
  - `Get-Content docs/architecture/runtime/modularity-audit-2026-03-19.md`
  - `rg -n "get_snapshot_engine\\(|src\\.(render|notify|telegram|services\\.attachments|entrypoints\\.http)" src`
- Result:
  - current code still matches the audit diagnosis that ownership facades exist but several technical clusters still compete as implementation centers

## Notes
- This campaign opens the architecture-recovery canon only.
- Later phases must remove or hard-deprecate at least one old path per wave.
- 2026-03-20: active top path no longer routes through `IndexDispatcher`; the dispatcher stays only as transitional compatibility code.
- 2026-03-20: `platform.runtime.queue_bootstrap` no longer wires domain jobs through direct `src.jobs/*` imports; job assembly now enters through owning context facades.
- 2026-03-20: active HTTP attachment entrypoints no longer import `src.services.attachments` directly; `admin_task_attachments_handler`, `task_attachment_read_handler`, and attachment mime publication in `info_handler` now enter through `src.contexts.attachments.public`.
- 2026-03-20: added a recovery guardrail that fails if active HTTP entrypoints re-introduce direct `src.services.attachments` imports.
- 2026-03-20: attachment mutation jobs no longer import HTTP cache helpers directly; default frontend cache invalidation now enters through `src.platform.runtime.frontend_cache_invalidation`, with a guardrail banning `src.entrypoints.http.frontend_response_cache` imports from jobs.
- 2026-03-20: active reminder and group-query execution paths no longer import `src.notify` or `src.telegram` directly in `send_reminders_job`, `group_query_reply_job`, and `planner_runtime_entry`; those paths now build requests and senders through owning context public surfaces.
- 2026-03-20: `src.notify/*` is now compatibility-only; owning reminder implementation lives under `src.contexts.reminders.internal/*`, and the reminders context module builds from its own internal package instead of the old technical root.
- 2026-03-20: `src.telegram/*` is now compatibility-only; owning telegram implementation lives under `src.contexts.telegram_interaction.internal/*`, and the telegram interaction context module now builds parser/router/sender/webhook/group-query pieces from its own internal package.
- 2026-03-20: `src.render/*` is now compatibility-only; owning rendering implementation lives under `src.contexts.rendering.internal/*`, and the rendering context module now builds usecases/job/writer/target-guard from its own internal package.
- 2026-03-20: `src.services.attachments/*` is now compatibility-only; owning attachment implementation lives under `src.contexts.attachments.internal/*`, and the attachments context module now builds storage/finalize/read/metadata pieces from its own internal package.
- 2026-03-20: active contexts no longer import `src.contexts.snapshot.public.get_snapshot_engine`; rendering, reminders, telegram interaction, attachments, runtime orchestration, and update flows now use snapshot-owned read/update/attachment/query capabilities instead of the broad engine surface.
- 2026-03-20: active HTTP read handlers no longer depend on the broad snapshot engine surface directly; `frontend_v2_handler`, `info_handler`, and `people_snapshot_handler` now build against snapshot query capability, while `admin_queue_handler` reads snapshot state through `get_prep_snapshot` only.
- 2026-03-20: `access_api` now owns frontend root, frontend v2, info, people snapshot, and attachment read handlers under `src.contexts.access_api.internal/*`; `src.contexts.access_api.module` builds from that internal package instead of `src.entrypoints.http.*`.
- 2026-03-20: direct API outer-trace finalization now follows the active `HttpShell` top path; `function_total`, outer debug headers, and recent outer-trace recording no longer depend on the retired `IndexDispatcher` path.
- 2026-03-20: old HTTP handler modules (`frontend_compat_handlers`, `frontend_v2_handler`, `info_handler`, `people_snapshot_handler`, `task_attachment_read_handler`) are now compatibility wrappers only; the owning implementation center is `access_api`.
- 2026-03-20: `src.entrypoints.index_dispatcher.IndexDispatcher` is now compatibility-only and delegates into `src.entrypoint.handler`; active top-path ownership stays in the thin entrypoint plus shells.
- 2026-03-20: added `docs/integrations/attachments/frontend-card-publication.md` and rewired recovery/module/product docs so attachment-related waves are judged by publication into the cached task card payload, not by upload/finalize alone.
- 2026-03-20: active attachment consumers no longer import `src.services.attachments`; `attach_task_file_job`, `snapshot_engine.engine`, and `snapshot_engine.frontend_v2_payload_builder` now consume attachment-owned contracts/policy from `src.contexts.attachments.contracts`, with a guardrail banning regressions in those active paths.
- 2026-03-20: active `access_api` code no longer imports `src.entrypoints.http.frontend_response_cache`; the default frontend response cache helper now lives under `src.contexts.access_api.internal.frontend_response_cache`, while the old HTTP helper path is compatibility-only.
