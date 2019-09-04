import time
from copy import copy
from threading import Lock

import google_account

_entries_lock = Lock()
_entries = None
_entries_fetch_time = None


def get_agenda(max_items=10):
    global _entries_fetch_time, _entries
    with _entries_lock:
        if _entries_fetch_time is None or time.mktime(time.localtime()) - time.mktime(_entries_fetch_time) > 600:
            _entries = google_account.fetch_calendar_events(max_items=max_items)
            _entries_fetch_time = time.localtime()
        return copy(_entries)
