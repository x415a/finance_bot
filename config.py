import constants
import json


__all__ = ['get_config']


class Config:
    def __init__(self):
        with open(constants.CONFIG, 'r', encoding='utf-8') as fs:
            self._vars = json.load(fs)

    def get_spreadsheets_list(self):
        return iter(self._vars['spreadsheets_url'].items())

    def get_spreadsheet_tag_info(self, tag: str):
        return self._vars['worksheets'][tag]


_config = Config()


def get_config() -> Config:
    return _config
