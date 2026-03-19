# Evidence - CAM-2026-03-19-MODULAR-MONOLITH-REFORM-V1

## Trust gate
- source: current runtime code, current architecture docs, owner-provided split/campaign briefs
- last_verified_at: 2026-03-19
- verified_by: Codex
- evidence:
  - `index.py`
  - `src/app/bootstrap.py`
  - `src/entrypoints/*`
  - `src/worker/*`
  - `src/jobs/*`
  - `src/services/attachments/*`
  - `src/snapshot_engine/*`
  - `src/telegram/*`
  - `docs/architecture/runtime/*`
  - `agent/intructions/split.md`
  - `agent/intructions/camps.md`
- trust_level: medium
- notes:
  - current code paths were verified as the real active contour for kickoff
  - owner-provided split/campaign docs are treated as target intent, not as executable truth by themselves
  - this campaign is the canonical umbrella for the modular-monolith refactor wave
  - child campaign decomposition must follow the rule in `plan.md` and `docs/architecture/runtime/modular-monolith-v2.md`
  - owner explicitly lifted the temporary Telegram/reminder/group-query freeze on 2026-03-19; extraction can continue inside this umbrella campaign

## Planned early verification
- mode routing tests
- command routing tests
- import-boundary tests
- `os.getenv` grep/test gate
- active-path no-legacy-import gate
- snapshot/rendering boundary test

## Notes
- current blocked operational focus remains `CAM-2026-03-15-TASK-ATTACHMENTS-LIVE-SMOKE-V1`
- this campaign opens the normative architecture and tracking shell for future implementation waves
- `send_reminders` now routes through `src.contexts.reminders.public`
- Telegram webhook/router and `group_query_reply` now route through `src.contexts.telegram_interaction.public`
- rendering-owned jobs now depend on `src.contexts.snapshot.public` / `src.contexts.snapshot.contracts` instead of direct `src.snapshot_engine` imports
- browser-facing HTTP handlers now route through `src.contexts.access_api.public`
