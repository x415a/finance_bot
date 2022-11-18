from telebot import TeleBot
from telebot.types import Message
from handlers import get_config, get_users_handler
import bot_funcs


_bot = TeleBot(get_config().get_bot_token('finance'))


@_bot.message_handler(commands=['start'])
def command_start(msg: Message):
    _bot.send_message(msg.chat.id, text=get_config().get_message_text('hello_msg'))


@_bot.message_handler(commands=['auth'])
def command_auth(msg: Message):
    _bot.send_message(msg.chat.id, text=get_config().get_message_text('auth'))
    get_users_handler().reset_user_registration(msg.from_user.id)


@_bot.message_handler(commands=['new_record'])
def command_new_record(msg: Message):
    if not get_users_handler().is_user_has_access(msg.from_user.id):
        bot_funcs.send_access_denied(_bot, msg.chat)
    else:
        bot_funcs.add_new_record(_bot, msg)


def get_bot() -> TeleBot:
    return _bot


_bot.register_message_handler(bot_funcs.handle_user_message, content_types=['text'], pass_bot=True)
_bot.register_callback_query_handler(bot_funcs.handle_user_callback, lambda *args: True, True)
