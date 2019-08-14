from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/generic')
def generic():
    return render_template('generic.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


app.run(debug=True)
