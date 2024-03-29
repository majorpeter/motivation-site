import random
import time
from copy import copy
from datetime import date, timedelta, datetime
from threading import Lock
from typing import NamedTuple

import redminelib
from flask import render_template
from flask_babel import gettext, ngettext
from redminelib.exceptions import ResourceAttrError


class Tasks:
    OPEN_CLOSED_ID = 'tasks-open-closed'
    IN_PROGRESS_DAY_COLORS = {
        0: '#cccccc',
        4: '#7d7d7d',
        10: '#ff9f24',
        20: '#ff2424',
    }

    class CachedData:
        def __init__(self, config):
            self._config = config
            self._redmine = redminelib.Redmine(config['url'], key=config['api_key'])

            self._last_updated = None
            self._update_lock = Lock()

            self.open_closed_timeline = {}
            self.contributions = {}
            self.issues_in_progress = []
            self.issues_closed = []
            self.issue_states_data = {}

        def update(self):
            with self._update_lock:  # fields can still be taken but the lock has to be used when invoking update
                if self.is_up_to_date(max_age=10):
                    return  # if another request already triggered the update recently, this call can be skipped

                self._update_contributions_and_open_closed_timeline()
                self._update_issues_in_progress()
                self._update_issues_closed()
                self.update_issue_states_data()

                self._last_updated = time.localtime()

        def _update_contributions_and_open_closed_timeline(self):
            if 'contributions_and_timeline' in self._config and self._config['contributions_and_timeline']:
                creation_dates = []
                close_dates = []
                journal_dates = []
                issues = self._redmine.issue.all(sort='id:asc', include=['journals'])
                for issue in issues:
                    creation_dates.append(issue.created_on.date())
                    if issue.closed_on is not None:
                        close_dates.append(issue.closed_on.date())

                    for journal in issue.journals:
                        journal_dates.append(journal.created_on.date())

                # walk through dates to recreate open/closed timeline
                open_closed_timeline_dates = sorted(list(set(creation_dates + close_dates)))
                open_closed_timeline = {}
                opened = 0
                closed = 0
                from_date = date.today() - timedelta(days=365)  # only care about the last year
                for _date in open_closed_timeline_dates:
                    opened += creation_dates.count(_date)
                    closed += close_dates.count(_date)
                    if _date >= from_date:
                        open_closed_timeline[_date] = {'opened': opened, 'closed': closed}

                self.open_closed_timeline = open_closed_timeline
                self.contributions = {_date: journal_dates.count(_date) for _date in set(journal_dates)}

        def _update_issues_in_progress(self):
            issues = []
            if 'in_progress_id' in self._config:
                issue_state = self._redmine.issue_status.get(self._config['in_progress_id'])
                for issue in issue_state.issues:
                    days_since_update = (datetime.now() - issue.updated_on).days
                    issues.append({
                        'subject': issue.subject,
                        'url': self._config['url'] + 'issues/' + str(issue.id),
                        'done_ratio': issue.done_ratio,
                        'updated': issue.updated_on,
                        'days_since_update': ngettext('{num} day ago', '{num} days ago', days_since_update).format(
                            num=days_since_update) if days_since_update > 0 else None,
                        'days_since_update_color': Tasks.IN_PROGRESS_DAY_COLORS[max(k for k in Tasks.IN_PROGRESS_DAY_COLORS if k <= days_since_update)],
                    })
            self.issues_in_progress = sorted(issues, key=lambda x: x['updated'])

        def _update_issues_closed(self):
            issues = []
            if 'closed_id' in self._config:
                issue_state = self._redmine.issue_status.get(self._config['closed_id'])
                for issue in issue_state.issues:
                    parent = self._redmine.issue.get(issue.parent.id) if hasattr(issue, 'parent') else None
                    issues.append({
                        'id': issue.id,
                        'subject': issue.subject,
                        'url': self._config['url'] + 'issues/' + str(issue.id),
                        'closed_date': issue.closed_on.strftime(self._config['date_format']),
                        'parent_subject': parent.subject if parent else None,
                        'parent_url': self._config['url'] + 'issues/' + str(parent.id) if parent else None,
                    })
            self.issues_closed = issues

        def update_issue_states_data(self):
            states = self._redmine.issue_status.all()
            names = []
            counts = []
            urls = []
            backgrounds = []
            closed_count = 0

            for state in states:
                if len(state.issues) > 0:
                    names.append(state.name)
                    counts.append(len(state.issues))
                    urls.append(self.issue_by_state_listing_url(state.id))
                    backgrounds.append(self._get_background_color_for_issue_state(state.id))
                if state.is_closed:
                    closed_count += len(state.issues)
            total_count = sum(counts)
            self.issue_states_data = {
                'states_names': names, 'states_counts': counts, 'states_urls': urls, 'states_backgrounds': backgrounds,
                'states_message': gettext('%s issues are closed.') % ('<strong>%d/%d</strong>' % (closed_count, total_count))
               }

        def get_random_closed_issue(self):
            with self._update_lock:
                if len(self.issues_closed) > 0:
                    return copy(random.choice(self.issues_closed))
            return None

        def is_up_to_date(self, max_age=1800):
            if self._last_updated is None:
                return False
            if time.mktime(time.localtime()) - time.mktime(self._last_updated) > max_age:
                return False
            return True

        def issue_by_state_listing_url(self, state_id):
            #TODO nicer solution :/
            return self._config['url'] + 'issues?utf8=✓&set_filter=1&sort=id%3Adesc&f%5B%5D=status_id&op%5Bstatus_id%5D=%3D&v%5Bstatus_id%5D%5B%5D=' + str(state_id) + '&f%5B%5D='

        def _get_background_color_for_issue_state(self, state_id):
            if 'issue_state_colors' in self._config:
                if state_id in self._config['issue_state_colors']:
                    return self._config['issue_state_colors'][state_id]
            # fall back to default from chartjs
            return '#0000001A'

    def __init__(self, config):
        self._config = config
        self._redmine = redminelib.Redmine(config['url'], key=config['api_key'])
        self._cached_data = Tasks.CachedData(config)

    def render_random_closed_task(self):
        issue = self._cached_data.get_random_closed_issue()
        if issue:
            return render_template('tasks_closed.html', **issue)
        return gettext('No closed issues found')

    def get_chart_states_data(self, use_cached=False):
        if not use_cached:
            self._cached_data.update_issue_states_data()
        return self._cached_data.issue_states_data

    def render_in_progress_list_html(self):
        if not self._cached_data.is_up_to_date():
            self._cached_data.update()
        return render_template('tasks_in_progress.html', issues_in_progress=self._cached_data.issues_in_progress)

    def render_layout(self):
        vars = {
            'id': Tasks.OPEN_CLOSED_ID,
            'issues_in_progress': self._cached_data.issues_in_progress,
            'all_issues_url': self._config['url'] + 'issues',
            'all_projects_url': self._config['url'] + 'projects',

            # to be filled by funcions below
            'states_names': [], 'states_counts': [], 'states_urls': [], 'states_backgrounds': [],
            'states_message': ''
        }
        vars.update(self.get_chart_states_data(use_cached=True))
        if 'contributions_and_timeline' in self._config and self._config['contributions_and_timeline']:
            vars.update(self.get_chart_contributions_vars(use_cached=True))
            vars.update(self.get_chart_open_closed_timeline_vars(use_cached=True))
        return render_template('tasks.html', **vars)

    def get_chart_contributions_vars(self, range_days=365, use_cached=False):
        class Day(NamedTuple):
            day: date
            count: int

            limits = {
                8: '#32701a',
                5: '#49a027',
                3: '#8ec865',
                1: '#cde184'
            }

            @property
            def color(self):
                for limit, color in Day.limits.items():
                    if self.count >= limit:
                        return color

                return '#f1f4f3'

        if not use_cached and not self._cached_data.is_up_to_date():
            self._cached_data.update()

        journal = copy(self._cached_data.contributions)
        end_date = date.today()
        _date = end_date - timedelta(days=range_days)
        _date += timedelta(days=7 - _date.weekday())  # find Monday in that week
        calendar = []
        sum = 0
        while _date <= end_date:
            if _date.weekday() == 0:
                calendar.append([])
            count = journal[_date] if _date in journal else 0
            calendar[-1].append(Day(_date, count))

            sum += count
            _date += timedelta(days=1)
        return {
            'contrib_calendar': calendar,
            'contrib_sum': sum,
            'contrib_url_prefix': self._config['url'] + 'activity?from=',
            'contrib_need_update': not self._cached_data.is_up_to_date()
        }

    def render_chart_contributions(self, range_days=365):
        return render_template('tasks_contributions.html', **self.get_chart_contributions_vars(range_days=range_days))

    def get_chart_open_closed_timeline_vars(self, use_cached=False):
        if not use_cached and not self._cached_data.is_up_to_date():
            self._cached_data.update()

        open_closed_timeline = copy(self._cached_data.open_closed_timeline)

        # check whether the last change was a long time ago, add today with the same values to fix the graph
        if len(open_closed_timeline.keys()) > 0:
            day_of_last_change = sorted(open_closed_timeline.keys())[-1]
            days_since_last_change = (date.today() - day_of_last_change).days
            if days_since_last_change > 0:
                open_closed_timeline[date.today()] = open_closed_timeline[day_of_last_change]

        return {
            'dates': [str(k) for k in open_closed_timeline.keys()],
            'open': [v['opened'] - v['closed'] for k, v in open_closed_timeline.items()],
            'closed': [v['closed'] for k, v in open_closed_timeline.items()],
            'total': [v['opened'] for k, v in open_closed_timeline.items()],
            'open_close_need_update': not self._cached_data.is_up_to_date()
        }

    def render_chart_open_closed_timeline(self, use_cached=False):
        return render_template('tasks_open_closed_timeline.html', **self.get_chart_open_closed_timeline_vars(use_cached=use_cached))
