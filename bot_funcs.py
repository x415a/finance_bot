from threading import Thread
from typing import Optional
from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Chat, Message
from telebot.apihelper import ApiTelegramException
from handlers import QueryManager, get_users_handler, get_config
import menus
import fields


def register_user(message: Message, bot: TeleBot):
    try:
        code = int(message.text.strip())
        if get_users_handler().register_user(message.from_user.id, code):
            user = get_users_handler().get_user_access_info(message.from_user.id)
            bot.send_message(message.chat.id, get_config().get_message_text('auth_success').format(name=user.username))
        else:
            bot.send_message(message.chat.id, get_config().get_message_text('auth_failed'))
    except ValueError:
        send_access_denied(bot, message.chat)


def send_access_denied(bot: TeleBot, chat: Chat):
    bot.send_message(chat.id, get_config().get_message_text('auth'))


def handle_user_message(msg: Message, bot: TeleBot):
    if (q := get_users_handler().get_user_query(bot, msg.from_user.id)) is None:
        if not get_users_handler().is_user_has_access(msg.from_user.id):
            register_user(msg, bot)
        return
    text, kb = q.handle_message(msg)
    msg = q.get_current_content_message()
    try:
        bot.edit_message_text(text, msg.chat.id, msg.message_id, reply_markup=kb)
    except ApiTelegramException:
        pass

    if q.has_summary_message():
        edit_query_summary(bot, *q.generate_summary_message(), q)

    update_query(bot, q, msg.chat)


def handle_user_callback(callback: CallbackQuery, bot: TeleBot):
    bot.answer_callback_query(callback.id)
    cb_data = menus.decode_callback_data(callback.data)

    if ((q := get_users_handler().get_user_query(bot, callback.from_user.id)) is None
            or q.get_query_code() != cb_data.query):
        return

    if cb_data.data == 'summary':
        if not get_users_handler().is_user_has_access(callback.from_user.id):
            send_access_denied(bot, callback.message.chat)
            return
        update_query_summary(bot, q, callback)
        return

    text, kb = q.handle_callback_query(callback, cb_data)
    try:
        bot.edit_message_text(text, callback.message.chat.id, callback.message.message_id, reply_markup=kb)
    except ApiTelegramException:
        pass

    if q.has_summary_message():
        edit_query_summary(bot, *q.generate_summary_message(), q)

    update_query(bot, q, callback.message.chat)


def update_query_summary(bot: TeleBot, q: QueryManager, callback: CallbackQuery):
    msg, kb = q.confirm_summary_message()
    edit_query_summary(bot, msg, kb, q)

    if q.is_done():
        get_users_handler().reset_user_query(bot, callback.from_user.id)


def edit_query_summary(bot: TeleBot, text: str, kb: Optional[InlineKeyboardMarkup], q: QueryManager):
    message = q.get_current_summary_message()
    try:
        bot.edit_message_text(text, message.chat.id, message.message_id, reply_markup=kb)
    except ApiTelegramException:
        pass


def update_query(bot: TeleBot, q: QueryManager, chat: Chat):
    if q.is_waits():
        if q.is_done():
            if q.has_summary_message():
                edit_query_summary(bot, *q.generate_summary_message(), q)
            else:
                msg, kb = q.generate_summary_message()
                res = bot.send_message(chat.id, text=msg, reply_markup=kb)
                q.set_current_summary_message(res)
        else:
            send_invite(bot, q, chat)


def send_invite(bot: TeleBot, q: QueryManager, chat: Chat):
    text, kb = q.get_invite_message()
    msg = bot.send_message(chat.id, text=text, reply_markup=kb)
    q.set_current_content_message(msg)


def add_new_record(bot: TeleBot, msg: Message):
    q = QueryManager(
        (fields.DDSField, True),
        (fields.PaymentTypes, True),
        (fields.PriceAmount, True),
        (fields.Contractor, False),
        (fields.Project, False),
        (fields.Comments, False)
    )
    get_users_handler().set_user_query(bot, msg.from_user.id, q)
    send_invite(bot, q, msg.chat)


def start_bot(bot: TeleBot) -> Thread:
    (th := Thread(target=bot.infinity_polling)).start()
    return th
