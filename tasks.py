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
        for state in states:
            names.append(state.name)
            counts.append(len(state.issues))
            urls.append(self.issue_by_state_listing_url(state.id))
        return render_template('tasks_open_closed_content.html', names=names, counts=counts, urls=urls)

    @staticmethod
    def chart_open_closed_lazyload():
        return render_template('tasks_open_closed.html', id=Tasks.OPEN_CLOSED_ID)

    def issue_by_state_listing_url(self, state_id):
        #TODO nicer solution :/
        return self._config['url'] + 'issues?utf8=✓&set_filter=1&sort=id%3Adesc&f%5B%5D=status_id&op%5Bstatus_id%5D=%3D&v%5Bstatus_id%5D%5B%5D=' + str(state_id) + '&f%5B%5D='
