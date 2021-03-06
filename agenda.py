import time
from collections import defaultdict
from copy import copy
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
from typing import List, Dict, NamedTuple

from flask import render_template
from flask_babel import gettext

import google_account
from google_account import CalendarEvent

_weekdays = [gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'),
             gettext('Saturday'), gettext('Sunday')]
_weekdays_short_array = gettext('Mon;Tue;Wed;Thu;Fri;Sat;Sun')
_months = [gettext('January'), gettext('February'), gettext('March'), gettext('April'), gettext('May'), gettext('June'),
           gettext('July'), gettext('August'), gettext('September'), gettext('October'),
           gettext('November'), gettext('December')]


class DateClass(Enum):
    PAST = -1
    TODAY = 1
    TOMORROW = 2
    THIS_WEEK = 3
    NEXT_WEEK = 4
    THIS_MONTH = 5
    NEXT_MONTH = 6
    LATER = 7

    def to_string(self, today: time.struct_time = None) -> str:
        if today is None:
            today = time.localtime()

        if self == DateClass.PAST:
            return gettext('Past')
        if self == DateClass.TODAY:
            return gettext('Today')
        if self == DateClass.TOMORROW:
            return gettext('Tomorrow (%s)') % gettext(_weekdays[(today.tm_wday + 1) % 7])
        if self == DateClass.THIS_WEEK:
            return gettext('This week')
        if self == DateClass.NEXT_WEEK:
            return gettext('Next week')
        if self == DateClass.THIS_MONTH:
            return gettext('This month (%s)') % gettext(_months[today.tm_mon - 1])
        if self == DateClass.NEXT_MONTH:
            return gettext('Next month (%s)') % gettext(_months[(today.tm_mon - 1 + 1) % 12])

        return gettext('Later')


class LocalizedCalendarEvent(NamedTuple):
    """
    Based on the one in google_account
    """
    title: str
    time: datetime
    url: str

    @staticmethod
    def from_calendar_event(event: CalendarEvent):
        return LocalizedCalendarEvent(title=event.title, time=event.time, url=event.url)

    @property
    def day_in_month(self) -> int:
        return self.time.day

    @property
    def day_name_short(self) -> str:
        return gettext(_weekdays_short_array).split(';')[self.time.weekday()]


class Agenda:
    def __init__(self):
        self._entries_lock = Lock()
        self._entries = defaultdict(list)
        self._entries_fetch_time = None

    def get_items(self, max_items=10, use_cached=False) -> Dict[DateClass, List[CalendarEvent]]:
        with self._entries_lock:
            if not use_cached and not self.is_cache_up_to_date():
                calendar_entries = google_account.fetch_calendar_events(max_items=max_items)
                self._entries = Agenda.sort_calendar_entries(calendar_entries)
                self._entries_fetch_time = time.localtime()
            return copy(self._entries)

    def is_cache_up_to_date(self, max_age=600):
        if self._entries_fetch_time is None:
            return False
        if time.mktime(time.localtime()) - time.mktime(self._entries_fetch_time) > max_age:
            return False
        return True

    @staticmethod
    def classify_datetime(date: datetime, today: datetime) -> DateClass:
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
            first_of_next_month = datetime(year=today.year, month=today.month + 1, day=1, tzinfo=today.tzinfo)
        else:
            first_of_next_month = datetime(year=today.year + 1, month=1, day=1, tzinfo=today.tzinfo)
        if date < first_of_next_month:
            return DateClass.THIS_MONTH

        if first_of_next_month.month < 12:
            first_of_next_next_month = datetime(year=first_of_next_month.year, month=first_of_next_month.month + 1, day=1, tzinfo=today.tzinfo)
        else:
            first_of_next_next_month = datetime(year=first_of_next_month.year + 1, month=1, day=1, tzinfo=today.tzinfo)
        if date < first_of_next_next_month:
            return DateClass.NEXT_MONTH

        return DateClass.LATER

    @staticmethod
    def sort_calendar_entries(entries: List[CalendarEvent]) -> Dict[DateClass, List[CalendarEvent]]:
        result = defaultdict(list)
        for entry in entries:
            now = datetime.now(tz=entry.time.tzinfo)
            today = datetime(year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo)
            result[Agenda.classify_datetime(entry.time, today)].append(LocalizedCalendarEvent.from_calendar_event(entry))
        return result

    def render_agenda_cached(self):
        return render_template('agenda.html', agenda=self.get_items(use_cached=True),
                               need_update=not self.is_cache_up_to_date())

    def render_agenda_content(self):
        return render_template('agenda_content.html', agenda=self.get_items())
