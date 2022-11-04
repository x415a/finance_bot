from typing import Any, Iterable, Optional
from tables import UserInfo
import constants
import json


__all__ = ['get_config', 'get_users_handler']


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


class UsersAccessHandler:
    def __init__(self):
        pass

    def update_users_list(self, users_list: Iterable[UserInfo]):
        pass

    def search_by_tg_id(self, id_: int):
        pass

    def search_by_userid(self):
        pass


_users = UsersAccessHandler()
_config = Config()


def get_config() -> Config:
    return _config


def get_users_handler() -> UsersAccessHandler:
    return _users
