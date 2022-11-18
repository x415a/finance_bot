import time


__all__ = ['get_next_query_code']


_current_query = int(time.time())


def get_next_query_code():
    global _current_query

    _current_query += 1
    return _current_query - 1
