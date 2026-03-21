# CAM-2026-03-21-FINAL-AESTHETIC-CLOSEOUT-V1 Plan

Smell:
- the active contour no longer has structural beauty defects, but a few last seams still read more technical than intentional

Target ideal:
- the repo reads as "beautiful enough" for external presentation, with no obvious stale runtime aliases or assembly-flavored helper seams left in active paths

Kill criteria:
- `src/platform/app_context.py` no longer exists as a thin alias boundary
- planner runtime reads through the canonical platform seam in `src/platform/bootstrap.py`
- remaining `_build_*` helper seams in active reminders/telegram/runtime paths are renamed to `make_*`
- beauty audit and tracking no longer imply that several required beauty waves are still ahead

Scope boundary:
- active runtime seam cleanup
- active helper naming cleanup
- beauty audit and tracking closeout only

Non-goals:
- no runtime behavior redesign
- no module ownership changes
- no new umbrella campaign
