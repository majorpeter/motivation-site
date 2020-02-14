from collections import namedtuple

import yaml
from flask import Flask, render_template

import quotes
from agenda import Agenda
from tasks import Tasks
from workout import Workout

NavigationItem = namedtuple('NavigationItem', 'id title icon')

app = Flask(__name__)
with open('config.yaml', 'r') as f:
    config = yaml.full_load(f)

_agenda = Agenda()
_workout = None
if 'workout' in config:
    _workout = Workout(config['workout'])
_tasks = None
if 'redmine' in config:
    _tasks = Tasks(config['redmine'])


@app.route('/')
def index_page():
    data = ''
    navigation = []

    data += quotes.quote()
    navigation.append(NavigationItem('quote-of-the-day', 'Quote of the day', 'message'))

    data += _agenda.render_agenda_cached()
    navigation.append(NavigationItem('agenda', 'Agenda', 'calendar_today'))

    if _workout is not None:
        data += Workout.chart_lazy_load()
        navigation.append(NavigationItem('workout-chart', 'Workout Chart', 'show_chart'))

        data += Workout.calendar_lazy_load()
        navigation.append(NavigationItem('workout-stats', 'Workout Stats', 'table_chart'))

    if _tasks is not None:
        data += Tasks.chart_open_closed_lazyload()
        navigation.append(NavigationItem(Tasks.OPEN_CLOSED_ID, 'Tasks Open/Closed', 'playlist_add_check'))

    return render_template('index.html',
                           navigation=navigation,
                           sections_data=data)


@app.route('/agenda')
def agenda_get():
    return _agenda.render_agenda_content()


@app.route('/workout-chart')
def workout_chart_get():
    return _workout.chart_content()


@app.route('/workout-calendar')
def workout_calendar_get():
    return _workout.calendar_content()


@app.route('/tasks-open-closed')
def tasks_open_closed_get():
    return _tasks.chart_open_closed()


@app.route('/tasks-in-progress')
def tasks_in_progress():
    return _tasks.get_in_progress_list_html()


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(host='0.0.0.0', debug=True, use_reloader=False)
