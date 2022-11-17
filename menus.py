import constants
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


__all__ = ['ValuesListMenu', 'decode_callback_data', 'encode_callback_data']


def encode_callback_data(*args):
    return constants.BUTTONS_CALLBACK_SEP.join(map(str, args))


def decode_callback_data(data: str, *types):
    return [types[min(i, len(types) - 1)](v) for i, v in enumerate(data.split(constants.BUTTONS_CALLBACK_SEP))]


def _generate_buttons_list(data: list[str], menu_code: int, query_code: int, page: int):
    height = constants.MENU_HEIGHT if len(data) < constants.MENU_HEIGHT else constants.MENU_HEIGHT - 2
    max_page = len(data) // height + (1 if len(data) % height else 0)
    page = min(max_page, max(1, page))

    buttons = [InlineKeyboardButton(text=t, callback_data=encode_callback_data(menu_code, query_code, id_))
               for id_, t in enumerate(data[height * (page - 1):height * page])]
    if height < constants.MENU_HEIGHT:
        pages = [(p := max(1, page - 1), f'<< {p} / {max_page} стр.'),
                 (p := min(max_page, page + 1), f'>> {p} / {max_page} стр.')]
        buttons.extend(InlineKeyboardButton(text=t,
                                            callback_data=encode_callback_data(menu_code, query_code, 'page', page))
                       for page, t in pages)
    return buttons


class ValuesListMenu:
    def __init__(self, menu_code: int):
        self._code = menu_code
        self._page = []

    def menu_code(self):
        return self._code

    def get_values(self) -> list[str]:
        raise NotImplementedError()

    def query_code(self) -> int:
        raise NotImplementedError()

    def on_choice(self, value: str) -> str:
        raise NotImplementedError()

    def generate_menu(self, page: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardMarkup()
        self._page = self.get_values()
        kb.add(*_generate_buttons_list(self._page, self._code, self.query_code(), page), row_width=1)
        return kb

    def handle_callback(self, callback: CallbackQuery, data: str) -> tuple[str, InlineKeyboardMarkup]:
        if data.startswith('page'):
            return callback.message.text, self.generate_menu(int(data[4:]))
        return self.on_choice(self._page[int(data)]), callback.message.reply_markup
