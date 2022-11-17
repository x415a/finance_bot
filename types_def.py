from collections import namedtuple
from typing import Optional
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message
import menus


T_MESSAGE = tuple[str, Optional[InlineKeyboardMarkup]]
DDSInfo = namedtuple('DDSInfo', 'dds type pl')
PaymentTypeInfo = namedtuple('PaymentTypeInfo', 'value')
UserInfo = namedtuple('UserInfo', 'username userid access')


class Field:
    __slots__ = ()

    def id(self) -> int:
        raise NotImplementedError()

    @classmethod
    def get_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def get_alias(cls) -> str:
        raise NotImplementedError()

    def query_code(self) -> int:
        raise NotImplementedError()

    def is_required(self) -> bool:
        raise NotImplementedError()

    def invite_text(self) -> str:
        raise NotImplementedError()

    def set_value(self, value):
        raise NotImplementedError()

    def get_value(self, default_v):
        raise NotImplementedError()

    def is_ready(self) -> bool:
        raise NotImplementedError()

    def get_invite(self) -> T_MESSAGE:
        raise NotImplementedError()

    def on_message(self, message: Message) -> str:
        raise NotImplementedError()

    def on_callback(self, callback: CallbackQuery, cb_data: menus.CallbackData) -> str:
        raise NotImplementedError()

    def handle_message(self, message: Message) -> T_MESSAGE:
        raise NotImplementedError()

    def handle_callback(self, callback: CallbackQuery, data: menus.CallbackData) -> T_MESSAGE:
        raise NotImplementedError()

    def set_content_message(self, message: Message):
        raise NotImplementedError()

    def get_content_message(self) -> Message:
        raise NotImplementedError()

    def get_str_value(self) -> Optional[str]:
        raise NotImplementedError()
