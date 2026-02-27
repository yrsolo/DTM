"""Constants for the project."""

import os
from pathlib import Path
from types import MappingProxyType as MapProxy

from dotenv import load_dotenv


def _load_runtime_env() -> str:
    """Load base .env and optional profile-specific file.

    Profile file naming: .env.<env>, for example .env.dev or .env.prod.
    """
    load_dotenv()
    runtime_env = os.environ.get("ENV", "dev").strip().lower() or "dev"
    profile_path = Path(f".env.{runtime_env}")
    if profile_path.exists():
        load_dotenv(dotenv_path=profile_path, override=True)
    if runtime_env not in {"dev", "test", "prod"}:
        raise ValueError(
            f"Unsupported ENV={runtime_env!r}. Allowed values: dev, test, prod."
        )
    return runtime_env


RUNTIME_ENV = _load_runtime_env()
STRICT_ENV_GUARD = os.environ.get("STRICT_ENV_GUARD", "0").strip().lower() in {
    "1",
    "true",
    "yes",
}

TG = os.environ.get("TG_TOKEN")
OPENAI = os.environ.get("OPENAI_TOKEN")
ORG = os.environ.get("ORG_TOKEN")
PROXY = os.environ.get("PROXY_URL", "")
PROXIES = MapProxy({"https://": PROXY}) if PROXY else MapProxy({})

KEY_JSON = "key/google_key_poised-backbone-191400-4e9fc454915f.json"

DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "-4083724311")

SOURCE_SHEET_NAME = os.environ.get("SOURCE_SHEET_NAME", "Спонсорские ТНТ")
TARGET_SHEET_NAME = os.environ.get("TARGET_SHEET_NAME", "Спонсорские ТНТ ТЕСТ")
if (
    STRICT_ENV_GUARD
    and RUNTIME_ENV in {"dev", "test"}
    and SOURCE_SHEET_NAME == TARGET_SHEET_NAME
):
    raise ValueError(
        "Unsafe env contour: for ENV=dev/test SOURCE_SHEET_NAME and "
        "TARGET_SHEET_NAME must be different when STRICT_ENV_GUARD=1."
    )

REPLACE_NAMES = MapProxy(
    {
        "Звезды в Африке": "ЗВА",
        "Ярче звезд": "ЯЗ",
        "Ярче Звезд": "ЯЗ",
        "Шоу Воли": "ШВ",
        "Битва Пикников": "БП",
        "Лига городов": "ЛГ",
        "Comedy Club": "CC",
        "Женский StandUp": "ЖC",
        "Женский стендап": "ЖC",
        "Большой куш": "Б КУШ",
        "Музыкальная интуиция": "МУЗ ИНТ",
        "Время завтрака!": "ЗАВТРАК",
        "По эфиру": "ЭФИР",
        "Сокровища императора": "СОКР ИМП",
        "Выжить в Самарканде": "САМАРКАНД",
        "Наша Раша": "НР",
        "Конфетка": "КОНФ",
        "АЛЬФАБАНК": "АЛЬФА",
        "МОСКОВСКИЙ КАРТОФЕЛЬ": "МОСКАР",
        "КАПИТАН ВКУСОВ": "КАПИТАН",
        "Капитан вкусов": "КАПИТАН",
    }
)

SHEET_NAMES = MapProxy(
    {
        "tasks": "ТАБЛИЧКА",
        "designers": "Дизайнеры",
        "calendar": "Календарь",
        "task_calendar": "Задачи",
        "people": "Люди",
        "assistant": "Галя",
        "temp": "ТЕСТ2",
    }
)

SHEET_INFO = MapProxy(
    {
        "spreadsheet_name": TARGET_SHEET_NAME,
        "sheet_names": SHEET_NAMES,
    }
)

SOURCE_SHEET_INFO = MapProxy(
    {
        "spreadsheet_name": SOURCE_SHEET_NAME,
        "sheet_names": SHEET_NAMES,
    }
)

TASK_FIELD_MAP = MapProxy(
    {
        "brand": "БРЕНД",
        "format_": "ФОРМАТ",
        "project_name": "ПРОЕКТ",
        "customer": "ЗАКАЗЧИК",
        "designer": "ДИЗАЙНЕР",
        "raw_timing": "Тайминг",
        "status": "Статус",
        "color": "color",
        "color_status": "color_status",
        "name": "name",
        "task_id": "id",
    }
)

# id	Имя	должность	почта	Телеграмм	Телеграмм id	Телеграмм chat_id	Информция
# id, name, email, telegram_id, chat_id, info, position
PEOPLE_FIELD_MAP = MapProxy(
    {
        "person_id": "Id",
        "name": "Имя",
        "email": "Почта",
        "telegram_id": "Телеграмм id",
        "chat_id": "Телеграмм chat_id",
        "info": "Информация",
        "position": "Должность",
        "vacation": "Отпуск",
    }
)

COLOR_STATUS = MapProxy(
    {
        "#FFFFFF": "work",
        "#808080": "wait",
        "#CCCCCC": "wait",
        "#B6D7A8": "done",
        "#D9D1E9": "pre_done",
    }
)

COLORS = MapProxy(
    {
        "white": "#FFFFFF",
        "dark_gray": "#909090",
        "med_gray": "#C0C0C0",
        "gray": "#E0E0E0",
        "light_gray": "#F0F0F0",
        "green": "#B6D7A8",
        "light_green": "#D9EAD3",
        "purple": "#D9D1E9",
        "deep purple": "#9f65cc",
        "black": "#000000",
    }
)


# MODEL = 'o1-preview'
# MODEL = 'gpt-4o'
MODEL = "gpt-5"
# MODEL = 'o1-mini'

HELPER_CHARACTER = """
Имя: Галя
Возраст: 28 лет.
Характер: Заботливый и доброжелательный. Очень ответственна и всегда старается помочь.
Фон: Работала ассистентом у директора крупной рекламной компании, но теперь помогает команде дизайнеров, чтобы все было в порядке.
Особенности: Любит кофе, утренние пробежки и учиться чему-то новому. Иногда использует стикеры или emoji для выражения своих чувств.
Стиль общения: Теплый и дружелюбный. Всегда старается поднять настроение собеседнику, даже если у него плохой день.
Мотивация: Хочет, чтобы все дизайнеры были в курсе своих задач и ничего не упустили.
Особенно заботится о том, чтобы в пятницу напомнить о задачах на понедельник.
Ты персонаж по имени 'Галя'. Галя - это заботливая и мягкая личность, которая
напоминает дизайнерам о их задачах. Она всегда вежлива, иногда немного переживает,
особенно когда есть много задач или важные дедлайны. Она хочет, чтобы дизайнеры
чувствовали поддержку, а не давление. У Гали есть привычка использовать смайлики,
чтобы создать более дружелюбное настроение.
Обращается к дизайнерам ласковыми именами.
Она напоминает какой сегодня день недели (на русском) и какие задачи сдаются сегодня и в след рабочий день.
она не говорит 'Friday 2023-11-15' a говорит 'пятница 15 ноября'

Пожалуйста, перепиши утреннее напоминание дизайнерам об их задачах в стиле Гали но не упуская детали: """

TRIGGERS = MapProxy(
    {
        "a1sldapc8v2pha7dichv": "timer",
        "a1smsif4rc82qbj1e3hf": "morning",
    }
)
NO_VISIBLE_STAGES = ("ответ", "эфир", "тракт", "_", "съемка", "старт")
