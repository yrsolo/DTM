# DTM architecture diagram generation prompts

These prompts generate only restrained visual backplates or module-icon references. Exact module names, arrows, boundaries, and labels live in deterministic SVG files:

- `assets/backend-flow-light.svg`
- `assets/frontend-flow-light.svg`
- `assets/notification-flow-light.svg`
- `assets/screen-workspace.svg`

The separation is intentional: a generative model may improve visual texture, but it must not define architecture facts.

## Backend light hybrid diagram

```text
Use case: infographic-diagram
Asset type: restrained light technical architecture illustration for a resume portfolio page
Primary request: create a technically credible backend diagram background for a Python modular-monolith system; modules may look like clean symbolic 3D blocks, but the final module names, labels, and arrows will be overlaid in SVG
Scene/backdrop: warm off-white paper background, subtle engineering grid, soft shadows, no dark sci-fi mood
Subject: two lanes. Upper read lane: Google Sheets source block, snapshot processing block, object storage block, access API block, browser SPA target. Lower async lane: HTTP/Telegram/timer entrypoints, command queue, worker shell, owning application contexts, publication returning to the read lane. Bottom operational rail for job status, logs, metrics, Grafana/DataLens.
Style/medium: precise vector-like systems diagram with modest 3D module objects, professional software architecture visual, readable and calm
Composition/framing: wide 16:9, strict alignment, generous whitespace for labels, clear arrow corridors, no decorative extra services
Color palette: warm paper, dark ink, muted teal for read flow, muted terracotta for async flow, pale green and sand module fills
Constraints: no generated text, no letters, no logos, no people, no fake database that is not in the system, no invented Kubernetes, no decorative pipes, no excessive dust/glow, no watermark; prioritize technical clarity over spectacle
```

## Frontend light hybrid diagram

```text
Use case: infographic-diagram
Asset type: restrained light technical architecture illustration for a React/Vite frontend
Primary request: create a technically credible frontend diagram background; modules may be clean symbolic 3D UI blocks, but final labels and arrows will be overlaid in SVG
Scene/backdrop: warm off-white paper background, subtle grid, soft shadows, light portfolio-page palette
Subject: left side has three client entry surfaces: desktop browser, mobile web, Telegram Mini App. Center has one React/Vite SPA boundary containing timeline, analytics, admin, mobile/tools surfaces and a runtime/layout hub. Right side has data/auth plane blocks: public runtime config, API client with ETag/stale fallback, SnapshotV1 schema, Yandex OAuth and temp links.
Style/medium: precise vector-like software architecture diagram, modest 3D blocks, no cinematic tech fantasy
Composition/framing: wide 16:9, clear left-to-right flow, large readable module zones, no crowded microtext
Color palette: warm paper, dark ink, muted teal for data flow, muted terracotta for auth/config blocks
Constraints: no generated text, no logos, no people, no invented services, no fake dashboards, no complex wires without meaning, no watermark; prioritize technical clarity over spectacle
```

## Notification light hybrid diagram

```text
Use case: infographic-diagram
Asset type: restrained light technical workflow illustration for a notification/reminder subsystem
Primary request: create a workflow diagram background for reminder delivery in a design-operations service; final labels and exact arrows will be overlaid in SVG
Scene/backdrop: warm off-white paper background, subtle grid, soft shadows, professional product-engineering style
Subject: scheduler/timer module feeds reminder context module built from tasks/deadlines/owners; context passes to text-enhancer module using configured OpenAI mode with fallback; result goes through message queue worker with retry and job status; final delivery is a Telegram module for groups/users/Mini App. Include a visible result rail for sent reminder, delivery status, logs, and job status.
Style/medium: symbolic 3D modules with simple recognizable forms, flat accurate arrows, restrained color
Composition/framing: wide 16:9, left-to-right flow with one lower queue/worker return path, generous whitespace for labels
Color palette: warm paper, dark ink, muted teal for main flow, muted terracotta for enhancer/worker path
Constraints: no generated text, no logos, no people, no fake email/SMS channels, no invented notification vendors, no excessive glow/dust, no watermark; keep it technically credible
```

## Product screen mock

```text
Use case: product-screenshot-style illustration
Asset type: clean UI mock background for a design operations dashboard
Primary request: create a polished but technically plausible DTM workspace screen: filters, operational timeline, task drawer, attachments, team load, and reminder status; final small labels may be drawn in SVG
Scene/backdrop: light portfolio page, browser chrome frame, warm paper palette
Subject: left filter sidebar, center timeline with task bars and milestones, right task drawer with status, attachments, and Telegram reminders; top line shows snapshot/ETag freshness.
Style/medium: crisp SaaS UI mock, no photorealistic monitor, no fictional product branding
Composition/framing: wide 16:9, readable high-level zones, no tiny fake data tables
Color palette: dark teal browser frame, warm off-white panels, muted teal, terracotta, olive accents
Constraints: no random text generation, no logos, no sensitive data, no people, no excessive decoration
```

## Rules for future regeneration

- Keep generated text disabled where possible; labels belong in SVG.
- Preserve lane topology and color semantics.
- Reject outputs that invent services, databases, or connections.
- Keep module symbols slightly volumetric and recognizable, while keeping connections flat, explicit, and technically authoritative.
- Prefer one short module name plus one short role line; move detailed explanation into page copy instead of the diagram.
