from collections import namedtuple

import yaml
from flask import Flask, render_template
from flask_babel import Babel, gettext

import quotes
from agenda import Agenda
from tasks import Tasks
from workout import Workout

NavigationItem = namedtuple('NavigationItem', 'id title icon')

app = Flask(__name__)
with open('config.yaml', 'r') as f:
    config = yaml.full_load(f)

locale = config['locale'] if 'locale' in config else 'en'
babel = Babel(app, default_locale=locale)

_agenda = Agenda()
_workout = None
if 'workout' in config:
    _workout = Workout(config['workout'])
_tasks = None
if 'redmine' in config:
    _tasks = Tasks(config['redmine'])


@app.route('/')
def index_page():
    content_left = ''
    content_right = ''
    navigation = []

    content_right += quotes.quote()
    navigation.append(NavigationItem('quote-of-the-day', gettext('Quote of the day'), 'message'))

    content_right += _agenda.render_agenda_cached()
    navigation.append(NavigationItem('agenda', gettext('Agenda'), 'calendar_today'))

    if _workout is not None:
        content_left += _workout.render_layout()
        navigation.append(NavigationItem('workout-chart', gettext('Workout Chart'), 'show_chart'))

    if _tasks is not None:
        content_left += _tasks.render_layout()
        navigation.append(NavigationItem(Tasks.OPEN_CLOSED_ID, gettext('Tasks Open/Closed'), 'playlist_add_check'))

    return render_template('index.html',
                           title=config['title'] if 'title' in config else gettext('Motivational Site'),
                           navigation=navigation,
                           content_left=content_left,
                           content_right=content_right)


@app.route('/agenda')
def agenda_get():
    return _agenda.render_agenda_content()


@app.route('/workout-chart')
def workout_chart_get():
    return _workout.render_chart_content()


@app.route('/workout-calendar')
def workout_calendar_get():
    return _workout.render_calendar_content()


@app.route('/tasks-open-closed')
def tasks_open_closed_get():
    return _tasks.render_chart_states()


@app.route('/tasks-in-progress')
def tasks_in_progress():
    return _tasks.render_in_progress_list_html()


@app.route('/tasks-contributions')
def tasks_contributions():
    return _tasks.render_chart_contributions()


@app.route('/tasks-open-closed-timeline')
def tasks_open_closed_timeline():
    return _tasks.render_chart_open_closed_timeline()


app.run(host='0.0.0.0', debug=True, use_reloader=False)
