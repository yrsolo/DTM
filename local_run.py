"""Local launcher for running the planner without Yandex Cloud."""

import argparse
import asyncio
import json
from pathlib import Path

from main import main


def build_event(trigger_id):
    """Build minimal event payload compatible with cloud handler contract."""
    return {
        "messages": [
            {
                "details": {
                    "trigger_id": trigger_id,
                }
            }
        ]
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Run planner locally")
    parser.add_argument(
        "--mode",
        choices=("timer", "morning", "test", "sync-only", "reminders-only"),
        help="Direct mode override (recommended for local runs).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Disable Google Sheets write operations (read-only verification run).",
    )
    parser.add_argument(
        "--event-file",
        type=Path,
        help="Path to Yandex event JSON file (optional).",
    )
    parser.add_argument(
        "--trigger-id",
        help="Synthetic trigger_id for event emulation.",
    )
    parser.add_argument(
        "--quality-report-file",
        type=Path,
        help="Optional path to write quality report JSON.",
    )
    parser.add_argument(
        "--mock-external",
        action="store_true",
        help="Disable OpenAI and Telegram external calls in reminder flow.",
    )
    return parser.parse_args()


def load_event(args):
    if args.event_file:
        return json.loads(args.event_file.read_text(encoding="utf-8"))
    if args.trigger_id:
        return build_event(args.trigger_id)
    return None


if __name__ == "__main__":
    args = parse_args()
    event = load_event(args)
    quality_report = asyncio.run(
        main(
            mode=args.mode,
            event=event,
            dry_run=args.dry_run,
            mock_external=args.mock_external,
        )
    )
    if args.quality_report_file:
        args.quality_report_file.parent.mkdir(parents=True, exist_ok=True)
        args.quality_report_file.write_text(
            json.dumps(quality_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"quality_report_file={args.quality_report_file}")
