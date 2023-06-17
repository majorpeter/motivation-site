from collections import namedtuple

import yaml
from flask import Flask, render_template, request
from flask_babel import Babel, gettext

import quotes
from agenda import Agenda
from audio import Audio
from journaling import Journaling
from tasks import Tasks
from todos import Todos
from user import get_user_content_right
from workout import Workout

NavigationItem = namedtuple('NavigationItem', 'id title icon')

app = Flask(__name__)
with open('config.yaml', 'r') as f:
    config = yaml.full_load(f)

locale = config['locale'] if 'locale' in config else 'en'
babel = Babel(app, default_locale=locale)

with app.app_context():  # this is required to have translations in loading functions
    _agenda = Agenda()
    _journaling = Journaling(config['journaling'])
    _workout = None
    if 'workout' in config:
        _workout = Workout(config['workout'])
    _tasks = None
    if 'redmine' in config:
        config['redmine']['date_format'] = config['date_format']  # copy from global
        _tasks = Tasks(config['redmine'])
    _todos = None
    if 'todos' in config:
        _todos = Todos(config['todos'])
    _audio = None
    if 'audio' in config:
        _audio = Audio(config['audio'])


@app.route('/')
def index_page():
    content_left = ''
    content_right = ''
    navigation = []

    content_right += _agenda.render_agenda_cached()
    navigation.append(NavigationItem('agenda', gettext('Agenda'), 'calendar_today'))

    content_right += get_user_content_right()

    content_right += _journaling.render_journal() + render_template('journaling_static.html')
    navigation.append(NavigationItem('journaling', gettext('Journal'), 'class'))

    content_right += quotes.quote()
    navigation.append(NavigationItem('quote-of-the-day', gettext('Quote of the day'), 'message'))

    if _todos is not None:
        content_left += _todos.render_layout()
    if _workout is not None:
        content_left += _workout.render_layout()
        navigation.append(NavigationItem('workout-chart', gettext('Workout Chart'), 'show_chart'))

    if _tasks is not None:
        content_left += _tasks.render_layout()
        navigation.append(NavigationItem(Tasks.OPEN_CLOSED_ID, gettext('Tasks Open/Closed'), 'playlist_add_check'))

    if _audio is not None:
        content_right += _audio.render_layout()

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

@app.route('/tasks-closed')
def tasks_closed_get():
    return _tasks.render_random_closed_task()


@app.route('/tasks-states')
def tasks_states_data_get():
    return _tasks.get_chart_states_data()


@app.route('/tasks-in-progress')
def tasks_in_progress():
    return _tasks.render_in_progress_list_html()


@app.route('/tasks-contributions')
def tasks_contributions():
    return _tasks.render_chart_contributions()


@app.route('/tasks-open-closed-timeline')
def tasks_open_closed_timeline():
    return _tasks.render_chart_open_closed_timeline()


@app.route('/journal-data', methods=['GET', 'POST'])
def journal_data_get_set():
    if request.method == 'POST':
        days_before = int(request.form.get('days_before')) if 'days_before' in request.form else None
        _journaling.set_journal_data(entries=request.form.getlist('entries[]'), days_before=days_before)

    days_before = int(request.args['days_before']) if 'days_before' in request.args else None
    return _journaling.get_journal_data(days_before=days_before)


@app.route('/journal')
def journal_box():
    return _journaling.render_journal(update_from_server=request.args.get('update') == 'true')


@app.route('/todos')
def todos():
    return _todos.render_content()


app.run(host='0.0.0.0', debug=True, use_reloader=False)
