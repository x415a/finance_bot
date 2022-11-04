from typing import Any, Iterable, Optional
import constants
import json


__all__ = ['get_config']


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


_config = Config()


def get_config() -> Config:
    return _config
