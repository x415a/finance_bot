from telebot import TeleBot
from telebot.types import Message
from handlers import get_config
from threading import Thread
from util import BotExcHandler, get_next_query_code
from handlers import get_config


_bot = TeleBot(get_config().get_bot_token('finance'))
_bot.exception_handler = BotExcHandler()


@_bot.message_handler(commands=['start'])
def command_start(msg: Message):
    _bot.send_message(msg.chat.id, text=get_config().get_message_text('hello_msg'))


@_bot.message_handler(commands=['auth'])
def command_auth(msg: Message):
    _bot.send_message(msg.chat.id, text=get_config().get_message_text('auth'))


@_bot.message_handler(commands=['new_record'])
def command_new_record(msg: Message):
    add_new_record(msg)


def add_new_record(msg: Message):
    pass


def start_bot() -> Thread:
    (th := Thread(target=_bot.infinity_polling)).start()
    return th
