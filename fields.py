from typing import Optional

from telebot.types import InlineKeyboardMarkup, Message, CallbackQuery
import constants
import menus
from tables import get_dds_list, get_payment_types
from handlers import get_config
from types_def import T_MESSAGE, Field as FieldBase


class Field(FieldBase):
    __FNAME__ = None
    __slots__ = ('_query', '_val', '_id', '_req', '_skipped', '_msg')

    def __init__(self, query: int, field_id: int, required: bool):
        self._query = query
        self._val = None
        self._id = field_id
        self._req = required
        self._skipped = False
        self._msg = None

    def _get_default_kb(self) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup()
        kb.row(*menus.get_control_buttons(self._query, self._id, self._req))
        return kb

    def id(self) -> int:
        return self._id

    @classmethod
    def get_name(cls) -> str:
        return cls.__FNAME__

    @classmethod
    def get_alias(cls) -> str:
        return get_config().get_field_info(cls.__FNAME__)['alias']

    def query_code(self) -> int:
        return self._query

    def is_required(self) -> bool:
        return self._req

    def invite_text(self) -> str:
        return get_config().get_field_info(self.__FNAME__)['text']

    def set_value(self, value):
        self._val = value

    def get_value(self, default_v):
        return self._val if not self._skipped else default_v

    def is_ready(self) -> bool:
        return self._skipped or self._val is not None

    def get_invite(self) -> T_MESSAGE:
        return self.invite_text(), self._get_default_kb()

    def on_message(self, message: Message) -> str:
        raise NotImplementedError()

    def on_callback(self, callback: CallbackQuery, cb_data: menus.CallbackData) -> str:
        raise NotImplementedError()

    def handle_message(self, message: Message) -> T_MESSAGE:
        return self.on_message(message), self._get_default_kb()

    def get_content_message(self) -> Message:
        return self._msg

    def handle_callback(self, callback: CallbackQuery, cb_data: menus.CallbackData) -> T_MESSAGE:
        if cb_data.button == constants.BUTTON_TYPE_CONTROL:
            if cb_data.data == 'change':
                self._val = None
                self._skipped = False
                return self.get_invite()
            elif cb_data.data == 'skip' and not self._req:
                self._skipped = True
                return self.invite_text() + get_config().get_message_text('value_skipped'), callback.message.reply_markup
            else:
                raise RuntimeError(f'Invalid control button ("{callback.data}")')
        else:
            text, kb = self.on_callback(callback, cb_data)
            if kb is None:
                kb = callback.message.reply_markup
            return text, kb

    def set_content_message(self, message: Message):
        self._msg = message

    def get_str_value(self) -> Optional[str]:
        return str(self._val) if self._val is not None else None


class StrictField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._page = []

    def _generate_menu(self, page: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup()
        self._page = self.get_values()
        kb.add(*menus.generate_buttons_list(self._page, self.query_code(), self.id(), page), row_width=1)
        return kb

    def get_invite(self) -> T_MESSAGE:
        return self.invite_text(), self._generate_menu(1)

    def on_callback(self, callback: CallbackQuery, cb_data: menus.CallbackData) -> T_MESSAGE:
        if cb_data.data.startswith('page'):
            offs = len(f'page{constants.BUTTONS_CALLBACK_SEP}')
            return callback.message.text, self._generate_menu(int(cb_data.data[offs:]))
        return self.on_choice(self._page[int(cb_data.data)]), callback.message.reply_markup

    def get_values(self) -> list[str]:
        raise NotImplementedError()

    def on_choice(self, value: str) -> str:
        raise NotImplementedError()


class DDSField(StrictField):
    __FNAME__ = 'dds'

    def get_values(self) -> list[str]:
        return [i.dds for i in get_dds_list()]

    def on_choice(self, value: str) -> str:
        self.set_value(value)
        return self.invite_text() + value


class PaymentTypes(StrictField):
    __FNAME__ = 'payment_type'

    def get_values(self) -> list[str]:
        return [i.value for i in get_payment_types()]

    def on_choice(self, value: str) -> str:
        self.set_value(value)
        return self.invite_text() + value


class PriceAmount(Field):
    __FNAME__ = 'price_amount'

    def on_message(self, message: Message) -> str:
        try:
            self.set_value(v := float(message.text.strip()))
            return self.invite_text() + (f'{v:.0f}' if v.is_integer() else f'{v:.2f}')
        except ValueError:
            return f'{self.invite_text()}\n\n' + get_config().get_error_text('invalid_price_amount')

    def get_str_value(self) -> Optional[str]:
        if (v := self.get_value(None)) is None:
            return None
        return f'{v:.0f}' if v.is_integer() else f'{v:.2f}'


class Contractor(Field):
    __FNAME__ = 'contractor'

    def on_message(self, message: Message) -> str:
        self.set_value(message.text)
        return self.invite_text() + self.get_value('')


class Project(Field):
    __FNAME__ = 'project'

    def on_message(self, message: Message) -> str:
        self.set_value(message.text)
        return self.invite_text() + self.get_value('')


class Comments(Field):
    __FNAME__ = 'comments'

    def on_message(self, message: Message) -> str:
        self.set_value(message.text)
        return self.invite_text() + self.get_value('')
