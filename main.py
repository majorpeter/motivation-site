from flask import Flask, render_template

import quotes
import workout

app = Flask(__name__)


@app.route('/')
def index_page():
    days_since_workout_message, days_since_workout_icon = workout.days_since_workout_message_html()
    workout_cal_header, workout_cal = workout.workout_calendar()
    workout_days_data = workout.get_workout_days_for_range()

    workout_dates = [x['date'] for x in workout_days_data]
    weight_measurements = [x['weight'] if 'weight' in x else None for x in workout_days_data]
    workouts_per_week = [x['count'] for x in workout_days_data]

    workout_dates.reverse()
    weight_measurements.reverse()
    workouts_per_week.reverse()

    data = {
        'quote': quotes.get_random_quote()[:-1].replace('\n', '<br/>'),
        'days_since_workout': days_since_workout_message,
        'days_since_workout_fas_icon': days_since_workout_icon,
        'workout_cal_header': workout_cal_header,
        'workout_cal': workout_cal,
        'workout_dates': workout_dates,
        'workouts_per_week': workouts_per_week,
        'weight_measurements': weight_measurements,
        'workout': workout_days_data,
    }
    return render_template('index.html', **data)


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(host='0.0.0.0', debug=True)
