import calendar
import json
import time
from copy import copy
from threading import Lock

import google_account

with open('config.json', 'r') as f:
    config = json.load(f)


_entries_lock = Lock()
_entries = None
_entries_fetch_time = None


def _get_entries():
    global _entries_fetch_time, _entries
    with _entries_lock:
        if _entries_fetch_time is None or time.mktime(time.localtime()) - time.mktime(_entries_fetch_time) > 1000:
            _entries = google_account.fetch_cells_from_sheet(config['workout_days_sheet_id'], config['workout_days_sheet_range'])
            _entries_fetch_time = time.localtime()
        return copy(_entries)


def get_workout_days_for_range(days_range=7):
    entries = _get_entries()
    result = []

    i = len(entries) - 1
    date = time.localtime()
    date_str = time.strftime(config['date_format'], date)

    while i >= 0:
        count = 0
        for j in range(i, -1, -1):
            day_earlier = time.strptime(entries[j][0], config['date_format'])
            delta_sec = time.mktime(date) - time.mktime(day_earlier)
            delta_day = int(delta_sec / 24 / 3600)
            if delta_day >= days_range:
                break
            count += 1

        if entries[i][0] == date_str:
            data = {'date': date_str, 'count': count, 'workout_day': True, 'weight': float(entries[i][1])}
            i -= 1
        else:
            data = {'date': date_str, 'count': count, 'workout_day': False}
        result.append(data)

        date = time.localtime(time.mktime(date) - 24 * 3600)
        date_str = time.strftime(config['date_format'], date)
    return result


def days_since_workout():
    entries = _get_entries()
    last_workout_date = time.strptime(entries[-1][0], config['date_format'])
    date = time.localtime()
    delta_sec = time.mktime(date) - time.mktime(last_workout_date)
    delta_day = int(delta_sec / 24 / 3600)
    return delta_day


def days_since_workout_message_html():
    days = days_since_workout()
    if days == 0:
        return 'You have worked out <strong>today</strong>, great job!', 'fa-thumbs-up'
    elif days == 1:
        return 'You have worked out <strong>yesterday</strong>.', 'fa-thumbs-up'
    elif days < 4:
        return 'You have worked out <strong>%d days ago</strong>, maybe it\'s time to hit the gym?' % days, 'fa-exclamation-triangle'
    else:
        return 'You haven\'t worked out in <strong>%d days</strong>! Go training now!' % days, 'fa-exclamation'


def workout_calendar():
    t = time.localtime()
    cal = calendar.monthcalendar(t.tm_year, t.tm_mon)
    days = get_workout_days_for_range(days_range=7)
    result = []
    for row in cal:
        rrow = []
        for cell in row:
            if cell == 0:
                rrow.append(None)
            else:
                date_str = time.strftime(config['date_format'], (t.tm_year, t.tm_mon, cell, 0, 0, 0, 0, 0, 0))
                workout_day = [x for x in days if x['date'] == date_str]
                rrow.append({
                    'day': cell,
                    'today': cell == t.tm_mday,
                    'workout': len(workout_day) != 0 and workout_day[0]['workout_day'],
                    'hint': '%d workouts in the last week' % workout_day[0]['count'] if len(workout_day) != 0 else 'No data'
                })
        result.append(rrow)
    return 'Your workout days in %d.%02d. so far:' % (t.tm_year, t.tm_mon), result
