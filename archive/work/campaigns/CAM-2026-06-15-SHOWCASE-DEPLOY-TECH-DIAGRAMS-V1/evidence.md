# CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1 Evidence

## Trust Gate

| source | last_verified_at | verified_by | evidence | trust_level | notes |
|---|---|---|---|---|---|
| GitHub repository and auth | 2026-06-15 | Codex | `gh auth status`, `gh repo view yrsolo/DTM` | high | Authenticated owner account; public repository; default branch is `main`. |
| GitHub Pages state | 2026-06-15 | Codex | `gh api repos/yrsolo/DTM/pages` returned 404 | high | Pages must be enabled for workflow deployment. |
| backend architecture | 2026-06-15 | Codex | current `src/**`, `config/runtime.yaml`, active architecture docs | high | Must remain the source for diagram labels and flow. |
| frontend architecture | 2026-06-15 | Codex | current public `yrsolo/DTM-front` runnable artifacts | high | Must remain the source for diagram labels and flow. |

## Completed Tasks
- [x] `CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1-P01-T001`
- [x] `CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1-P02-T001`
- [x] `CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1-P02-T002`
- [x] `CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1-P02-T003`
- [x] `CAM-2026-06-15-SHOWCASE-DEPLOY-TECH-DIAGRAMS-V1-P03-T001`

## Verification
- Initial deployment:
  - commit `63b6068` pushed to `main`
  - GitHub Pages enabled with workflow build type
  - workflow run `27567188974` completed successfully
  - `https://yrsolo.github.io/DTM/` returned HTTP 200 and contained the required repository links
- Technical diagram verification:
  - backend sources: active `docs/architecture/*`, `docs/modules/*`, and current module/entrypoint/runtime code
  - frontend sources: current public `DTM-front` `SYSTEM_ARCHITECTURE.md`, `DATA_FLOW.md`, `App.tsx`, and `useSnapshot.ts`
  - generated backplates saved as `site/assets/*-backplate-v2.png`
  - exact prompts saved in `site/diagram-prompts.md`
  - deterministic labels and connections saved in `site/assets/*-architecture.svg`
  - SVG XML parse passed
  - rendered diagram review passed after correcting clipped labels
  - owner feedback incorporated: exact topology retained while major modules received symbolic volumetric icons and lifted panels
  - local page checks passed at `1440x1000` and `390x844`
  - no horizontal overflow or browser console errors
  - hybrid symbolic-module revision deployed in commit `59697b2`
  - GitHub Pages run `27568968775` completed successfully
  - public page, both SVG diagrams, and saved prompt document returned HTTP 200
