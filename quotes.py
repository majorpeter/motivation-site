import os
from random import randint

from flask import render_template


def read_quotes_db():
    fname = 'quotes.txt'
    if not os.path.exists(fname):
        fname = 'quotes.sample.txt'

    with open(fname, 'r') as f:
        quotes = []
        s = ''
        while True:
            line = f.readline()
            if line == '':
                break
            if line == '\n' and s != '':
                quotes.append(s)
                s = ''
            else:
                s += line
        if s != '':
            quotes.append(s)
    return quotes


def get_random_quote():
    quotes = read_quotes_db()
    return quotes[randint(0, len(quotes) -1)]


def quote():
    return render_template('quote.html', quote=get_random_quote()[:-1].replace('\n', '<br/>'))
