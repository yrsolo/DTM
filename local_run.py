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
        choices=("timer", "morning", "test"),
        help="Direct mode override (recommended for local runs).",
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
    asyncio.run(main(mode=args.mode, event=event))
