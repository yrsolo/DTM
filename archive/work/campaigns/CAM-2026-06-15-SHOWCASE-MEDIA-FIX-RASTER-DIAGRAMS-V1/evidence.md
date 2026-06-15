# Evidence

## Freshness And Trust

- source: owner request in current chat
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: Owner reported the video player does not work, requested generated raster-style diagrams like the attached references, asked to remove the hero CTA button row, and asked to rewrite the annotation.
  - trust_level: high
  - notes: Direct current owner instruction.
- source: current repo state
  - last_verified_at: 2026-06-15
  - verified_by: Codex
  - evidence: `git status --short --branch` showed clean `dev...origin/dev` before new edits.
  - trust_level: high
  - notes: Static showcase changes only.

## Implementation Evidence

- source: video playback diagnosis
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: Local `DTM_lo.mp4` from the frontend inspect clone was HEVC/H.265 (`codec_name=hevc`), which is not a reliable browser playback format. It was transcoded to `site/assets/DTM_promo_h264.mp4` with H.264 (`codec_name=h264`, 854x480), and the video element now uses the H.264 MP4 directly with `preload="none"`.
  - trust_level: high
  - notes: The CSS bug that made the hidden fallback visible was fixed with `.video-fallback[hidden] { display: none; }`.
- source: generated raster diagrams
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: Generated and inspected `backend-generated.png`, `frontend-generated.png`, and `notification-generated.png`; each is 1672x941 and follows the requested light isometric technical-infographic reference style.
  - trust_level: high
  - notes: Prompts are saved in `site/diagram-prompts.md`; exact text labels remain in page captions/copy instead of generated image text.
- source: local static smoke
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: Local static server returned HTTP 200 for `/` and `assets/DTM_promo_h264.mp4`. Local HTML reference check found no missing local assets, confirmed generated PNG tab references, no old SVG tab references, and no hero CTA row.
  - trust_level: high
  - notes: Desktop screenshots were rendered with headless Edge for the video and backend tab.
- source: public GitHub Pages deployment
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: GitHub Actions `Deploy GitHub Pages showcase` completed successfully for `feat: add generated showcase diagrams and stable video` on `main`. Public checks returned HTTP 200 for `/`, `assets/DTM_promo_h264.mp4`, `video-poster.jpg`, all three generated PNG diagrams, and `diagram-prompts.md`; public HTML contains generated PNG references, no HLS runtime, and no hero CTA row.
  - trust_level: high
  - notes: Live screenshot of `https://yrsolo.github.io/DTM/#back` shows the generated raster backend diagram.
