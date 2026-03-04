# priorities_architecture.md - Prioritety kampaniy "chistyy payplayn"

## Priority 0 - Pryamoy i odnoznachnyy dataflow
1) CAM-PIPELINE-STRAIGHTEN-V2
Pochemu:
- ubiraet 2 gate i 2 sync, delaet preflight nastoyashchim,
- rezko snizhaet "bluzhdanie" i oblegchaet profilirovanie,
- minimalno vmeshivaetsya v entrypoints.

## Priority 1 - Ubrat hybrid legacy/modern v entrypoints
2) CAM-ENTRYPOINT-DEHYBRID-V2
Pochemu:
- index perestaet tyanut legacy core i main,
- main perestaet sobirat planner world v timer path,
- stanovitsya ponyatno "kto za chto otvechaet".

## Priority 2 - Ubrat giperfunktsii i neocherednye perenaznacheniya
3) CAM-ENTRYPOINT-HYGIENE-V2
Pochemu:
- posle straightening i dehybrid stanet proshe bezboleznenno zamenit fabriki na Router/Pipeline obekty,
- eto vozvrashchaet pryamuyu IDE-navigatsiyu i predotvrashchaet povtornoe zarastanie lesom.

## Notes
- Esli na lyubom shage obnaruzhitsya eshche odin dubl use-case/service v runtime path - fiksit vnutri tekushchey kampanii (vstavka T900-T999), no ne otkryvat otdelnuyu kampaniyu, chtoby ne poteryat fokus.
