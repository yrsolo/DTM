import traceback

from core.reminder import TelegramNotifier
from main import main


async def handler(event, _):
    """Yandex Cloud handler."""
    request_payload = event if isinstance(event, dict) else {}
    if request_payload.get("healthcheck"):
        return {
            "statusCode": 200,
            "body": "!HEALTHY!",
        }

    run_mode = request_payload.get("mode")
    dry_run = bool(request_payload.get("dry_run", False))
    mock_external = request_payload.get("mock_external")
    planner_event = request_payload.get("event", event)

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
