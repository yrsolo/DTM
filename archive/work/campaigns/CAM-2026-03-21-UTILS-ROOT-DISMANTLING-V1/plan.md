# CAM-2026-03-21-UTILS-ROOT-DISMANTLING-V1

## Goal

Remove `utils/` as an active repo root by redistributing its still-live code into role-true homes under `src/`.

## Scope

- `utils/**`
- live imports in `src/`, `agent/`, `tests/`, `web_prototype/`, and `local_run.py`
- guardrails and tracking for the resulting contour

## Non-goals

- no new business behavior
- no redesign of snapshot or rendering flows beyond moving helper homes
- no archive rewrite outside link hygiene

## Tasks

- [x] register trust gate from `utils/` contents and live import graph
- [x] move Google Sheets service helpers into `src/platform/integrations/google_sheets/`
- [x] move S3 snapshot storage helper into `src/platform/infra/`
- [x] move render-color helpers into `src/contexts/rendering/internal/`
- [x] localize the remaining stage-filter helper where it is actually used
- [x] update imports/tests and add anti-regression guardrails
- [x] remove `utils/` as an active Python root
- [x] run targeted contour checks

## Done when

- active code no longer imports `utils.*`
- `utils/` contains no tracked active Python code
- each former helper now lives in a role-true home inside `src/`
