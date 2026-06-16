# Evidence

## Trust Gate
- source: `site/index.html`, `site/styles.css`, `site/app.js`
- last_verified_at: 2026-06-16
- verified_by: Codex
- evidence: current Git working tree is clean on `dev`; existing GitHub Pages showcase lives under `site/`.
- trust_level: high
- notes: Owner provided exact target copy and HLS promo URL in the current chat. Public copy typos are corrected where clearly accidental.

## Local Verification
- 2026-06-16: `git diff --check` passed with only existing Windows CRLF warnings.
- 2026-06-16: `node --check site/app.js` passed.
- 2026-06-16: local `href/src` scan passed; all local asset targets exist.
- 2026-06-16: external `https://storage.yandexcloud.net/dtm-presets/video/DTM_hi.m3u8` returned `200 application/x-mpegurl`.
- 2026-06-16: external `https://cdn.jsdelivr.net/npm/hls.js@1/dist/hls.min.js` returned `200 application/javascript`.
- 2026-06-16: local Edge smoke on `http://127.0.0.1:8770/` confirmed title `DTM — управление задачами дизайн-отдела`, h1 text `DTM: управление задачами дизайн-отдела`, desktop h1 font size `76px`, `video.currentSrc` equal to the requested HLS URL, video fallback hidden, and updated video/screen/notification captions.

## Deployment Verification
- 2026-06-16: pushed `feat: polish showcase hero video copy` to `main` as `fce2ffd`.
- 2026-06-16: GitHub Actions run `27586377397` (`Deploy GitHub Pages showcase`) completed successfully.
- 2026-06-16: `https://yrsolo.github.io/DTM/` returned `200` and contained the new title, requested HLS URL, updated video caption, updated notification copy, and no old `Реальный экран сервиса.` prefix.
- 2026-06-16: public Edge smoke confirmed title `DTM — управление задачами дизайн-отдела`, h1 text `DTM: управление задачами дизайн-отдела`, desktop h1 font size `76px`, `video.currentSrc` equal to `https://storage.yandexcloud.net/dtm-presets/video/DTM_hi.m3u8`, fallback hidden, and no old screenshot prefix.
