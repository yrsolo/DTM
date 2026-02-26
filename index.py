import sys
import os
import traceback

from config import TG
from core.reminder import TelegramNotifier
from main import main

async def handler(event, _):
    """
    Yandex Cloud handler.

    Args:
        event: Yandex Cloud event.
        _: Yandex Cloud context.

    Returns:
        dict: Response.
    """
    try:
        await main(event=event)
    except Exception as ex:

        tr = str(traceback.format_exc())
        txt = f'Нам худо: \n{ex}\nTRACKBAR\n{tr}\n'

        print(txt)
        await TelegramNotifier().alog(txt)

        return {
            'statusCode': 200,
            'body': '!!!EGGORR!!!',
        }

    return {
        'statusCode': 200,
        'body': '!GOOD!',
    }
