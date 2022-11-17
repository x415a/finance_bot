from telebot import TeleBot
from telebot.types import Message, CallbackQuery, Chat
from handlers import get_users_handler, QueryManager
from threading import Thread
from util import BotExcHandler
from handlers import get_config
import menus
import fields


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


@_bot.message_handler(content_types=['text'])
def handle_user_message(msg: Message):
    if (q := get_users_handler().get_user_query(msg.from_user.id)) is None:
        return
    text, kb = q.handle_message(msg)
    msg = q.get_current_content_message()
    _bot.edit_message_text(text, msg.chat.id, msg.message_id, reply_markup=kb)

    if q.has_summary_message():
        edit_query_summary(*q.generate_summary_message(), q)

    update_query(q, msg.chat)


@_bot.callback_query_handler(func=lambda *args: True)
def handle_user_callback(callback: CallbackQuery):
    _bot.answer_callback_query(callback.id)
    cb_data = menus.decode_callback_data(callback.data)

    if (q := get_users_handler().get_user_query(callback.from_user.id)) is None or q.get_query_code() != cb_data.query:
        return

    if cb_data.data == 'summary':
        update_query_summary(q, callback)
        return

    text, kb = q.handle_callback_query(callback, cb_data)
    _bot.edit_message_text(text, callback.message.chat.id, callback.message.message_id, reply_markup=kb)

    if q.has_summary_message():
        edit_query_summary(*q.generate_summary_message(), q)

    update_query(q, callback.message.chat)


def add_new_record(msg: Message):
    q = QueryManager(
        (fields.DDSField, True),
        (fields.PaymentTypes, True),
        (fields.PriceAmount, True),
        (fields.Contractor, False),
        (fields.Project, False),
        (fields.Comments, False)
    )
    get_users_handler().set_user_query(msg.from_user.id, q)
    send_invite(q, msg.chat)


def update_query_summary(q: QueryManager, callback: CallbackQuery):
    msg, kb = q.confirm_summary_message()
    edit_query_summary(msg, kb, q)

    if q.is_done():
        get_users_handler().reset_user_query(callback.from_user.id)


def edit_query_summary(text, kb, q):
    message = q.get_current_summary_message()
    _bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=kb)


def update_query(q: QueryManager, chat: Chat):
    if q.is_waits():
        if q.is_done():
            if q.has_summary_message():
                edit_query_summary(*q.generate_summary_message(), q)
            else:
                msg, kb = q.generate_summary_message()
                res = _bot.send_message(chat.id, text=msg, reply_markup=kb)
                q.set_current_summary_message(res)
        else:
            send_invite(q, chat)


def send_invite(q: QueryManager, chat: Chat):
    text, kb = q.get_invite_message()
    msg = _bot.send_message(chat.id, text=text, reply_markup=kb)
    q.set_current_content_message(msg)


def start_bot() -> Thread:
    (th := Thread(target=_bot.infinity_polling)).start()
    return th
