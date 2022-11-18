import constants
from telebot.types import InlineKeyboardButton
from collections import namedtuple


__all__ = ['decode_callback_data', 'encode_callback_data', 'generate_buttons_list']

CallbackData = namedtuple('CallbackData', 'query field button data')


def encode_callback_data(query, field, button, *args):
    args = (query, field, button, *args)
    return constants.BUTTONS_CALLBACK_SEP.join(map(str, args))


def decode_callback_data(data: str) -> CallbackData:
    types = [int, int, int, str]
    return CallbackData(*(types[i](v)
                        for i, v in enumerate(data.split(constants.BUTTONS_CALLBACK_SEP, maxsplit=len(types) - 1))))


def generate_buttons_list(data: list[str], query_code: int, field_id: int, page: int):
    height = constants.MENU_HEIGHT if len(data) < constants.MENU_HEIGHT else constants.MENU_HEIGHT - 2
    max_page = len(data) // height + (1 if len(data) % height else 0)
    page = min(max_page, max(1, page))

    first = height * (page - 1)
    buttons = [InlineKeyboardButton(text=t,
                                    callback_data=encode_callback_data(query_code,
                                                                       field_id,
                                                                       constants.BUTTON_TYPE_INFO,
                                                                       first + id_))
               for id_, t in enumerate(data[first:height * page])]

    if height < constants.MENU_HEIGHT:
        page = max(1, min(max_page, page))
        pages = ([(p := page - 1, f'< {p} / {max_page} стр.')] if page > 1 else []) + \
                ([(p := page + 1, f'{p} / {max_page} стр. >')] if page < max_page else [])
        buttons.extend(InlineKeyboardButton(text=t,
                                            callback_data=encode_callback_data(query_code,
                                                                               field_id,
                                                                               constants.BUTTON_TYPE_INFO,
                                                                               'page', page))
                       for page, t in pages)
    return buttons


def get_control_buttons(query_code: int, field_id: int, required_field: bool) -> list[InlineKeyboardButton]:
    from handlers import get_config

    return [
        InlineKeyboardButton(text=get_config().get_control_button_text('button_change'),
                             callback_data=encode_callback_data(query_code, field_id,
                                                                constants.BUTTON_TYPE_CONTROL, 'change'))
    ] + ([
        InlineKeyboardButton(text=get_config().get_control_button_text('button_skip'),
                             callback_data=encode_callback_data(query_code, field_id,
                                                                constants.BUTTON_TYPE_CONTROL, 'skip'))
    ] if not required_field else [])


def get_summary_control(query_code: int):
    from handlers import get_config

    return [
        InlineKeyboardButton(text=get_config().get_control_button_text('summary'),
                             callback_data=encode_callback_data(query_code, -1,
                                                                constants.BUTTON_TYPE_CONTROL, 'summary'))
    ]
