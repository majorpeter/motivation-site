import yaml
from flask import Flask, render_template

import agenda
import quotes
from workout import Workout

app = Flask(__name__)
with open('config.yaml', 'r') as f:
    config = yaml.full_load(f)

_workout = None
if 'workout' in config:
    _workout = Workout(config['workout'])


@app.route('/')
def index_page():
    data = ''
    navigation = []

    data += quotes.quote()
    navigation.append(('intro', 'Quote of the day'))

    data += agenda.agenda_lazy_load()
    navigation.append(('agenda', 'Agenda'))

    if _workout is not None:
        data += Workout.chart_lazy_load()
        navigation.append(('workout-chart', 'Workout Chart'))

        data += Workout.calendar_lazy_load()
        navigation.append(('workout-stats', 'Workout Stats'))

    return render_template('index.html',
                           navigation=navigation,
                           sections_data=data)


@app.route('/agenda')
def agenda_get():
    return agenda.agenda()


@app.route('/workout-chart')
def workout_chart_get():
    return _workout.chart_content()


@app.route('/workout-calendar')
def workout_calendar_get():
    return _workout.calendar_content()


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(host='0.0.0.0', debug=True)
