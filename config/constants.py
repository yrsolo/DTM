"""Constants for the project."""

import base64
import os
import tempfile
from pathlib import Path
from types import MappingProxyType as MapProxy
from typing import Mapping

from dotenv import load_dotenv

ALLOWED_ENVS = frozenset({"dev", "test", "prod"})
ALLOWED_LLM_PROVIDERS = frozenset({"openai", "google", "yandex"})


def _env(name: str, default: str = "") -> str:
    """Return stripped environment value."""

    return os.environ.get(name, default).strip()


def _env_flag(name: str, default: str = "0") -> bool:
    """Parse bool-like flag from environment."""

    return _env(name, default).lower() in {"1", "true", "yes"}


def _load_runtime_env() -> str:
    """Load base .env and optional profile-specific file.

    Profile file naming: .env.<env>, for example .env.dev or .env.prod.
    """
    load_dotenv()
    runtime_env = _env("ENV", "dev").lower() or "dev"
    profile_path = Path(f".env.{runtime_env}")
    if profile_path.exists():
        load_dotenv(dotenv_path=profile_path, override=True)
    if runtime_env not in ALLOWED_ENVS:
        raise ValueError(
            f"Unsupported ENV={runtime_env!r}. Allowed values: dev, test, prod."
        )
    return runtime_env


RUNTIME_ENV = _load_runtime_env()
STRICT_ENV_GUARD = _env_flag("STRICT_ENV_GUARD")

TG = os.environ.get("TG_TOKEN")
TG_BOT_USERNAME = _env("TG_BOT_USERNAME")
OPENAI = os.environ.get("OPENAI_TOKEN")
ORG = os.environ.get("ORG_TOKEN")
LLM_PROVIDER = _env("LLM_PROVIDER", "openai").lower()
if LLM_PROVIDER not in ALLOWED_LLM_PROVIDERS:
    raise ValueError(
        f"Unsupported LLM_PROVIDER={LLM_PROVIDER!r}. "
        "Allowed values: openai, google, yandex."
    )
OPENAI_MODEL = _env("OPENAI_MODEL", "")
GOOGLE_LLM_API_KEY = _env("GOOGLE_LLM_API_KEY")
GOOGLE_LLM_MODEL = _env("GOOGLE_LLM_MODEL", "gemini-2.0-flash")
YANDEX_LLM_API_KEY = _env("YANDEX_LLM_API_KEY")
YANDEX_LLM_MODEL_URI = _env("YANDEX_LLM_MODEL_URI")
LLM_HTTP_TIMEOUT_SECONDS = float(_env("LLM_HTTP_TIMEOUT_SECONDS", "25"))
LLM_HTTP_RETRY_ATTEMPTS = max(1, int(_env("LLM_HTTP_RETRY_ATTEMPTS", "2")))
LLM_HTTP_RETRY_BACKOFF_SECONDS = max(0.0, float(_env("LLM_HTTP_RETRY_BACKOFF_SECONDS", "0.8")))
if not YANDEX_LLM_MODEL_URI:
    yc_folder_id = _env("YC_FOLDER_ID")
    if yc_folder_id:
        YANDEX_LLM_MODEL_URI = f"gpt://{yc_folder_id}/yandexgpt/latest"
PROXY = _env("PROXY_URL")
PROXIES: Mapping[str, str] = MapProxy({"https://": PROXY}) if PROXY else MapProxy({})


def _resolve_google_key_json_path() -> str:
    """Resolve Google service-account key path.

    Priority:
    1) GOOGLE_KEY_JSON_PATH (already materialized file path)
    2) GOOGLE_KEY_JSON_B64 (base64-encoded JSON payload)
    3) GOOGLE_KEY_JSON (raw JSON payload text)
    4) local development fallback file path in repository
    """
    key_path = _env("GOOGLE_KEY_JSON_PATH")
    if key_path:
        return key_path

    key_b64 = _env("GOOGLE_KEY_JSON_B64")
    key_text = _env("GOOGLE_KEY_JSON")
    if key_b64:
        key_text = base64.b64decode(key_b64).decode("utf-8")

    if key_text:
        tmp_file = Path(tempfile.gettempdir()) / "dtm_google_key.json"
        tmp_file.write_text(key_text, encoding="utf-8")
        return str(tmp_file)

    return "key/google_key_poised-backbone-191400-4e9fc454915f.json"


KEY_JSON = _resolve_google_key_json_path()

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


# MODEL is kept for backward compatibility with older code paths.
# MODEL = 'o1-preview'
# MODEL = 'gpt-4o'
MODEL = OPENAI_MODEL or "gpt-5"
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
