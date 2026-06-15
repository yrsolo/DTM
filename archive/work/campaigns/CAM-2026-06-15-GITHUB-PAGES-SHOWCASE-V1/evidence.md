# CAM-2026-06-15-GITHUB-PAGES-SHOWCASE-V1 Evidence

## Trust Gate

| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| backend runnable artifacts | 2026-06-15 | Codex | `src/contexts`, `src/entrypoints`, `src/platform`, `config/runtime.yaml` | high | Current `dev` branch confirms read-model, queue/worker, attachments, rendering, reminders, Telegram, and observability contours. |
| backend active docs | 2026-06-15 | Codex | `docs/product/*`, `docs/architecture/*` compared with runnable artifacts | high | Active docs match current code-level architecture. |
| frontend runnable artifacts | 2026-06-15 | Codex | current public `yrsolo/DTM-front` clone: `apps/web`, `apps/auth`, `packages/schema`, runtime config | high | React/Vite SPA, auth/admin facade, SnapshotV1 and browser-facing BFF paths verified against runnable artifacts. |
| promo video | 2026-06-15 | Codex | supplied HLS URL loaded in local browser with `readyState=4` | high | HLS playback and fallback behavior verified. |

## Completed Tasks
- [x] `CAM-2026-06-15-GITHUB-PAGES-SHOWCASE-V1-P01-T001`
- [x] `CAM-2026-06-15-GITHUB-PAGES-SHOWCASE-V1-P02-T001`
- [x] `CAM-2026-06-15-GITHUB-PAGES-SHOWCASE-V1-P02-T002`
- [x] `CAM-2026-06-15-GITHUB-PAGES-SHOWCASE-V1-P03-T001`

## Verification
- Command:
  - local reference and required-link check
  - `git diff --check`
  - local HTTP server + in-app browser verification
  - Playwright desktop check at `1440x1000`
  - Playwright mobile check at `390x844`
- Result:
  - all local assets resolve
  - required repository and video links exist
  - no horizontal overflow at desktop or mobile widths
  - generated architecture images load
  - HLS video reaches `readyState=4`
  - mobile layout collapses navigation, labels, architecture, and repository grids as intended

## Notes
- Built-in image generation produced `site/assets/backend-system.png` and `site/assets/frontend-system.png`.
- The page is a public presentation surface; no product runtime behavior is changed.
