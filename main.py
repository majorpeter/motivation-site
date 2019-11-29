from flask import Flask, render_template

import agenda
import quotes
import workout

app = Flask(__name__)


@app.route('/')
def index_page():
    data = ''
    data += quotes.quote()
    data += agenda.agenda_lazy_load()
    data += workout.chart_lazy_load()
    data += workout.calendar_lazy_load()

    return render_template('index.html',
                           sections_data=data)


@app.route('/agenda')
def agenda_get():
    return agenda.agenda()


@app.route('/workout-chart')
def workout_chart_get():
    return workout.chart_content()


@app.route('/workout-calendar')
def workout_calendar_get():
    return workout.calendar_content()


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(host='0.0.0.0', debug=True)
