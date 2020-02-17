from builtins import map
from datetime import date
from typing import NamedTuple

import redminelib
from flask import render_template
from flask_babel import gettext
from redminelib.exceptions import ResourceAttrError


class Tasks:
    OPEN_CLOSED_ID = 'tasks-open-closed'

    def __init__(self, config):
        self._config = config
        self._redmine = redminelib.Redmine(config['url'], key=config['api_key'])

    def chart_open_closed(self):
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
        message = gettext('%s issues are closed.') % ('<strong>%d/%d</strong>' % (closed_count, total_count))
        return render_template('tasks_open_closed_content.html', message=message, names=names, counts=counts, urls=urls,
                               backgrounds=backgrounds)

    def get_open_closed_timeline(self):
        creation_dates = []
        close_dates = []
        issues = self._redmine.issue.all(sort='id:asc')
        for issue in issues:
            creation_dates.append(issue.created_on.date())
            try:
                close_dates.append(issue.closed_on.date())
            except ResourceAttrError:
                pass  # not closed yet

        # walk through dates to recreate timeline
        timeline_dates = sorted(list(set(creation_dates + close_dates)))
        timeline = {}
        opened = 0
        closed = 0
        for _date in timeline_dates:
            opened += creation_dates.count(_date)
            closed += close_dates.count(_date)
            timeline[_date] = {'opened': opened, 'closed': closed}
        return timeline

    def get_in_progress_list_html(self):
        issues = []
        if 'in_progress_id' in self._config:
            issue_state = self._redmine.issue_status.get(self._config['in_progress_id'])
            for issue in issue_state.issues:
                issues.append({
                    'subject': issue.subject,
                    'url': self._config['url'] + 'issues/' + str(issue.id),
                    'done_ratio': issue.done_ratio
                })
        return render_template('tasks_in_progress.html', issues=issues)

    def render_chart_open_closed_lazyload(self):
        return render_template('tasks_open_closed.html', id=Tasks.OPEN_CLOSED_ID,
                               all_issues_url=self._config['url'] + 'issues',
                               all_projects_url=self._config['url'] + 'projects')

    def render_chart_open_closed_timeline(self):
        timeline = self.get_open_closed_timeline()
        variables = {
            'dates': [str(k) for k in timeline.keys()],
            'open': [v['opened'] - v['closed'] for k, v in timeline.items()],
            'closed': [v['closed'] for k, v in timeline.items()],
            'total': [v['opened'] for k, v in timeline.items()],
        }
        return render_template('tasks_open_closed_timeline.html', **variables)

    def issue_by_state_listing_url(self, state_id):
        #TODO nicer solution :/
        return self._config['url'] + 'issues?utf8=✓&set_filter=1&sort=id%3Adesc&f%5B%5D=status_id&op%5Bstatus_id%5D=%3D&v%5Bstatus_id%5D%5B%5D=' + str(state_id) + '&f%5B%5D='

    def _get_background_color_for_issue_state(self, state_id):
        if 'issue_state_colors' in self._config:
            if state_id in self._config['issue_state_colors']:
                return self._config['issue_state_colors'][state_id]
        # fall back to default from chartjs
        return '#0000001A'
