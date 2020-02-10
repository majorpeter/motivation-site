import redminelib
from flask import render_template


class Tasks:
    OPEN_CLOSED_ID = 'tasks-open-closed'
    STATE_COLOR_MAP = {
        #TODO
    }

    def __init__(self, config):
        self._config = config
        self._redmine = redminelib.Redmine(config['url'], key=config['api_key'])

    def chart_open_closed(self):
        states = self._redmine.issue_status.all()
        names = []
        counts = []
        urls = []
        backgrounds = []
        for state in states:
            if len(state.issues) > 0:
                names.append(state.name)
                counts.append(len(state.issues))
                urls.append(self.issue_by_state_listing_url(state.id))
                backgrounds.append(self._get_background_color_for_issue_state(state.id))
        return render_template('tasks_open_closed_content.html', names=names, counts=counts, urls=urls,
                               backgrounds=backgrounds)

    @staticmethod
    def chart_open_closed_lazyload():
        return render_template('tasks_open_closed.html', id=Tasks.OPEN_CLOSED_ID)

    def issue_by_state_listing_url(self, state_id):
        #TODO nicer solution :/
        return self._config['url'] + 'issues?utf8=✓&set_filter=1&sort=id%3Adesc&f%5B%5D=status_id&op%5Bstatus_id%5D=%3D&v%5Bstatus_id%5D%5B%5D=' + str(state_id) + '&f%5B%5D='

    def _get_background_color_for_issue_state(self, state_id):
        if 'issue_state_colors' in self._config:
            if state_id in self._config['issue_state_colors']:
                return self._config['issue_state_colors'][state_id]
        # fall back to default from chartjs
        return '#0000001A'
