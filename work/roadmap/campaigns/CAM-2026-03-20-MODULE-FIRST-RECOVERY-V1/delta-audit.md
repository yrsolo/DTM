# CAM-2026-03-20-MODULE-FIRST-RECOVERY-V1 Delta Audit

## Required table

| Scenario | Owning module | Current path | Target path | Status | Surviving old path | Fake-modularity risk | Next kill move | Required guardrail |
|---|---|---|---|---|---|---|---|---|
| Main browser read payload | `access_api` | `index.py -> src/entrypoint/handler.py -> HttpShell -> HttpRouter -> access_api internal handlers` | `entrypoint -> platform.runtime/http shell -> access_api` | partial | `HttpRouter` still directly owns admin/info/task-attachment route table and mixes access-api with non-access-api handlers | medium | split browser-facing routes from admin/runtime routes and make access-api the single obvious browser read center | top-path readability guard |
| Attachment publication to main task-list payload | `attachments` + `platform.runtime` + `snapshot` + `access_api` | mutation job -> runtime invalidation helper -> snapshot projection -> frontend payload | `attachments mutation -> platform/runtime aftermath -> snapshot projection -> access_api cached delivery` | partial | readiness/status semantics are documented, but code-facing readiness/publication contract is still implicit and spread between jobs, runtime invalidation, and read payload assembly | medium | define explicit publication/readiness contract surface in code or runtime docs before next attachment wave | publication/readiness guard |
| Attachment mutation lifecycle | `attachments` | HTTP/admin handler -> attachments public/module -> attachment jobs in `src/jobs/*` | `entrypoint -> runtime/http shell -> attachments` | partial | `src/jobs/attach_task_file_job.py`, `delete_task_attachment_job.py`, `generate_attachment_preview_job.py`, `cleanup_task_attachments_job.py` remain generic top-level job roots | medium | move attachment job runners under context-owned package or demote `src/jobs/*` from scenario reading paths | no-generic-job-center guard |
| Reminder delivery | `reminders` | trigger/runtime -> reminder public/module -> `src/jobs/send_reminders_job.py` | `entrypoint/runtime -> reminders` | partial | top-level reminder job root still lives in `src/jobs/send_reminders_job.py` | medium | move reminder job runner inward or provide one obvious context-owned execution entry | no-generic-job-center guard |
| Telegram reserve capability | `telegram_interaction` | HTTP router -> webhook handler + `src/jobs/group_query_reply_job.py` | `entrypoint/runtime -> telegram_interaction` | partial | group-query execution still depends on top-level job root and router-level Telegram mounting | low | keep reserve contour stable and avoid new Telegram-led ownership spread; later move job runner inward | reserve-capability regression guard |
| Snapshot/rendering hard boundary | `snapshot` / `rendering` | runtime -> rendering context -> snapshot capabilities | `entrypoint/runtime -> rendering` with capability-only snapshot boundary | true | none in active code path | low | keep as-is; guard against reintroduction of broad engine access | snapshot capability guard |
| Queue command routing | `platform.runtime` + owning modules | queue worker -> `src/platform/runtime/queue_dispatch.py` -> jobs resolved through context public facades | `platform.runtime -> owning module job runner` | partial | dispatcher still executes top-level `src.jobs/*` classes obtained from context public helpers | medium | demote generic jobs by moving runners under context-owned packages | no-generic-job-center guard |
| Top-path clarity | `entrypoint` + `platform.runtime` | `index.py -> handle_entrypoint(... get_http_shell/get_worker_shell/get_trigger_shell, telegram_webhook_path=_get_app_context()...)` | `index.py -> entrypoint handler -> runtime shell/context` | partial | `_get_app_context()` seam and eager webhook-path fetch keep a small but real top-path indirection | low | remove eager app-context lookup for webhook path and keep entrypoint on pure delegation inputs | top-path readability guard |
| Bootstrap gravity | `platform.runtime` | `src/platform/bootstrap.py` builds app context, runtime shell, http shell, worker shell, trigger shell, and lazy mappings | `bootstrap` remains delegation-only and scenario-neutral | partial | `LazyMapping`, shell singletons, and transport shell construction still make bootstrap a visible coordination center | medium | record which pieces are acceptable runtime glue vs which still smell like hidden control center | bootstrap-gravity guard |

## What is already true

- Active code really reads through `index.py`, `src/entrypoint/*`, `src/platform/*`, and owning contexts instead of the removed historical technical roots.
- `snapshot` and `rendering` now use capability-oriented boundaries rather than broad engine-shaped external access.
- `access_api`, `attachments`, `reminders`, and `telegram_interaction` all have real context-owned public/module surfaces.
- The main browser read-side and attachment publication semantics are now explicit in docs.
- Telegram is already documented and treated as reserve capability rather than the main product center.

## What is still violated or only partial

- Generic top-level `src/jobs/*` classes still remain part of the real scenario path for attachments, reminders, Telegram, queue dispatch, and snapshot update.
- Browser read ownership is improved but still visually mixed inside `HttpRouter`, where access-api, admin, ops, and Telegram handlers coexist in one route table.
- Attachment publication/readiness is scenario-correct in docs, but code still lacks a single explicit readiness/publication contract surface.
- Bootstrap is better than before but still carries enough shell-building weight to deserve a dedicated gravity review rather than being assumed solved.
- The entry top path is thin, but still has one extra eager context lookup for Telegram webhook path.

## Most urgent remaining fake-modularity or readability risks

1. `src/jobs/*` still acts as a de facto execution center even though the canon says generic jobs must not be scenario ownership centers.
2. Browser-read ownership is not yet visually pure because `HttpRouter` still mixes browser, admin, ops, and Telegram paths.
3. Attachment publication readiness exists as a scenario, but not yet as one obvious code-facing contract.

## Recommended next kill move

Open the next code wave around **generic jobs demotion**:

- move attachment, reminder, Telegram, and snapshot-triggered job runners under context-owned packages
- keep `src/jobs/*` as temporary compatibility bridges only if unavoidable
- add a guardrail that no new scenario should be introduced by reading `src/jobs/*` first

Secondary follow-up after that:

- split browser read routing from admin/ops/Telegram routing so `access_api` becomes the single obvious browser read center
