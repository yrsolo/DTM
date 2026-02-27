"""Модуль для напоминаний о задачах."""
import asyncio
import json
from collections import defaultdict

import aiohttp
import httpx
import pandas as pd
import pytz
from telegram.ext import Application

from core.adapters import ChatAdapter, LoggerAdapter, MessageAdapter, NullLogger
from utils.func import filter_stages
from openai import AsyncOpenAI
from config import TG, DEFAULT_CHAT_ID


def _safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(str(text).encode("unicode_escape").decode("ascii"))


def _sanitize_proxy_url(url):
    if not url:
        return None
    return str(url).strip().strip('"').strip("'")


class TelegramNotifier(object):
    """Интерфейс для отправки сообщений в Telegram."""

    def __init__(self, bot_token=TG, default_chat_id=DEFAULT_CHAT_ID):
        """Инициализация интерфейса для отправки сообщений в Telegram.

        Args:
            bot_token (str): Токен бота.
            default_chat_id (str): ID чата по умолчанию.
        """
        self.bot = Application.builder().token(bot_token).build().bot
        self.default_chat_id = default_chat_id

    async def send_message(self, chat_id, text, parse_mode='Markdown'):
        """Отправить сообщение в Telegram.

        Args:
            chat_id (str): ID чата.
            text (str): Текст сообщения.

        Returns:
            str: Ответ Telegram.
        """
        try:
            return await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        except Exception as e:
            _safe_print(f'Ошибка при отправке сообщения в Telegram: {e}')
            _safe_print('Повторная попытка отправки сообщения в Telegram без разметки')
            self.log(f'Ошибка при отправке сообщения в Telegram: {e} \n Сообщение: \n{text}')
            try:
                return await self.bot.send_message(chat_id=chat_id, text=text, parse_mode=None)
            except Exception as e:
                _safe_print(f'Ошибка при отправке сообщения в Telegram без разметки: {e}')
                _safe_print(f'Сообщение: {text}')

    def log(self, text):
        """Логирование сообщения в Telegram.

        Args:
            text (str): Текст сообщения.

        """
        func = self.send_message(self.default_chat_id, text)
        loop = asyncio.get_running_loop()
        asyncio.run_coroutine_threadsafe(func, loop)

    async def alog(self, text):
        """Логирование сообщения в Telegram.

        Args:
            text (str): Текст сообщения.
        """

        return await self.send_message(self.default_chat_id, text, parse_mode=None)


class AsyncOpenAIChatAgent(object):
    """Агент для чатов с OpenAI."""

    def __init__(self, api_key, proxies=None, model=None, organization=None, logger: LoggerAdapter = None):
        """Инициализация агента для чатов с OpenAI.

        Args:
            api_key (str): API ключ для OpenAI.
            model (str): model.
            organization (str): Название организации.
            proxies (dict): Прокси.
        """

        self.api_key = api_key
        self.organization = organization
        self.proxies = dict(proxies or {})
        self.endpoint = 'https://api.openai.com/v1/chat/completions'
        self.model = model
        self.logger = logger or NullLogger()


    async def chat(self, messages, model=None):
        """Чат с OpenAI GPT.

        Args:
            messages (list): Список сообщений.
            model: GPT-model.

        Returns:
            str: Ответ OpenAI.

        Raises:
            Exception: Если запрос к OpenAI не удался.
        """

        _safe_print(f"openai_proxies={self.proxies}")

        proxy_url = _sanitize_proxy_url(self.proxies.get("https://") or self.proxies.get("http://"))
        client_kwargs = {}
        if proxy_url:
            # httpx>=0.28 uses singular "proxy" argument.
            client_kwargs["proxy"] = proxy_url

        client = AsyncOpenAI(
            api_key=self.api_key,
            http_client=httpx.AsyncClient(**client_kwargs),
        )

        if isinstance(messages, str):
            messages = [{'role': 'user', 'content': messages}]


        if not model:
            model = self.model

        if not model:
            model = 'gpt-3.5-turbo'

        _safe_print(f"openai_messages={messages}")

        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=messages,
            )
        except Exception as e:
            error_text = f"""Ошибка при обращении к OpenAI:
            {e}
            {messages}
            """
            _safe_print(e)
            self.logger.log(error_text)

            return None

        return completion.choices[0].message.content


class MockOpenAIChatAgent(object):
    """Mock агент для тестового режима без внешних вызовов OpenAI."""

    async def chat(self, messages, model=None):
        if isinstance(messages, str):
            return messages
        if isinstance(messages, list):
            for message in reversed(messages):
                if message.get("role") == "user":
                    return message.get("content")
        return None


class Reminder(object):
    """Напоминания о задачах."""

    def __init__(
            self,
            task_repository,
            openai_agent: ChatAdapter,
            helper_character,
            tg_bot_token=None,
            people_manager=None,
            mock_openai=False,
            mock_telegram=False,
            telegram_adapter: MessageAdapter = None,
    ):
        """Инициализация напоминаний о задачах.

        Args:
            task_repository (TaskRepository): Репозиторий задач.
            openai_agent (AsyncOpenAIChatAgent): Агент для чатов с OpenAI.
            helper_character (str): Промт для персонажа-помощника.
            tg_bot_token (str): Токен бота Telegram.
            people_manager (PeopleManager): Менеджер людей.
        """
        self.task_repository = task_repository
        self.openai_agent = openai_agent
        self.mock_openai = bool(mock_openai)
        self.mock_telegram = bool(mock_telegram)
        if self.mock_telegram:
            self.tg_bot = None
        else:
            self.tg_bot = telegram_adapter or TelegramNotifier(tg_bot_token)
        self.helper_character = helper_character
        self.draft_messages = {}
        self.enhanced_messages = {}
        self.today = None
        self.next_work_day = None
        self.people_manager = people_manager

    async def get_tasks_for_date(self, date):
        """Получить задачи на конкретную дату.

        Args:
            date (pd.Timestamp): Дата.

        Returns:
            list: Список задач.
        """
        return self.task_repository.get_tasks_by_date(date)

    async def get_enhanced_message(self, designer, tasks_today, tasks_next_day):
        """Получить улучшенное сообщение для дизайнера.

        Args:
            designer (str): Имя дизайнера.
            tasks_today (list): Список задач на сегодня.
            tasks_next_day (list): Список задач на завтра.

        Returns:
            str: Улучшенное сообщение.
        """
        draft = self.generate_draft_message(designer, tasks_today, tasks_next_day)
        if draft:
            self.draft_messages[designer] = draft  # Сохраняем черновое сообщение
            if self.mock_openai:
                self.enhanced_messages[designer] = draft
                return draft
            try:
                enhanced = await self.enhance_message(draft)
                self.enhanced_messages[designer] = enhanced  # Сохраняем улучшенное сообщение
                return enhanced
            except Exception as e:
                # В случае ошибки при обращении к серверу, вернуть исходное сообщение
                _safe_print(f"chat_enhancer_error: {e}")
                self.enhanced_messages[designer] = draft
                return draft

        return None

    def calculate_dates(self):
        """Рассчитать даты.

        Returns:
            tuple: Кортеж из сегодняшней даты и даты следующего рабочего дня.
        """
        self.today = pd.Timestamp.today().normalize()
        dow = self.today.dayofweek
        day = pd.Timedelta(days=1)
        self.next_work_day = self.today + day * (7-dow) if dow in {4, 5} else self.today + day
        return self.today, self.next_work_day

    def distribute_tasks(self, date):
        """Распределить задачи по дизайнерам.

        Args:
            date (pd.Timestamp): Дата.

        Returns:
            dict: Словарь задач по дизайнерам.
        """
        tasks = self.task_repository.get_tasks_by_date(date)
        tasks_by_designer = defaultdict(list)
        for task in tasks:
            tasks_by_designer[task.designer].append(task)
        return tasks_by_designer

    def day_messages(self, tasks, day):
        """Сформировать сообщение для дизайнера на конкретный день.

        Args:
            tasks (list): Список задач.
            day (pd.Timestamp): Дата.

        Returns:
            list: Список сообщений.
        """
        day_messages = []
        idx = 1
        for task in tasks:
            format_ = task.format_.split('\n')[0]
            stages = filter_stages(task.timing[day])
            if stages:
                stages = ', '.join(stages)
                day_messages.append(
                    f'{idx}. {task.brand} // {format_} // для проекта «{task.project_name}» - сдаём «{stages}»',
                )
                idx += 1
        return day_messages

    def generate_draft_message(self, designer, tasks_today, tasks_next_day):
        """Сформировать черновое сообщение для дизайнера.

        Args:
            designer (str): Имя дизайнера.
            tasks_today (list): Список задач на сегодня.
            tasks_next_day (list): Список задач на завтра.

        Returns:
            str: Черновое сообщение.
        """
        moscow_tz = pytz.timezone('Europe/Moscow')
        now_moscow = pd.Timestamp.now(tz=moscow_tz)
        today_str = now_moscow.strftime('%A, %d.%m')
        time_str = now_moscow.strftime('%H:%M')
        intro = f'Привет {designer}! Сегодня {today_str} в {time_str}.\n'
        m = intro

        today_messages = self.day_messages(tasks_today, self.today)
        if today_messages:
            tasks = '\n'.join(today_messages)
            m += f'\nЗадачи на сегодня:\n{tasks})'
        next_day_messages = self.day_messages(tasks_next_day, self.next_work_day)
        if next_day_messages:
            next_day_str = self.next_work_day.strftime('%A, %d.%m')
            tasks = '\n'.join(next_day_messages)
            m += f'\nЗадачи на {next_day_str}:\n{tasks})'

        return None if m == intro else m

    async def enhance_message(self, message):
        """Улучшение сообщения с помощью GPT.

        Args:
            message (str): Сообщение.

        Returns:
            str: Улучшенное сообщение.
        """
        instruction = {
            'role': 'system',
            'content': self.helper_character,
        }
        user_input = {'role': 'user', 'content': message}
        return await self.openai_agent.chat(messages=[instruction, user_input])

    async def get_reminders(self):
        """Получить напоминания.

        Returns:
            dict: Словарь улучшенных сообщений.
        """
        today, next_work_day = self.calculate_dates()
        tasks_today = self.distribute_tasks(today)
        tasks_next_day = self.distribute_tasks(next_work_day)


        for designer in set(tasks_today.keys()) | set(tasks_next_day.keys()):
            await self.get_enhanced_message(designer, tasks_today.get(designer, []), tasks_next_day.get(designer, []))

        return self.enhanced_messages

    async def send_reminders(self, mode='test'):
        """Отправить напоминания.

        Args:
            mode (str): Режим работы.
        """
        for designer_name, message in self.enhanced_messages.items():
            designer = self.people_manager.get_person(designer_name)
            if designer:
                vacation = designer.vacation != 'да'
                test_chat_id = 91864013
                test = mode == 'test'
                chat_id = test_chat_id if test else designer.chat_id
                _safe_print(f'{mode=} {designer_name=} {chat_id=} {message=}')
                if self.mock_telegram:
                    _safe_print(f'mock_telegram_send: skipped for {designer_name} to chat_id={chat_id}')
                    continue
                if chat_id and self.tg_bot and vacation:
                    await self.tg_bot.send_message(chat_id, message)
