from telebot import ExceptionHandler
import time
import traceback as tb


__all__ = ['BotExcHandler', 'get_next_query_code']


_current_query = int(time.time())


class BotExcHandler(ExceptionHandler):
    def handle(self, exception):
        tb.print_exception(exception)


def get_next_query_code():
    global _current_query

    _current_query += 1
    return _current_query - 1
