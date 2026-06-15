# DTM architecture diagram generation prompts

These prompts generate only restrained visual backplates. Exact module names, arrows, boundaries, and labels live in deterministic SVG files:

- `assets/backend-architecture.svg`
- `assets/frontend-architecture.svg`

The separation is intentional: a generative model may improve visual texture, but it must not define architecture facts.

## Backend backplate

```text
Use case: infographic-diagram
Asset type: restrained technical background plate for an engineering architecture diagram
Primary request: create a clean, technically credible flat 2D infrastructure diagram background for a Python modular-monolith backend; the final module names and arrows will be overlaid separately, so include no text and no labels
Scene/backdrop: dark graphite engineering canvas with a very subtle orthogonal grid
Subject: two clearly separated horizontal lanes. Upper read lane: a spreadsheet source block on the far left, a structured processing/module boundary in the center, an object storage cylinder, then a browser API boundary on the right. Lower async lane: three intake ports feeding a command queue, then a worker block, then four small application-module blocks, with a publication arrow returning to the upper read lane. A thin monitoring rail sits along the bottom.
Style/medium: precise flat vector-like systems diagram, restrained enterprise architecture aesthetic, minimal depth, no decorative machinery
Composition/framing: wide 16:9, strict alignment, generous spacing for HTML/SVG labels, clear arrow corridors
Color palette: charcoal, off-white, muted cyan for read flow, acid lime for publication flow, muted amber for async flow
Constraints: no words, no letters, no logos, no people, no fake UI, no 3D glass, no crystals, no vaults, no conveyor belts, no cinematic lighting, no decorative sci-fi elements, no watermark; prioritize technical clarity over visual spectacle
```

## Frontend backplate

```text
Use case: infographic-diagram
Asset type: restrained technical background plate for an engineering architecture diagram
Primary request: create a clean, technically credible flat 2D architecture background for a React/Vite frontend runtime; final module names and arrows will be overlaid separately, so include no text and no labels
Scene/backdrop: dark graphite engineering canvas with a very subtle orthogonal grid
Subject: center-left is one browser SPA boundary containing five clearly separated route/surface blocks and a central runtime/layout block. Below it is a data plane with configuration, API client, normalization, Snapshot model, selectors, and browser cache blocks in a clear sequence. On the right are two distinct gateway boundaries: one for browser data and one for auth/admin; behind auth/admin are a session store and a bucket for presets/shared app state. On the far left are desktop browser, mobile browser, and Telegram Mini App entry surfaces.
Style/medium: precise flat vector-like systems diagram, restrained enterprise architecture aesthetic, minimal depth, no decorative machinery
Composition/framing: wide 16:9, strict alignment, generous spacing for HTML/SVG labels, clear arrow corridors
Color palette: charcoal, off-white, muted cyan for snapshot/data flow, acid lime for UI/runtime flow, muted violet for auth flow
Constraints: no words, no letters, no logos, no people, no fake UI screenshots, no 3D glass, no crystals, no cinematic lighting, no decorative sci-fi elements, no watermark; prioritize technical clarity over visual spectacle
```

## Rules for future regeneration

- Keep generated text disabled; labels belong in SVG.
- Preserve lane topology and color semantics.
- Reject outputs that invent services, databases, or connections.
- Use the backplate at low opacity so the SVG remains readable without it.
