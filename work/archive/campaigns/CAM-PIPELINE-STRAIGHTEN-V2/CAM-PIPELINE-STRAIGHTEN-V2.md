# CAM-PIPELINE-STRAIGHTEN-V2 - One Sync, One Gate, Real Preflight

## Goal
Sdelat edinstvennyy kanonicheskiy payplayn sinka:
- odin SyncService (odna realizatsiya)
- odin hash gate (po snapshot values+colors i dtm_sync_state v YDB)
- preflight realno ekonomit chtenie full snapshot
- isklyuchit vtoroy gate i lishnie krugi

## Non-goals
- Ne delaem dehybrid index/main (eto otdelnaya kampaniya).
- Ne perepisyvaem biznes-algoritmy normalizatsii/versiy/milstounov.
- Ne menyaem API kontrakt.

## DoD
- V runtime path ispolzuetsya rovno odin sync_service.
- V standartnom timer path net MIGRATION_ENABLE_SOURCE_HASH_GATE i state-file gate.
- Pri no-change run full snapshot ne chitaetsya.
- Obnovleny docs: dataflow + entrypoints behavior.

## PHASE P01 - Unify SyncService
### CAM-PIPELINE-STRAIGHTEN-V2-P01-T001 - Runtime usage map
- Nayti vse importy/ispolzovaniya:
  - `src/services/sync_service.py`
  - `src/services/sync/sync_service.py`
- Vypisat, kakoy realno ispolzuetsya v timer path.

### CAM-PIPELINE-STRAIGHTEN-V2-P01-T002 - Select canonical sync
- Vybrat odin modul kak kanonicheskiy (tot, kotoryy realno ispolzuetsya seychas v timer pipeline).
- Zafiksirovat vybor kommentom v module (header: "CANONICAL").

### CAM-PIPELINE-STRAIGHTEN-V2-P01-T003 - Remove/Quarantine duplicate sync
- Vtoroy modul:
  - libo udalit,
  - libo peremestit v `src/legacy/sync/` i isklyuchit iz runtime importov.
- Dobavit "DEPRECATED - DO NOT USE" header.

### CAM-PIPELINE-STRAIGHTEN-V2-P01-T004 - Smoke after dedup
- Prognat minimalnye rezhimy:
  - timer (bez realnogo deploya)
  - API v2 handler (lokalno)
- Ubeditsya, chto importy ne lomayutsya.

## PHASE P02 - Remove second gate from main path
### CAM-PIPELINE-STRAIGHTEN-V2-P02-T001 - Identify old gate block
- V `main.py` nayti:
  - `MIGRATION_ENABLE_SOURCE_HASH_GATE`
  - build_hash_basis / evaluate_hash_gate / save_last_hash
  - state file logic
- Vypisat, gde eto vliyaet na `allow_sync`.

### CAM-PIPELINE-STRAIGHTEN-V2-P02-T002 - Remove from standard timer path
- Udalit/oboyti etu logiku v standartnom timer run.
- Reshenie "delat sync ili net" ostaetsya tolko vnutri YdbSyncService po dtm_sync_state.

### CAM-PIPELINE-STRAIGHTEN-V2-P02-T003 - Keep as dev-only tool (optional)
- Esli nado sokhranit dlya otladki:
  - vynesti v otdelnyy script v `scripts/` ili `agent/`,
  - vyklyuchit po umolchaniyu,
  - ne ispolzovat v `main.py`.

## PHASE P03 - Make preflight cheap (no full snapshot unless needed)
### CAM-PIPELINE-STRAIGHTEN-V2-P03-T001 - Change pipeline order
- V `src/services/pipeline_runtime.py` (ili gde pipeline):
  1) fetch preflight snapshot
  2) vychislit preflight hash
  3) reshit "nuzhen li full sync"
  4) fetch full snapshot tolko esli nuzhen

### CAM-PIPELINE-STRAIGHTEN-V2-P03-T002 - Expose decision API
- V YdbSyncService:
  - dobavit metod `decide_need_full_sync(preflight_hash, now) -> (bool, reason)`
  - ili izmenit `run()` tak, chtoby on umel rabotat v dvukh shagakh (preflight-only vs full).
- Zapreshcheno: chitat full snapshot vsegda.

### CAM-PIPELINE-STRAIGHTEN-V2-P03-T003 - Logs for evidence
- Dobavit logi:
  - `full_snapshot_fetch=skipped reason=...`
  - `full_snapshot_fetch=performed reason=...`

### CAM-PIPELINE-STRAIGHTEN-V2-P03-T004 - Tests (minimal)
- Unit: preflight unchanged + not stale => need_full_sync False.
- Unit: stale daily => need_full_sync True.

## PHASE P04 - Docs update
### CAM-PIPELINE-STRAIGHTEN-V2-P04-T001
- Obnovit `docs/system/dataflow.md`:
  - odin gate v YDB sync_state
  - preflight realno ekonomit full fetch

### CAM-PIPELINE-STRAIGHTEN-V2-P04-T002
- Obnovit `docs/system/entrypoints_index_main.md`:
  - gde teper kanonicheskiy timer path

## PHASE P05 - Evidence
### CAM-PIPELINE-STRAIGHTEN-V2-P05-T001
- Dobavit evidence file:
  - No-change run: full_snapshot_fetch skipped
  - Change run: full_snapshot_fetch performed
