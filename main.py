from flask import Flask, render_template

import agenda
import quotes
import workout

app = Flask(__name__)


@app.route('/')
def index_page():
    data = ''
    data += quotes.quote()
    data += agenda.agenda()
    data += workout.workout_chart()
    data += workout.workout_calendar()

    return render_template('index.html',
                           sections_data=data)


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(host='0.0.0.0', debug=True)
