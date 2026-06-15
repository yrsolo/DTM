# Evidence

## Freshness And Trust

- source: owner request in current chat
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: Owner requested replacing the object tray in the notification image with a friendly female virtual character, using `site/assets/Screenshot 2026-06-16 012844.png` for the site screenshot, clarifying scheme descriptions, and adding `https://dtm.solofarm.ru`.
  - trust_level: high
  - notes: Direct current owner instruction.
- source: current repo state
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: `git status --short --branch` showed `dev...origin/dev`; the requested screenshot exists as `site/assets/Screenshot 2026-06-16 012844.png` and is currently untracked.
  - trust_level: high
  - notes: Static site polish only.

## Implementation Evidence

- source: notification visual edit
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: Used the built-in image generation/edit flow to replace the lower-left object tray in `site/assets/notification-generated.png` with a friendly female virtual assistant character while preserving the notification workflow topology. The edit prompt is saved in `site/diagram-prompts.md`.
  - trust_level: high
  - notes: The edited image was visually inspected before replacing the project asset.
- source: page copy and media references
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: `screen` tab now references `site/assets/Screenshot 2026-06-16 012844.png`; scheme captions now describe what each visual shows and how the flow works; repositories section now includes `https://dtm.solofarm.ru`.
  - trust_level: high
  - notes: HTML uses URL-encoded spaces for the screenshot path.
- source: local static/browser checks
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: Local asset reference parser found 9 local refs and 0 missing files. Local server returned HTTP 200 for `/` and the URL-encoded screenshot path. Headless Edge rendered `#screen` and `#notification` screenshots for visual review. `https://dtm.solofarm.ru` returned HTTP 200.
  - trust_level: high
  - notes: The notification image is 1672x941; the provided site screenshot is 1933x1054.
- source: public GitHub Pages deployment
  - last_verified_at: 2026-06-16
  - verified_by: Codex
  - evidence: GitHub Actions `Deploy GitHub Pages showcase` completed successfully for `feat: polish showcase media and captions` on `main`. Public checks returned HTTP 200 for `/`, the URL-encoded screenshot asset, and `assets/notification-generated.png`; public HTML contains the screenshot reference and `https://dtm.solofarm.ru`. A live `#notification` screenshot shows the virtual assistant character.
  - trust_level: high
  - notes: Public Pages deployment is updated.
