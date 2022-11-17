from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, Message, CallbackQuery
from typing import Optional, Union
from menus import ValuesListMenu, decode_callback_data, encode_callback_data
from constants import MENUCODE_DDS_LIST, MENUCODE_PAYMENT_TYPES
from tables import get_dds_list, get_payment_types
from handlers import get_config
from util import get_next_query_code


_MSG_T_ALIAS = tuple[str, Optional[Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]]]


class Field:
    __FNAME__ = None
    __slots__ = ('_query', '_val', '_name')

    def __init__(self, q_code: int, name: str):
        self._query = q_code
        self._val = None
        self._name = name

    def get_default_text(self) -> str:
        return get_config().get_field_info(self.__FNAME__)['text']

    def name(self) -> str:
        return self._name

    def get_invite(self) -> _MSG_T_ALIAS:
        raise NotImplementedError()

    def on_message(self, message: Message):
        raise NotImplementedError()

    def query_code(self) -> int:
        return self._query

    def set_value(self, value):
        self._val = value

    def get_value(self):
        return self._val

    def is_ready(self) -> bool:
        return self._val is not None


class DDSField(Field, ValuesListMenu):
    __FNAME__ = 'dds'

    def __init__(self, q_code: int):
        Field.__init__(self, q_code, get_config().get_field_info(self.__FNAME__)['alias'])
        ValuesListMenu.__init__(self, MENUCODE_DDS_LIST)

    def get_invite(self) -> _MSG_T_ALIAS:
        return self.get_default_text(), self.generate_menu(1)

    def get_values(self) -> list[str]:
        return [i.dds for i in get_dds_list()]

    def on_choice(self, value: str) -> str:
        self.set_value(value)
        return self.get_default_text() + value


class PaymentTypes(Field, ValuesListMenu):
    __FNAME__ = 'payment_type'

    def __init__(self, q_code: int):
        Field.__init__(self, q_code, get_config().get_field_info(self.__FNAME__)['alias'])
        ValuesListMenu.__init__(self, MENUCODE_PAYMENT_TYPES)

    def get_invite(self) -> _MSG_T_ALIAS:
        return self.get_default_text(), self.generate_menu(1)

    def get_values(self) -> list[str]:
        return [i.value for i in get_payment_types()]

    def on_choice(self, value: str) -> str:
        self.set_value(value)
        return self.get_default_text() + value


class PriceAmount(Field):
    __FNAME__ = 'price_amount'

    def get_invite(self) -> _MSG_T_ALIAS:
        return self.get_default_text(), None

    def on_message(self, message: Message) -> str:
        try:
            self.set_value(float(message.text.strip()))
            return ''
        except ValueError:
            return get_config().get_error_text('invalid_price_amount')


class QueryManager:
    __slots__ = ('_query', '_fields', '_menus', '_cur_field', '_aliases')

    def __init__(self, *fields: Field):
        self._query = get_next_query_code()
        self._fields = fields
        self._cur_field: Optional[Field] = None
        self._menus: dict[int, ValuesListMenu] = {}
        self._aliases = {i.name: i for i in fields}

    def _get_next_empty_field(self) -> Optional[Field]:
        for f in self._fields:
            if not f.is_ready():
                if isinstance(f, ValuesListMenu):
                    self._menus[f.menu_code()] = f
                    return f
        return None

    def is_done(self) -> bool:
        for f in self._fields:
            if not f.is_ready():
                return False
        return True

    def get_field(self, field: str) -> Field:
        return self._aliases[field]

    def get_query_code(self):
        return self._query

    def get_first_message(self) -> _MSG_T_ALIAS:
        self._cur_field = self._get_next_empty_field()
        return self._cur_field.get_invite()

    def handle_new_message(self, message: Message) -> _MSG_T_ALIAS:
        t = self._cur_field.on_message(message)
        if self._cur_field.is_ready():
            self._cur_field = self._get_next_empty_field()
        return t

    def handle_callback_query(self, callback: CallbackQuery) -> _MSG_T_ALIAS:
        _, menu, *args = decode_callback_data(callback.data, int, int, str)
        res = self._menus[menu].handle_callback(callback, encode_callback_data(*args))
        if self._cur_field.is_ready():
            self._cur_field = self._get_next_empty_field()
        return res
