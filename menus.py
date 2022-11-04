import constants
from config import get_config
from tables import update_dds_list
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


__all__ = ['generate_dds_list_menu']


def _encode_callback_data(*args):
    return constants.BUTTONS_CALLBACK_SEP.join(map(str, args))


def _decode_callback_data(data: str, *types):
    return [types[i](v) for i, v in enumerate(data.split(constants.BUTTONS_CALLBACK_SEP))]


def _generate_buttons_list(data: list[str], menu_code: int, query_code: int, page: int):
    height = constants.MENU_HEIGHT if len(data) < constants.MENU_HEIGHT else constants.MENU_HEIGHT - 2
    max_page = len(data) // height + (1 if len(data) % height else 0)
    page = min(max_page, max(1, page))

    buttons = [InlineKeyboardButton(text=t, callback_data=_encode_callback_data(menu_code, query_code, id_))
               for id_, t in enumerate(data[height * (page - 1):height * page])]
    if height < constants.MENU_HEIGHT:
        pages = [(p := max(1, page - 1), f'<< {p} / {max_page} стр.'),
                 (p := min(max_page, page + 1), f'>> {p} / {max_page} стр.')]
        buttons.extend(InlineKeyboardButton(text=t,
                                            callback_data=_encode_callback_data(menu_code, query_code, 'page', page))
                       for page, t in pages)
    return buttons


def generate_dds_list_menu(query_code: int, page: int) -> InlineKeyboardMarkup:
    if get_config().get_saved_data('dds_types') is None:
        update_dds_list()
    dds = [i.dds for i in get_config().get_saved_data('dds_types')]
    kb = InlineKeyboardMarkup()
    kb.add(*_generate_buttons_list(dds, constants.MENUCODE_DDS_LIST, query_code, page), row_width=1)
    return kb
