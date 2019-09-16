import time
from collections import defaultdict
from copy import copy
from datetime import datetime, timedelta, timezone
from enum import Enum
from threading import Lock

import google_account

_entries_lock = Lock()
_entries = None
_entries_fetch_time = None

_weekdays = ['Monday, Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
            'November', 'December']


def get_agenda(max_items=10):
    global _entries_fetch_time, _entries
    with _entries_lock:
        if _entries_fetch_time is None or time.mktime(time.localtime()) - time.mktime(_entries_fetch_time) > 600:
            calendar_entries = google_account.fetch_calendar_events(max_items=max_items)
            _entries = sort_calendar_entries(calendar_entries)
            _entries_fetch_time = time.localtime()
        return copy(_entries)


class DateClass(Enum):
    PAST = -1
    TODAY = 1
    TOMORROW = 2
    THIS_WEEK = 3
    NEXT_WEEK = 4
    THIS_MONTH = 5
    NEXT_MONTH = 6
    LATER = 7

    def to_string(self, today=datetime.today()):
        if self == DateClass.PAST:
            return 'Past'
        if self == DateClass.TODAY:
            return 'Today'
        if self == DateClass.TOMORROW:
            return 'Tomorrow (%s)' % _weekdays[(today.weekday() + 1) % 7]
        if self == DateClass.THIS_WEEK:
            return 'This week'
        if self == DateClass.NEXT_WEEK:
            return 'Next week'
        if self == DateClass.THIS_MONTH:
            return 'This month (%s)' % _months[today.month - 1]
        if self == DateClass.NEXT_MONTH:
            return 'Next month (%s)' % _months[(today.month - 1 + 1) % 12]

        return 'Later'


def classify_datetime(date, today=datetime.today()):
    """
    classifies input date into a DateClass value
    :param date: datetime to classify
    :param today: current day
    :return: DateClass instance
    """
    if today > date:
        return DateClass.PAST # just in case

    delta = date - today
    if delta.days == 0:
        return DateClass.TODAY
    if delta.days == 1:
        return DateClass.TOMORROW

    next_monday = today + timedelta(days=7-today.weekday())
    if date < next_monday:
        return DateClass.THIS_WEEK

    next_next_monday = next_monday + timedelta(days=7)
    if date < next_next_monday:
        return DateClass.NEXT_WEEK

    if today.month < 12:
        first_of_next_month = datetime(year=today.year, month=today.month + 1, day=1)
    else:
        first_of_next_month = datetime(year=today.year + 1, month=1, day=1)
    if date < first_of_next_month:
        return DateClass.THIS_MONTH

    if first_of_next_month.month < 12:
        first_of_next_next_month = datetime(year=first_of_next_month.year, month=first_of_next_month.month + 1, day=1)
    else:
        first_of_next_next_month = datetime(year=first_of_next_month.year + 1, month=1, day=1)
    if date < first_of_next_next_month:
        return DateClass.NEXT_MONTH

    return DateClass.LATER


def sort_calendar_entries(entries):
    result = defaultdict(list)
    today = datetime.utcfromtimestamp(time.time())
    for entry in entries:
        result[classify_datetime(entry['time'].replace(tzinfo=None), today)].append(entry)
    return result
