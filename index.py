import json
import traceback

from core.reminder import TelegramNotifier
from main import main


def _extract_payload(event):
    if not isinstance(event, dict):
        return {}, False
    if "body" not in event:
        return event, False

    raw_body = event.get("body")
    if isinstance(raw_body, dict):
        return raw_body, True
    if isinstance(raw_body, str) and raw_body.strip():
        try:
            parsed = json.loads(raw_body)
            if isinstance(parsed, dict):
                return parsed, True
        except json.JSONDecodeError:
            pass
    return {}, True


async def handler(event, _):
    """Yandex Cloud handler."""
    request_payload, is_http_event = _extract_payload(event)
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    run_mode = request_payload.get("mode")
    dry_run = bool(request_payload.get("dry_run", False))
    mock_external = request_payload.get("mock_external")
    planner_event = request_payload.get("event")
    if planner_event is None and not is_http_event:
        planner_event = event

    try:
        await main(
            event=planner_event,
            mode=run_mode,
            dry_run=dry_run,
            mock_external=mock_external,
        )
    except Exception as ex:
        tr = str(traceback.format_exc())
        txt = f"Runtime failure:\n{ex}\nTRACEBACK\n{tr}\n"

        print(txt)
        try:
            await TelegramNotifier().alog(txt)
        except Exception as notifier_error:
            print(f"Error notifier failed: {notifier_error}")

        return {
            "statusCode": 200,
            "body": "!!!EGGORR!!!",
        }

    return {
        "statusCode": 200,
        "body": "!GOOD!",
    }
