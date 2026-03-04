# Runtime modes (Current)

## Overview
The code supports multiple run modes (jobs + HTTP).
The intent is:
- timer/sync mode updates YDB from Sheets and refreshes readmodel
- api mode serves frontend v2 payload from YDB readmodel
- render mode draws views (often back to Sheets)
- reminder mode sends Telegram notifications

## timer (sync + readmodel)
Pseudo:
1) read preflight snapshot (values+colors)
2) hash gate
3) if needed: read full snapshot → normalize → version → write YDB
4) build frontend v2 readmodel snapshot

## api
- read `dtm_readmodel_frontend_v2` (1 query)
- apply request filtering (if implemented)
- return payload

## render
- read tasks (prefer readmodel/bulk)
- render to sheet target ranges

## reminder
- read tasks (prefer readmodel/bulk)
- select tasks for the day/window
- format message (optional LLM)
- send via Telegram

## forced refresh
`FORCE_REFRESH=1` modifies timer mode:
- may refresh operational head and readmodel
- must NOT create new versions or write a new milestones_v revision
