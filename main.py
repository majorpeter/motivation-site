from flask import Flask, render_template

import quotes
import workout

app = Flask(__name__)


@app.route('/')
def index_page():
    days_since_workout_message, days_since_workout_icon = workout.days_since_workout_message_html()
    workout_cal_header, workout_cal = workout.workout_calendar()
    data = {
        'quote': quotes.get_random_quote()[:-1].replace('\n', '<br/>'),
        'days_since_workout': days_since_workout_message,
        'days_since_workout_fas_icon': days_since_workout_icon,
        'workout_cal_header': workout_cal_header,
        'workout_cal': workout_cal,
        'workout': workout.get_workout_days_for_range()
    }
    return render_template('index.html', **data)


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(debug=True)
