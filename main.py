from flask import Flask, render_template

import quotes

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html', quote=quotes.get_random_quote()[:-1].replace('\n', '<br/>'))


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(debug=True)
