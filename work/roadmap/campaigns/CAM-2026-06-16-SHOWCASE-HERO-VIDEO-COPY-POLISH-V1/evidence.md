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
