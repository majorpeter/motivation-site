import calendar
import time
from copy import copy
from datetime import timedelta, date, datetime
from threading import Lock

from flask import render_template
from flask_babel import gettext

import google_account


class Workout:
    def __init__(self, config):
        self._config = config

        self._entries_lock = Lock()
        self._entries = []
        self._last_updated = None

    def update(self, max_age_days=60):
        with self._entries_lock:
            entries = google_account.fetch_cells_from_sheet(self._config['sheet_id'], self._config['sheet_range'])

            min_date = date.today() - timedelta(days=max_age_days)
            for keep_index in range(len(entries)):
                _date = datetime.strptime(entries[keep_index][0], self._config['date_format']).date()
                if _date >= min_date:
                    break
            self._entries = entries[keep_index:]
            self._last_updated = time.localtime()

    def is_up_to_date(self, max_age=1000):
        if self._last_updated is None:
            return False
        if time.mktime(time.localtime()) - time.mktime(self._last_updated) > max_age:
            return False
        return True

    def get_workout_days_for_range(self, days_range=7, use_cached=False):
        if not use_cached and not self.is_up_to_date():
            self.update()

        entries = copy(self._entries)
        result = []

        i = len(entries) - 1
        date = time.localtime()
        date_str = time.strftime(self._config['date_format'], date)

        while i >= 0:
            count = 0
            for j in range(i, -1, -1):
                day_earlier = time.strptime(entries[j][0], self._config['date_format'])
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
            date_str = time.strftime(self._config['date_format'], date)
        return result

    def days_since_workout(self, use_cached=False):
        if not use_cached and not self.is_up_to_date():
            self.update()

        entries = copy(self._entries)
        if len(entries) == 0:
            return -1
        last_workout_date = time.strptime(entries[-1][0], self._config['date_format'])
        date = time.localtime()
        delta_sec = time.mktime(date) - time.mktime(last_workout_date)
        delta_day = int(delta_sec / 24 / 3600)
        return delta_day

    def days_since_workout_message_html(self, use_cached=False):
        days = self.days_since_workout(use_cached=use_cached)
        if days < 0: # error state
            return gettext('Fetching data...'), 'error'
        elif days == 0:
            return gettext('You have worked out <strong>today</strong>, great job!'), 'thumb_up'
        elif days == 1:
            return gettext('You have worked out <strong>yesterday</strong>.'), 'thumb_up'
        elif days < 4:
            return gettext('You have worked out <strong>%d days ago</strong>, maybe it\'s time to hit the gym?') % days, 'warning'
        else:
            return gettext('You haven\'t worked out in <strong>%d days</strong>! Go training now!') % days, 'error'

    def workout_calendar_data(self, use_cached=False):
        t = time.localtime()
        cal = calendar.monthcalendar(t.tm_year, t.tm_mon)
        days = self.get_workout_days_for_range(days_range=7, use_cached=use_cached)
        result = []
        for row in cal:
            rrow = []
            for cell in row:
                if cell == 0:
                    rrow.append(None)
                else:
                    date_str = time.strftime(self._config['date_format'], (t.tm_year, t.tm_mon, cell, 0, 0, 0, 0, 0, 0))
                    workout_day = [x for x in days if x['date'] == date_str]
                    rrow.append({
                        'day': cell,
                        'today': cell == t.tm_mday,
                        'workout': len(workout_day) != 0 and workout_day[0]['workout_day'],
                        'hint': gettext('%d workouts in the last week') % workout_day[0]['count'] if len(
                            workout_day) != 0 else gettext('No data')
                    })
            result.append(rrow)
        return gettext('Your workout days in %d.%02d. so far:') % (t.tm_year, t.tm_mon), result

    def chart_lazy_load(self):
        # merge the dicts returned by the two to pass as kwargs
        return render_template('workout_chart.html',
                               **{**self.get_chart_content(use_cached=True),
                                  **self.get_calendar_content(use_cached=True)})

    def get_chart_content(self, use_cached=False):
        days_since_workout_message, days_since_workout_icon = self.days_since_workout_message_html(use_cached=use_cached)
        workout_days_data = self.get_workout_days_for_range(use_cached=use_cached)

        workout_dates = [x['date'] for x in workout_days_data]
        weight_measurements = [x['weight'] if 'weight' in x else None for x in workout_days_data]
        workouts_per_week = [x['count'] for x in workout_days_data]

        workout_dates.reverse()
        weight_measurements.reverse()
        workouts_per_week.reverse()
        return {
            'days_since_workout': days_since_workout_message,
            'days_since_workout_icon': days_since_workout_icon,
            'workout_dates': workout_dates,
            'workouts_per_week': workouts_per_week,
            'weight_measurements': weight_measurements,
            'need_update': not self.is_up_to_date()
        }

    def render_chart_content(self):
        return render_template('workout_chart_content.html', **self.get_chart_content(use_cached=False))

    def get_calendar_content(self, use_cached=False):
        workout_cal_header, workout_cal = self.workout_calendar_data(use_cached=use_cached)
        workout_days_data = self.get_workout_days_for_range(use_cached=use_cached)
        return {
            'workout_cal_header': workout_cal_header,
            'workout_cal': workout_cal,
            'workout': workout_days_data[:10]
        }

    def render_calendar_content(self):
        return render_template('workout_calendar_content.html', **self.get_calendar_content(use_cached=False))
