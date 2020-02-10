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
        for state in states:
            names.append(state.name)
            counts.append(len(state.issues))
        return render_template('tasks_open_closed_content.html', names=names, counts=counts)

    @staticmethod
    def chart_open_closed_lazyload():
        return render_template('tasks_open_closed.html', id=Tasks.OPEN_CLOSED_ID)
