# Designers Task Manager (DTM)

DTM is a real-world pet project built as a portfolio case about evolving legacy automation into a maintainable product architecture.

## What the project does
- Reads task data from Google Sheets.
- Builds visual planning views for a design team (timeline and designer-focused boards).
- Sends morning reminders to designers via Telegram.
- Uses OpenAI to improve reminder text style.

## Why this repository exists
- Show practical refactoring of a working legacy system.
- Demonstrate safe migration approach: preserve business behavior while improving code quality.
- Build a foundation for moving from Google Sheets visualization to a dedicated frontend.

## Tech stack
- Python
- Google Sheets / Drive API
- Telegram Bot API
- OpenAI API
- Yandex Cloud / Object Storage

## Engineering focus
- Separation of source and target sheets for safer testing.
- Local test contour for repeatable verification.
- Documentation-first reconstruction plan.
- Security hygiene for public repository readiness.

## Project status
- Production workflow is active.
- Architecture is under phased reconstruction.
- Legacy snapshot is kept in `old/` for controlled comparison during migration.
