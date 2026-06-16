# Evidence

## Trust Gate
- source: `site/assets/hf_20260616_032749_f20b8e07-ae3d-4b08-b04d-ba13143cc894.png`, `site/index.html`, `site/styles.css`, `site/app.js`
- last_verified_at: 2026-06-16
- verified_by: Codex
- evidence: source poster image exists locally at `2752x1536`, current page uses `site/assets/video-poster.jpg` as the video poster, and the owner requested this new placeholder before video click.
- trust_level: high
- notes: The generated poster should be optimized as a web asset and the play affordance should be overlaid by page UI rather than baked into the image.

## Local Verification
- 2026-06-16: Generated `site/assets/video-poster.webp` from the provided PNG with `ffmpeg`, scaled/cropped to `1600x900`, WebP quality 82, final size `125 KB`.
- 2026-06-16: Added `.gitignore` rule for temporary `site/assets/hf_*.png` source files so raw multi-megabyte generated inputs are not committed.
- 2026-06-16: `node --check site/app.js` passed.
- 2026-06-16: `git diff --check` passed with only existing Windows CRLF warnings.
- 2026-06-16: local `href/src/poster` scan passed; all referenced local assets exist.
- 2026-06-16: local Edge smoke on `http://127.0.0.1:8771/` confirmed `poster="./assets/video-poster.webp"`, requested HLS source still active, play overlay visible before playback, overlay hidden after click, video playback started, and fallback stayed hidden.

## Deployment Verification
- 2026-06-16: pushed `feat: add optimized showcase video poster` to `main` as `9330b94`.
- 2026-06-16: GitHub Actions run `27593457320` (`Deploy GitHub Pages showcase`) completed successfully.
- 2026-06-16: `https://yrsolo.github.io/DTM/` returned `200`, referenced `./assets/video-poster.webp`, and contained the play overlay markup.
- 2026-06-16: `https://yrsolo.github.io/DTM/assets/video-poster.webp` returned `200 image/webp`, `128008` bytes.
- 2026-06-16: public Edge smoke confirmed poster `./assets/video-poster.webp`, HLS source still active, play overlay visible before playback, overlay hidden after click, video playback started, and fallback stayed hidden.
