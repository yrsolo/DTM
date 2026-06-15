# DTM generated diagram prompts

These prompts were used with the built-in image generation tool to create project-bound raster assets for the GitHub Pages showcase.

Generated assets:

- `assets/backend-generated.png`
- `assets/frontend-generated.png`
- `assets/notification-generated.png`

The images intentionally contain no generated text. Exact project wording belongs in the surrounding page copy and captions so the architecture facts stay editable and readable.

## Backend

```text
Use case: infographic-diagram
Asset type: website tab image for the DTM backend architecture
Primary request: Generate a polished light isometric technical infographic in the style of the provided reference images: warm off-white paper background, subtle engineering grid, realistic 3D module objects, clean arrows, professional product-engineering look. Show the DTM backend architecture as a real flow, not an abstract decoration.
Subject: left side has a Google Sheets-like spreadsheet source block with rows and columns. It flows by a solid teal arrow into a central snapshot processing machine/rack with layered cards. Then a solid teal arrow goes to an object storage block represented as a clean storage crate/cylinder. Then to a browser API gateway block and finally to a laptop/browser UI card on the right. Lower lane: three small intake ports for HTTP/admin, Telegram webhook, and timer trigger feed a terracotta dashed arrow into a command queue box, then into a worker server, then into four small application module cubes for attachments, rendering, reminders, and telegram. A return arrow from workers goes back up to the prepared browser payload. Bottom rail has subtle observability objects: job status log, metrics panel, dashboard.
Style/medium: generated raster illustration, realistic clean 3D isometric modules, technical infographic, similar to the attached examples, not flat SVG.
Composition/framing: wide 16:9, all modules clearly separated, flow left-to-right, upper read lane and lower async lane, generous whitespace, suitable for website hero/tab card.
Lighting/mood: soft studio lighting, calm enterprise architecture, no dark sci-fi.
Color palette: warm ivory background, dark graphite modules, muted teal arrows for read path, muted terracotta arrows for async path, pale sand/green accents.
Text: no generated text, no labels, no letters.
Constraints: no logos, no people, no fake Kubernetes, no extra databases, no code text, no watermark, no blurry microtext, no decorative dust, keep the topology technically plausible and readable.
```

## Frontend

```text
Use case: infographic-diagram
Asset type: website tab image for the DTM frontend architecture
Primary request: Generate a polished light isometric technical infographic in the same style as the provided reference images: warm off-white paper background, subtle engineering grid, realistic 3D module objects, clean arrows. Show the DTM frontend architecture as a real flow, not a flat SVG diagram.
Subject: left side has three client surfaces as separate devices/cards: desktop browser monitor, mobile web phone, Telegram Mini App phone card. They flow into one central React/Vite SPA workstation represented as a large clean monitor/server console with several UI panels. Inside/around it show route modules as small cards: timeline, analytics, admin, mobile, tools. From the SPA a solid teal arrow goes to a data plane on the right: runtime config card, API client card with cache/ETag symbol, SnapshotV1 contract block, selectors block. Another smaller terracotta/auth path goes to access modules: Yandex OAuth gate, temporary link key, masked/full access toggle. The data plane connects back to UI panels, showing browser cache/warm start as a small storage tray under the central workstation.
Style/medium: generated raster illustration, realistic clean 3D isometric modules, technical infographic, similar to the attached examples, not flat SVG.
Composition/framing: wide 16:9, left-to-right flow, modules clearly separated, generous whitespace, suitable for website tab card.
Lighting/mood: soft studio lighting, calm product engineering, no dark sci-fi.
Color palette: warm ivory background, dark graphite equipment, muted teal arrows for snapshot data, muted terracotta for auth/config, pale sand/green UI panels.
Text: no generated text, no labels, no letters.
Constraints: no logos, no people, no fake cloud providers, no invented services, no code text, no watermark, no blurry microtext, no decorative dust, keep the topology technically plausible and readable.
```

## Notification

```text
Use case: infographic-diagram
Asset type: website tab image for the DTM notification/reminders workflow
Primary request: Generate a polished light isometric technical infographic in the style of the attached references: warm off-white background, subtle grid, realistic 3D modules, clean arrows. Show the DTM notifications workflow as a real system flow.
Subject: left side has a scheduler/timer module like a small clock console and a manual trigger button. It flows to a reminder context assembly tray with task cards, deadline markers, and owner avatars as abstract icons. From there an arrow goes to a text-enhancer module represented by a compact AI/LLM processor box with a small brain/network symbol, but no letters. Then a terracotta dashed arrow goes to a message queue cassette, then to a worker server. The worker sends final messages to Telegram delivery: phone and chat cards on the right with notification bubbles. Include a feedback/status path down to a job-status/log panel and metrics dashboard at the bottom. Show that tasks/deadlines/owners come from a prepared snapshot block, not from direct per-task reads.
Style/medium: generated raster illustration, realistic clean 3D isometric modules, technical infographic, similar to the attached examples, not flat SVG.
Composition/framing: wide 16:9, left-to-right flow with a lower status feedback rail, modules separated and readable, generous whitespace.
Lighting/mood: soft studio lighting, serious product engineering, no dark sci-fi.
Color palette: warm ivory background, dark graphite modules, muted teal main flow, muted terracotta queue/worker flow, soft green status accents.
Text: no generated text, no labels, no letters.
Constraints: no logos, no people, no fake email/SMS channels, no invented notification vendor, no code text, no watermark, no blurry microtext, no decorative dust, keep the topology technically plausible and readable.
```

## Notification Persona Edit

```text
Edit the provided DTM notification workflow infographic. Preserve the entire image style, canvas, lighting, arrows, scheduler clock, task tray, AI processor, queue cassette, worker server, Telegram phone/cards, and bottom analytics rail.

Change only the lower-left transparent tray that currently contains assorted objects (camera, plant, vase, chair, shoe, cube). Replace that tray with a friendly young female virtual assistant character, the persona from whose voice notifications are written. She should fit the same light isometric 3D infographic style: approachable, professional, warm, slightly stylized, seated or standing on a small clean platform, with a small chat/notification aura or message cards around her. Keep her non-photorealistic, product-infographic friendly, no brand logos, no text, no letters.

Important constraints: do not alter the main flow topology; keep the teal connection line from the persona area into the reminder/status flow; keep the warm off-white background and subtle grid; keep all other modules in their original positions; no extra people; no watermark; no generated text.
```

## Regeneration Rules

- Use the attached reference style: light isometric product-engineering infographic, not a dry vector architecture chart.
- Keep generated text disabled. Put exact module names in page copy, captions, or editable overlays.
- Preserve the real topology: do not invent services, databases, vendors, or hidden dependencies.
- Keep arrows meaningful: teal for read/data flow, terracotta for async/command flow.
- Reject outputs that are only decorative or hide the system shape behind generic 3D objects.
