"""Constants for the project."""

import os
from types import MappingProxyType as MapProxy

from dotenv import load_dotenv

load_dotenv()

TG = os.environ.get("TG_TOKEN")
OPENAI = os.environ.get("OPENAI_TOKEN")
ORG = os.environ.get("ORG_TOKEN")
PROXY_URL = os.environ.get("PROXY_URL")

KEY_JSON = "key/google_key_poised-backbone-191400-4e9fc454915f.json"

DEFAULT_CHAT_ID = os.environ.get("DEFAULT_CHAT_ID", "-4083724311")

SHEET_NAME = "Спонсорские ТНТ ТЕСТ"

REPLACE_NAMES = MapProxy(
    {
        "Звезды в Африке": "ЗВА",
        "Ярче звезд": "ЯЗ",
        "Ярче Звезд": "ЯЗ",
        "Шоу Воли": "ШВ",
        "Битва Пикников": "БП",
        "Лига городов": "ЛГ",
        "Comedy Club": "CC",
        "Женский StandUp": "ЖS",
        "МОСКОВСКИЙ КАРТОФЕЛЬ": "МОСКАР",
        "КАПИТАН ВКУСОВ": "КАПИТАН",
    }
)

SHEET_NAMES = MapProxy(
    {
        "tasks": "ТАБЛИЧКА",
        "designers": "Дизайнеры",
        "calendar": "Календарь",
        "task_calendar": "Задачи",
        "people": "Люди",
    }
)

SHEET_INFO = MapProxy(
    {
        "spreadsheet_name": SHEET_NAME,
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
        "black": "#000000",
    }
)

PROXIES = MapProxy({"https://": PROXY_URL}) if PROXY_URL else MapProxy({})

MODEL = "gpt-4o"

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
