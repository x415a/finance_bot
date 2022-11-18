from typing import Any, Iterable, Optional, Type
from telebot import TeleBot
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup
from types_def import Field
from types_def import T_MESSAGE, UserInfo
from util import get_next_query_code
import constants
import menus
import json


__all__ = ['get_config', 'get_users_handler', 'QueryManager']


class Config:
    def __init__(self):
        with open(constants.CONFIG, 'r', encoding='utf-8') as fs:
            self._vars = json.load(fs)
        self._temp = {}

    def save_data(self, tag: str, data) -> None:
        self._temp[tag] = data

    def get_saved_data(self, tag: str) -> Optional[Any]:
        return self._temp.get(tag, None)

    def get_spreadsheets_list(self) -> Iterable[tuple[str, str]]:
        return iter(self._vars['spreadsheets_url'].items())

    def get_spreadsheet_tag_info(self, tag: str) -> dict[str, Any]:
        return self._vars['worksheets'][tag]

    def get_bot_token(self, bot_name: str) -> str:
        return self._vars['tokens'][bot_name]

    def get_message_text(self, message_tag: str) -> str:
        return self._vars['messages'][message_tag]

    def get_field_info(self, field: str) -> dict[str, Any]:
        return self._vars[f'fields'][field]

    def get_error_text(self, error: str) -> str:
        return self._vars['errors'][error]

    def get_control_button_text(self, button: str) -> str:
        return self._vars['control_buttons'][button]


class QueryManager:
    __slots__ = ('_query', '_fields', '_menus', '_cur_field', '_aliases', '_summary')

    def __init__(self, *fields: tuple[Type[Field], bool]):
        self._query = q = get_next_query_code()
        self._fields = tuple(f[0](query=q, field_id=i, required=f[1])
                             for i, f in enumerate(fields))
        self._aliases = {i.get_name(): i for i in self._fields}
        self._cur_field: Optional[Field] = None
        self._summary = None

    def _get_next_empty_field(self) -> Optional[Field]:
        for f in self._fields:
            if not f.is_ready():
                return f
        return None

    def is_done(self) -> bool:
        return self._get_next_empty_field() is None

    def is_waits(self) -> bool:
        return self._cur_field.is_ready()

    def get_field(self, field: str) -> Field:
        return self._aliases[field]

    def get_query_code(self):
        return self._query

    def get_invite_message(self) -> T_MESSAGE:
        self._cur_field = self._get_next_empty_field()
        return self._cur_field.get_invite()

    def handle_message(self, message: Message) -> Optional[T_MESSAGE]:
        try:
            t = self._cur_field.handle_message(message)
            return t
        except NotImplementedError:
            return None

    def handle_callback_query(self, callback: CallbackQuery, cb_data: menus.CallbackData) -> T_MESSAGE:
        res = (f := self._fields[cb_data.field]).handle_callback(callback, cb_data)
        if not f.is_ready():
            self._cur_field = f
        return res

    def get_current_content_message(self) -> Message:
        return self._cur_field.get_content_message()

    def set_current_content_message(self, message: Message):
        self._cur_field.set_content_message(message)

    def generate_summary_message(self, add_text='') -> T_MESSAGE:
        res = '\n'.join(f'{f.get_alias()}: {v if (v := f.get_str_value()) is not None else "-"}' for f in self._fields)
        kb = InlineKeyboardMarkup()
        kb.add(*menus.get_summary_control(self._query))
        return get_config().get_message_text('summary_text').format(res) + add_text, kb

    def confirm_summary_message(self) -> T_MESSAGE:
        if not self.is_done():
            return self.generate_summary_message(get_config().get_message_text('summary_not_done'))
        text, _ = self.generate_summary_message(get_config().get_message_text('summary_confirmed'))
        return text, None

    def has_summary_message(self) -> bool:
        return self._summary is not None

    def set_current_summary_message(self, message: Message):
        self._summary = message

    def get_current_summary_message(self) -> Message:
        return self._summary


class UsersAccessHandler:
    __slots__ = ('_queries', '_telegram_users', '_database_users')

    def __init__(self):
        self._queries: dict[str, Optional[QueryManager]] = {}
        self._telegram_users = {}
        self._database_users = {}
        self._load()

    def _save(self):
        with open(constants.USERS, 'w', encoding='utf-8') as fs:
            json.dump([self._telegram_users, self._database_users], fs)

    def _load(self):
        with open(constants.USERS, 'r', encoding='utf-8') as fs:
            self._telegram_users, self._database_users = json.load(fs)

    def update_users_list(self, users: list[UserInfo]):
        self._database_users = {u.userid: u for u in users}
        self._telegram_users = {k: v for k, v in self._telegram_users.items() if v in self._database_users}
        self._save()

    def reset_user_registration(self, telegram_id: int):
        self._telegram_users.pop(telegram_id, None)
        self._save()

    def register_user(self, telegram_id: int, user_id: int) -> bool:
        if user_id not in self._database_users or user_id in self._telegram_users.values():
            return False
        self._telegram_users[telegram_id] = user_id
        return True

    def get_user_access_info(self, telegram_id: int) -> Optional[UserInfo]:
        return self._database_users.get(self._telegram_users.get(telegram_id, None), None)

    def get_user_query(self, bot: TeleBot, user_id: int) -> Optional[QueryManager]:
        return self._queries.get(f'{bot.token}{user_id}', None)

    def is_user_has_access(self, telegram_id: int) -> bool:
        return self._telegram_users.get(telegram_id, None) is not None

    def set_user_query(self, bot: TeleBot, user_id: int, query: QueryManager):
        self._queries[f'{bot.token}{user_id}'] = query

    def reset_user_query(self, bot: TeleBot, user_id: int):
        self._queries[f'{bot.token}{user_id}'] = None


_users = UsersAccessHandler()
_config = Config()


def get_config() -> Config:
    return _config


def get_users_handler() -> UsersAccessHandler:
    return _users
